import datetime as dt

from schedules.calendar import Calendar
from schedules.objects import Country, DayLocation, Location, Person, StrID


def default_location() -> Location:
    return Location(country=Country.NETHERLANDS, city=StrID("Amsterdam"))


def sample_person() -> Person:
    return Person(
        last_name=StrID("lastname"),
        first_name=StrID("firstname"),
        home_location=default_location(),
    )


class TestCalendar:
    def test_daily_calendar_no_trips(self):

        calendar = Calendar(person=sample_person(), trips=[])
        home_all_day = DayLocation(start=default_location(), end=default_location())

        daily_calendar_actual = calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 24))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): home_all_day,
            dt.date(2024, 6, 23): home_all_day,
            dt.date(2024, 6, 24): home_all_day,
        }
        assert daily_calendar_actual == daily_calendar_expected
