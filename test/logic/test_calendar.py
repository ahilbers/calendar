import datetime as dt
from typing import Any

import pytest

from schedules.logic import objects
from schedules.logic.calendar import FullCalendar, SinglePersonCalendar
from schedules.logic.errors import CalendarError
from schedules.logic.objects import Country, DayLocation, Location, Person, StrID, Trip
from schedules.logic.requests import REQUEST_TYPE_ID, RequestType


def sample_home_location() -> Location:
    return Location(country=Country.NETHERLANDS, city=StrID("Amsterdam"))


def sample_person() -> Person:
    return Person(
        last_name=StrID("lastname"),
        first_name=StrID("firstname"),
        home=sample_home_location(),
    )


class TestSinglePersonCalendar:

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.calendar = SinglePersonCalendar(sample_person())

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

    def test_raises_if_same_start_date(self, caplog: pytest.LogCaptureFixture):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 24))
        trip_2 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        self.calendar.add_trip(trip_1)
        with pytest.raises(CalendarError):
            self.calendar.add_trip(trip_2)

    def test_raises_if_same_end_date(self, caplog: pytest.LogCaptureFixture):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 24))
        trip_2 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 22), dt.date(2024, 6, 24))
        self.calendar.add_trip(trip_1)
        with pytest.raises(CalendarError):
            self.calendar.add_trip(trip_2)

    def test_raises_if_overlapping_and_starting_earlier(self, caplog: pytest.LogCaptureFixture):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        trip_2 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 22), dt.date(2024, 6, 24))
        self.calendar.add_trip(trip_1)
        with pytest.raises(CalendarError):
            self.calendar.add_trip(trip_2)

    def test_raises_if_overlapping_and_starting_later(self, caplog: pytest.LogCaptureFixture):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        trip_2 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 24), dt.date(2024, 6, 26))
        self.calendar.add_trip(trip_1)
        with pytest.raises(CalendarError):
            self.calendar.add_trip(trip_2)

    def test_trip_fully_contained(self):
        """A trip that is fully contained in another should be added without issues."""
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 22), dt.date(2024, 6, 25))
        trip_2 = Trip(Location(Country.UNITED_KINGDOM, StrID("London")), dt.date(2024, 6, 23), dt.date(2024, 6, 24))
        self.calendar.add_trip(trip_1)
        self.calendar.add_trip(trip_2)
        assert self.calendar.trip_list == [trip_1, trip_2]


class TestDailyCalendar:

    @pytest.fixture(autouse=True)
    def set_up(self):
        self.calendar = SinglePersonCalendar(sample_person())

    def test_no_trips(self):
        """Without any trips, the daily calendar should be starting and ending each day in the home location."""

        daily_calendar_actual = self.calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 24))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): DayLocation(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 23): DayLocation(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 24): DayLocation(start=self.calendar.person.home, end=self.calendar.person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected

    def test_single_trip(self):
        """A single trip inside the calendar should be calculated properly."""

        trip = Trip(Location(Country.NETHERLANDS, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        self.calendar.add_trip(trip)

        daily_calendar_actual = self.calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 26))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): DayLocation(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 23): DayLocation(start=self.calendar.person.home, end=trip.location),
            dt.date(2024, 6, 24): DayLocation(start=trip.location, end=trip.location),
            dt.date(2024, 6, 25): DayLocation(start=trip.location, end=self.calendar.person.home),
            dt.date(2024, 6, 26): DayLocation(start=self.calendar.person.home, end=self.calendar.person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected

    def test_trips_disjoint(self):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        trip_2 = Trip(Location(Country.UNITED_KINGDOM, StrID("London")), dt.date(2024, 6, 27), dt.date(2024, 6, 29))
        self.calendar.add_trip(trip_1)
        self.calendar.add_trip(trip_2)

        daily_calendar_actual = self.calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 30))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): DayLocation(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 23): DayLocation(start=self.calendar.person.home, end=trip_1.location),
            dt.date(2024, 6, 24): DayLocation(start=trip_1.location, end=trip_1.location),
            dt.date(2024, 6, 25): DayLocation(start=trip_1.location, end=self.calendar.person.home),
            dt.date(2024, 6, 26): DayLocation(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 27): DayLocation(start=self.calendar.person.home, end=trip_2.location),
            dt.date(2024, 6, 28): DayLocation(start=trip_2.location, end=trip_2.location),
            dt.date(2024, 6, 29): DayLocation(start=trip_2.location, end=self.calendar.person.home),
            dt.date(2024, 6, 30): DayLocation(start=self.calendar.person.home, end=self.calendar.person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected

    def test_trips_connected(self):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 23), dt.date(2024, 6, 25))
        trip_2 = Trip(Location(Country.UNITED_KINGDOM, StrID("London")), dt.date(2024, 6, 25), dt.date(2024, 6, 27))
        self.calendar.add_trip(trip_1)
        self.calendar.add_trip(trip_2)

        daily_calendar_actual = self.calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 28))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): DayLocation(start=self.calendar.person.home, end=self.calendar.person.home),
            dt.date(2024, 6, 23): DayLocation(start=self.calendar.person.home, end=trip_1.location),
            dt.date(2024, 6, 24): DayLocation(start=trip_1.location, end=trip_1.location),
            dt.date(2024, 6, 25): DayLocation(start=trip_1.location, end=trip_2.location),
            dt.date(2024, 6, 26): DayLocation(start=trip_2.location, end=trip_2.location),
            dt.date(2024, 6, 27): DayLocation(start=trip_2.location, end=self.calendar.person.home),
            dt.date(2024, 6, 28): DayLocation(start=self.calendar.person.home, end=self.calendar.person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected

    def test_trip_fully_contained(self):
        trip_1 = Trip(Location(Country.SWITZERLAND, StrID("Zurich")), dt.date(2024, 6, 22), dt.date(2024, 6, 28))
        trip_2 = Trip(Location(Country.UNITED_KINGDOM, StrID("London")), dt.date(2024, 6, 24), dt.date(2024, 6, 26))
        self.calendar.add_trip(trip_1)
        self.calendar.add_trip(trip_2)

        daily_calendar_actual = self.calendar.get_daily_calendar(dt.date(2024, 6, 22), dt.date(2024, 6, 28))

        daily_calendar_expected = {
            dt.date(2024, 6, 22): DayLocation(start=self.calendar.person.home, end=trip_1.location),
            dt.date(2024, 6, 23): DayLocation(start=trip_1.location, end=trip_1.location),
            dt.date(2024, 6, 24): DayLocation(start=trip_1.location, end=trip_2.location),
            dt.date(2024, 6, 25): DayLocation(start=trip_2.location, end=trip_2.location),
            dt.date(2024, 6, 26): DayLocation(start=trip_2.location, end=trip_1.location),
            dt.date(2024, 6, 27): DayLocation(start=trip_1.location, end=trip_1.location),
            dt.date(2024, 6, 28): DayLocation(start=trip_1.location, end=self.calendar.person.home),
        }
        assert daily_calendar_actual == daily_calendar_expected


class TestFullCalendar:
    @pytest.fixture(autouse=True)
    def set_up(self):
        self.calendar = FullCalendar()
        self.add_person_request: dict[str, Any] = {
            REQUEST_TYPE_ID: RequestType.ADD_PERSON,
            "last_name": "lastname",
            "first_name": "firstname",
            "country": objects.Country.NETHERLANDS.name,
            "city": "Amsterdam",
        }

    def test_bad_response_if_no_request_type(self):
        response = self.calendar.process_frontend_request(request_raw={"missing_request_id_col": "some_value"})
        assert response.code == 400
        assert "must contain key" in response.message

    def test_bad_response_if_unrecognized_request_type(self):
        response = self.calendar.process_frontend_request(request_raw={REQUEST_TYPE_ID: "unknown_value"})
        assert response.code == 400
        assert "Unknown request type" in response.message

    def test_add_person(self):
        response = self.calendar.process_frontend_request(self.add_person_request)
        assert response.code == 200
        assert len(self.calendar.calendars) == 1
        person_calendar = list(self.calendar.calendars.values())[0]
        assert isinstance(person_calendar.person, Person)
        assert person_calendar.person.last_name == StrID("lastname")
        assert person_calendar.person.first_name == StrID("firstname")
        assert person_calendar.person.home == Location(Country.NETHERLANDS, city=StrID("Amsterdam"))
        assert person_calendar.trip_list == []

    def test_raises_on_adding_existing_person(self):
        _ = self.calendar.process_frontend_request(self.add_person_request)
        response = self.calendar.process_frontend_request(self.add_person_request)
        assert response.code == 400
        assert "is already in calendar" in response.message

    def test_clear_all_people(self):
        _ = self.calendar.process_frontend_request(self.add_person_request)
        assert len(self.calendar.calendars) == 1
        response = self.calendar.process_frontend_request({REQUEST_TYPE_ID: RequestType.CLEAR_ALL_PEOPLE})
        assert response.code == 200
        assert len(self.calendar.calendars) == 0

    def test_add_trip(self):
        self.calendar.process_frontend_request(self.add_person_request)
        person = list(self.calendar.calendars.keys())[0]
        add_trip_request = {
            "request_type": "ADD_TRIP",
            "person_id": str(hash(person)),
            "country": "NETHERLANDS",
            "city": "Amsterdam",
            "start_date": "2025-11-25",
            "end_date": "2025-11-28",
        }
        response = self.calendar.process_frontend_request(add_trip_request)
        assert response.code == 200
        trip_list = self.calendar.calendars[person].trip_list
        assert len(trip_list) == 1
        trip = trip_list[0]
        assert trip.location == Location(Country.NETHERLANDS, city=StrID("Amsterdam"))
        assert trip.start_date == dt.date(2025, 11, 25)
        assert trip.end_date == dt.date(2025, 11, 28)

    def test_get_daily_calendars_home(self):
        person_1_request = self.add_person_request.copy()
        person_2_request: dict[str, Any] = {
            REQUEST_TYPE_ID: RequestType.ADD_PERSON,
            "last_name": "familyname",
            "first_name": "givenname",
            "country": objects.Country.UNITED_KINGDOM.name,
            "city": "london",
        }
        update_daily_calendars_dates_request: dict[str, Any] = {
            REQUEST_TYPE_ID: RequestType.UPDATE_DAILY_CALENDARS_DATES,
            "start_date": "2025-12-01",
            "end_date": "2025-12-03",
        }
        self.calendar.process_frontend_request(person_1_request)
        self.calendar.process_frontend_request(person_2_request)
        self.calendar.process_frontend_request(update_daily_calendars_dates_request)

        daily_calendars = self.calendar.get_daily_calendars_to_display()

        assert len(self.calendar.people_sorted_by_name) == 2
        familyname, lastname = self.calendar.people_sorted_by_name
        for date in [dt.date(2025, 12, 1), dt.date(2025, 12, 2), dt.date(2025, 12, 3)]:
            assert daily_calendars[date][familyname].start == Location(Country.UNITED_KINGDOM, city=StrID("london"))
            assert daily_calendars[date][familyname].end == Location(Country.UNITED_KINGDOM, city=StrID("london"))
            assert daily_calendars[date][lastname].start == Location(Country.NETHERLANDS, city=StrID("amsterdam"))
            assert daily_calendars[date][lastname].end == Location(Country.NETHERLANDS, city=StrID("amsterdam"))

    def test_get_daily_calendars_with_trip(self):
        person_1_request = self.add_person_request.copy()
        self.calendar.process_frontend_request(person_1_request)
        person = list(self.calendar.calendars.keys())[0]
        update_daily_calendars_dates_request: dict[str, Any] = {
            REQUEST_TYPE_ID: RequestType.UPDATE_DAILY_CALENDARS_DATES,
            "start_date": "2025-12-01",
            "end_date": "2025-12-03",
        }
        self.calendar.process_frontend_request(update_daily_calendars_dates_request)
        add_trip_request = {
            "request_type": "ADD_TRIP",
            "person_id": str(hash(person)),
            "country": "ICELAND",
            "city": "reykjavik",
            "start_date": "2025-12-02",
            "end_date": "2025-12-03",
        }
        self.calendar.process_frontend_request(add_trip_request)

        daily_calendars = self.calendar.get_daily_calendars_to_display()

        assert daily_calendars[dt.date(2025, 12, 1)][person].start == Location(Country.NETHERLANDS, StrID("amsterdam"))
        assert daily_calendars[dt.date(2025, 12, 1)][person].end == Location(Country.NETHERLANDS, StrID("amsterdam"))
        assert daily_calendars[dt.date(2025, 12, 2)][person].start == Location(Country.NETHERLANDS, StrID("amsterdam"))
        assert daily_calendars[dt.date(2025, 12, 2)][person].end == Location(Country.ICELAND, StrID("reykjavik"))
        assert daily_calendars[dt.date(2025, 12, 3)][person].start == Location(Country.ICELAND, StrID("reykjavik"))
        assert daily_calendars[dt.date(2025, 12, 3)][person].end == Location(Country.NETHERLANDS, StrID("amsterdam"))

    def test_all_together_one_person(self):
        self.calendar.process_frontend_request(self.add_person_request)
        self.calendar.process_frontend_request({
            REQUEST_TYPE_ID: RequestType.UPDATE_DAILY_CALENDARS_DATES,
            "start_date": "2025-12-01",
            "end_date": "2025-12-03",
        })  # fmt: skip
        with pytest.raises(CalendarError):
            self.calendar.is_everyone_together(dt.date(2025, 11, 30))  # Outside range of daily calendar
        assert self.calendar.is_everyone_together(dt.date(2025, 12, 1))
        assert self.calendar.is_everyone_together(dt.date(2025, 12, 2))
        assert self.calendar.is_everyone_together(dt.date(2025, 12, 3))
        with pytest.raises(CalendarError):
            self.calendar.is_everyone_together(dt.date(2025, 12, 4))  # Outside range of daily calendar

    def test_all_together_two_people_with_trip(self):
        person_1_request = self.add_person_request.copy()
        person_2_request: dict[str, Any] = {
            REQUEST_TYPE_ID: RequestType.ADD_PERSON,
            "last_name": "familyname",
            "first_name": "givenname",
            "country": objects.Country.UNITED_KINGDOM.name,
            "city": "london",
        }
        self.calendar.process_frontend_request(person_1_request)
        self.calendar.process_frontend_request(person_2_request)
        person = list(self.calendar.calendars.keys())[0]

        add_trip_request = {
            "request_type": "ADD_TRIP",
            "person_id": str(hash(person)),
            "country": "UNITED_KINGDOM",
            "city": "london",
            "start_date": "2025-12-02",
            "end_date": "2025-12-03",
        }
        update_daily_calendars_dates_request: dict[str, Any] = {
            REQUEST_TYPE_ID: RequestType.UPDATE_DAILY_CALENDARS_DATES,
            "start_date": "2025-12-01",
            "end_date": "2025-12-03",
        }
        self.calendar.process_frontend_request(add_trip_request)
        self.calendar.process_frontend_request(update_daily_calendars_dates_request)

        assert not self.calendar.is_everyone_together(dt.date(2025, 12, 1))
        assert self.calendar.is_everyone_together(dt.date(2025, 12, 2))
        assert not self.calendar.is_everyone_together(dt.date(2025, 12, 3))
