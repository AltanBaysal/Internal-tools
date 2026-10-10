"""What Try again does in each status (Madde 461): the use case alone, with a store that counts."""
from backend.features.workspace.domain.chat import Chat, Message, Version
from backend.features.workspace.domain.usecases.retry_turn import retry_turn

AT = "2026-10-10T10:00:00.000+00:00"


class Counting:
    """A chat store that keeps what it is given and counts it -- Try again is handed the chat."""

    def __init__(self):
        self.written = []

    def get(self, project_id, chat_id):
        raise AssertionError("Try again read the chat again")

    def replace(self, project_id, chat):
        self.written.append(chat)


def _chat(*said, **fields):
    return Chat(id="c1", title="hi", created_at=AT, messages=tuple(said), **fields)


def _user(text="hi", **fields):
    return Message(role="user", at=AT, text=text, **fields)


def _ai(text="Done.", **fields):
    return Message(role="ai", at=AT, text=text, **fields)


def test_a_question_nobody_answered_is_answered_and_nothing_is_written():
    # The question is on disk already: writing it again is what put it there twice (Madde 449).
    store, chat = Counting(), _chat(_user())
    assert retry_turn(store, "p1", chat) == chat
    assert store.written == []


def test_a_failed_answer_goes_and_its_question_is_answered_in_one_write():
    store = Counting()
    chat = _chat(_user(), _ai("HTTP 502", failed="technical"))
    started = retry_turn(store, "p1", chat)
    assert [m.text for m in started.messages] == ["hi"]
    assert store.written == [started]


def test_a_refused_answer_goes_the_same_way():
    store = Counting()
    started = retry_turn(store, "p1", _chat(_user(), _ai("x", failed="refused")))
    assert [m.role for m in started.messages] == ["user"]


def test_a_failed_answers_trim_moves_to_its_question():
    # Continue here marks the line's last message, which can be the failed answer. The trim
    # outlives it: the mark moves to the question in front of it, still on the same line.
    store = Counting()
    chat = _chat(_user(), _ai(), _user("more"), _ai("HTTP 502", failed="technical", trimmed=2))
    started = retry_turn(store, "p1", chat)
    assert [(m.text, m.trimmed) for m in started.messages] == [("hi", 0), ("Done.", 0), ("more", 2)]


def test_only_the_open_lines_failed_answer_goes():
    store = Counting()
    chat = _chat(
        _user(),
        _ai(),
        versions=(Version(id="l2", parent="", at=0, messages=(_user("again"), _ai("x", failed="technical"))),),
        active="l2",
    )
    started = retry_turn(store, "p1", chat)
    assert [m.text for m in started.versions[0].messages] == ["again"]
    assert [m.text for m in started.messages] == ["hi", "Done."]


def test_an_answered_chat_has_nothing_to_try_again():
    # The answer was written while the browser was not looking (the backlog's loop): nothing runs,
    # nothing is written, and whoever asked reads the answer.
    store = Counting()
    assert retry_turn(store, "p1", _chat(_user(), _ai())) is None
    assert store.written == []


def test_a_stopped_answer_has_nothing_to_try_again():
    # The user's answer of 10 October: a stopped answer offers no Try again.
    store = Counting()
    assert retry_turn(store, "p1", _chat(_user(), _ai("", stopped=True))) is None
    assert store.written == []


def test_an_empty_chat_has_nothing_to_try_again():
    assert retry_turn(Counting(), "p1", _chat()) is None
