"""The calendar, which holds one person's schedule."""

import datetime as dt
import logging
from typing import Any, OrderedDict, TYPE_CHECKING

from schedules.logic.requests import Mapping, Request, RequestType, Response
from schedules.logic.errors import (
    CalendarBaseException,
    CalendarError,
    RequestError,
    get_message_from_handled_error_else_raise,
)
from schedules.logic.objects import DayLocation, Location, Person, Trip

if TYPE_CHECKING:
    from schedules.logic.storage import CalendarRepository


class SinglePersonCalendar:
    """A single person's calendar."""

    def __init__(self, person: Person) -> None:
        self.person: Person = person
        self._home: Location = person.home
        self._trips: set[Trip] = set()
        self._trip_list_cache: list[Trip] | None = None  # Cache sorted list, cleared whenever new trip is added
        logging.info("Created calendar for %s", self.person)

    def __repr__(self):
        return f"SinglePersonCalendar({self.person})"

    def _raise_if_invalid_trip(self, candidate: Trip) -> None:
        """Check candidate new trip against existing trips and raise if it is invalid."""
        for existing in self._trips:
            if candidate.start_date == existing.start_date:
                raise CalendarError(f"Candidate {candidate} has same start date as {existing}.")
            if candidate.end_date == existing.end_date:
                raise CalendarError(f"Candidate {candidate} has same end date as {existing}.")
            if candidate.start_date < existing.start_date and candidate.end_date > existing.start_date:
                raise CalendarError(f"Candidate {candidate} falls partially in {existing}.")
            if candidate.start_date < existing.end_date and candidate.end_date > existing.end_date:
                raise CalendarError(f"Candidate {candidate} falls partially in {existing}.")

    @property
    def trip_list(self) -> list[Trip]:
        """Get list of trips, in order from earliest to latest."""
        if self._trip_list_cache is None:
            self._trip_list_cache = sorted(self._trips, key=lambda trip: (trip.start_date, trip.end_date))
        return self._trip_list_cache

    def add_trip(self, trip: Trip) -> None:
        self._trip_list_cache = None  # Clear cache whenever new trip is added, needs to be recalculated
        self._raise_if_invalid_trip(candidate=trip)
        logging.info("Adding trip %s to calendar %s", trip, self)
        self._trips.add(trip)

    def _get_travel_start_of_trip(self, trip_idx: int) -> DayLocation:
        trip = self.trip_list[trip_idx]

        # If first trip, start at home
        if trip == self.trip_list[0]:
            return DayLocation(start=self._home, end=trip.location)

        # If trip starts on or before last day of previous trip, travel straight
        previous_trip = self.trip_list[trip_idx - 1]
        if trip.start_date <= previous_trip.end_date:
            return DayLocation(start=previous_trip.location, end=trip.location)

        # Else travel from home
        return DayLocation(start=self._home, end=trip.location)

    def _get_travel_end_of_trip(self, trip_idx: int) -> DayLocation:
        trip = self.trip_list[trip_idx]

        # If trip ends before last day of previous trip, travel back there
        if trip != self.trip_list[0] and trip.end_date < (previous_trip := self.trip_list[trip_idx - 1]).end_date:
            return DayLocation(start=trip.location, end=previous_trip.location)

        # If last trip, end at home
        if trip == self.trip_list[-1]:
            return DayLocation(start=trip.location, end=self._home)

        # If trip ends on first day of next trip, travel straight
        next_trip = self.trip_list[trip_idx + 1]
        if trip.end_date == next_trip.start_date:
            return DayLocation(start=trip.location, end=next_trip.location)

        # Else travel to home
        return DayLocation(start=trip.location, end=self._home)

    def _get_travel_days(self) -> dict[dt.date, DayLocation]:
        """Determine the days at which travel occurs."""
        if not self._trips:
            return dict()

        travel_days: dict[dt.date, DayLocation] = {}
        for trip_idx, trip in enumerate(self.trip_list):
            travel_days[trip.start_date] = self._get_travel_start_of_trip(trip_idx)
            travel_days[trip.end_date] = self._get_travel_end_of_trip(trip_idx)

        return travel_days

    def get_daily_calendar(self, start_date: dt.date, end_date: dt.date) -> dict[dt.date, DayLocation]:
        """Construct a calendar of where the person is on every day."""
        num_days = (end_date - start_date).days + 1  # Include endpoints
        daily_calendar: dict[dt.date, DayLocation] = {}

        # Determine where person starts and ends each day
        travel_days = self._get_travel_days()
        for day in (start_date + dt.timedelta(days=i) for i in range(num_days)):
            if not travel_days or day < min(travel_days) or day > max(travel_days):
                daily_calendar[day] = DayLocation(start=self._home, end=self._home)
            elif day in travel_days:
                daily_calendar[day] = travel_days[day]
            else:
                last_travel_day = max(date for date in travel_days.keys() if date < day)
                last_travel_end = travel_days[last_travel_day].end
                daily_calendar[day] = DayLocation(start=last_travel_end, end=last_travel_end)

        return daily_calendar


class FullCalendar:
    """A full calendar, with multiple people and support for interacting with frontend."""

    def __init__(self, database_repository: "CalendarRepository | None" = None) -> None:
        self.calendars: dict[Person, SinglePersonCalendar] = dict()
        self._id_to_person: dict[str, Person] = dict()
        self._database_repository = database_repository  # Optional, for persistence
        self._people_sorted_cache: list[Person] | None = None
        self._daily_calendars_start_date: dt.date | None = None
        self._daily_calendars_end_date: dt.date | None = None
        self._daily_calendars_to_display: OrderedDict[dt.date, OrderedDict[Person, DayLocation]] | None = None

    def _add_person(self, person: Person) -> None:
        if any(person == existing_person for existing_person in self.calendars.keys()):
            raise CalendarError(f"Person {person} is already in calendar.")
        self.calendars[person] = SinglePersonCalendar(person)
        self._id_to_person[str(person.unique_id)] = person
        self._people_sorted_cache = None  # Needs to be recalculated
        self._daily_calendars_to_display = None  # Needs to be recalculated
        if self._database_repository:
            self._database_repository.add_person(person)
        logging.info("Added %s to calendar", person)

    def _remove_person(self, person: Person) -> None:
        """Remove a person from the calendar and database."""
        if person not in self.calendars:
            raise CalendarError(f"Person {person} is not in calendar.")
        del self.calendars[person]
        del self._id_to_person[str(person.unique_id)]
        self._people_sorted_cache = None  # Needs to be recalculated
        self._daily_calendars_to_display = None  # Needs to be recalculated
        if self._database_repository:
            self._database_repository.remove_person(person)
        logging.info(f"Removed {person} from calendar")

    def load_from_repository(self) -> None:
        """Load all people from the repository."""
        if not self._database_repository:
            logging.warning("No database repository set. Performing no action.")
            return

        # Load people from database
        people = self._database_repository.get_all_people()
        for person in people:
            # Add person without persisting again (no repository call)
            self.calendars[person] = SinglePersonCalendar(person)
            self._id_to_person[str(person.unique_id)] = person

        # Load trips for each person from database
        for person in people:
            trips = self._database_repository.get_trips_for_person(person)
            for trip in trips:
                self.calendars[person].add_trip(trip)

        self._people_sorted_cache = None  # Needs to be recalculated
        self._daily_calendars_to_display = None  # Needs to be recalculated
        logging.info(f"Loaded {len(people)} people from repository.")

    def _add_trip(self, person: Person, trip: Trip) -> None:
        self.calendars[person].add_trip(trip)
        self._daily_calendars_to_display = None  # Needs to be recalculated
        if self._database_repository:
            self._database_repository.add_trip(person, trip)
        logging.info(f"Added {trip} to calendar for {person}.")

    def process_frontend_request(self, request_raw: Mapping[str, Any]) -> Response:
        """Process request (e.g. POST) from frontend and return string response."""
        logging.info("Processing request %s", request_raw)
        try:
            request = Request(request_raw)
        except RequestError as err:
            return Response(code=400, message=f"Failed to parse request: {err}")

        if request.request_type == RequestType.ADD_PERSON:
            try:
                person = Person.from_request(request)
                self._add_person(person)
                return Response(code=200, message=f"Added person {person}.")
            except CalendarError as err:
                message = get_message_from_handled_error_else_raise(err)
                return Response(code=400, message=f"Failed to add person: {message}")

        if request.request_type == RequestType.REMOVE_PERSON:
            try:
                person = self._id_to_person[request.payload["person_id"]]
                self._remove_person(person)
                return Response(code=200, message=f"Removed person {person}.")
            except (CalendarBaseException, KeyError) as err:
                message = get_message_from_handled_error_else_raise(err)
                return Response(code=400, message=f"Failed to remove person: {message}")

        if request.request_type == RequestType.ADD_TRIP:
            try:
                person = self._id_to_person[request.payload["person_id"]]
                trip = Trip.from_request(request)
                self._add_trip(person=person, trip=trip)
                return Response(code=200, message=f"Added {trip} to calendar for {person}.")
            except (CalendarBaseException, KeyError) as err:
                message = get_message_from_handled_error_else_raise(err)
                return Response(code=400, message=f"Failed to add trip: {message}")

        if request.request_type == RequestType.UPDATE_DAILY_CALENDARS_DATES:
            try:
                start_date = dt.date.strptime(request.payload["start_date"], "%Y-%m-%d")
                end_date = dt.date.strptime(request.payload["end_date"], "%Y-%m-%d")
                self._update_daily_calendars_dates(start_date, end_date)
                return Response(code=200, message=f"Updated daily calendars dates, {start_date} to {end_date}.")
            except (CalendarBaseException, KeyError) as err:
                message = get_message_from_handled_error_else_raise(err)
                return Response(code=400, message=f"Failed to update daily calendar: {message}")

        return Response(code=400, message=f"Unknown request type: {request.request_type}.")

    @property
    def people_sorted_by_name(self) -> list[Person]:
        if not self._people_sorted_cache:
            self._people_sorted_cache = sorted(
                self.calendars.keys(), key=lambda person: (person.last_name, person.first_name)
            )
        return self._people_sorted_cache

    @property
    def single_person_calendars(self) -> list[SinglePersonCalendar]:
        """Get list of single-person calendars, sorted by name."""
        return [self.calendars[person] for person in self.people_sorted_by_name]

    def _update_daily_calendars_dates(self, start_date: dt.date, end_date: dt.date) -> None:
        self._daily_calendars_start_date = start_date
        self._daily_calendars_end_date = end_date
        self._daily_calendars_to_display = None  # Needs to be recalculated
        logging.info(f"Updated daily calendar dates: {start_date}, {end_date}.")

    def _update_daily_calendars(self) -> None:
        start_date = self._daily_calendars_start_date
        end_date = self._daily_calendars_end_date
        if start_date is None or end_date is None:
            raise CalendarError(f"Both start_date and end_date must be set: {start_date}, {end_date}.")
        days = [start_date + dt.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
        daily_calendars = {
            person: self.calendars[person].get_daily_calendar(start_date, end_date)
            for person in self.people_sorted_by_name
        }
        self._daily_calendars_to_display = OrderedDict({
            day: OrderedDict({person: daily_calendars[person][day] for person in self.people_sorted_by_name})
            for day in days
        })  # fmt: skip
        logging.info("Updated daily calendars.")

    def get_daily_calendars_to_display(self) -> OrderedDict[dt.date, OrderedDict[Person, DayLocation]]:
        """Get daily calendars for all calendar members in format that can be used by frontend."""
        if self._daily_calendars_start_date is None or self._daily_calendars_end_date is None:
            return OrderedDict(OrderedDict())
        if self._daily_calendars_to_display is None:
            self._update_daily_calendars()
        if self._daily_calendars_to_display is None:
            raise CalendarError("Failed to update daily calendars.")
        return self._daily_calendars_to_display

    def is_everyone_together(self, date: dt.date) -> bool:
        daily_calendars = self.get_daily_calendars_to_display()
        try:
            return len(set(day.end for day in daily_calendars[date].values())) == 1
        except KeyError:
            raise CalendarError(
                f"Date {date} outside daily calendar range {min(daily_calendars.keys())}-{max(daily_calendars.keys())}."
            )
