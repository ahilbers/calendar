"""HTTP request utils."""

from copy import copy
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final, Mapping

from schedules.logic.errors import RequestError


REQUEST_TYPE_ID: Final[str] = "request_type"  # Key used in HTTP requests to indicate the type of request


class RequestType(StrEnum):
    """Request types (e.g. GET or POST) sent between frontend and backend"""

    ADD_PERSON = "ADD_PERSON"


class Request:
    """Parsed request from frontend, splitting request type and payload."""

    def __init__(self, request_raw: Mapping[str, Any]):
        request_raw = copy(request_raw)
        request_type = request_raw.get(REQUEST_TYPE_ID)
        if not isinstance(request_type, str):
            raise RequestError(f"Raw request {request_raw} must contain key `{REQUEST_TYPE_ID}` with string value.")
        if not request_type in RequestType:
            raise RequestError(f"Unknown request type: `{request_type}`.")
        self.request_type = RequestType(request_raw.pop(REQUEST_TYPE_ID))  # type: ignore
        self.payload = request_raw  # Remaining fields after request type is popped off


@dataclass(frozen=True)
class Response:
    """Response sent by server in response to client request."""

    code: int
    message: str

    @property
    def frontend_message(self) -> str:
        """Print something that can be presented by the front-end"""
        return f"Error ({self.code}): {self.message}"
