from backend.features.workspace.data.xai_engine import XaiEngine
from backend.features.workspace.domain.prompt import SYSTEM_PROMPT

CONVERSATION = [{"role": "user", "content": "a"}, {"role": "ai", "content": "b"}]


DEFAULT = "grok-4.3"


def _engine(client, prompt_writer=DEFAULT, **others):
    """One engine over a named set of clients, since Madde 146.

    Written here rather than in every test: what most of these ask about is the translation of
    roles, and that is the same whichever transport speaks. Only the ones at the foot of the file
    care which transport did it.

    The third name is Madde 175's: which of them writes a prompt when a tool asks for one. It
    defaults to the same client here so the tests that do not care about it can stay quiet.
    """
    return XaiEngine({DEFAULT: client, **others}, default=DEFAULT, prompt_writer=prompt_writer)


class FakeClient:
    # Still no model: which one this is stands in the engine's map rather than inside the client, so
    # a client that was handed one would die here rather than quietly working.
    def __init__(self):
        self.seen = None
        self.on_open = None
        self.conversation_id = None

    def write_once(self, messages):
        self.seen = messages
        return {"text": "hi", "spent": {"sent": 40, "cached": 0, "answered": 8}}

    def stream(self, messages, tools=None, on_open=None, conversation_id=""):
        self.seen = messages
        self.on_open = on_open
        self.conversation_id = conversation_id
        return iter(["hi"])


def test_the_system_prompt_leads_and_the_roles_are_translated():
    client = FakeClient()
    list(_engine(client).stream(CONVERSATION))
    assert client.seen[0]["role"] == "system"
    # Leads it rather than is all of it (Madde 196): what follows is the owner's second part, and
    # this app's own page is what comes first. Pinning the whole string would put this test in the
    # way of the one thing that madde exists for -- somebody writing that part.
    assert client.seen[0]["content"].startswith(SYSTEM_PROMPT)
    # Disk keeps the design's own word; xAI is told OpenAI's.
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


# --- the one question a tool asks (Madde 175) -----------------------------------------------------
#
# The other road, and the opposite of stream in every way that matters: no tools, no conversation,
# no turn stamp, and a system prompt the caller brings. It exists because the model that writes a
# prompt is not this app's agent -- it is a writer with one job, and everything QueenAgent tells its
# agent would be noise in front of it.


def test_write_once_goes_to_the_prompt_writer_rather_than_the_turns_model():
    # The whole point of the third name. The turn's model is the user's choice; who writes a prompt
    # is a role in config.py, and the user does not pick it (their decision, 5 Sep).
    agent, writer = FakeClient(), FakeClient()
    engine = XaiEngine(
        {"deepseek-v4-flash": agent, "grok-4.3": writer},
        default="deepseek-v4-flash",
        prompt_writer="grok-4.3",
    )
    engine.write_once("you write prompts", "frame 3")
    assert writer.seen is not None
    assert agent.seen is None


def test_write_once_carries_its_own_system_prompt_and_no_conversation():
    # QueenAgent's own SYSTEM_PROMPT would be a page about tools, files and chats put in front of a
    # model that has one sentence to write.
    client = FakeClient()
    _engine(client).write_once("you write prompts", "frame 3")
    assert client.seen == [
        {"role": "system", "content": "you write prompts"},
        {"role": "user", "content": "frame 3"},
    ]
    assert SYSTEM_PROMPT not in [message["content"] for message in client.seen]


def test_write_once_hands_back_the_text_and_what_it_spent():
    # Both, because the answer is a tool's result and the spending is the turn's: a request the user
    # pays for that no stamp ever mentions is a request nobody can find.
    client = FakeClient()
    answer = _engine(client).write_once("s", "u")
    assert answer["text"] == "hi"
    assert answer["spent"] == {"sent": 40, "cached": 0, "answered": 8}


def test_the_way_to_cut_the_answer_travels_down_to_the_client():
    # Madde 90. The engine translates roles and nothing else, and that includes not swallowing
    # this: only the client holds a socket, so only the client can hand out a way to cut one.
    client = FakeClient()

    def handed(cut):
        pass

    list(_engine(client).stream(CONVERSATION, on_open=handed))
    assert client.on_open is handed


def test_the_conversation_id_travels_down_to_the_client():
    # Madde 124. The engine translates roles and nothing else -- the name a conversation goes to
    # the cache under passes through it untouched.
    client = FakeClient()
    list(_engine(client).stream(CONVERSATION, conversation_id="c7"))
    assert client.conversation_id == "c7"


def test_the_turn_is_spoken_by_the_model_it_names():
    # The reversal of Madde 82's lock. Which model answers is no longer one line in config.py: it
    # arrives with the turn, so the engine is the place that has to pick a transport for it.
    grok, flash = FakeClient(), FakeClient()
    engine = _engine(grok, **{"deepseek-v4-flash": flash})
    list(engine.stream(CONVERSATION, model="deepseek-v4-flash"))
    assert flash.seen is not None
    assert grok.seen is None


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


def test_the_frame_writer_is_handed_the_text_it_was_given(monkeypatch):
    # Madde 175's system prompt is the caller's, one sentence about one job, and this app's own page
    # about tools and files has never gone with it. Neither does its second part.
    _with_suffix(monkeypatch, "This workspace is used for X.")
    client = FakeClient()
    _engine(client).write_once("Write one action line.", "aylin, in the kitchen")
    assert client.seen[0] == {"role": "system", "content": "Write one action line."}


def test_an_unknown_or_absent_model_is_spoken_by_the_default():
    # The same rule config.engine_for keeps, held here as well because this is the layer a record
    # written before Madde 146 actually reaches: its messages name no model at all.
    grok, flash = FakeClient(), FakeClient()
    engine = _engine(grok, **{"deepseek-v4-flash": flash})
    # A name that can never be wired. It used to be grok-4.3, which Madde 183 turned into the
    # default above -- and an unknown example that becomes known tests nothing at all.
    list(engine.stream(CONVERSATION, model="a-model-nobody-wired"))
    list(engine.stream(CONVERSATION))
    assert flash.seen is None
    assert grok.seen is not None
