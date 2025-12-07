"""Errors related to calendars and schedules."""


class CalendarBaseException(Exception):
    def __init__(self, message: str):
        self.message = message


class CalendarError(CalendarBaseException):
    pass


class RequestError(CalendarBaseException):
    pass


def get_message_from_handled_error_else_raise(error: Exception) -> str:
    if hasattr(error, "message"):
        return str(error.message)  # type: ignore
    elif isinstance(error, KeyError):
        return f"Key Error: {error}"
    else:
        raise error
