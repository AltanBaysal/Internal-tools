from backend.features.workspace.data.xai_engine import XaiEngine
from backend.features.workspace.domain.prompt import SYSTEM_PROMPT

CONVERSATION = [{"role": "user", "content": "a"}, {"role": "ai", "content": "b"}]


class FakeClient:
    # No model since Madde 82: this client would be built knowing which one. An engine that still
    # passed one would die here rather than quietly working.
    def __init__(self):
        self.seen = None
        self.on_open = None

    def complete(self, messages, tools=None):
        self.seen = messages
        return {"role": "assistant", "content": "hi"}

    def stream(self, messages, tools=None, on_open=None):
        self.seen = messages
        self.on_open = on_open
        return iter(["hi"])


def test_the_system_prompt_leads_and_the_roles_are_translated():
    client = FakeClient()
    XaiEngine(client).complete(CONVERSATION)
    assert client.seen[0] == {"role": "system", "content": SYSTEM_PROMPT}
    # Disk keeps the design's own word; xAI is told OpenAI's.
    assert [message["role"] for message in client.seen] == ["system", "user", "assistant"]


def test_the_fixed_part_leads_and_the_last_word_stays_last():
    # Madde 93's shape, end to end: what is fixed at the front, what changes at the back. The
    # engine adds to the front and reorders nothing -- if it ever sorted or grouped by role, the
    # instruction would land in the middle again and nothing else would notice.
    client = FakeClient()
    tail = {"role": "system", "content": "the instruction"}
    XaiEngine(client).complete(CONVERSATION + [tail])
    assert client.seen[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert client.seen[-1] == tail


def test_streaming_is_prepared_the_same_way():
    client = FakeClient()
    list(XaiEngine(client).stream(CONVERSATION))
    assert client.seen[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert [message["role"] for message in client.seen] == ["system", "user", "assistant"]


def test_the_way_to_cut_the_answer_travels_down_to_the_client():
    # Madde 90. The engine translates roles and nothing else, and that includes not swallowing
    # this: only the client holds a socket, so only the client can hand out a way to cut one.
    client = FakeClient()

    def handed(cut):
        pass

    list(XaiEngine(client).stream(CONVERSATION, on_open=handed))
    assert client.on_open is handed


def test_the_engine_hands_over_no_model():
    # Madde 82: which model answers belongs to the wiring, and the wiring is one line in config.py.
    # The engine translates roles and nothing else.
    client = FakeClient()
    list(XaiEngine(client).stream(CONVERSATION))
    assert client.seen is not None
