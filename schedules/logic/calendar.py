"""The calendar, which holds one person's schedule."""

import datetime as dt
import logging
from typing import Any, MutableMapping, Set

from schedules.logic.requests import Request, RequestType, Response
from schedules.logic.errors import CalendarBaseException, CalendarError
from schedules.logic.objects import Day, Location, Person, Trip


class SinglePersonCalendar:
    """A single person's calendar."""

    def __init__(self, person: Person) -> None:
        self.person: Person = person
        self._home: Location = person.home
        self._trips: Set[Trip] = set()
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

    def _get_travel_start_of_trip(self, trip_idx: int) -> Day:
        trip = self.trip_list[trip_idx]

        # If first trip, start at home
        if trip == self.trip_list[0]:
            return Day(start=self._home, end=trip.location)

        # If trip starts on or before last day of previous trip, travel straight
        previous_trip = self.trip_list[trip_idx - 1]
        if trip.start_date <= previous_trip.end_date:
            return Day(start=previous_trip.location, end=trip.location)

        # Else travel from home
        return Day(start=self._home, end=trip.location)

    def _get_travel_end_of_trip(self, trip_idx: int) -> Day:
        trip = self.trip_list[trip_idx]

        # If trip ends before last day of previous trip, travel back there
        if trip != self.trip_list[0] and trip.end_date < (previous_trip := self.trip_list[trip_idx - 1]).end_date:
            return Day(start=trip.location, end=previous_trip.location)

        # If last trip, end at home
        if trip == self.trip_list[-1]:
            return Day(start=trip.location, end=self._home)

        # If trip ends on first day of next trip, travel straight
        next_trip = self.trip_list[trip_idx + 1]
        if trip.end_date == next_trip.start_date:
            return Day(start=trip.location, end=next_trip.location)

        # Else travel to home
        return Day(start=trip.location, end=self._home)

    def _get_travel_days(self) -> dict[dt.date, Day]:
        """Determine the days at which travel occurs."""
        if not self._trips:
            return dict()

        travel_days: dict[dt.date, Day] = {}
        for trip_idx, trip in enumerate(self.trip_list):
            travel_days[trip.start_date] = self._get_travel_start_of_trip(trip_idx)
            travel_days[trip.end_date] = self._get_travel_end_of_trip(trip_idx)

        return travel_days

    def get_daily_calendar(self, start_date: dt.date, end_date: dt.date) -> dict[dt.date, Day]:
        """Construct a calendar of where the person is on every day."""
        num_days = (end_date - start_date).days + 1  # Include endpoints
        daily_calendar: dict[dt.date, Day] = {}

        # Determine where person starts and ends each day
        travel_days = self._get_travel_days()
        for day in (start_date + dt.timedelta(days=i) for i in range(num_days)):
            if not travel_days or day < min(travel_days) or day > max(travel_days):
                daily_calendar[day] = Day(start=self._home, end=self._home)
            elif day in travel_days:
                daily_calendar[day] = travel_days[day]
            else:
                last_travel_day = max(date for date in travel_days.keys() if date < day)
                last_travel_end = travel_days[last_travel_day].end
                daily_calendar[day] = Day(start=last_travel_end, end=last_travel_end)

        return daily_calendar


class FullCalendar:
    """A full calendar, with multiple people."""

    def __init__(self) -> None:
        self.calendars: MutableMapping[Person, SinglePersonCalendar] = dict()

    def __repr__(self) -> str:
        return f"FullCalendar({','.join(sorted(str(person) for person in self.calendars.keys()))})"

    def _add_person(self, person: Person) -> None:
        if person in self.calendars.keys():
            raise CalendarError(f"Person {person} is already in calendar.")
        self.calendars[person] = SinglePersonCalendar(person)
        logging.info("Added %s to calendar", person)

    def process_frontend_request(self, request_raw: MutableMapping[str, Any]) -> Response:
        """Process request (e.g. POST) from frontend and return string response."""
        logging.info("Processing request %s", request_raw)
        request = Request(request_raw)
        if request.request_type == RequestType.ADD_PERSON:
            try:
                person = Person.from_request(request)
                self._add_person(person)
                return Response(code=200, message=f"Added person {person}.")
            except CalendarBaseException as err:
                return Response(code=400, message=f"Failed to add person: {err.message}")
        else:
            return Response(code=400, message=f"Unknown request type: `{request.request_type}`.")

    def render(self) -> str:
        logging.info("Rendering calendar.")
        return f"TODO: Render Calendar Here."
