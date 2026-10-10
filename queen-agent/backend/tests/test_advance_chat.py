"""Advancing a chat (Madde 461): the hold, the one read, and the turn that answers -- with fake turns."""
import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.chat import Chat, Message
from backend.features.workspace.domain.errors import (
    ChatFull,
    ChatHeld,
    ChatNotFound,
    EmptyMessage,
    NothingToAnswer,
    ProjectNotFound,
)
from backend.features.workspace.domain.usecases.advance_chat import (
    NO_TEXT,
    Nothing,
    Started,
    advance_chat,
)
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.services.store.store import Store

AT = "2026-10-10T10:00:00.000+00:00"


class FakeTurns:
    """Turns that hold what they are told and run nothing: what the use case asked is the test."""

    def __init__(self, free=True):
        self.free = free
        self.held = []
        self.released = []
        self.started = []

    def reserve(self, project_id, chat_id):
        if not self.free:
            return None
        turn = object()
        self.held.append((project_id, chat_id, turn))
        return turn

    def release(self, project_id, chat_id, turn):
        self.released.append((project_id, chat_id, turn))

    def start(self, project_id, turn, chat, pieces):
        self.started.append((project_id, turn, chat))


class Unreadable:
    def get(self, project_id, chat_id):
        raise OSError("Drive went away")


def _stores(tmp_path, *said):
    store = Store(str(tmp_path))
    projects = FileProjectStore(store)
    chats = FileChatStore(store, projects)
    create_project(projects, new_id="p1", name="Thesis", now=AT)
    if said:
        chats.add("p1", Chat(id="c1", title="hi", created_at=AT, messages=said))
    return projects, chats


def _advance(turns, chats, projects, wanted="c1", text="more", **fields):
    return advance_chat(
        turns, chats, projects, None, None, "p1", wanted, text, lambda: AT, new_id="c9", line_id="l1", **fields
    )


def _user(text="hi"):
    return Message(role="user", at=AT, text=text)


def _ai(text="Done.", **fields):
    return Message(role="ai", at=AT, text=text, **fields)


def test_a_message_starts_a_turn_on_the_record_it_wrote_and_keeps_the_chat_held(tmp_path):
    projects, chats = _stores(tmp_path, _user(), _ai())
    turns = FakeTurns()
    started = _advance(turns, chats, projects)
    assert isinstance(started, Started)
    assert [m.text for m in started.chat.messages] == ["hi", "Done.", "more"]
    assert turns.started == [("p1", started.turn, started.chat)]
    # The turn lets go at its own end, not here.
    assert turns.released == []


def test_a_draft_is_held_by_the_id_it_is_born_as(tmp_path):
    projects, chats = _stores(tmp_path)
    turns = FakeTurns()
    started = _advance(turns, chats, projects, wanted="", text="hello")
    assert started.chat.id == "c9"
    assert [(project, chat) for project, chat, _ in turns.held] == [("p1", "c9")]


def test_a_held_chat_is_refused_before_anything_is_read(tmp_path):
    projects, _ = _stores(tmp_path)
    with pytest.raises(ChatHeld):
        _advance(FakeTurns(free=False), Unreadable(), projects)


@pytest.mark.parametrize(
    ("wanted", "text", "refusal"),
    [
        ("c1", "   ", EmptyMessage),
        ("nope", "hi", ChatNotFound),
        ("", NO_TEXT, NothingToAnswer),
        ("nope", NO_TEXT, NothingToAnswer),
    ],
)
def test_every_refusal_lets_the_chat_go_and_starts_nothing(tmp_path, wanted, text, refusal):
    projects, chats = _stores(tmp_path, _user(), _ai())
    turns = FakeTurns()
    with pytest.raises(refusal):
        _advance(turns, chats, projects, wanted=wanted, text=text)
    assert [(p, c, t) for p, c, t in turns.held] == turns.released
    assert turns.started == []


def test_try_again_in_a_project_that_is_not_there_names_the_project(tmp_path):
    projects, chats = _stores(tmp_path)
    turns = FakeTurns()
    with pytest.raises(ProjectNotFound):
        advance_chat(
            turns, chats, projects, None, None, "nope", "c1", NO_TEXT, lambda: AT, new_id="c9", line_id="l1"
        )
    assert turns.released == turns.held


def test_a_full_chat_is_refused_for_its_ceiling_first(tmp_path):
    projects, chats = _stores(tmp_path, _user(), _ai("a" * 170_000, failed=""))
    turns = FakeTurns()
    with pytest.raises(ChatFull):
        _advance(turns, chats, projects, text=NO_TEXT)
    assert turns.released == turns.held


def test_a_fault_while_reading_lets_the_chat_go(tmp_path):
    projects, _ = _stores(tmp_path)
    turns = FakeTurns()
    with pytest.raises(OSError):
        _advance(turns, Unreadable(), projects)
    assert turns.released == turns.held


def test_try_again_with_nothing_to_try_again_starts_nothing_and_lets_go(tmp_path):
    projects, chats = _stores(tmp_path, _user(), _ai())
    turns = FakeTurns()
    nothing = _advance(turns, chats, projects, text=NO_TEXT)
    # The chat as it was read, handed back: whoever asked shows the answer already written, and
    # reading it again would be a second trip for the same record (Madde 462).
    assert isinstance(nothing, Nothing)
    assert [m.text for m in nothing.chat.messages] == ["hi", "Done."]
    assert turns.started == [] and turns.released == turns.held


def test_try_again_on_an_unanswered_question_starts_without_writing_it(tmp_path):
    projects, chats = _stores(tmp_path, _user())
    started = _advance(FakeTurns(), chats, projects, text=NO_TEXT)
    assert [m.text for m in started.chat.messages] == ["hi"]


def test_a_null_sentence_is_not_try_again(tmp_path):
    # Absent asks for the answer; null is a sentence that is not one, and it breaks as one --
    # nothing is answered, and the chat is let go.
    projects, chats = _stores(tmp_path, _user())
    turns = FakeTurns()
    with pytest.raises(Exception):
        _advance(turns, chats, projects, text=None)
    assert turns.started == [] and turns.released == turns.held
