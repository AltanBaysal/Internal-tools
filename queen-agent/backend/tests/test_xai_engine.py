from backend.features.workspace.data.xai_engine import XaiEngine
from backend.features.workspace.domain.prompt import SYSTEM_PROMPT

CONVERSATION = [{"role": "user", "content": "a"}, {"role": "ai", "content": "b"}]


class FakeClient:
    def __init__(self):
        self.seen = None
        self.model = "not asked"

    def complete(self, messages, tools=None, model=None):
        self.seen = messages
        self.model = model
        return {"role": "assistant", "content": "hi"}

    def stream(self, messages, tools=None, model=None):
        self.seen = messages
        self.model = model
        return iter(["hi"])


def test_the_system_prompt_leads_and_the_roles_are_translated():
    client = FakeClient()
    XaiEngine(client).complete(CONVERSATION)
    assert client.seen[0] == {"role": "system", "content": SYSTEM_PROMPT}
    # Disk keeps the design's own word; xAI is told OpenAI's.
    assert [message["role"] for message in client.seen] == ["system", "user", "assistant"]


def test_streaming_is_prepared_the_same_way():
    client = FakeClient()
    list(XaiEngine(client).stream(CONVERSATION))
    assert client.seen[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert [message["role"] for message in client.seen] == ["system", "user", "assistant"]


def test_the_model_travels_with_the_call():
    # One client, many chats: which model answers is a property of the question, not of the wiring.
    client = FakeClient()
    list(XaiEngine(client).stream(CONVERSATION, model="grok-4.3"))
    assert client.model == "grok-4.3"


def test_no_model_asked_for_is_passed_on_as_none():
    client = FakeClient()
    list(XaiEngine(client).stream(CONVERSATION))
    assert client.model is None
