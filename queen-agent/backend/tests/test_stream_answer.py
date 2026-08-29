import json
from dataclasses import replace

import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.chat import Chat, ToolCall, Usage
from backend.features.workspace.domain.errors import ChatNotFound, EmptyMessage, EngineFailed
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.domain.tools import MAX_ROUNDS, FileStarted, FileWritten
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.features.workspace.domain.usecases.stream_answer import stream_answer
from backend.services.store.store import Store

NOW = "2026-08-09T11:06:00.000+00:00"

STRUCTURE = json.dumps(
    {
        "quality": "score_9_up",
        "characters": {"aylin": "1girl"},
        "outfits": {"gecelik": "white nightgown"},
        "locations": {"bedroom": "sunlit bedroom"},
        "frames": [
            {
                "characters": {"aylin": ["gecelik"]},
                "location": "bedroom",
                "action": "one",
                "camera": "wide",
            }
        ],
    }
)


def call(tool, call_id="t1", **arguments):
    return {"id": call_id, "function": {"name": tool, "arguments": json.dumps(arguments)}}


class NeverStops:
    """The stop registry as most tests need it: nobody ever asks."""

    def hold(self, project_id, chat_id, cut):
        pass

    def wanted(self, project_id, chat_id):
        return False

    def clear(self, project_id, chat_id):
        pass


NEVER = NeverStops()


class NeverAsked:
    """The permission registry as most tests need it: in edit mode nothing ever reaches here.

    Raising rather than answering is the point -- a turn that started asking in a mode that asks for
    nothing is a broken gate, and a fake that quietly said yes would hide it.
    """

    def answer(self, project_id, chat_id, allowed, reason):
        raise AssertionError("the turn answered its own question")

    def wait(self, project_id, chat_id, tick):
        raise AssertionError("nothing in this mode should have been asked")

    def wake(self, project_id, chat_id):
        raise AssertionError("nothing in this mode should have been asked")

    def clear(self, project_id, chat_id):
        # Every turn clears on its way out, asked or not.
        pass


UNASKED = NeverAsked()


class Answers:
    """A registry with its decisions written out, one per question.

    A None in the list is a tick that passed with nobody answering, which is what makes the beat
    visible. Running out raises: a gate that asked forever would otherwise spin this test until the
    suite was killed.
    """

    def __init__(self, *decisions, on_wait=None):
        self.decisions = list(decisions)
        self.on_wait = on_wait
        self.asked = []
        self.cleared = []

    def answer(self, project_id, chat_id, allowed, reason):
        raise AssertionError("the turn answered its own question")

    def wait(self, project_id, chat_id, tick):
        self.asked.append((project_id, chat_id))
        if self.on_wait:
            self.on_wait()
        if not self.decisions:
            raise AssertionError("the turn asked more than this test answers")
        return self.decisions.pop(0)

    def wake(self, project_id, chat_id):
        pass

    def clear(self, project_id, chat_id):
        self.cleared.append((project_id, chat_id))


class StopsWhileWaiting:
    """A stop that lands while the turn is paused on a question.

    Cut says yes to `wanted` from the first breath, which ends the round before the tool loop is
    ever reached -- so it cannot describe this moment. Here the press happens on the way into the
    wait, which is the one stretch of a turn with no socket to cut.
    """

    def __init__(self):
        self.pressed = False
        self.woke = None

    def hold(self, project_id, chat_id, cut):
        self.woke = cut

    def want(self, project_id, chat_id):
        self.pressed = True
        self.woke()

    def wanted(self, project_id, chat_id):
        return self.pressed

    def clear(self, project_id, chat_id):
        pass


class Cut:
    """The registry after a stop: however this answer ended, we are the ones who ended it.

    Since Madde 90 nothing counts here. The flag is not asked frame by frame any more -- the cut
    ends the round on its own, and the only question left is whose cut it was.
    """

    def __init__(self):
        self.held = []
        self.cleared = []

    def hold(self, project_id, chat_id, cut):
        self.held.append((project_id, chat_id, cut))

    def wanted(self, project_id, chat_id):
        return True

    def clear(self, project_id, chat_id):
        self.cleared.append((project_id, chat_id))


CUT = object()
"""Where the connection dies inside a round.

In production it is a socket that was shut down and a chunked body that stopped in the middle; here
it is a piece the engine refuses to get past.
"""


class ScriptedEngine:
    """Each round is a list of pieces the engine hands back."""

    def __init__(self, rounds, blow_up_after=None):
        self.rounds = list(rounds)
        self.blow_up_after = blow_up_after
        self.seen = []
        self.handed = []
        # Which tools each round was offered. Since Madde 91 that is the mode's whole consequence.
        self.tools = []
        # Which conversation each round said it belonged to (Madde 124).
        self.conversation_ids = []

    # No model since Madde 82: the engine is built knowing which one. A use case that still passed
    # one would die here rather than quietly working.
    def stream(self, messages, tools=None, on_open=None, conversation_id=""):
        self.seen.append(list(messages))
        self.tools.append([spec["function"]["name"] for spec in tools or []])
        self.conversation_ids.append(conversation_id)
        if on_open:
            on_open(self._cut)
        if self.blow_up_after is not None and len(self.seen) > self.blow_up_after:
            raise RuntimeError("connection dropped")
        pieces = self.rounds.pop(0) if self.rounds else []
        for piece in pieces:
            if piece is CUT:
                # What Python says when a chunked body stops in the middle. Nothing in the words
                # says who did it, which is the whole difficulty this item deals with.
                raise RuntimeError("IncompleteRead(0 bytes read)")
            yield piece

    def _cut(self):
        self.handed.append("cut")


def _seeded(tmp_path):
    store = Store(str(tmp_path))
    projects, chats, files = FileProjectStore(store), FileChatStore(store), FileFileStore(store)
    now = "2026-08-09T11:04:00.000+00:00"
    create_project(projects, new_id="p1", now=now)
    # Naming no chat is what asks for one, since Madde 87.
    append_message(chats, "p1", "", "hi", now, project_store=projects, new_id="c1")
    return chats, files


def _run(tmp_path, rounds, stops=NEVER, **kwargs):
    # The same run with nothing to ask. Edit mode is what the app defaults to and it stops for
    # nothing, so UNASKED raising is a guard here rather than an inconvenience.
    return _gated(tmp_path, rounds, stops=stops, mode="edit", **kwargs)


def allowed():
    from backend.features.workspace.domain.permission import Decision

    return Decision(True, "")


def refused(reason=""):
    from backend.features.workspace.domain.permission import Decision

    return Decision(False, reason)


def _gated(tmp_path, rounds, stops=NEVER, permissions=UNASKED, mode="ask", **kwargs):
    """_run's sibling, with the registry the turn reads its answer from.

    Its own helper for one turn only: _run's shape belongs to the tests already written, and
    breaking every one of them would bury this turn's reds. They meet in the implementation tour.
    """
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine(rounds, **kwargs)
    produced = list(stream_answer(chats, files, engine, "p1", "c1", NOW, stops, permissions, mode))
    return chats, files, engine, produced


# --- the names the project holds, handed over rather than asked for (Madde 127) ------------------
#
# The trial that opened Blok 10: every turn began with list_files, and one turn invented a name --
# read_file("plan.md") when the file on disk was milf-cheating-hentai-plan.md. Names are true every
# turn, so they belong in every request.


def _files_line(seen):
    """The one message naming the project's files, out of a round's messages.

    Matched on its opening rather than on the word project: a skill's instruction is a system
    message too, and prompt+ says project inside its own second paragraph.
    """
    return next(
        (
            message["content"]
            for message in seen
            if message["role"] == "system"
            and message["content"].startswith(("The project's files", "This project holds no"))
        ),
        "",
    )


def test_the_request_carries_the_names_the_project_holds(tmp_path):
    chats, files = _seeded(tmp_path)
    files.write("p1", "bar-scene.json", "{}")
    files.write("p1", "bar-scene-scenes.md", "one")
    engine = ScriptedEngine([[{"text": "hi"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    said = _files_line(engine.seen[0])
    assert "bar-scene.json" in said and "bar-scene-scenes.md" in said


def test_an_empty_project_says_it_holds_nothing(tmp_path):
    # Counting to zero does not say "there are none" -- the same sentence rule the listing tool
    # followed before it was taken away.
    _, _, engine, _ = _run(tmp_path, [[{"text": "hi"}]])
    assert "This project holds no files yet." in _files_line(engine.seen[0])


def test_the_names_are_fresh_in_every_round(tmp_path):
    # Built per round rather than once: a file born in round one is on disk for round two, and a
    # list that was assembled before the turn started would not know it.
    rounds = [
        [{"tool_calls": [call("create_file", name="plan.md", content="x")]}],
        [{"text": "done"}],
    ]
    _, _, engine, _ = _run(tmp_path, rounds)
    assert "plan.md" not in _files_line(engine.seen[0])
    assert "plan.md" in _files_line(engine.seen[1])


def test_the_names_ride_behind_the_conversation_and_before_the_instruction(tmp_path):
    # Madde 93's order, unbroken: what is fixed leads, what changes trails, and the skill's
    # instruction stays the last word. The names sit between them -- behind the conversation so a
    # file born mid-turn is seen, in front of the instruction so the instruction still closes.
    chats, files = _seeded(tmp_path)
    stored = chats.get("p1", "c1")
    chats.replace("p1", replace(stored, messages=(replace(stored.messages[0], skill="start-a-scenario"),)))
    engine = ScriptedEngine([[{"text": "hi"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    seen = engine.seen[0]
    assert seen[-1]["content"] == instruction_for("start-a-scenario")
    assert "This project holds no files yet." in seen[-2]["content"]
    assert seen[-3]["role"] == "user"


# --- the context box: what was read, as it is now (Madde 129) ------------------------------------
#
# A read's result froze where it was written: the file moved on and the message did not, so the
# model read it again -- three times in the trial, each copy riding every later request. The box
# holds names and reads the contents from disk, so there is one entry and it is never stale.


def _box(seen):
    """The one message carrying the opened files' contents, out of a round's messages."""
    return next(
        (
            message["content"]
            for message in seen
            if message["role"] == "system" and message["content"].startswith("Files you have opened")
        ),
        "",
    )


def test_the_request_carries_the_contents_of_what_was_read(tmp_path):
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "the body of the plan")
    rounds = [[{"tool_calls": [call("read_file", name="plan.md")]}], [{"text": "done"}]]
    engine = ScriptedEngine(rounds)
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    # Not in the first round -- nothing had been read yet -- and in the second, whole.
    assert _box(engine.seen[0]) == ""
    assert "plan.md" in _box(engine.seen[1])
    assert "the body of the plan" in _box(engine.seen[1])


def test_the_box_is_refreshed_from_disk_every_round(tmp_path):
    # The claim that makes the read-back unnecessary: what the box shows is what is on disk now,
    # not what the read returned when it ran.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "first")
    rounds = [
        [{"tool_calls": [call("read_file", name="plan.md")]}],
        [{"tool_calls": [call("edit_file", name="plan.md", old="first", new="second")]}],
        [{"text": "done"}],
    ]
    engine = ScriptedEngine(rounds)
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    assert "first" in _box(engine.seen[1])
    assert "second" in _box(engine.seen[2])
    assert "first" not in _box(engine.seen[2])


def test_a_file_read_in_an_earlier_turn_is_still_in_the_box(tmp_path):
    # Across turns, not only rounds: the trial opened every turn by reading the same pair again.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "the body")
    append_message(
        chats, "p1", "c1", "read it", NOW, role="ai", calls=(ToolCall("read_file", "plan.md", "1 line"),)
    )
    append_message(chats, "p1", "c1", "and now?", NOW)
    engine = ScriptedEngine([[{"text": "here"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    assert "the body" in _box(engine.seen[0])


def test_a_deleted_file_falls_out_of_the_box(tmp_path):
    # Quietly: the box holds a name, and a name with nothing behind it is simply not shown. An
    # empty heading would read as an empty file.
    chats, files = _seeded(tmp_path)
    files.write("p1", "gone.md", "for now")
    append_message(
        chats, "p1", "c1", "read it", NOW, role="ai", calls=(ToolCall("read_file", "gone.md", "1 line"),)
    )
    append_message(chats, "p1", "c1", "and now?", NOW)
    files.delete("p1", "gone.md")
    engine = ScriptedEngine([[{"text": "here"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    assert "gone.md" not in _box(engine.seen[0])


def test_the_schema_reaches_the_box_too(tmp_path):
    # One text for the whole app, so it travels by name rather than by lookup. Fetched once in a
    # chat, it is in front of the model from then on.
    chats, files = _seeded(tmp_path)
    rounds = [[{"tool_calls": [call("read_prompt_structure_schema")]}], [{"text": "done"}]]
    engine = ScriptedEngine(rounds)
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    from backend.features.workspace.domain.schema import SCHEMA

    # Unnumbered, and Madde 131 leaves it so: numbers are there to pick an anchor, and no anchor is
    # ever written into the schema.
    assert SCHEMA in _box(engine.seen[1])


def test_the_box_numbers_the_lines_it_shows(tmp_path):
    # Madde 131. Since 129 the box is where a file is actually looked at -- the model does not read
    # it a second time -- so numbering the tool's own answer alone would number the copy nobody
    # reads.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "alpha\nbeta")
    rounds = [[{"tool_calls": [call("read_file", name="plan.md")]}], [{"text": "done"}]]
    engine = ScriptedEngine(rounds)
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    assert "     1\talpha\n     2\tbeta" in _box(engine.seen[1])


def test_the_box_and_a_read_show_a_file_the_same_way(tmp_path):
    # One file, one shape. Two would leave the model deciding which of them its anchor has to
    # match, and the wrong pick is a refused edit.
    from backend.features.workspace.domain.tools import run_tool

    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "alpha\nbeta")
    rounds = [[{"tool_calls": [call("read_file", name="plan.md")]}], [{"text": "done"}]]
    engine = ScriptedEngine(rounds)
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    handed_back = run_tool(files, "p1", "read_file", json.dumps({"name": "plan.md"})).text
    assert handed_back in _box(engine.seen[1])


def test_the_box_rides_between_the_names_and_the_instruction(tmp_path):
    # Madde 93's order still holds: the instruction closes the request. The names and the box are
    # the request's own words, behind the conversation and in front of it.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "the body")
    stored = chats.get("p1", "c1")
    chats.replace(
        "p1", replace(stored, messages=(replace(stored.messages[0], skill="start-a-scenario"),))
    )
    append_message(
        chats, "p1", "c1", "read it", NOW, role="ai", calls=(ToolCall("read_file", "plan.md", "1 line"),)
    )
    append_message(chats, "p1", "c1", "carry on", NOW, skill="start-a-scenario")
    engine = ScriptedEngine([[{"text": "here"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, "edit"))
    seen = engine.seen[0]
    assert seen[-1]["content"] == instruction_for("start-a-scenario")
    assert seen[-2]["content"].startswith("Files you have opened")
    assert _files_line([seen[-3]])


def test_a_chat_that_read_nothing_carries_no_box(tmp_path):
    # Nothing to say is said by saying nothing: an empty heading is a line the model has to read
    # before finding out it is empty.
    _, _, engine, _ = _run(tmp_path, [[{"text": "hi"}]])
    assert _box(engine.seen[0]) == ""


def test_the_engine_is_told_which_chat_is_asking(tmp_path):
    # Madde 124: the chat is the conversation, and its id is the name the service's cache files
    # this turn's prefix under. A request that never says whose it is starts cold every time.
    _, _, engine, _ = _run(tmp_path, [[{"text": "hi"}]])
    assert engine.conversation_ids == ["c1"]


def _write_round(name="plan.md"):
    return [{"tool_calls": [call("create_file", name=name, content="x")]}]


def test_a_round_without_tools_ends_the_loop(tmp_path):
    chats, _, engine, produced = _run(tmp_path, [[{"text": "He"}, {"text": "llo"}]])
    assert produced[:-1] == ["He", "llo"]
    assert isinstance(produced[-1], Chat)
    assert len(engine.seen) == 1


def test_a_tool_call_is_run_and_the_answer_goes_back_to_the_model(tmp_path):
    rounds = [[{"tool_calls": [call("read_file", name="ghost.md")]}], [{"text": "Nothing yet."}]]
    _, _, engine, _ = _run(tmp_path, rounds)
    assert len(engine.seen) == 2
    # The conversation's own tail: what the model said, then what the tool answered back. Behind
    # them ride the request's fixed words -- since Madde 127 the file names, and the instruction.
    spoken = [message for message in engine.seen[1] if message["role"] in ("assistant", "tool")]
    assert spoken[-2]["tool_calls"][0]["id"] == "t1"
    assert spoken[-1] == {
        "role": "tool",
        "tool_call_id": "t1",
        "content": "There is no file by that name.",
    }


def test_two_calls_in_one_round_are_both_run(tmp_path):
    # Two names rather than the same one twice. The claim is that the loop runs both calls; it used
    # to rest that on the numbered copy the second one produced, and since Madde 69 a create over a
    # name that is taken writes nothing. Two files is the same claim measured without that lean.
    rounds = [
        [
            {
                "tool_calls": [
                    call("create_file", call_id="a", name="plan.md", content="x"),
                    call("create_file", call_id="b", name="notes.md", content="y"),
                ]
            }
        ],
        [{"text": "done"}],
    ]
    _, files, _, _ = _run(tmp_path, rounds)
    assert sorted(files.list_names("p1")) == ["notes.md", "plan.md"]


def test_text_from_every_round_becomes_one_message(tmp_path):
    rounds = [[{"text": "Looking. "}, {"tool_calls": [call("read_prompt_structure_schema")]}], [{"text": "Nothing."}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    stored = chats.get("p1", "c1").messages
    assert [(m.role, m.text) for m in stored] == [("user", "hi"), ("ai", "Looking. Nothing.")]


def test_the_tool_traffic_is_never_written_to_the_chat(tmp_path):
    rounds = [[{"tool_calls": [call("read_prompt_structure_schema")]}], [{"text": "done"}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    # The chat is what the user reads, not the model's bookkeeping.
    assert [m.role for m in chats.get("p1", "c1").messages] == ["user", "ai"]


def test_the_loop_stops_at_the_round_limit_and_still_writes(tmp_path):
    forever = [[{"text": "."}, {"tool_calls": [call("read_prompt_structure_schema")]}] for _ in range(MAX_ROUNDS + 3)]
    chats, _, engine, _ = _run(tmp_path, forever)
    assert len(engine.seen) == MAX_ROUNDS
    assert chats.get("p1", "c1").messages[-1].text == "." * MAX_ROUNDS


def test_a_file_the_model_asks_for_reaches_the_disk(tmp_path):
    rounds = [
        [{"tool_calls": [call("create_file", name="Chapter 2", content="# Intro")]}],
        [{"text": "Saved."}],
    ]
    _, files, _, _ = _run(tmp_path, rounds)
    assert files.list_names("p1") == ["Chapter-2.md"]
    assert files.read("p1", "Chapter-2.md") == "# Intro"


def test_a_created_file_announces_itself_twice(tmp_path):
    rounds = [
        [{"tool_calls": [call("create_file", name="plan.md", content="x")]}],
        [{"text": "Saved."}],
    ]
    _, _, _, produced = _run(tmp_path, rounds)
    # The dashed card goes up before the tool runs, the filled one after it.
    assert isinstance(produced[0], FileStarted)
    assert produced[1] == FileWritten("plan.md")


def test_the_reply_remembers_the_file_it_produced(tmp_path):
    rounds = [
        [{"tool_calls": [call("create_file", name="plan.md", content="x")]}],
        [{"text": "Saved."}],
    ]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert chats.get("p1", "c1").messages[-1].files == ("plan.md",)


def test_a_reply_without_a_file_remembers_none(tmp_path):
    chats, _, _, _ = _run(tmp_path, [[{"text": "just talking"}]])
    assert chats.get("p1", "c1").messages[-1].files == ()


def test_reading_a_file_announces_nothing(tmp_path):
    rounds = [[{"tool_calls": [call("read_file", name="ghost.md")]}], [{"text": "Not there."}]]
    _, _, _, produced = _run(tmp_path, rounds)
    assert not any(isinstance(piece, (FileStarted, FileWritten)) for piece in produced)


def test_building_prompts_announces_itself_twice(tmp_path):
    chats, files = _seeded(tmp_path)
    files.write("p1", "frames.json", STRUCTURE)
    rounds = [[{"tool_calls": [call("build_prompts", name="frames.json")]}], [{"text": "done"}]]
    produced = list(stream_answer(chats, files, ScriptedEngine(rounds), "p1", "c1", NOW, NEVER, UNASKED))
    # A file is born here too, so it gets the same dashed card and the same filled one.
    assert isinstance(produced[0], FileStarted)
    assert produced[1] == FileWritten("frames.py")


def test_editing_a_file_announces_nothing(tmp_path):
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "alpha")
    rounds = [
        [{"tool_calls": [call("edit_file", name="plan.md", old="alpha", new="beta")]}],
        [{"text": "done"}],
    ]
    produced = list(stream_answer(chats, files, ScriptedEngine(rounds), "p1", "c1", NOW, NEVER, UNASKED))
    # An edit is not a birth: a card would claim a file the user already has is new.
    assert not any(isinstance(piece, (FileStarted, FileWritten)) for piece in produced)
    assert files.read("p1", "plan.md") == "beta"


def test_a_name_born_twice_in_one_turn_is_remembered_once(tmp_path):
    chats, files = _seeded(tmp_path)
    files.write("p1", "frames.json", STRUCTURE)
    rounds = [
        [
            {
                "tool_calls": [
                    call("build_prompts", call_id="a", name="frames.json"),
                    call("build_prompts", call_id="b", name="frames.json"),
                ]
            }
        ],
        [{"text": "done"}],
    ]
    list(stream_answer(chats, files, ScriptedEngine(rounds), "p1", "c1", NOW, NEVER, UNASKED))
    # The card says a file exists, not how many times it was written.
    assert chats.get("p1", "c1").messages[-1].files == ("frames.py",)


def test_a_silent_turn_that_made_a_file_is_still_an_answer(tmp_path):
    # The model that only works and never speaks is the common case under a skill, and what it
    # made is the answer.
    rounds = [[{"tool_calls": [call("create_file", name="plan.md", content="x")]}], []]
    _, _, _, produced = _run(tmp_path, rounds)
    assert isinstance(produced[-1], Chat)


def test_the_silent_answer_keeps_the_file_and_no_words(tmp_path):
    rounds = [[{"tool_calls": [call("create_file", name="plan.md", content="x")]}], []]
    chats, _, _, _ = _run(tmp_path, rounds)
    kept = chats.get("p1", "c1").messages[-1]
    assert kept.text == ""
    assert kept.files == ("plan.md",)


def test_the_silent_answer_is_still_one_reply_in_the_chat(tmp_path):
    rounds = [[{"tool_calls": [call("create_file", name="plan.md", content="x")]}], []]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert [m.role for m in chats.get("p1", "c1").messages] == ["user", "ai"]


def test_a_turn_that_said_nothing_and_made_nothing_is_not_an_answer(tmp_path):
    # The boundary of the rule: reading a file is not making one, so this turn produced neither a
    # word nor a file and there is nothing to keep.
    rounds = [[{"tool_calls": [call("read_file", name="ghost.md")]}], []]
    with pytest.raises(EmptyMessage):
        _run(tmp_path, rounds)


def test_a_silent_turn_that_runs_out_of_rounds_is_not_an_answer_either(tmp_path):
    # Same rule down a different road: the loop stops at its limit rather than at a quiet round.
    forever = [[{"tool_calls": [call("read_prompt_structure_schema")]}] for _ in range(MAX_ROUNDS + 3)]
    with pytest.raises(EmptyMessage):
        _run(tmp_path, forever)


def _said_with(tmp_path, *turns):
    """Run one answer over a chat whose messages were sent with the given skills."""
    chats, files = _seeded(tmp_path)
    for number, (text, skill) in enumerate(turns):
        append_message(chats, "p1", "c1", text, f"2026-08-09T12:0{number}:00.000+00:00", skill=skill)
    engine = ScriptedEngine([[{"text": "ok"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED))
    return chats, engine.seen[0]


def _instructions(conversation):
    """The skill instructions a request carries -- never the file names.

    Since Madde 127 those ride as a system message of their own, in every request, whether or not
    a skill is selected. Counting them here would read as an instruction nobody selected.
    """
    return [
        piece["content"]
        for piece in conversation
        if piece["role"] == "system" and not _files_line([piece])
    ]


def test_the_instruction_is_the_last_thing_in_the_request(tmp_path):
    # Two measures point at the same place. Attention: accuracy is highest at the two ends of a
    # context and falls by more than a third in the middle. Cache: what is fixed stays at the front
    # so the prefix holds, and what changes sits at the end so only it goes stale.
    _, conversation = _said_with(tmp_path, ("write me the prompts", "generate-prompts-plus"))
    assert conversation[-1] == {
        "role": "system",
        "content": instruction_for("generate-prompts-plus"),
    }
    # Two back rather than one since Madde 127: the file names sit between the conversation and
    # the instruction, and the instruction is still what closes the request.
    assert conversation[-3]["content"] == "write me the prompts"


def test_only_the_current_skill_is_sent_whatever_came_before(tmp_path):
    # However many times the selection changed, one instruction goes and it is this turn's. Before
    # Madde 93 a chat that had changed skill four times carried four texts, the oldest of them
    # forty messages back -- and the model had to find the newest copy among them.
    # The two values are the skill and no skill: since Madde 94 the menu holds one name, and letting
    # a selection go is the other thing a user can do with it.
    _, conversation = _said_with(
        tmp_path,
        ("one", "generate-prompts-plus"),
        ("and again", "generate-prompts-plus"),
        ("never mind", ""),
    )
    assert _instructions(conversation) == []


def test_no_instruction_stands_among_the_messages(tmp_path):
    # The other half of the same move: the block did not just get a new place, the old places are
    # empty. Measured on the messages rather than on the whole request, because the one at the end
    # is the one that is supposed to be there.
    _, conversation = _said_with(
        tmp_path, ("one", "generate-prompts-plus"), ("and the rest", "generate-prompts-plus")
    )
    # Three, because the chat was born with a message of its own before these two. The file names
    # are dropped rather than counted: they are the request's, not the conversation's.
    said = [piece for piece in conversation[:-1] if not _files_line([piece])]
    assert [piece["role"] for piece in said] == ["user", "user", "user"]


def test_the_instruction_moves_to_the_end_of_every_round(tmp_path):
    # An answer runs up to sixteen rounds and each sends its own request. Left where it was, the
    # block would sit behind the tool exchanges from the second round on -- and the reason this
    # item exists would stop holding after the first one.
    chats, files = _seeded(tmp_path)
    append_message(chats, "p1", "c1", "build me the prompts", NOW, skill="generate-prompts-plus")
    engine = ScriptedEngine([[{"tool_calls": [call("read_prompt_structure_schema")]}], [{"text": "clean"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED))
    second = engine.seen[1]
    assert second[-1] == {"role": "system", "content": instruction_for("generate-prompts-plus")}
    # And what it moved past: the round that asked for the tool, and the tool's answer. Counted
    # from the conversation's own end rather than from the request's -- what the request adds
    # behind it has grown twice already (the names in 127, the box in 129) and each time this
    # line had to be renumbered for a claim that never changed.
    spoken = [piece for piece in second if piece["role"] in ("assistant", "tool")]
    assert [piece["role"] for piece in spoken[-2:]] == ["assistant", "tool"]


def test_a_chat_without_a_skill_is_told_nothing_extra(tmp_path):
    _, conversation = _said_with(tmp_path, ("hello", ""))
    assert _instructions(conversation) == []


def test_a_skill_nobody_knows_adds_nothing_and_still_answers(tmp_path):
    chats, conversation = _said_with(tmp_path, ("hello", "web-search"))
    assert _instructions(conversation) == []
    assert chats.get("p1", "c1").messages[-1].text == "ok"


def test_the_instruction_is_never_written_to_the_chat(tmp_path):
    chats, _ = _said_with(tmp_path, ("write me the prompts", "generate-prompts-plus"))
    # The transcript is what the user reads: user sentences and answers, nothing else.
    assert [m.role for m in chats.get("p1", "c1").messages] == ["user", "user", "ai"]


def test_a_stream_that_breaks_writes_nothing(tmp_path):
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "half"}]], blow_up_after=0)
    with pytest.raises(EngineFailed):
        list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED))
    assert [m.text for m in chats.get("p1", "c1").messages] == ["hi"]


def test_an_unknown_chat_is_reported_before_anything_streams(tmp_path):
    chats, files = _seeded(tmp_path)
    with pytest.raises(ChatNotFound):
        list(stream_answer(chats, files, ScriptedEngine([]), "p1", "nope", NOW, NEVER, UNASKED))


def test_the_engine_is_asked_without_a_model(tmp_path):
    # Madde 82: which model answers belongs to the wiring, not to the chat. ScriptedEngine.stream
    # refuses one, so a use case that passed a model would die here.
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "hi"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED))
    assert len(engine.seen) == 1


# --- the calls a turn made, seen and kept (Madde 66) ---------------------------------------------


def _lines(produced):
    return [piece for piece in produced if isinstance(piece, ToolCall)]


def test_each_call_leaves_a_line_as_it_happens(tmp_path):
    rounds = [[{"tool_calls": [call("read_prompt_structure_schema")]}], [{"text": "Nothing yet."}]]
    _, _, _, produced = _run(tmp_path, rounds)
    assert _lines(produced) == [ToolCall("read_prompt_structure_schema", "", "Schema")]


def test_the_line_says_which_file_was_touched(tmp_path):
    rounds = [
        [{"tool_calls": [call("create_file", name="plan.md", content="x")]}],
        [{"tool_calls": [call("read_file", call_id="t2", name="plan.md")]}],
        [{"text": "Read it."}],
    ]
    _, _, _, produced = _run(tmp_path, rounds)
    assert _lines(produced) == [
        ToolCall("create_file", "plan.md", "Saved"),
        ToolCall("read_file", "plan.md", "1 line"),
    ]


def test_the_answer_remembers_the_calls_it_made(tmp_path):
    # The other half of the item: a line that only exists while the answer streams leaves the chat
    # as blind tomorrow as it is today.
    rounds = [[{"tool_calls": [call("read_prompt_structure_schema")]}], [{"text": "done"}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert chats.get("p1", "c1").messages[-1].calls == (ToolCall("read_prompt_structure_schema", "", "Schema"),)


def test_an_answer_that_called_nothing_remembers_none(tmp_path):
    chats, _, _, _ = _run(tmp_path, [[{"text": "Hello"}]])
    assert chats.get("p1", "c1").messages[-1].calls == ()


def test_the_kept_call_says_how_it_went(tmp_path):
    # Madde 78. The tests above pin the tool and the file; none of them asks whether the line under
    # the call survived, and that is the half a reader a week later is looking at.
    rounds = [[{"tool_calls": [call("read_prompt_structure_schema")]}], [{"text": "done"}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert chats.get("p1", "c1").messages[-1].calls[0].outcome == "Schema"


def test_reading_the_same_file_twice_is_two_lines(tmp_path):
    # Files fold a repeat away, because a name born twice is still one file. Calls do not: reading
    # the same file twice really is two steps, and hiding one would misreport the turn.
    rounds = [
        [{"tool_calls": [call("create_file", name="plan.md", content="x")]}],
        [{"tool_calls": [call("read_file", call_id="t2", name="plan.md")]}],
        [{"tool_calls": [call("read_file", call_id="t3", name="plan.md")]}],
        [{"text": "done"}],
    ]
    chats, _, _, _ = _run(tmp_path, rounds)
    kept = chats.get("p1", "c1").messages[-1].calls
    assert kept.count(ToolCall("read_file", "plan.md", "1 line")) == 2


# --- stopping an answer that is already running (Madde 67) ---------------------------------------

TWO_ROUNDS = [[{"text": "Half a "}, {"tool_calls": [call("read_prompt_structure_schema")]}], [{"text": "sentence."}]]


def test_a_stop_ends_the_answer_without_asking_the_model_again(tmp_path):
    # The first round asked for a tool, which is what would normally open a second one.
    _, _, engine, _ = _run(tmp_path, TWO_ROUNDS, stops=Cut())
    assert len(engine.seen) == 1


def test_what_was_already_said_is_kept(tmp_path):
    # The owner's choice: stopping is something you decide, and what you had read stays yours.
    chats, _, _, _ = _run(tmp_path, TWO_ROUNDS, stops=Cut())
    assert chats.get("p1", "c1").messages[-1].text == "Half a"


def test_a_stopped_answer_says_it_was_stopped(tmp_path):
    # Half a sentence with no mark cannot be told from a model that finished on one.
    chats, _, _, _ = _run(tmp_path, TWO_ROUNDS, stops=Cut())
    assert chats.get("p1", "c1").messages[-1].stopped is True


def test_the_running_answer_hands_the_registry_a_way_to_cut_it(tmp_path):
    # Madde 90. The registry is reached from the thread carrying the stop and holds no socket of
    # its own; this is the one moment where the two meet.
    stops = Cut()
    _, _, engine, _ = _run(tmp_path, [[{"text": "Hi"}]], stops=stops)
    assert [(project, chat) for project, chat, _ in stops.held] == [("p1", "c1")]
    stops.held[0][2]()
    assert engine.handed == ["cut"]


def test_a_connection_we_cut_is_a_stop_rather_than_a_failure(tmp_path):
    # Our own cut and a network that dropped arrive as the same words -- nothing in the failure
    # says who ended it. The registry is the only thing that knows, so it is asked before the
    # failure is believed.
    chats, _, _, _ = _run(tmp_path, [[{"text": "Half a "}, CUT]], stops=Cut())
    kept = chats.get("p1", "c1").messages[-1]
    assert kept.text == "Half a"
    assert kept.stopped is True


def test_an_answer_that_runs_to_the_end_is_not_marked(tmp_path):
    chats, _, _, _ = _run(tmp_path, [[{"text": "All of it."}]])
    assert chats.get("p1", "c1").messages[-1].stopped is False


def test_stopping_before_a_word_still_writes_that_it_was_stopped(tmp_path):
    # Nothing was said and nothing was made, but something happened: somebody stopped it. Written
    # down, because a press that leaves no trace reads as a press that did nothing -- and because
    # the chat's last word would otherwise still be the user's, which means owed an answer, which
    # means the browser asks for one again the moment the page is reloaded.
    #
    # This is the press Madde 90 was written for: it lands while the model is still thinking, and
    # the connection dies before a single word has come down it.
    chats, _, _, _ = _run(tmp_path, [[CUT]], stops=Cut())
    kept = chats.get("p1", "c1").messages
    assert [m.role for m in kept] == ["user", "ai"]
    assert kept[-1].text == ""
    assert kept[-1].stopped is True


def test_the_request_is_cleared_when_the_answer_ends(tmp_path):
    # Left standing it would cut the next answer as it was born.
    stops = Cut()
    _run(tmp_path, TWO_ROUNDS, stops=stops)
    assert stops.cleared == [("p1", "c1")]


# --- what the answer spent (Madde 68) ------------------------------------------------------------


def spent(sent, cached, answered):
    """A piece the engine hands over the same way it hands over words."""
    return {"usage": {"sent": sent, "cached": cached, "answered": answered}}


def _kept(chats):
    return chats.get("p1", "c1").messages[-1]


def test_the_answer_remembers_what_it_spent(tmp_path):
    chats, _, _, _ = _run(tmp_path, [[{"text": "Hello"}, spent(1200, 900, 42)]])
    assert _kept(chats).usage == Usage(1200, 900, 42)


def test_what_two_rounds_spent_is_added_up(tmp_path):
    # Each round is its own stream and its own bill: the second one resends the whole conversation,
    # which is exactly the growth this item exists to make visible.
    rounds = [
        [{"tool_calls": [call("read_prompt_structure_schema")]}, spent(1000, 600, 10)],
        [{"text": "done"}, spent(1500, 1200, 20)],
    ]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert _kept(chats).usage == Usage(2500, 1800, 30)


def test_counts_repeated_inside_one_round_are_not_added_twice(tmp_path):
    # Inside one stream the service restates a running total rather than reporting a share, so the
    # newest reading replaces the one before it. Adding them would multiply the bill by the number
    # of chunks that happened to arrive.
    rounds = [[spent(1200, 900, 1), {"text": "Hi"}, spent(1200, 900, 2)]]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert _kept(chats).usage == Usage(1200, 900, 2)


def test_an_answer_nobody_measured_spent_nothing(tmp_path):
    # Zero is what unknown looks like, and it is the same zero an answer from before this existed
    # reads back as. Nothing is drawn for either.
    chats, _, _, _ = _run(tmp_path, [[{"text": "Hello"}]])
    assert _kept(chats).usage == Usage()


def test_a_stopped_answer_still_says_what_it_spent(tmp_path):
    # Whatever was measured before the cut is kept, and the fold happens before the stop is acted
    # on so that it can be. The window is narrow -- the engine reports once, at the end of the
    # round -- but a stop landing between that frame and the end of the loop is a real moment, and
    # dropping the figure there would throw away something already paid for.
    rounds = [[spent(1200, 900, 5), {"text": "Half a "}, CUT]]
    chats, _, _, _ = _run(tmp_path, rounds, stops=Cut())
    assert _kept(chats).text == "Half a"
    assert _kept(chats).usage == Usage(1200, 900, 5)


def test_an_answer_stopped_before_the_counts_arrive_spent_nothing_it_knows_of(tmp_path):
    # Madde 76, and the honest record of a limit rather than a guard on a behaviour. The engine
    # reports once, in a frame just before the stream closes; an answer cut short never reaches it.
    # So a stopped answer usually says nothing about what it spent, even though it spent it.
    rounds = [[{"text": "Half a "}, CUT, spent(1200, 900, 5)]]
    chats, _, _, _ = _run(tmp_path, rounds, stops=Cut())
    assert _kept(chats).text == "Half a"
    assert _kept(chats).usage == Usage()


# --- permission asked in the middle of a turn (Madde 99) -----------------------------------------


def test_a_call_the_mode_does_not_cover_is_asked_about(tmp_path):
    permissions = Answers(allowed())
    _gated(tmp_path, [_write_round(), [{"text": "done"}]], permissions=permissions)
    assert permissions.asked == [("p1", "c1")]


def test_the_question_carries_the_tool_and_its_arguments(tmp_path):
    # Raw, the way the model wrote them. Parsing here would be a second parser beside run_tool's,
    # and the two would drift on the first change to either.
    from backend.features.workspace.domain.permission import PermissionWanted

    _, _, _, produced = _gated(
        tmp_path, [_write_round(), [{"text": "done"}]], permissions=Answers(allowed())
    )
    asked = [piece for piece in produced if isinstance(piece, PermissionWanted)]
    assert asked == [
        PermissionWanted("create_file", json.dumps({"name": "plan.md", "content": "x"}))
    ]


def test_an_allowed_call_runs(tmp_path):
    _, files, _, _ = _gated(
        tmp_path, [_write_round(), [{"text": "done"}]], permissions=Answers(allowed())
    )
    assert files.list_names("p1") == ["plan.md"]


def test_an_allowed_call_changes_the_mode_for_the_rest_of_the_turn(tmp_path):
    # One answer for two writes. Measured by the registry running out if it is asked twice, which
    # is exactly what a mode that did not change would do.
    rounds = [
        [
            {
                "tool_calls": [
                    call("create_file", call_id="a", name="one.md", content="x"),
                    call("create_file", call_id="b", name="two.md", content="y"),
                ]
            }
        ],
        [{"text": "done"}],
    ]
    permissions = Answers(allowed())
    _, files, _, _ = _gated(tmp_path, rounds, permissions=permissions)
    assert len(permissions.asked) == 1
    assert sorted(files.list_names("p1")) == ["one.md", "two.md"]


def test_a_refused_call_does_not_run(tmp_path):
    _, files, _, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], permissions=Answers(refused())
    )
    assert files.list_names("p1") == []


def test_a_refused_call_tells_the_model_why(tmp_path):
    # A wall with nothing written on it is a wall the model walks into again.
    _, _, engine, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], permissions=Answers(refused())
    )
    # The conversation's last word, which since Madde 127 is no longer the request's: the file
    # names ride behind it.
    said = [piece for piece in engine.seen[1] if piece["role"] == "tool"][-1]
    assert said["role"] == "tool"
    assert said["tool_call_id"] == "t1"
    assert "create_file" in said["content"]
    assert "mode has not changed" in said["content"]


def test_the_users_own_reason_reaches_the_model(tmp_path):
    _, _, engine, _ = _gated(
        tmp_path,
        [_write_round(), [{"text": "ok"}]],
        permissions=Answers(refused("that file is mine")),
    )
    refusal = [piece for piece in engine.seen[1] if piece["role"] == "tool"][-1]
    assert "that file is mine" in refusal["content"]


def test_a_refused_call_is_still_a_card(tmp_path):
    # Madde 84 and 85 do not bend for a refusal: what the turn did is what the chat shows. No file
    # name, because no file was touched.
    chats, _, _, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], permissions=Answers(refused())
    )
    assert chats.get("p1", "c1").messages[-1].calls == (ToolCall("create_file", "", "Not allowed"),)


def test_a_refusal_does_not_end_the_turn(tmp_path):
    _, _, engine, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], permissions=Answers(refused())
    )
    assert len(engine.seen) == 2


def test_a_stop_while_waiting_ends_the_turn(tmp_path):
    stops = StopsWhileWaiting()
    permissions = Answers(None, on_wait=lambda: stops.want("p1", "c1"))
    chats, files, engine, _ = _gated(
        tmp_path,
        [_write_round(), [{"text": "never"}]],
        stops=stops,
        permissions=permissions,
    )
    assert files.list_names("p1") == []
    assert len(engine.seen) == 1
    assert chats.get("p1", "c1").messages[-1].stopped


def test_a_tick_with_no_answer_beats_and_keeps_waiting(tmp_path):
    # The beat is what keeps a tunnel from closing a silent stream, and what notices a tab that
    # went away. Then the answer arrives and the turn carries on as if nothing happened.
    from backend.features.workspace.domain.permission import Waiting

    _, files, _, produced = _gated(
        tmp_path, [_write_round(), [{"text": "done"}]], permissions=Answers(None, allowed())
    )
    assert [piece for piece in produced if isinstance(piece, Waiting)] == [Waiting()]
    assert files.list_names("p1") == ["plan.md"]


def test_edit_mode_never_reaches_the_registry(tmp_path):
    # UNASKED raises when it is touched, so this is measured rather than asserted.
    _, files, _, _ = _gated(tmp_path, [_write_round(), [{"text": "done"}]], mode="edit")
    assert files.list_names("p1") == ["plan.md"]


def test_every_mode_is_offered_every_tool(tmp_path):
    # The mode stopped being the request's tool list here. What it decides now is which of them run
    # without a question.
    from backend.features.workspace.domain.tools import TOOL_SPECS

    _, _, engine, _ = _gated(tmp_path, [[{"text": "hi"}]])
    assert engine.tools == [[spec["function"]["name"] for spec in TOOL_SPECS]]


def test_the_question_comes_before_the_dashed_card(tmp_path):
    # The other way round the card would stand there through the whole wait, saying a file is on
    # its way while nobody has agreed to it yet.
    from backend.features.workspace.domain.permission import PermissionWanted

    _, _, _, produced = _gated(
        tmp_path, [_write_round(), [{"text": "done"}]], permissions=Answers(allowed())
    )
    kinds = [type(piece) for piece in produced]
    assert kinds.index(PermissionWanted) < kinds.index(FileStarted)


def test_the_registry_is_cleared_however_the_turn_ends(tmp_path):
    permissions = Answers(refused())
    _gated(tmp_path, [_write_round(), [{"text": "ok"}]], permissions=permissions)
    assert permissions.cleared == [("p1", "c1")]


# --- what a mode decides (Madde 91, and Madde 99) ------------------------------------------------
#
# What the mode decided used to be which tools the request carried, and the test for that is gone:
# since Madde 99 every request carries all of them. Its replacement lives with this turn's own
# reds, as test_every_mode_is_offered_every_tool.


def _in_mode(tmp_path, rounds, mode):
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine(rounds)
    produced = list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED, mode))
    return chats, engine, produced


def test_a_turn_that_names_no_mode_carries_the_writing_tools(tmp_path):
    # The retry road sends no mode of its own, and neither does any caller written before this.
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "Hi"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, UNASKED))
    assert "create_file" in engine.tools[0]


def test_in_plan_mode_the_turn_ends_when_the_plan_is_written(tmp_path):
    # The plan is on disk and the next move is the user's: they read it, fix it in the file itself,
    # then run it in edit mode. A second round here would be the model running its own plan.
    rounds = [
        [{"tool_calls": [call("write_plan", name="bar-scene", content="1. ...")]}],
        [{"text": "never reached"}],
    ]
    _, engine, _ = _in_mode(tmp_path, rounds, "plan")
    assert len(engine.seen) == 1
