"""The calendar, which holds one person's schedule."""

import dataclasses
import datetime as dt

from schedules.objects import DayLocation, Person, Trip


@dataclasses.dataclass
class Calendar:
    """A single person's schedule."""

    person: Person
    trips: list[Trip]

    def get_daily_calendar(self, start_date: dt.date, end_date: dt.date) -> dict[dt.date, DayLocation]:
        """Construct a calendar of where the person is on every day."""
        num_days = (end_date - start_date).days + 1  # Include endpoints
        daily_calendar: dict[dt.date, DayLocation] = {}

        # Determine where person starts and ends each day
        for day in (start_date + dt.timedelta(days=i) for i in range(num_days)):
            start_location = self.person.home_location
            end_location = self.person.home_location
            daily_calendar[day] = DayLocation(start_location, end_location)

        return daily_calendar
