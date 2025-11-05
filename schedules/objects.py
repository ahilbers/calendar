"""Base objects used in calendars."""

import dataclasses
import datetime as dt
import enum


class Country(enum.Enum):
    NETHERLANDS = "NETHERLANDS"
    NORWAY = "NORWAY"
    SWITZERLAND = "SWITZERLAND"
    UNITED_KINGDOM = "UNITED_KINGDOM"
    UNITED_STATES = "UNITED_STATES"


class StrID(str):
    """A string, but always lowercase for good comparisons."""

    def __new__(cls, original_string: str):
        return super().__new__(cls, original_string.lower())

    def __repr__(self):
        return self.title()


@dataclasses.dataclass(frozen=True)
class Location:
    country: Country
    city: StrID

    def __repr__(self):
        return f"{self.country.value}:{self.city.upper()}"


@dataclasses.dataclass(frozen=True)
class Person:
    last_name: StrID
    first_name: StrID
    home: Location


@dataclasses.dataclass(frozen=True)
class Trip:
    location: Location
    start_date: dt.date
    end_date: dt.date


@dataclasses.dataclass(frozen=True)
class Day:
    start: Location
    end: Location
