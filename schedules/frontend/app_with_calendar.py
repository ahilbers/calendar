"""Base objects used in frontend."""

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schedules.logic.calendar import FullCalendar


class AppWithCalendar(Flask):
    """An app, with a calendar object attached."""

    def __init__(self, import_name: str):
        super().__init__(import_name)
        self.calendar = FullCalendar()
        self.database_session = sessionmaker(bind=create_engine("sqlite:///data/test.db"))
