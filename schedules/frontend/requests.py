"""HTTP request utils."""

from enum import StrEnum


class RequestType(StrEnum):
    """Request types (e.g. GET or POST) sent between frontend and backend"""

    ADD_PERSON = "ADD_PERSON"
