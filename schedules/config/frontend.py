"""Config for interaction between frontend and backend."""

from enum import StrEnum


class Requests(StrEnum):
    """Request types (e.g. GET or POST) sent between frontend and backend"""

    ADD_PERSON: str
