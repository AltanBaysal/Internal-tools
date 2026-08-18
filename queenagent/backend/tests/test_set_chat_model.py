import pytest

from backend.features.workspace.domain.chat import Chat, Message
from backend.features.workspace.domain.errors import ChatNotFound
from backend.features.workspace.domain.usecases.set_chat_model import set_chat_model


class FakeChatStore:
    def __init__(self, chat=None):
        self.chat = chat
        self.replaced = []

    def get(self, project_id, chat_id):
        return self.chat if self.chat and self.chat.id == chat_id else None

    def replace(self, project_id, chat):
        self.replaced.append((project_id, chat))
        self.chat = chat


def _chat():
    return Chat(
        id="c1",
        title="Hello",
        created_at="2026-08-09T11:04:00+00:00",
        messages=(Message(role="user", at="2026-08-09T11:04:00+00:00", text="Hello"),),
    )


def test_the_chat_keeps_the_model_it_was_given():
    store = FakeChatStore(_chat())
    changed = set_chat_model(store, "p1", "c1", "grok-4.3")
    assert changed.model == "grok-4.3"
    assert store.replaced == [("p1", changed)]


def test_what_was_already_said_is_not_touched():
    # Changing the model mid-conversation answers the next question differently; it does not
    # rewrite the ones already answered.
    store = FakeChatStore(_chat())
    changed = set_chat_model(store, "p1", "c1", "grok-4.3")
    assert changed.messages == _chat().messages
    assert changed.title == "Hello"


def test_choosing_nothing_puts_the_chat_back_on_the_default():
    store = FakeChatStore(Chat(**{**vars(_chat()), "model": "grok-4.3"}))
    assert set_chat_model(store, "p1", "c1", "").model == ""


def test_a_chat_that_is_not_there_changes_nothing():
    store = FakeChatStore()
    with pytest.raises(ChatNotFound):
        set_chat_model(store, "p1", "nope", "grok-4.3")
    assert store.replaced == []
