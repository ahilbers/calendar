"""Errors related to calendars and schedules."""


class CalendarBaseException(Exception):
    def __init__(self, message: str):
        self.message = message


class CalendarError(CalendarBaseException):
    pass


class RequestError(CalendarBaseException):
    pass
