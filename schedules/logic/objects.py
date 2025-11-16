"""Base objects used in (backend) logic."""

import dataclasses
import datetime as dt
import enum
from typing import Self

from schedules.frontend.requests import Request
from schedules.logic.errors import RequestError


class Country(enum.Enum):
    NETHERLANDS = "NETHERLANDS"
    NORWAY = "NORWAY"
    SWITZERLAND = "SWITZERLAND"
    UNITED_KINGDOM = "UNITED_KINGDOM"
    UNITED_STATES = "UNITED_STATES"


class StrID(str):
    """A string, but always lowercase for good comparisons."""

    def __new__(cls, original_string: str) -> Self:
        return super().__new__(cls, original_string.lower())

    def __repr__(self) -> str:
        return self.title()


@dataclasses.dataclass(frozen=True)
class Location:
    country: Country
    city: StrID

    def __repr__(self) -> str:
        return f"{self.country.value}:{self.city.upper()}"

    def __post_init__(self) -> None:
        if not len(self.city) > 0:
            raise RequestError(f"City name must be set: `{self.city}`.")


@dataclasses.dataclass(frozen=True)
class Person:
    last_name: StrID
    first_name: StrID
    home: Location

    def __post_init__(self) -> None:
        if not (len(self.last_name) > 0 and len(self.first_name) > 0):
            raise RequestError(f"Both first name and last name must be set: `{self.last_name}`, `{self.first_name}`.")

    @classmethod
    def from_request(cls, request: Request) -> Self:
        return cls(
            last_name=StrID(str(request.payload.get("last_name"))),
            first_name=StrID(str(request.payload.get("first_name"))),
            home=Location(country=Country.NETHERLANDS, city=StrID("Amsterdam")),  # TODO: Actually set
        )


@dataclasses.dataclass(frozen=True)
class Trip:
    location: Location
    start_date: dt.date
    end_date: dt.date

    def __post_init__(self) -> None:
        if not self.start_date < self.end_date:
            raise ValueError(f"Trip start date must be before end date: `{self.start_date}`, `{self.end_date}`.")


@dataclasses.dataclass(frozen=True)
class Day:
    start: Location
    end: Location
