from schedules.logic.objects import Country, Location, Person, StrID


class TestStrID:
    def test_case_insensitive(self):
        id_all_caps = StrID("TEST STRING")
        id_title = StrID("Test String")
        id_lower = StrID("test string")
        assert id_all_caps == id_title == id_lower


class TestPerson:
    def test_equal_different_objects(self):
        person_1 = Person(
            unique_id=StrID("a"),
            last_name=StrID("lastname"),
            first_name=StrID("firstname"),
            home=Location(Country.NETHERLANDS, city=StrID("amsterdam")),
        )
        assert not person_1 == 0

    def test_equal_different_people(self):
        person_1 = Person(
            unique_id=StrID("a"),
            last_name=StrID("lastname"),
            first_name=StrID("firstname"),
            home=Location(Country.NETHERLANDS, city=StrID("amsterdam")),
        )
        person_2 = Person(
            unique_id=StrID("b"),
            last_name=StrID("familyname"),
            first_name=StrID("givenname"),
            home=Location(Country.NETHERLANDS, city=StrID("amsterdam")),
        )
        assert not person_1 == person_2

    def test_equal_different_id_and_location(self):
        person_1 = Person(
            unique_id=StrID("a"),
            last_name=StrID("lastname"),
            first_name=StrID("firstname"),
            home=Location(Country.NETHERLANDS, city=StrID("amsterdam")),
        )
        person_2 = Person(
            unique_id=StrID("b"),
            last_name=StrID("lastname"),
            first_name=StrID("firstname"),
            home=Location(Country.NETHERLANDS, city=StrID("amsterdam")),
        )
        assert person_1 == person_2
