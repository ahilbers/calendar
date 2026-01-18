"""Interaction with persistenst storage, e.g. database."""

import logging

from typing import Self
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.exc import OperationalError

from schedules.logic.errors import CalendarError
from schedules.logic.objects import Country, Location, Person, StrID

Base = declarative_base()


class PersonDBEntry(Base):
    """A database entry for a Person."""

    __tablename__ = "person"
    id = Column(String, primary_key=True)
    last_name = Column(String)
    first_name = Column(String)
    country = Column(String)
    city = Column(String)

    @classmethod
    def from_python_class(cls, person: Person) -> Self:
        return cls(
            id=person.unique_id,
            last_name=person.last_name,
            first_name=person.first_name,
            country=person.home.country,
            city=person.home.city,
        )

    def to_python_class(self) -> Person:
        return Person(
            unique_id=StrID(str(self.id)),
            last_name=StrID(str(self.last_name)),
            first_name=StrID(str(self.first_name)),
            home=Location(country=Country(self.country), city=StrID(str(self.city))),
        )


def add_person_to_database(database_session: Session, person: Person) -> None:
    try:
        person_db_entry = PersonDBEntry.from_python_class(person)
        database_session.add(person_db_entry)
        logging.info(f"Added {person} to database, id {person_db_entry.id}.")
        database_session.commit()
    except OperationalError as err:
        raise CalendarError(message=f"Failed to add person to database: {err}") from err


def read_all_people_from_database(database_session: Session) -> list[Person]:
    person_db_entries = database_session.query(PersonDBEntry).all()
    return [person_db_entry.to_python_class() for person_db_entry in person_db_entries]
