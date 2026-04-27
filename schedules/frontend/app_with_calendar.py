"""Base objects used in frontend."""

import os
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schedules.logic.storage import Base


class AppWithCalendar(Flask):
    """An app, with a calendar object attached."""

    def __init__(self, import_name: str):
        super().__init__(import_name)

        # Set up database - use PostgreSQL if DATABASE_URL is set, otherwise SQLite
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            database_engine = create_engine(database_url)
        else:
            database_engine = create_engine("sqlite:///data/database.db")

        Base.metadata.create_all(database_engine)
        self.database_session_maker = sessionmaker(bind=database_engine)
