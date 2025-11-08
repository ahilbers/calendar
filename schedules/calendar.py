"""The calendar, which holds one person's schedule."""

import datetime as dt
import logging
from typing import Set

from schedules.errors import TripNotValidError
from schedules.objects import Day, Location, Person, Trip


class Calendar:
    """A single person's calendar."""

    def __init__(self, person: Person) -> None:
        self.person: Person = person
        self._home: Location = person.home
        self._trips: Set[Trip] = set()
        logging.info("Created calendar for %s", self.person)

    def __repr__(self):
        return f"Calendar({self.person})"

    def _raise_if_invalid_trip(self, candidate: Trip) -> None:
        """Check candidate new trip against existing trips and raise if it is invalid."""
        for existing in self._trips:
            if candidate.start_date == existing.start_date:
                print(0)
                raise TripNotValidError(f"Candidate {candidate} has same start date as {existing}.")
            if candidate.end_date == existing.end_date:
                raise TripNotValidError(f"Candidate {candidate} has same end date as {existing}.")
            if candidate.start_date < existing.start_date and candidate.end_date > existing.start_date:
                raise TripNotValidError(f"Candidate {candidate} falls partially in {existing}.")
            if candidate.start_date < existing.end_date and candidate.end_date > existing.end_date:
                raise TripNotValidError(f"Candidate {candidate} falls partially in {existing}.")

    @property
    def trip_list(self) -> list[Trip]:
        """Get list of trips, in order from earliest to latest."""
        return sorted(self._trips, key=lambda trip: (trip.start_date, trip.end_date))

    def add_trip(self, trip: Trip) -> None:
        try:
            self._raise_if_invalid_trip(candidate=trip)
            logging.info("Adding trip %s to calendar %s", trip, self)
            self._trips.add(trip)
        except TripNotValidError as err:
            logging.exception("Failed to add trip: %s", err)

    def _get_travel_days(self) -> dict[dt.date, Day]:
        """Construct a daily calendar starting on the day of the first trip and ending in the day of the last trip."""
        if not self._trips:
            return dict()

        travel_days: dict[dt.date, Day] = {}

        for trip in self.trip_list:
            travel_days[trip.start_date] = Day(start=self._home, end=trip.location)
            travel_days[trip.end_date] = Day(start=trip.location, end=self._home)

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

        return daily_calendar
