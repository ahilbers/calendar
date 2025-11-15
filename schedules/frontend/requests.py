"""HTTP request utils."""

from enum import StrEnum
from typing import Any


class RequestType(StrEnum):
    """Request types (e.g. GET or POST) sent between frontend and backend"""

    ADD_PERSON = "ADD_PERSON"


class Request:
    """Used to pass around requests between frontend and backend"""

    request_type: RequestType
    payload: dict[str, Any]
