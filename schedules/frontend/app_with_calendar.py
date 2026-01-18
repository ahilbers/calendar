"""Base objects used in frontend."""

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schedules.logic.calendar import FullCalendar
from schedules.logic.storage import Base, CalendarRepository


class AppWithCalendar(Flask):
    """An app, with a calendar object attached."""

    def __init__(self, import_name: str):
        super().__init__(import_name)

        # Set up database
        database_engine = create_engine("sqlite:///data/database.db")  # Created if it does not exist
        Base.metadata.create_all(database_engine)
        self.database_session_maker = sessionmaker(bind=database_engine)

        # Create repository and calendar
        session = self.database_session_maker()
        database_repository = CalendarRepository(session)
        self.calendar = FullCalendar(database_repository=database_repository)

        # Load existing data
        self.calendar.load_from_repository()
        session.close()
