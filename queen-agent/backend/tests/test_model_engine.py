import inspect

from backend.features.workspace.data.model_engine import ModelEngine
from backend.features.workspace.domain.prompt import SYSTEM_PROMPT

CONVERSATION = [{"role": "user", "content": "a"}, {"role": "ai", "content": "b"}]


DEFAULT = "deepseek-flash"


def _engine(client, **others):
    """One engine over a named set of clients, since Madde 146.

    Written here rather than in every test: what most of these ask about is the translation of
    roles, and that is the same whichever transport speaks.
    """
    return ModelEngine({DEFAULT: client, **others}, default=DEFAULT)


class FakeClient:
    # Still no model: which one this is stands in the engine's map rather than inside the client, so
    # a client that was handed one would die here rather than quietly working.
    def __init__(self):
        self.seen = None
        self.on_open = None

    def stream(self, messages, tools=None, on_open=None):
        self.seen = messages
        self.on_open = on_open
        return iter(["hi"])


def test_the_system_prompt_leads_and_the_roles_are_translated():
    client = FakeClient()
    list(_engine(client).stream(CONVERSATION))
    assert client.seen[0]["role"] == "system"
    # Leads it rather than is all of it (Madde 196): what follows is the owner's second part, and
    # this app's own page is what comes first. Pinning the whole string would put this test in the
    # way of the one thing that madde exists for -- somebody writing that part.
    assert client.seen[0]["content"].startswith(SYSTEM_PROMPT)
    # Disk keeps the design's own word; the model is told OpenAI's.
    assert [message["role"] for message in client.seen] == ["system", "user", "assistant"]


def test_the_fixed_part_leads_and_the_last_word_stays_last():
    # Madde 93's shape, end to end: what is fixed at the front, what changes at the back. The
    # engine adds to the front and reorders nothing -- if it ever sorted or grouped by role, the
    # instruction would land in the middle again and nothing else would notice.
    client = FakeClient()
    tail = {"role": "system", "content": "the instruction"}
    list(_engine(client).stream(CONVERSATION + [tail]))
    # The head is asked about the same way as above, and for the same reason.
    assert client.seen[0]["role"] == "system"
    assert client.seen[0]["content"].startswith(SYSTEM_PROMPT)
    assert client.seen[-1] == tail


def test_the_way_to_cut_the_answer_travels_down_to_the_client():
    # Madde 90. The engine translates roles and nothing else, and that includes not swallowing
    # this: only the client holds a socket, so only the client can hand out a way to cut one.
    client = FakeClient()

    def handed(cut):
        pass

    list(_engine(client).stream(CONVERSATION, on_open=handed))
    assert client.on_open is handed


def test_the_turn_names_no_model():
    # Madde 358. One model, and config.py names it: the engine is not told which one to speak with.
    assert "model" not in inspect.signature(ModelEngine.stream).parameters


def test_the_engine_is_told_of_no_prompt_writer():
    # Madde 395, the owner's decision of 30 September: the main model writes each frame's action
    # itself, so the role that wrote them for a tool is gone.
    assert "prompt_writer" not in inspect.signature(ModelEngine).parameters


def test_every_turn_is_spoken_by_the_default():
    # The map can hold more than one transport, and a turn goes to the one the engine was built
    # with as its default.
    turns, other = FakeClient(), FakeClient()
    engine = _engine(turns, **{"another-model": other})
    list(engine.stream(CONVERSATION))
    assert turns.seen is not None
    assert other.seen is None


# --- the second part of the system prompt (Madde 196) --------------------------------------------


def _with_suffix(monkeypatch, text):
    """The module's own constant, moved for one test.

    Patched on the module rather than handed in: the text is one of this app's texts and lives where
    the others do (Madde 189). What the engine must do is read it when the request is built, so a
    suffix written today is in the very next turn.
    """
    from backend.features.workspace.domain import prompt

    monkeypatch.setattr(prompt, "SYSTEM_PROMPT_SUFFIX", text)


def test_the_second_part_rides_at_the_end_of_the_system_message(monkeypatch):
    _with_suffix(monkeypatch, "This workspace is used for X.")
    client = FakeClient()
    list(_engine(client).stream(CONVERSATION))
    said = client.seen[0]["content"]
    assert said.startswith(SYSTEM_PROMPT)
    assert said.endswith("This workspace is used for X.")


def test_an_empty_second_part_leaves_the_request_exactly_as_it_was(monkeypatch):
    # Byte for byte. The system prompt is the fixed head the service files this conversation's
    # cached prefix under, and one trailing blank line would move that prefix on the first day --
    # for a sentence nobody has written yet.
    _with_suffix(monkeypatch, "")
    client = FakeClient()
    list(_engine(client).stream(CONVERSATION))
    assert client.seen[0] == {"role": "system", "content": SYSTEM_PROMPT}


def test_the_second_part_reaches_the_system_message_and_nothing_else(monkeypatch):
    _with_suffix(monkeypatch, "This workspace is used for X.")
    client = FakeClient()
    list(_engine(client).stream(CONVERSATION))
    assert client.seen[1:] == [
        {"role": "user", "content": "a"},
        {"role": "assistant", "content": "b"},
    ]
