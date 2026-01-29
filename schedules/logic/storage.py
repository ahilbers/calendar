"""Interaction with persistenst storage, e.g. database."""

import datetime as dt
import logging

from typing import Self
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.exc import IntegrityError, OperationalError

from schedules.logic.errors import CalendarError
from schedules.logic.objects import Country, Location, Person, StrID, Trip

Base = declarative_base()


class PersonDBEntry(Base):
    """A database entry for a Person."""

    __tablename__ = "person"
    id = Column(String, primary_key=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)

    @classmethod
    def from_python(cls, person: Person) -> Self:
        return cls(
            id=person.unique_id,
            last_name=person.last_name,
            first_name=person.first_name,
            country=person.home.country,
            city=person.home.city,
        )

    def to_python(self) -> Person:
        return Person(
            unique_id=StrID(str(self.id)),
            last_name=StrID(str(self.last_name)),
            first_name=StrID(str(self.first_name)),
            home=Location(country=Country(self.country), city=StrID(str(self.city))),
        )


class TripDBEntry(Base):
    """A database entry for a Trip."""

    __tablename__ = "trip"
    id = Column(String, primary_key=True)
    person_id = Column(String, nullable=False)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    start_date = Column(Integer, nullable=False)
    end_date = Column(Integer, nullable=False)

    @classmethod
    def from_python(cls, person: Person, trip: Trip) -> Self:
        return cls(
            id=str(trip.unique_id),
            person_id=str(person.unique_id),
            location_country=trip.location.country,
            location_city=trip.location.city,
            start_date=int(trip.start_date.strftime("%Y%m%d")),
            end_date=int(trip.end_date.strftime("%Y%m%d")),
        )

    def to_python(self) -> Trip:
        return Trip(
            unique_id=StrID(str(self.id)),
            location=Location(country=Country(self.country), city=StrID(str(self.city))),
            start_date=dt.datetime.strptime(str(self.start_date), "%Y%m%d").date(),
            end_date=dt.datetime.strptime(str(self.end_date), "%Y%m%d").date(),
        )


class CalendarRepository:
    """Handles all database operations for the calendar."""

    def __init__(self, session: Session):
        self.session = session

    def add_person(self, person: Person) -> None:
        """Save a person to the database."""
        try:
            person_db_entry = PersonDBEntry.from_python(person)
            self.session.add(person_db_entry)
            self.session.commit()
            logging.info(f"Saved {person} to database, id {person_db_entry.id}.")
        except (OperationalError, IntegrityError) as err:
            raise CalendarError(message=f"Failed to add person to database: {err}") from err

    def get_all_people(self) -> list[Person]:
        """Load all people from the database."""
        person_db_entries = self.session.query(PersonDBEntry).all()
        return [entry.to_python() for entry in person_db_entries]

    def remove_person(self, person: Person) -> None:
        """Remove a person from the database."""
        try:
            person_db_entry = self.session.query(PersonDBEntry).filter_by(id=str(person.unique_id)).first()
            if not person_db_entry:
                raise CalendarError(message=f"Person with id {person.unique_id} not found in database.")
            if person_db_entry:
                self.session.delete(person_db_entry)
                self.session.commit()
                logging.info(f"Removed {person} from database, id {person_db_entry.id}.")
        except OperationalError as err:
            raise CalendarError(message=f"Failed to remove person from database: {err}") from err

    def add_trip(self, person: Person, trip: Trip) -> None:
        """Save a trip for a person to the database."""
        try:
            trip_db_entry = TripDBEntry.from_python(person, trip)
            self.session.add(trip_db_entry)
            self.session.commit()
            logging.info(f"Saved trip {trip}, id {trip.unique_id} for person {person} to database.")
        except (OperationalError, IntegrityError) as err:
            raise CalendarError(message=f"Failed to add trip to database: {err}") from err

    def get_trips_for_person(self, person: Person) -> list[Trip]:
        """Load all trips for a specific person from the database."""
        trip_db_entries = self.session.query(TripDBEntry).filter_by(person_id=str(person.unique_id)).all()
        return [entry.to_python() for entry in trip_db_entries]

    def remove_trip(self, trip: Trip) -> None:
        """Remove a trip from the database."""
        try:
            trip_db_entry = self.session.query(TripDBEntry).filter_by(id=str(trip.unique_id)).first()
            if not trip_db_entry:
                raise CalendarError(message=f"Trip with id {trip.unique_id} not found in database.")
            self.session.delete(trip_db_entry)
            self.session.commit()
            logging.info(f"Removed trip {trip.unique_id} from database.")
        except OperationalError as err:
            raise CalendarError(message=f"Failed to remove trip from database: {err}") from err
