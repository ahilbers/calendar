import datetime as dt

import pytest

from schedules.calendar import Calendar
from schedules.objects import Country, Day, Location, Person, StrID, Trip


@pytest.fixture
def sample_home_location() -> Location:
    return Location(country=Country.NETHERLANDS, city=StrID("Amsterdam"))


@pytest.fixture
def sample_person(sample_home_location: Location) -> Person:
    return Person(
        last_name=StrID("lastname"),
        first_name=StrID("firstname"),
        home=sample_home_location,
    )


def test_daily_calendar_no_trips(sample_person: Person):
    """Without any trips, the daily calendar should be starting and ending each day in the home location."""

    calendar = Calendar(person=sample_person, trips=set())

    daily_calendar_actual = calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 24))

    daily_calendar_expected = {
        dt.date(2024, 6, 22): Day(start=sample_person.home, end=sample_person.home),
        dt.date(2024, 6, 23): Day(start=sample_person.home, end=sample_person.home),
        dt.date(2024, 6, 24): Day(start=sample_person.home, end=sample_person.home),
    }
    assert daily_calendar_actual == daily_calendar_expected


def test_daily_calendar_trip_in_calendar(sample_home_location: Location, sample_person: Person):
    """A single trip inside the calendar should be calculated properly."""

    trip_location = Location(country=Country.NETHERLANDS, city=StrID("Zurich"))
    trip = Trip(
        location=trip_location,
        start_date=dt.date(2024, 6, 23),
        end_date=dt.date(2024, 6, 24),
    )
    calendar = Calendar(person=sample_person, trips={trip})

    daily_calendar_actual = calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 25))

    daily_calendar_expected = {
        dt.date(2024, 6, 22): Day(start=sample_home_location, end=sample_home_location),
        dt.date(2024, 6, 23): Day(start=sample_home_location, end=trip_location),
        dt.date(2024, 6, 24): Day(start=trip_location, end=sample_home_location),
        dt.date(2024, 6, 25): Day(start=sample_home_location, end=sample_home_location),
    }
    assert daily_calendar_actual == daily_calendar_expected
