import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.chat import Chat
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.usecases.start_chat_in_new_project import (
    start_chat_in_new_project,
)
from backend.features.workspace.domain.usecases.stream_answer import stream_answer
from backend.services.store.store import Store

NOW = "2026-08-09T11:06:00.000+00:00"


class FakeEngine:
    def __init__(self, pieces=("He", "llo"), blow_up_after=None):
        self.pieces = pieces
        self.blow_up_after = blow_up_after

    def stream(self, messages, tools=None):
        for index, piece in enumerate(self.pieces):
            if self.blow_up_after is not None and index == self.blow_up_after:
                raise RuntimeError("connection dropped")
            yield piece


def _seeded(tmp_path):
    store = Store(str(tmp_path))
    projects, chats = FileProjectStore(store), FileChatStore(store)
    start_chat_in_new_project(projects, chats, "hi", "p1", "c1", "2026-08-09T11:04:00.000+00:00")
    return chats


def test_the_pieces_arrive_before_the_record(tmp_path):
    chats = _seeded(tmp_path)
    produced = list(stream_answer(chats, FakeEngine(), "p1", "c1", NOW))
    assert produced[:-1] == ["He", "llo"]
    assert isinstance(produced[-1], Chat)


def test_the_record_is_the_joined_text_and_reaches_disk(tmp_path):
    chats = _seeded(tmp_path)
    list(stream_answer(chats, FakeEngine(), "p1", "c1", NOW))
    stored = chats.get("p1", "c1").messages
    assert [(m.role, m.text) for m in stored] == [("user", "hi"), ("ai", "Hello")]


def test_a_stream_that_breaks_writes_nothing(tmp_path):
    chats = _seeded(tmp_path)
    with pytest.raises(EngineFailed):
        list(stream_answer(chats, FakeEngine(blow_up_after=1), "p1", "c1", NOW))
    # Half an answer is never kept: an answer either exists or it does not.
    assert [m.text for m in chats.get("p1", "c1").messages] == ["hi"]


def test_an_unknown_chat_is_reported_before_anything_streams(tmp_path):
    chats = _seeded(tmp_path)
    with pytest.raises(ChatNotFound):
        list(stream_answer(chats, FakeEngine(), "p1", "nope", NOW))
