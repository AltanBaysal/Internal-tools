import pytest

from backend.features.workspace.domain.chat import TITLE_LIMIT, chat_title
from backend.features.workspace.domain.errors import EmptyMessage, ProjectNotFound
from backend.features.workspace.domain.usecases.list_chats import list_chats
from backend.features.workspace.domain.usecases.start_chat import start_chat


class FakeProjectStore:
    def __init__(self, ids=("p1",)):
        self.ids = set(ids)

    def get(self, project_id):
        return object() if project_id in self.ids else None


class FakeChatStore:
    def __init__(self):
        self.saved = []

    def add(self, project_id, chat):
        self.saved.append((project_id, chat))

    def list_for(self, project_id):
        return [chat for pid, chat in self.saved if pid == project_id]


def _start(text, chat_store=None, new_id="c1", now="2026-08-09T11:04:00+00:00"):
    return start_chat(
        chat_store or FakeChatStore(),
        FakeProjectStore(),
        "p1",
        text,
        new_id=new_id,
        now=now,
    )


def test_a_chat_is_born_with_the_skill_that_was_selected():
    chat = start_chat(
        FakeChatStore(),
        FakeProjectStore(),
        "p1",
        "Hello",
        new_id="c1",
        now="2026-08-09T11:04:00+00:00",
        skill="create-scenario",
    )
    assert chat.skill == "create-scenario"
    # And the message that started it remembers what governed it.
    assert chat.messages[0].skill == "create-scenario"


def test_a_chat_started_without_a_skill_carries_none():
    chat = _start("Hello")
    assert chat.skill == ""
    assert chat.messages[0].skill == ""


def test_a_short_message_is_the_title_as_it_is():
    assert chat_title("Write the intro") == "Write the intro"


def test_a_long_message_is_cut_and_marked():
    assert chat_title("x" * 60) == "x" * TITLE_LIMIT + "…"


def test_a_message_of_exactly_the_limit_gets_no_ellipsis():
    # Nothing was cut off, so nothing should claim it was.
    assert chat_title("x" * TITLE_LIMIT) == "x" * TITLE_LIMIT


def test_the_chat_is_born_with_its_first_message():
    chat = _start("Hello there")
    assert chat.title == "Hello there"
    assert [(m.role, m.text) for m in chat.messages] == [("user", "Hello there")]
    assert chat.messages[0].at == "2026-08-09T11:04:00+00:00"


def test_the_chat_is_handed_to_the_store():
    store = FakeChatStore()
    chat = _start("Hello", chat_store=store)
    assert store.saved == [("p1", chat)]


@pytest.mark.parametrize("blank", ["", "   ", "\n\t"])
def test_an_empty_message_starts_nothing(blank):
    store = FakeChatStore()
    with pytest.raises(EmptyMessage):
        _start(blank, chat_store=store)
    assert store.saved == []


def test_an_unknown_project_starts_nothing():
    with pytest.raises(ProjectNotFound):
        start_chat(
            FakeChatStore(),
            FakeProjectStore(),
            "nope",
            "hi",
            new_id="c1",
            now="2026-08-09T11:04:00+00:00",
        )


def test_chats_come_back_newest_first():
    store = FakeChatStore()
    _start("first", chat_store=store, new_id="c1", now="2026-08-09T10:00:00+00:00")
    _start("second", chat_store=store, new_id="c2", now="2026-08-09T12:00:00+00:00")
    assert [c.id for c in list_chats(store, "p1")] == ["c2", "c1"]
