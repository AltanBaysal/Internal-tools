import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.data.xai_engine import XaiEngine
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.prompt import SYSTEM_PROMPT
from backend.features.workspace.domain.usecases.answer_in_chat import answer_in_chat
from backend.features.workspace.domain.usecases.start_chat_in_new_project import (
    start_chat_in_new_project,
)
from backend.services.store.store import Store

NOW = "2026-08-09T11:06:00.000+00:00"


class FakeEngine:
    def __init__(self, answer="Done.", blow_up=None):
        self.answer = answer
        self.blow_up = blow_up
        self.seen = None

    def complete(self, messages):
        self.seen = messages
        if self.blow_up:
            raise RuntimeError(self.blow_up)
        return {"role": "assistant", "content": self.answer}


def _seeded(tmp_path):
    store = Store(str(tmp_path))
    projects, chats = FileProjectStore(store), FileChatStore(store)
    start_chat_in_new_project(projects, chats, "hello", "p1", "c1", "2026-08-09T11:04:00.000+00:00")
    return chats


def test_the_answer_lands_at_the_end_and_reaches_disk(tmp_path):
    chats = _seeded(tmp_path)
    chat = answer_in_chat(chats, FakeEngine(), "p1", "c1", NOW)
    assert [(m.role, m.text) for m in chat.messages] == [("user", "hello"), ("ai", "Done.")]
    assert chats.get("p1", "c1").messages[-1].text == "Done."


def test_a_broken_engine_leaves_the_chat_untouched(tmp_path):
    chats = _seeded(tmp_path)
    with pytest.raises(EngineFailed):
        answer_in_chat(chats, FakeEngine(blow_up="boom"), "p1", "c1", NOW)
    # What the user typed is still there; only the answer is missing.
    assert [m.text for m in chats.get("p1", "c1").messages] == ["hello"]


def test_the_failure_carries_the_engines_words(tmp_path):
    chats = _seeded(tmp_path)
    with pytest.raises(EngineFailed) as failure:
        answer_in_chat(chats, FakeEngine(blow_up="401 bad key"), "p1", "c1", NOW)
    assert "401 bad key" in str(failure.value)


def test_an_unknown_chat_is_reported(tmp_path):
    chats = _seeded(tmp_path)
    with pytest.raises(ChatNotFound):
        answer_in_chat(chats, FakeEngine(), "p1", "nope", NOW)


def test_the_engine_receives_the_whole_conversation(tmp_path):
    chats = _seeded(tmp_path)
    engine = FakeEngine()
    answer_in_chat(chats, engine, "p1", "c1", NOW)
    assert engine.seen == [{"role": "user", "content": "hello"}]


class FakeClient:
    def __init__(self):
        self.seen = None

    def complete(self, messages, tools=None):
        self.seen = messages
        return {"role": "assistant", "content": "hi"}


def test_the_system_prompt_leads_and_the_roles_are_translated():
    client = FakeClient()
    XaiEngine(client).complete([{"role": "user", "content": "a"}, {"role": "ai", "content": "b"}])
    assert client.seen[0] == {"role": "system", "content": SYSTEM_PROMPT}
    # Disk keeps the design's own word; xAI is told OpenAI's.
    assert [message["role"] for message in client.seen] == ["system", "user", "assistant"]


def test_the_system_prompt_is_never_stored(tmp_path):
    chats = _seeded(tmp_path)
    answer_in_chat(chats, FakeEngine(), "p1", "c1", NOW)
    assert all(SYSTEM_PROMPT not in message.text for message in chats.get("p1", "c1").messages)
