from schedules.objects import StrID


class TestStrID:
    def test_case_insensitive(self):
        id_all_caps = StrID("TEST STRING")
        id_title = StrID("Test String")
        id_lower = StrID("test string")
        assert id_all_caps == id_title == id_lower
