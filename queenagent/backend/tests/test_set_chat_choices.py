import pytest

from backend.features.workspace.domain.chat import Chat, Message
from backend.features.workspace.domain.errors import ChatNotFound
from backend.features.workspace.domain.usecases.set_chat_choices import set_chat_choices


class FakeChatStore:
    def __init__(self, chat=None):
        self.chat = chat
        self.replaced = []

    def get(self, project_id, chat_id):
        return self.chat if self.chat and self.chat.id == chat_id else None

    def replace(self, project_id, chat):
        self.replaced.append((project_id, chat))
        self.chat = chat


def _chat(**fields):
    return Chat(
        id="c1",
        title="Hello",
        created_at="2026-08-09T11:04:00+00:00",
        messages=(Message(role="user", at="2026-08-09T11:04:00+00:00", text="Hello"),),
        **fields,
    )


def test_the_chat_keeps_the_model_it_was_given():
    store = FakeChatStore(_chat())
    changed = set_chat_choices(store, "p1", "c1", model="grok-4.3")
    assert changed.model == "grok-4.3"
    assert store.replaced == [("p1", changed)]


def test_the_chat_keeps_the_skill_it_was_given():
    store = FakeChatStore(_chat())
    assert set_chat_choices(store, "p1", "c1", skill="split-shots").skill == "split-shots"


# One use case, two choices, and neither reaches over into the other: the model menu and the skills
# menu are separate controls and a change in one must not clear the other.
def test_choosing_a_skill_leaves_the_model_alone():
    store = FakeChatStore(_chat(model="grok-4.3"))
    assert set_chat_choices(store, "p1", "c1", skill="verify").model == "grok-4.3"


def test_choosing_a_model_leaves_the_skill_alone():
    store = FakeChatStore(_chat(skill="verify"))
    assert set_chat_choices(store, "p1", "c1", model="grok-4.3").skill == "verify"


def test_what_was_already_said_is_not_touched():
    # Changing a choice mid-conversation answers the next question differently; it does not rewrite
    # the ones already answered.
    store = FakeChatStore(_chat())
    changed = set_chat_choices(store, "p1", "c1", model="grok-4.3")
    assert changed.messages == _chat().messages
    assert changed.title == "Hello"


def test_an_empty_skill_clears_the_selection():
    # Pressing the selected skill again clears it -- unlike a model, which is never absent.
    store = FakeChatStore(_chat(skill="verify"))
    assert set_chat_choices(store, "p1", "c1", skill="").skill == ""


def test_choosing_nothing_puts_the_chat_back_on_the_default_model():
    store = FakeChatStore(_chat(model="grok-4.3"))
    assert set_chat_choices(store, "p1", "c1", model="").model == ""


def test_a_chat_that_is_not_there_changes_nothing():
    store = FakeChatStore()
    with pytest.raises(ChatNotFound):
        set_chat_choices(store, "p1", "nope", model="grok-4.3")
    assert store.replaced == []
