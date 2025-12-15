"""Base objects used in (backend) logic."""

import dataclasses
import datetime as dt
from enum import StrEnum
from typing import Self
import uuid

from schedules.logic.requests import Request
from schedules.logic.errors import CalendarError, RequestError


class Country(StrEnum):
    ICELAND = "ISL"
    NETHERLANDS = "NLD"
    NORWAY = "NOR"
    SWITZERLAND = "CHE"
    UNITED_KINGDOM = "GBR"


class StrID(str):
    """A string, but always lowercase for good comparisons."""

    def __new__(cls, original_string: str) -> Self:
        return super().__new__(cls, original_string.lower())

    def __repr__(self) -> str:
        return self.lower()


@dataclasses.dataclass(frozen=True)
class Location:
    country: Country
    city: StrID

    def __post_init__(self) -> None:
        if not len(self.city) > 0:
            raise RequestError(f"City name must be set: `{self.city}`.")

    def __repr__(self) -> str:
        return f"{self.country.value}:{self.city.upper()}"

    @classmethod
    def from_request(cls, request: Request) -> Self:
        return cls(
            country=Country[str(request.payload.get("country"))],
            city=StrID(str(request.payload.get("city"))),
        )

    @property
    def display_name_frontend(self) -> str:
        return f"{self.city.title()}, {self.country.title().replace('_', ' ')}"


@dataclasses.dataclass(frozen=True)
class DayLocation:
    start: Location
    end: Location


@dataclasses.dataclass(frozen=True)
class Person:
    unique_id: str
    last_name: StrID
    first_name: StrID
    home: Location

    def __post_init__(self) -> None:
        if not (len(self.last_name) > 0 and len(self.first_name) > 0):
            raise RequestError(f"Both first name and last name must be set: `{self.last_name}`, `{self.first_name}`.")

    def __repr__(self):
        return f"Person({self.last_name}, {self.first_name})"

    @property
    def display_name_frontend(self) -> str:
        return f"{self.first_name.title()} {self.last_name.title()}"

    @classmethod
    def from_request(cls, request: Request) -> Self:
        return cls(
            unique_id=str(uuid.uuid4()),
            last_name=StrID(str(request.payload.get("last_name"))),
            first_name=StrID(str(request.payload.get("first_name"))),
            home=Location.from_request(request),
        )


@dataclasses.dataclass(frozen=True)
class Trip:
    location: Location
    start_date: dt.date
    end_date: dt.date

    def __post_init__(self) -> None:
        if not self.start_date < self.end_date:
            raise CalendarError(f"Trip start date must be before end date: `{self.start_date}`, `{self.end_date}`.")

    @classmethod
    def from_request(cls, request: Request) -> Self:
        return cls(
            location=Location.from_request(request),
            start_date=dt.date.strptime(request.payload["start_date"], "%Y-%m-%d"),
            end_date=dt.date.strptime(request.payload["end_date"], "%Y-%m-%d"),
        )
