"""Base objects used in frontend."""

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schedules.logic.calendar import FullCalendar
from schedules.logic.storage import Base


class AppWithCalendar(Flask):
    """An app, with a calendar object attached."""

    def __init__(self, import_name: str):
        super().__init__(import_name)
        self.calendar = FullCalendar()

        # Set up connection with database
        database_engine = create_engine("sqlite:///data/database.db")
        Base.metadata.create_all(database_engine)
        self.database_session = sessionmaker(bind=database_engine)

        # Sync with current database state
        session = self.database_session()
        self.calendar.load_people_from_database(session)
        session.close()
