import datetime as dt

import pytest

from schedules.calendar import Calendar
from schedules.errors import TripNotValidError
from schedules.objects import Country, Day, Location, Person, StrID, Trip


def sample_home_location() -> Location:
    return Location(country=Country.NETHERLANDS, city=StrID("Amsterdam"))


def sample_person() -> Person:
    return Person(
        last_name=StrID("lastname"),
        first_name=StrID("firstname"),
        home=sample_home_location(),
    )


class TestAddTrips:
    """Tests for calendar.add_trip."""

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.calendar = Calendar(sample_person())

    def test_no_trips(self):
        assert not self.calendar.trip_list

    def test_single_trip(self):
        trip = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 24))
        self.calendar.add_trip(trip)
        assert self.calendar.trip_list == [trip]

    def test_trips_returned_ordered(self):
        trip_later = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 25), dt.date(2024, 6, 26))
        trip_earlier = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 24))

        self.calendar.add_trip(trip_later)
        self.calendar.add_trip(trip_earlier)

        assert self.calendar.trip_list == [trip_earlier, trip_later]

    def test_fail_if_same_start_date(self, caplog: pytest.LogCaptureFixture):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 24))
        trip_2 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        self.calendar.add_trip(trip_1)
        with pytest.raises(TripNotValidError):
            self.calendar.add_trip(trip_2)

    def test_fail_if_same_end_date(self, caplog: pytest.LogCaptureFixture):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 24))
        trip_2 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 22), dt.date(2024, 6, 24))
        self.calendar.add_trip(trip_1)
        with pytest.raises(TripNotValidError):
            self.calendar.add_trip(trip_2)

    def test_fail_if_overlapping_and_starting_earlier(self, caplog: pytest.LogCaptureFixture):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        trip_2 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 22), dt.date(2024, 6, 24))
        self.calendar.add_trip(trip_1)
        with pytest.raises(TripNotValidError):
            self.calendar.add_trip(trip_2)

    def test_fail_if_overlapping_and_starting_later(self, caplog: pytest.LogCaptureFixture):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        trip_2 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 24), dt.date(2024, 6, 26))
        self.calendar.add_trip(trip_1)
        with pytest.raises(TripNotValidError):
            self.calendar.add_trip(trip_2)

    def test_trip_fully_contained(self):
        """A trip that is fully contained in another should be added without issues."""
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 22), dt.date(2024, 6, 25))
        trip_2 = Trip(Location(Country.UNITED_KINGDOM, StrID("London")), dt.date(2024, 6, 23), dt.date(2024, 6, 24))
        self.calendar.add_trip(trip_1)
        self.calendar.add_trip(trip_2)
        assert self.calendar.trip_list == [trip_1, trip_2]


class TestDailyCalendar:
    """Tests for calendar.get_daily_calendar."""

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.calendar = Calendar(sample_person())

    def test_no_trips(self):
        """Without any trips, the daily calendar should be starting and ending each day in the home location."""

        daily_calendar_actual = self.calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 24))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): Day(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 23): Day(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 24): Day(start=self.calendar.person.home, end=self.calendar.person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected

    def test_single_trip(self):
        """A single trip inside the calendar should be calculated properly."""

        trip = Trip(Location(Country.NETHERLANDS, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        self.calendar.add_trip(trip)

        daily_calendar_actual = self.calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 26))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): Day(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 23): Day(start=self.calendar.person.home, end=trip.location),
            dt.date(2024, 6, 24): Day(start=trip.location, end=trip.location),
            dt.date(2024, 6, 25): Day(start=trip.location, end=self.calendar.person.home),
            dt.date(2024, 6, 26): Day(start=self.calendar.person.home, end=self.calendar.person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected

    def test_trips_disjoint(self):

        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        trip_2 = Trip(Location(Country.UNITED_KINGDOM, StrID("London")), dt.date(2024, 6, 27), dt.date(2024, 6, 29))
        self.calendar.add_trip(trip_1)
        self.calendar.add_trip(trip_2)

        daily_calendar_actual = self.calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 30))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): Day(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 23): Day(start=self.calendar.person.home, end=trip_1.location),
            dt.date(2024, 6, 24): Day(start=trip_1.location, end=trip_1.location),
            dt.date(2024, 6, 25): Day(start=trip_1.location, end=self.calendar.person.home),
            dt.date(2024, 6, 26): Day(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 27): Day(start=self.calendar.person.home, end=trip_2.location),
            dt.date(2024, 6, 28): Day(start=trip_2.location, end=trip_2.location),
            dt.date(2024, 6, 29): Day(start=trip_2.location, end=self.calendar.person.home),
            dt.date(2024, 6, 30): Day(start=self.calendar.person.home, end=self.calendar.person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected

    def test_trips_connected(self):

        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        trip_2 = Trip(Location(Country.UNITED_KINGDOM, StrID("London")), dt.date(2024, 6, 25), dt.date(2024, 6, 27))
        self.calendar.add_trip(trip_1)
        self.calendar.add_trip(trip_2)

        daily_calendar_actual = self.calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 28))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): Day(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 23): Day(start=self.calendar.person.home, end=trip_1.location),
            dt.date(2024, 6, 24): Day(start=trip_1.location, end=trip_1.location),
            dt.date(2024, 6, 25): Day(start=trip_1.location, end=trip_2.location),
            dt.date(2024, 6, 26): Day(start=trip_2.location, end=trip_2.location),
            dt.date(2024, 6, 27): Day(start=trip_2.location, end=self.calendar.person.home),
            dt.date(2024, 6, 28): Day(start=self.calendar.person.home, end=self.calendar.person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected

    def test_trip_fully_contained(self):

        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 22), dt.date(2024, 6, 28))
        trip_2 = Trip(Location(Country.UNITED_KINGDOM, StrID("London")), dt.date(2024, 6, 24), dt.date(2024, 6, 26))
        self.calendar.add_trip(trip_1)
        self.calendar.add_trip(trip_2)

        daily_calendar_actual = self.calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 28))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): Day(start=self.calendar.person.home, end=trip_1.location),
            dt.date(2024, 6, 23): Day(start=trip_1.location, end=trip_1.location),
            dt.date(2024, 6, 24): Day(start=trip_1.location, end=trip_2.location),
            dt.date(2024, 6, 25): Day(start=trip_2.location, end=trip_2.location),
            dt.date(2024, 6, 26): Day(start=trip_2.location, end=trip_1.location),
            dt.date(2024, 6, 27): Day(start=trip_1.location, end=trip_1.location),
            dt.date(2024, 6, 28): Day(start=trip_1.location, end=self.calendar.person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected
