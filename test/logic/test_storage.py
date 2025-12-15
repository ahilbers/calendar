"""Test interactions with persistent storage, such as a database."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from schedules.logic.objects import Country, Location, Person, StrID
from schedules.logic.storage import Base, add_person_to_database, read_all_people_from_database


@pytest.fixture
def database_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()  # Runs after every test, automatic teardown


def sample_location() -> Location:
    return Location(country=Country.NETHERLANDS, city=StrID("Amsterdam"))


def sample_person() -> Person:
    return Person(
        unique_id="test_person_id",
        last_name=StrID("lastname"),
        first_name=StrID("firstname"),
        home=sample_location(),
    )


def test_add_person(database_session: Session):
    person = sample_person()
    add_person_to_database(database_session=database_session, person=person)
    people_read_back = read_all_people_from_database(database_session)
    assert [people_read_back] == person
