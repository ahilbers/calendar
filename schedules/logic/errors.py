"""Errors related to calendars and schedules."""


class CalendarBaseException(Exception):
    pass


class CalendarError(CalendarBaseException):
    pass


class RequestError(CalendarBaseException):
    pass
