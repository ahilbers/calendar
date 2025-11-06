import datetime as dt

import pytest

from schedules.calendar import Calendar
from schedules.objects import Country, Day, Location, Person, StrID, Trip


def sample_home_location() -> Location:
    return Location(country=Country.NETHERLANDS, city=StrID("Amsterdam"))


def sample_person() -> Person:
    return Person(
        last_name=StrID("lastname"),
        first_name=StrID("firstname"),
        home=sample_home_location(),
    )


class TestDailyCalendar:
    """Tests for calendar.get_daily_calendar."""

    def test_no_trips(self):
        """Without any trips, the daily calendar should be starting and ending each day in the home location."""

        person = sample_person()
        calendar = Calendar(person)

        daily_calendar_actual = calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 24))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): Day(start=person.home, end=person.home),
            dt.date(2024, 6, 23): Day(start=person.home, end=person.home),
            dt.date(2024, 6, 24): Day(start=person.home, end=person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected

    def test_single_trip(self):
        """A single trip inside the calendar should be calculated properly."""

        person = sample_person()
        trip = Trip(
            location=Location(country=Country.NETHERLANDS, city=StrID("Zurich")),
            start_date=dt.date(2024, 6, 23),
            end_date=dt.date(2024, 6, 24),
        )
        calendar = Calendar(person)
        calendar.add_trip(trip)

        daily_calendar_actual = calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 25))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): Day(start=person.home, end=person.home),
            dt.date(2024, 6, 23): Day(start=person.home, end=trip.location),
            dt.date(2024, 6, 24): Day(start=trip.location, end=person.home),
            dt.date(2024, 6, 25): Day(start=person.home, end=person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected

    def test_multiple_trips_disjoint(self):

        person = sample_person()
        trip_1 = Trip(
            location=Location(country=Country.NETHERLANDS, city=StrID("Zurich")),
            start_date=dt.date(2024, 6, 23),
            end_date=dt.date(2024, 6, 24),
        )
        trip_2 = Trip(
            location=Location(country=Country.UNITED_KINGDOM, city=StrID("London")),
            start_date=dt.date(2024, 6, 25),
            end_date=dt.date(2024, 6, 26),
        )
        calendar = Calendar(person)
        calendar.add_trip(trip_1)
        calendar.add_trip(trip_2)

        daily_calendar_actual = calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 27))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): Day(start=person.home, end=person.home),
            dt.date(2024, 6, 23): Day(start=person.home, end=trip_1.location),
            dt.date(2024, 6, 24): Day(start=trip_1.location, end=person.home),
            dt.date(2024, 6, 25): Day(start=person.home, end=trip_2.location),
            dt.date(2024, 6, 26): Day(start=trip_2.location, end=person.home),
            dt.date(2024, 6, 27): Day(start=person.home, end=person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected
