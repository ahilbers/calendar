"""Test interactions with persistent storage, such as a database."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from schedules.logic.errors import CalendarError
from schedules.logic.objects import Country, Location, Person, StrID
from schedules.logic.storage import Base, CalendarRepository


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
        unique_id=StrID("test_person_id"),
        last_name=StrID("lastname"),
        first_name=StrID("firstname"),
        home=sample_location(),
    )


def test_repository_get_empty_database(database_session: Session):
    """Test getting people from empty database returns empty list."""
    repository = CalendarRepository(database_session)
    people = repository.get_all_people()
    assert people == []


def test_add_person(database_session: Session):
    """Test basic add and retrieve with repository."""
    repository = CalendarRepository(database_session)
    person = sample_person()

    repository.add_person(person)
    people_read_back = repository.get_all_people()

    assert len(people_read_back) == 1
    assert people_read_back[0] == person


def test_multiple_people(database_session: Session):
    """Test adding and retrieving multiple people."""
    person1 = Person(
        unique_id=StrID("person1"),
        last_name=StrID("lastname"),
        first_name=StrID("firstname"),
        home=sample_location(),
    )
    person2 = Person(
        unique_id=StrID("person2"),
        last_name=StrID("familyname"),
        first_name=StrID("givenname"),
        home=sample_location(),
    )

    repository = CalendarRepository(database_session)
    repository.add_person(person1)
    repository.add_person(person2)

    people = repository.get_all_people()
    assert len(people) == 2
    assert person1 in people
    assert person2 in people


def test_duplicate_person_id(database_session: Session):
    """Test that adding person with same ID raises error."""
    repository = CalendarRepository(database_session)
    person = sample_person()

    repository.add_person(person)

    # Adding same person again should raise an error
    with pytest.raises(CalendarError):
        repository.add_person(person)


def test_remove_person(database_session: Session):
    """Test removing a person from the database."""
    repository = CalendarRepository(database_session)
    person = sample_person()
    repository.add_person(person)
    assert len(repository.get_all_people()) == 1

    repository.remove_person(person)

    people = repository.get_all_people()
    assert len(people) == 0


def test_remove_nonexistent_person(database_session: Session):
    """Test that removing a person that doesn't exist raises an error."""

    repository = CalendarRepository(database_session)
    person = sample_person()

    with pytest.raises(CalendarError):
        repository.remove_person(person)


def test_remove_one_of_multiple(database_session: Session):
    """Test removing one person when multiple people exist."""
    repository = CalendarRepository(database_session)
    person1 = Person(
        unique_id=StrID("person1"),
        last_name=StrID("lastname"),
        first_name=StrID("firstname"),
        home=sample_location(),
    )
    person2 = Person(
        unique_id=StrID("person2"),
        last_name=StrID("familyname"),
        first_name=StrID("givenname"),
        home=sample_location(),
    )
    repository.add_person(person1)
    repository.add_person(person2)
    assert len(repository.get_all_people()) == 2

    repository.remove_person(person1)

    people = repository.get_all_people()
    assert len(people) == 1
    assert people[0] == person2
