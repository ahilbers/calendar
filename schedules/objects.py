"""Calendar objects."""

import dataclasses
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


@dataclasses.dataclass(frozen=True)
class Person:
    first_name: StrID
    last_name: StrID
    home_location: Location
