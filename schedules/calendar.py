"""The calendar, which holds one person's schedule."""

import dataclasses
import datetime as dt

from schedules.objects import Day, Person, Trip


@dataclasses.dataclass
class Calendar:
    """A single person's schedule."""

    person: Person
    trips: set[Trip]

    def __post_init__(self):
        self._home = self.person.home
        self._travel_days = self._get_travel_days()

    def _get_travel_days(self) -> dict[dt.date, Day]:
        """Construct a daily calendar starting on the day of the first trip and ending in the day of the last trip."""
        if not self.trips:
            return dict()

        trips_ordered = sorted(self.trips, key=lambda trip: (trip.start_date, trip.end_date))
        travel_days: dict[dt.date, Day] = {}

        for trip in trips_ordered:
            travel_days[trip.start_date] = Day(start=self._home, end=trip.location)
            travel_days[trip.end_date] = Day(start=trip.location, end=self._home)

        return travel_days

    def get_daily_calendar(self, start_date: dt.date, end_date: dt.date) -> dict[dt.date, Day]:
        """Construct a calendar of where the person is on every day."""
        num_days = (end_date - start_date).days + 1  # Include endpoints
        daily_calendar: dict[dt.date, Day] = {}

        # Determine where person starts and ends each day
        for day in (start_date + dt.timedelta(days=i) for i in range(num_days)):
            if not self._travel_days or day < min(self._travel_days) or day > max(self._travel_days):
                daily_calendar[day] = Day(start=self._home, end=self._home)
            elif day in self._travel_days:
                daily_calendar[day] = self._travel_days[day]

        return daily_calendar
