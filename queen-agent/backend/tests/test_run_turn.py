import json
from dataclasses import replace

import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.black_box import REFUSED_SAID
from backend.features.workspace.domain.chat import Chat, ToolCall, Usage
from backend.features.workspace.domain.black_box import NOTHING
from backend.features.workspace.domain.errors import EngineFailed
from backend.features.workspace.domain.prompt import APPROVED
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.domain.tools import MAX_ROUNDS, FileStarted, FileWritten
from backend.features.workspace.domain.turn import Progress
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.run_turn import run_turn
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


def a_call(call_id="t1"):
    """Some tool call, for the tests that need a round rather than a particular tool.

    read_prompt_structure_schema was this until Madde 172 retired it: it took no arguments and
    touched no file, which made it the quietest thing to script. A read of a name nobody has is the
    nearest thing left -- it costs a round, needs no fixture, and files_opened skips a read that
    found nothing, so the context box stays out of tests that are about rounds.
    """
    return call("read_file", call_id, name="ghost.md")


# What that call leaves in the record.
A_STEP = ToolCall("read_file", "ghost.md", "No file by that name")


class Quiet:
    """The turn's control as most tests need it: nobody stops it, and nothing is ever asked.

    Raising on a decision rather than answering is the point -- a turn that started asking in a mode
    that asks for nothing is a broken gate, and a fake that quietly said yes would hide it.
    """

    def stopped(self):
        return False

    def hold(self, cut):
        pass

    def decision(self):
        raise AssertionError("nothing in this mode should have been asked")


NEVER = Quiet()


class Answers(Quiet):
    """A control with its decisions written out, one per question.

    Running out raises: a gate that asked forever would otherwise spin this test until the suite
    was killed.
    """

    def __init__(self, *decisions):
        self.decisions = list(decisions)
        self.asked = 0

    def decision(self):
        self.asked += 1
        if not self.decisions:
            raise AssertionError("the turn asked more than this test answers")
        return self.decisions.pop(0)


class StopsWhileWaiting(Quiet):
    """A stop that lands while the turn is paused on a question: the wait ends with no decision.

    Cut says it is stopped from the first breath, which ends the round before the tool loop is ever
    reached -- so it cannot describe this moment. Here the press lands during the wait, the one
    stretch of a turn with no socket to cut.
    """

    def __init__(self):
        self.pressed = False

    def stopped(self):
        return self.pressed

    def decision(self):
        self.pressed = True
        return None


class Cut(Quiet):
    """The control after a stop: however this answer ended, we are the ones who ended it.

    Since Madde 90 nothing counts here. The flag is not asked frame by frame any more -- the cut
    ends the round on its own, and the only question left is whose cut it was.
    """

    def __init__(self):
        self.held = []

    def hold(self, cut):
        self.held.append(cut)

    def stopped(self):
        return True


CUT = object()
"""Where the connection dies inside a round.

In production it is a socket that was shut down and a chunked body that stopped in the middle; here
it is a piece the engine refuses to get past.
"""

BROKEN = "IncompleteRead(0 bytes read)"


class PressedLater(Quiet):
    """A stop nobody has asked for until a piece of the script presses it."""

    def __init__(self):
        self.pressed = False

    def press(self):
        self.pressed = True

    def stopped(self):
        return self.pressed


class ScriptedEngine:
    """Each round is a list of pieces the engine hands back.

    A worded answer is checked (Madde 445): `checks` are the check's words in order, and past them
    it approves, so a test about rounds never has to mention it.
    """

    def __init__(self, rounds, blow_up_after=None, checks=()):
        self.rounds = list(rounds)
        self.blow_up_after = blow_up_after
        self.checks = list(checks)
        self.seen = []
        self.handed = []
        # Which tools each round was offered. Since Madde 91 that is the mode's whole consequence.
        self.tools = []

    def stream(self, messages, tools=None, on_open=None):
        self.seen.append(list(messages))
        self.tools.append([spec["function"]["name"] for spec in tools or []])
        if on_open:
            on_open(self._cut)
        if self.blow_up_after is not None and len(self.seen) > self.blow_up_after:
            raise RuntimeError("connection dropped")
        pieces = self.rounds.pop(0) if self.rounds else []
        for piece in pieces:
            if piece is CUT or callable(piece):
                # A callable is a press landing at that moment: the stop is asked for, and the
                # connection dies the way a cut one does.
                if callable(piece):
                    piece()
                # What Python says when a chunked body stops in the middle. Nothing in the words
                # says who did it, which is the whole difficulty this item deals with.
                raise RuntimeError(BROKEN)
            yield piece

    def stream_alone(self, system, text, on_open=None):
        yield {"text": self.checks.pop(0) if self.checks else APPROVED}

    def _cut(self):
        self.handed.append("cut")


def _seeded(tmp_path):
    store = Store(str(tmp_path))
    projects = FileProjectStore(store)
    chats, files = FileChatStore(store, projects), FileFileStore(store, projects)
    now = "2026-08-09T11:04:00.000+00:00"
    create_project(projects, new_id="p1", name="Thesis", now=now)
    # Handing no chat is what asks for one, since Madde 87.
    append_message(chats, "p1", None, "hi", now, project_store=projects, new_id="c1")
    return chats, files


def _answer(chats, files, engine, mode="edit", control=NEVER):
    """One turn of the seeded chat, handed its record the way the door hands it (Madde 461)."""
    return list(run_turn(chats, files, engine, "p1", chats.get("p1", "c1"), NOW, control, mode))


def _said(chats, text, at=NOW, **fields):
    """A message written into the seeded chat ahead of the turn under test."""
    return append_message(chats, "p1", chats.get("p1", "c1"), text, at, **fields)


def _run(tmp_path, rounds, control=NEVER, **kwargs):
    # The same run with nothing to ask. Edit mode is what the app defaults to and it stops for
    # nothing, so NEVER raising on a decision is a guard here rather than an inconvenience.
    return _gated(tmp_path, rounds, control=control, mode="edit", **kwargs)


def allowed():
    from backend.features.workspace.domain.permission import Decision

    return Decision(True, "")


def refused(reason=""):
    from backend.features.workspace.domain.permission import Decision

    return Decision(False, reason)


def _gated(tmp_path, rounds, control=NEVER, mode="ask", **kwargs):
    """_run's sibling in a mode that asks, with the control the turn reads its answers from."""
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine(rounds, **kwargs)
    produced = _answer(chats, files, engine, mode, control)
    return chats, files, engine, produced


class HandedOnly:
    """A chat store that writes and counts, and cannot read: the turn works from its record."""

    def __init__(self, chats):
        self._chats = chats
        self.written = 0

    def get(self, project_id, chat_id):
        raise AssertionError("the turn read the chat again")

    def replace(self, project_id, chat):
        self.written += 1
        self._chats.replace(project_id, chat)


def test_the_turn_works_from_the_record_it_is_handed_and_writes_its_answer_once(tmp_path):
    # Madde 461: the door read the chat once; the turn neither reads it again at its start nor
    # before its last write. On Drive each of those was a round trip.
    chats, files = _seeded(tmp_path)
    handed = HandedOnly(chats)
    engine = ScriptedEngine([[{"tool_calls": [a_call()]}], [{"text": "Done."}]])
    produced = list(run_turn(handed, files, engine, "p1", chats.get("p1", "c1"), NOW, NEVER, "edit"))
    assert handed.written == 1
    assert produced[-1] == chats.get("p1", "c1")
    assert [m.text for m in produced[-1].messages] == ["hi", "Done."]


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
    _answer(chats, files, engine)
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
    _answer(chats, files, engine)
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
            if message["role"] == "system" and message["content"].startswith("The last 5 files")
        ),
        "",
    )


def test_the_request_carries_the_contents_of_what_was_read(tmp_path):
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "the body of the plan")
    rounds = [[{"tool_calls": [call("read_file", name="plan.md")]}], [{"text": "done"}]]
    engine = ScriptedEngine(rounds)
    _answer(chats, files, engine)
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
    _answer(chats, files, engine)
    assert "first" in _box(engine.seen[1])
    assert "second" in _box(engine.seen[2])
    assert "first" not in _box(engine.seen[2])


def test_a_file_read_in_an_earlier_turn_is_still_in_the_box(tmp_path):
    # Across turns, not only rounds: the trial opened every turn by reading the same pair again.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "the body")
    _said(chats, "read it", role="ai", calls=(ToolCall("read_file", "plan.md", "1 line"),))
    _said(chats,"and now?", NOW)
    engine = ScriptedEngine([[{"text": "here"}]])
    _answer(chats, files, engine)
    assert "the body" in _box(engine.seen[0])


def test_a_deleted_file_falls_out_of_the_box(tmp_path):
    # Quietly: the box holds a name, and a name with nothing behind it is simply not shown. An
    # empty heading would read as an empty file.
    chats, files = _seeded(tmp_path)
    files.write("p1", "gone.md", "for now")
    _said(chats, "read it", role="ai", calls=(ToolCall("read_file", "gone.md", "1 line"),))
    _said(chats,"and now?", NOW)
    files.delete("p1", "gone.md")
    engine = ScriptedEngine([[{"text": "here"}]])
    _answer(chats, files, engine)
    assert "gone.md" not in _box(engine.seen[0])


def test_the_box_numbers_the_lines_it_shows(tmp_path):
    # Madde 131. Since 129 the box is where a file is actually looked at -- the model does not read
    # it a second time -- so numbering the tool's own answer alone would number the copy nobody
    # reads.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "alpha\nbeta")
    rounds = [[{"tool_calls": [call("read_file", name="plan.md")]}], [{"text": "done"}]]
    engine = ScriptedEngine(rounds)
    _answer(chats, files, engine)
    assert "     1\talpha\n     2\tbeta" in _box(engine.seen[1])


def test_a_file_that_was_read_rides_the_request_once(tmp_path):
    # Madde 179, and the whole of it. Madde 131 asked the box and the read to show a file the same
    # way, so the model would not have to decide which shape its anchor had to match; Madde 179
    # answers the question by taking one of them away.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "alpha\nbeta")
    rounds = [[{"tool_calls": [call("read_file", name="plan.md")]}], [{"text": "done"}]]
    engine = ScriptedEngine(rounds)
    _answer(chats, files, engine)
    whole = "\n".join(str(message.get("content") or "") for message in engine.seen[1])
    assert whole.count("alpha") == 1
    assert "alpha" in _box(engine.seen[1])


def test_a_file_edited_in_the_same_turn_rides_it_only_as_it_is_now(tmp_path):
    # What the second copy actually cost. The conversation held the file as it was when it was
    # read and the box held it as it is, so a turn that read and then wrote sent the model both --
    # and nothing in either said which one was the file.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "alpha\nbeta")
    rounds = [
        [{"tool_calls": [call("read_file", name="plan.md")]}],
        [{"tool_calls": [call("edit_file", "t2", name="plan.md", old="alpha", new="omega")]}],
        [{"text": "done"}],
    ]
    engine = ScriptedEngine(rounds)
    _answer(chats, files, engine)
    whole = "\n".join(str(message.get("content") or "") for message in engine.seen[2])
    assert "omega" in whole
    assert "alpha" not in whole


def test_the_box_rides_between_the_names_and_the_instruction(tmp_path):
    # Madde 93's order still holds: the instruction closes the request. The names and the box are
    # the request's own words, behind the conversation and in front of it.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "the body")
    stored = chats.get("p1", "c1")
    chats.replace(
        "p1", replace(stored, messages=(replace(stored.messages[0], skill="start-a-scenario"),))
    )
    _said(chats, "read it", role="ai", calls=(ToolCall("read_file", "plan.md", "1 line"),))
    _said(chats,"carry on", NOW, skill="start-a-scenario")
    engine = ScriptedEngine([[{"text": "here"}]])
    _answer(chats, files, engine)
    seen = engine.seen[0]
    assert seen[-1]["content"] == instruction_for("start-a-scenario")
    assert seen[-2]["content"].startswith("The last 5 files")
    assert _files_line([seen[-3]])


def test_the_box_says_it_holds_the_last_five(tmp_path):
    # Madde 179 made the box the only place a file is shown, which makes the limit worth stating:
    # a file that fell out of it is read again for the price of one sentence, and a model that did
    # not know the window existed would go looking for a file it can no longer see.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "alpha")
    rounds = [[{"tool_calls": [call("read_file", name="plan.md")]}], [{"text": "done"}]]
    engine = ScriptedEngine(rounds)
    _answer(chats, files, engine)
    assert _box(engine.seen[1]).startswith("The last 5 files you opened")


def test_a_chat_that_read_nothing_carries_no_box(tmp_path):
    # Nothing to say is said by saying nothing: an empty heading is a line the model has to read
    # before finding out it is empty.
    _, _, engine, _ = _run(tmp_path, [[{"text": "hi"}]])
    assert _box(engine.seen[0]) == ""


def _write_round(name="plan.md"):
    return [{"tool_calls": [call("create_file", name=name, content="x")]}]


def test_a_round_without_tools_ends_the_loop(tmp_path):
    chats, _, engine, produced = _run(tmp_path, [[{"text": "He"}, {"text": "llo"}]])
    assert isinstance(produced[-1], Chat)
    assert chats.get("p1", "c1").messages[-1].text == "Hello"
    assert len(engine.seen) == 1


def test_the_words_are_not_handed_on_piece_by_piece(tmp_path):
    # Madde 440: the answer comes back whole, and the screen shows it once the turn has ended -- so
    # nothing of it travels while the turn runs. The record is where the words are read.
    _, _, _, produced = _run(tmp_path, [[{"text": "He"}, {"text": "llo"}]])
    assert not [piece for piece in produced if isinstance(piece, str)]


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
    rounds = [[{"text": "Looking. "}, {"tool_calls": [a_call()]}], [{"text": "Nothing."}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    stored = chats.get("p1", "c1").messages
    assert [(m.role, m.text) for m in stored] == [("user", "hi"), ("ai", "Looking. Nothing.")]


def test_the_tool_traffic_is_never_written_to_the_chat(tmp_path):
    rounds = [[{"tool_calls": [a_call()]}], [{"text": "done"}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    # The chat is what the user reads, not the model's bookkeeping.
    assert [m.role for m in chats.get("p1", "c1").messages] == ["user", "ai"]


def test_the_loop_stops_at_the_round_limit_and_still_writes(tmp_path):
    forever = [[{"text": "."}, {"tool_calls": [a_call()]}] for _ in range(MAX_ROUNDS + 3)]
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
    # The dashed card goes up before the tool runs, the filled one after it. Read past the progress
    # pieces Madde 194 added: the claim is the order of these two, not where the round's own signal
    # falls between them.
    cards = [piece for piece in produced if isinstance(piece, (FileStarted, FileWritten))]
    assert isinstance(cards[0], FileStarted)
    assert cards[1] == FileWritten("plan.md")


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
    produced = _answer(chats, files, ScriptedEngine(rounds))
    # A file is born here too, so it gets the same dashed card and the same filled one.
    cards = [piece for piece in produced if isinstance(piece, (FileStarted, FileWritten))]
    assert isinstance(cards[0], FileStarted)
    assert cards[1] == FileWritten("frames.py")


def test_editing_a_file_announces_nothing(tmp_path):
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "alpha")
    rounds = [
        [{"tool_calls": [call("edit_file", name="plan.md", old="alpha", new="beta")]}],
        [{"text": "done"}],
    ]
    produced = _answer(chats, files, ScriptedEngine(rounds))
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
    _answer(chats, files, ScriptedEngine(rounds))
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
    assert kept.failed == ""


def test_the_silent_answer_is_still_one_reply_in_the_chat(tmp_path):
    rounds = [[{"tool_calls": [call("create_file", name="plan.md", content="x")]}], []]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert [m.role for m in chats.get("p1", "c1").messages] == ["user", "ai"]


def test_silence_after_a_file_is_not_asked_again(tmp_path):
    # Madde 38 kept through Madde 440 (the user, 9 October): the black box tries an empty answer
    # again only while the turn has made no file. Here it has, so the silence is the end.
    rounds = [
        [{"tool_calls": [call("create_file", name="plan.md", content="x")]}],
        [],
        [{"text": "never asked for"}],
    ]
    _, _, engine, _ = _run(tmp_path, rounds)
    assert len(engine.seen) == 2


def test_silence_after_an_edit_is_not_asked_again(tmp_path):
    # Editing a file the project already had is writing too (the user, 9 October): the turn wrote,
    # so its silence is the end.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "alpha")
    rounds = [
        [{"tool_calls": [call("edit_file", name="plan.md", old="alpha", new="beta")]}],
        [],
        [{"text": "never asked for"}],
    ]
    engine = ScriptedEngine(rounds)
    _answer(chats, files, engine)
    kept = chats.get("p1", "c1").messages[-1]
    assert (kept.text, kept.failed) == ("", "")
    assert len(engine.seen) == 2


def test_silence_after_a_create_that_wrote_nothing_is_asked_again(tmp_path):
    # "Already there": the call ran and touched no file, so nothing was written.
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "mine")
    rounds = [
        [{"tool_calls": [call("create_file", name="plan.md", content="x")]}],
        [],
        [{"text": "It was already there."}],
    ]
    engine = ScriptedEngine(rounds)
    _answer(chats, files, engine)
    assert chats.get("p1", "c1").messages[-1].text == "It was already there."
    assert len(engine.seen) == 3
    assert files.read("p1", "plan.md") == "mine"


def test_silence_before_any_file_is_asked_again(tmp_path):
    # The other side of the same line: nothing made yet, so an empty answer is not an answer.
    rounds = [[{"tool_calls": [call("read_file", name="ghost.md")]}], [], [{"text": "Not there."}]]
    chats, _, engine, _ = _run(tmp_path, rounds)
    assert chats.get("p1", "c1").messages[-1].text == "Not there."
    assert len(engine.seen) == 3


def test_a_turn_that_only_read_and_then_fell_silent_is_a_failed_answer(tmp_path):
    # What used to be refused as no answer at all: the read is a step but makes no file, so the
    # silence after it is five empty tries.
    rounds = [[{"tool_calls": [call("read_file", name="ghost.md")]}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    kept = chats.get("p1", "c1").messages[-1]
    assert kept.failed == "technical"
    assert kept.calls == (A_STEP,)


def test_a_silent_turn_that_runs_out_of_rounds_is_not_an_answer_either(tmp_path):
    # Same rule down a different road: the loop stops at its limit rather than at a quiet round.
    # It ends as the turn's own fault, in the black box's words for nothing (the route used to say
    # them): the turn has no answer to write, and its question stays unanswered.
    forever = [[{"tool_calls": [a_call()]}] for _ in range(MAX_ROUNDS + 3)]
    with pytest.raises(EngineFailed, match=NOTHING):
        _run(tmp_path, forever)


def _said_with(tmp_path, *turns):
    """Run one answer over a chat whose messages were sent with the given skills."""
    chats, files = _seeded(tmp_path)
    for number, (text, skill) in enumerate(turns):
        _said(chats,text, f"2026-08-09T12:0{number}:00.000+00:00", skill=skill)
    engine = ScriptedEngine([[{"text": "ok"}]])
    _answer(chats, files, engine)
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
    _, conversation = _said_with(tmp_path, ("write me the prompts", "edit-prompts"))
    assert conversation[-1] == {
        "role": "system",
        "content": instruction_for("edit-prompts"),
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
        ("one", "edit-prompts"),
        ("and again", "edit-prompts"),
        ("never mind", ""),
    )
    assert _instructions(conversation) == []


def test_no_instruction_stands_among_the_messages(tmp_path):
    # The other half of the same move: the block did not just get a new place, the old places are
    # empty. Measured on the messages rather than on the whole request, because the one at the end
    # is the one that is supposed to be there.
    _, conversation = _said_with(
        tmp_path, ("one", "edit-prompts"), ("and the rest", "edit-prompts")
    )
    # Three, because the chat was born with a message of its own before these two. The file names
    # are dropped rather than counted: they are the request's, not the conversation's.
    said = [piece for piece in conversation[:-1] if not _files_line([piece])]
    assert [piece["role"] for piece in said] == ["user", "user", "user"]


def test_the_instruction_moves_to_the_end_of_every_round(tmp_path):
    # An answer runs up to thirty-two rounds and each sends its own request. Left where it was, the
    # block would sit behind the tool exchanges from the second round on -- and the reason this
    # item exists would stop holding after the first one.
    chats, files = _seeded(tmp_path)
    _said(chats,"build me the prompts", NOW, skill="edit-prompts")
    engine = ScriptedEngine([[{"tool_calls": [a_call()]}], [{"text": "clean"}]])
    _answer(chats, files, engine)
    second = engine.seen[1]
    assert second[-1] == {"role": "system", "content": instruction_for("edit-prompts")}
    # And what it moved past: the round that asked for the tool, and the tool's answer. Counted
    # from the conversation's own end rather than from the request's -- what the request adds
    # behind it has grown twice already (the names in 127, the box in 129) and each time this
    # line had to be renumbered for a claim that never changed.
    spoken = [piece for piece in second if piece["role"] in ("assistant", "tool")]
    assert [piece["role"] for piece in spoken[-2:]] == ["assistant", "tool"]


# --- the last round closes the turn rather than asking for more (Madde 137) -----------------------
#
# Where this comes from: a run of seventy tool calls that ended in nothing. Sixteen rounds went on
# tools, no word was said, and append_message refused the whole turn -- the rule is right, and what
# was missing is that the sixteenth round was handed exactly what the first was. So the model
# answered it the way it answered the first, with another call, and no round was left to read the
# result.
#
# LAST_ROUND is imported inside each test for the reason test_prompt gives: until it exists, a
# module level import would stop this file being collected and bury sixty-odd greens in errors.


def _asking_forever(count):
    """A script that speaks a little and asks for a tool every round, `count` rounds long.

    The word matters: a turn that says nothing and makes nothing is refused before any of these
    could look at it, and what is under test here is the request rather than that rule.
    """
    return [
        [{"text": "."}, {"tool_calls": [a_call()]}] for _ in range(count)
    ]


def test_the_last_round_is_offered_no_tools(tmp_path):
    # The half of the item that does not depend on the model reading anything. A notice on its own
    # would be a request, and the failure it answers is a model misreading where the turn stands --
    # the same misreading would carry it straight past the sentence. A round with no tools in it has
    # nothing left to disobey with.
    _, _, engine, _ = _run(tmp_path, _asking_forever(MAX_ROUNDS))
    assert engine.tools[-1] == []
    # And only the last one: every round before it is still working, and a turn that lost its tools
    # early would finish sooner while looking like it had finished.
    assert all(engine.tools[:-1])


def test_the_last_round_says_it_is_the_last(tmp_path):
    # The other half. Without the words the model produces an answer because it has no choice,
    # which is not the same as an answer that knows it is closing something.
    from backend.features.workspace.domain.prompt import LAST_ROUND

    _, _, engine, _ = _run(tmp_path, _asking_forever(MAX_ROUNDS))
    assert engine.seen[-1][-1] == {"role": "system", "content": LAST_ROUND}


def test_the_notice_is_the_requests_last_word(tmp_path):
    # Madde 93 put the instruction at the end because what is fixed leads and what changes trails.
    # The instruction is fixed for the whole turn; this sentence shows up in one round out of
    # thirty-two. The same reasoning that gave 93 the last word takes it back here -- so the order
    # is extended rather than broken, and the test names both to say which one moved.
    from backend.features.workspace.domain.prompt import LAST_ROUND

    chats, files = _seeded(tmp_path)
    _said(chats,"build me the prompts", NOW, skill="edit-prompts")
    engine = ScriptedEngine(_asking_forever(MAX_ROUNDS))
    _answer(chats, files, engine)
    assert [piece["content"] for piece in engine.seen[-1][-2:]] == [
        instruction_for("edit-prompts"),
        LAST_ROUND,
    ]


def test_a_turn_that_ends_early_never_sees_the_notice(tmp_path):
    # The boundary. Reaching the limit is what this sentence is for, and most turns never do -- one
    # that spoke and stopped was never running out of anything, and telling it so would be a lie
    # about its own turn.
    from backend.features.workspace.domain.prompt import LAST_ROUND

    rounds = [[{"tool_calls": [a_call()]}], [{"text": "Done."}]]
    _, _, engine, _ = _run(tmp_path, rounds)
    assert not any(LAST_ROUND in piece["content"] for seen in engine.seen for piece in seen)
    assert all(engine.tools)


def test_a_chat_without_a_skill_is_told_nothing_extra(tmp_path):
    _, conversation = _said_with(tmp_path, ("hello", ""))
    assert _instructions(conversation) == []


def test_a_skill_nobody_knows_adds_nothing_and_still_answers(tmp_path):
    chats, conversation = _said_with(tmp_path, ("hello", "web-search"))
    assert _instructions(conversation) == []
    assert chats.get("p1", "c1").messages[-1].text == "ok"


def test_the_instruction_is_never_written_to_the_chat(tmp_path):
    chats, _ = _said_with(tmp_path, ("write me the prompts", "edit-prompts"))
    # The transcript is what the user reads: user sentences and answers, nothing else.
    assert [m.role for m in chats.get("p1", "c1").messages] == ["user", "user", "ai"]


def test_a_stream_that_keeps_breaking_ends_in_a_failed_answer(tmp_path):
    # Madde 440: the black box never throws. After five tries the failure's own words are the
    # answer, and the turn ends there.
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "half"}]], blow_up_after=0)
    produced = _answer(chats, files, engine)
    assert isinstance(produced[-1], Chat)
    kept = chats.get("p1", "c1").messages
    assert [(m.text, m.failed) for m in kept] == [("hi", ""), ("connection dropped", "technical")]
    assert len(engine.seen) == 5


# --- the black box (Madde 440) -------------------------------------------------------------------


class UnreadableFiles:
    """A file store whose disk has gone away: the turn's own code fails, not the model."""

    def list_names(self, project_id):
        raise OSError("the disk went away")


def test_a_fault_outside_the_box_still_ends_the_turn_as_one(tmp_path):
    # The black box answers for the model. What is left to raise is the turn's own code, and that
    # still travels inside the stream rather than breaking it -- with nothing written.
    chats, _ = _seeded(tmp_path)
    with pytest.raises(EngineFailed, match="the disk went away"):
        _answer(chats, UnreadableFiles(), ScriptedEngine([]))
    assert [m.text for m in chats.get("p1", "c1").messages] == ["hi"]


def test_after_a_broken_stream_the_same_request_goes_again(tmp_path):
    chats, _, engine, _ = _run(tmp_path, [[{"text": "Half"}, CUT], [{"text": "Done."}]])
    assert chats.get("p1", "c1").messages[-1].text == "Done."
    assert engine.seen[0] == engine.seen[1]
    # Nothing on the record says a try failed: the retries never show.
    assert chats.get("p1", "c1").messages[-1].failed == ""


def test_five_broken_streams_are_the_failure_and_nothing_more_is_asked(tmp_path):
    # The tool call never runs and no round follows: nothing goes back to the model.
    rounds = [[CUT]] * 5 + [[{"text": "never"}]]
    chats, _, engine, _ = _run(tmp_path, rounds)
    kept = chats.get("p1", "c1").messages[-1]
    assert (kept.text, kept.failed) == (BROKEN, "technical")
    assert len(engine.seen) == 5


def test_a_failed_answer_keeps_the_steps_and_files_but_not_the_words_before_it(tmp_path):
    rounds = [
        [
            {"text": "Writing it. "},
            {"tool_calls": [call("create_file", name="plan.md", content="x")]},
        ],
        *[[CUT]] * 5,
    ]
    chats, files, engine, _ = _run(tmp_path, rounds)
    kept = chats.get("p1", "c1").messages[-1]
    assert kept.text == BROKEN
    assert kept.files == ("plan.md",)
    assert kept.calls == (ToolCall("create_file", "plan.md", "Saved"),)
    assert files.list_names("p1") == ["plan.md"]
    assert len(engine.seen) == 6


def test_a_failed_answer_is_not_sent_to_the_model_on_the_next_turn(tmp_path):
    chats, files = _seeded(tmp_path)
    _said(chats,"HTTP 502", NOW, role="ai", failed="technical")
    _said(chats,"and now?", NOW)
    engine = ScriptedEngine([[{"text": "Here."}]])
    _answer(chats, files, engine)
    said = [message["content"] for message in engine.seen[0] if message["role"] in ("user", "ai")]
    assert said == ["hi", "and now?"]


# --- the check (Madde 445) -----------------------------------------------------------------------


def test_five_refusals_end_the_turn_in_the_refusal_message(tmp_path):
    # The refusal's own words never reach the record: the general message stands as the answer,
    # the steps the turn took stay, and nothing more is asked.
    rounds = [[{"tool_calls": [a_call()]}], *[[{"text": "I cannot help."}]] * 6]
    chats, _, engine, _ = _run(tmp_path, rounds, checks=["REFUSAL"] * 6)
    kept = chats.get("p1", "c1").messages[-1]
    assert (kept.text, kept.failed) == (REFUSED_SAID, "refused")
    assert kept.calls == (A_STEP,)
    assert len(engine.seen) == 6


def test_a_refused_answer_is_not_sent_to_the_model_on_the_next_turn(tmp_path):
    chats, files = _seeded(tmp_path)
    _said(chats,REFUSED_SAID, NOW, role="ai", failed="refused")
    _said(chats,"and now?", NOW)
    engine = ScriptedEngine([[{"text": "Here."}]])
    _answer(chats, files, engine)
    said = [message["content"] for message in engine.seen[0] if message["role"] in ("user", "ai")]
    assert said == ["hi", "and now?"]


def test_the_engine_is_asked_without_a_model(tmp_path):
    # Madde 358, as Madde 82 had it: one model, so which one answers belongs to the wiring, not to
    # the chat. ScriptedEngine.stream refuses one, so a use case that passed a model would die here.
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "hi"}]])
    _answer(chats, files, engine)
    assert len(engine.seen) == 1


def test_a_question_that_names_a_model_since_dropped_is_still_answered(tmp_path):
    # Messages on disk name deepseek-v4-pro or deepseek-v4-flash, and neither is a row of config.py
    # any more. The name is a record and steers nothing, so the chat is answered all the same.
    chats, files = _seeded(tmp_path)
    old = chats.get("p1", "c1")
    chats.replace("p1", replace(old, messages=(replace(old.messages[0], model="deepseek-v4-pro"),)))
    engine = ScriptedEngine([[{"text": "Done."}]])
    _answer(chats, files, engine)
    assert [m.text for m in chats.get("p1", "c1").messages] == ["hi", "Done."]


# --- the calls a turn made, seen and kept (Madde 66) ---------------------------------------------


def _lines(produced):
    return [piece for piece in produced if isinstance(piece, ToolCall)]


def test_each_call_leaves_a_line_as_it_happens(tmp_path):
    rounds = [[{"tool_calls": [a_call()]}], [{"text": "Nothing yet."}]]
    _, _, _, produced = _run(tmp_path, rounds)
    assert _lines(produced) == [A_STEP]


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
    rounds = [[{"tool_calls": [a_call()]}], [{"text": "done"}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert chats.get("p1", "c1").messages[-1].calls == (A_STEP,)


def test_an_answer_that_called_nothing_remembers_none(tmp_path):
    chats, _, _, _ = _run(tmp_path, [[{"text": "Hello"}]])
    assert chats.get("p1", "c1").messages[-1].calls == ()


def test_the_kept_call_says_how_it_went(tmp_path):
    # Madde 78. The tests above pin the tool and the file; none of them asks whether the line under
    # the call survived, and that is the half a reader a week later is looking at.
    rounds = [[{"tool_calls": [a_call()]}], [{"text": "done"}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert chats.get("p1", "c1").messages[-1].calls[0].outcome == "No file by that name"


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

TWO_ROUNDS = [[{"text": "Half a "}, {"tool_calls": [a_call()]}], [{"text": "sentence."}]]


def test_a_stop_ends_the_answer_without_asking_the_model_again(tmp_path):
    # The first round asked for a tool, which is what would normally open a second one.
    _, _, engine, _ = _run(tmp_path, TWO_ROUNDS, control=Cut())
    assert len(engine.seen) == 1


def test_a_stopped_turn_keeps_no_words(tmp_path):
    # Madde 440 turned the old rule round (the user, 5 October: "atılsın"). The answer was never on
    # screen and never checked, so none of it is kept -- not even what an earlier round said.
    chats, _, _, _ = _run(tmp_path, TWO_ROUNDS, control=Cut())
    assert chats.get("p1", "c1").messages[-1].text == ""


def test_a_stop_in_a_later_round_keeps_the_steps_and_the_files(tmp_path):
    # Only the request in flight is dropped: what the turn did before it stays.
    control = PressedLater()
    rounds = [
        [{"text": "Writing. "}, {"tool_calls": [call("create_file", name="plan.md", content="x")]}],
        [{"text": "Half a"}, control.press],
        [{"text": "never"}],
    ]
    chats, files, engine, _ = _run(tmp_path, rounds, control=control)
    kept = chats.get("p1", "c1").messages[-1]
    assert (kept.text, kept.stopped, kept.files) == ("", True, ("plan.md",))
    assert kept.calls == (ToolCall("create_file", "plan.md", "Saved"),)
    assert files.list_names("p1") == ["plan.md"]
    # The cut request is not sent again.
    assert len(engine.seen) == 2


def test_a_stopped_answer_says_it_was_stopped(tmp_path):
    # Half a sentence with no mark cannot be told from a model that finished on one.
    chats, _, _, _ = _run(tmp_path, TWO_ROUNDS, control=Cut())
    assert chats.get("p1", "c1").messages[-1].stopped is True


def test_the_running_answer_hands_its_control_a_way_to_cut_it(tmp_path):
    # Madde 90. The stop is reached from the thread carrying it and holds no socket of its own;
    # this is the one moment where the two meet.
    control = Cut()
    _, _, engine, _ = _run(tmp_path, [[{"text": "Hi"}]], control=control)
    assert len(control.held) == 1
    control.held[0]()
    assert engine.handed == ["cut"]


def test_a_connection_we_cut_is_a_stop_rather_than_a_failure(tmp_path):
    # Our own cut and a network that dropped arrive as the same words -- nothing in the failure
    # says who ended it. The registry is the only thing that knows, so it is asked before the
    # failure is believed.
    chats, _, engine, _ = _run(tmp_path, [[{"text": "Half a "}, CUT]], control=Cut())
    kept = chats.get("p1", "c1").messages[-1]
    assert kept.text == ""
    assert kept.stopped is True
    assert kept.failed == ""
    # A stop is never tried again.
    assert len(engine.seen) == 1


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
    chats, _, _, _ = _run(tmp_path, [[CUT]], control=Cut())
    kept = chats.get("p1", "c1").messages
    assert [m.role for m in kept] == ["user", "ai"]
    assert kept[-1].text == ""
    assert kept[-1].stopped is True


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
        [{"tool_calls": [a_call()]}, spent(1000, 600, 10)],
        [{"text": "done"}, spent(1500, 1200, 20)],
    ]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert _kept(chats).usage == Usage(2500, 1800, 30)


# --- what a running turn says about itself (Madde 194) -------------------------------------------
#
# The turn already ran its rounds one at a time and added up what they spent. What it never did was
# say so while it was still going: the stamp fell at the end, and a long turn showed three blinking
# dots for however long it took.


def _progress(produced):
    return [piece for piece in produced if isinstance(piece, Progress)]


def test_a_running_turn_says_which_round_it_is_on(tmp_path):
    _, _, _, produced = _run(tmp_path, [[{"text": "hi"}]])
    marks = _progress(produced)
    # Before anything else: the round number is what moves first, and it moves the moment the round
    # begins rather than when it ends.
    assert produced[0] == Progress(1, MAX_ROUNDS, 0)
    assert marks[0].of == MAX_ROUNDS


def test_every_round_says_so(tmp_path):
    rounds = [[{"tool_calls": [a_call()]}], [{"text": "done"}]]
    _, _, _, produced = _run(tmp_path, rounds)
    assert [mark.round for mark in _progress(produced)][:2] == [1, 2]


def test_the_number_is_everything_that_crossed_the_wire(tmp_path):
    # sent + cached + answered, which is how big the turn got rather than what it cost. Only `sent`
    # would hide half the work: cached tokens travel too, they are merely cheap. The bill is the
    # stamp's question and the stamp keeps answering it.
    _, _, _, produced = _run(tmp_path, [[{"text": "hi"}, spent(1000, 600, 40)]])
    assert _progress(produced)[-1].tokens == 1640
    # Said out loud, or a sum that quietly dropped the cache would read as right.
    assert _progress(produced)[-1].tokens != 1000


def test_two_rounds_add_up_as_they_go(tmp_path):
    rounds = [
        [{"tool_calls": [a_call()]}, spent(1000, 600, 10)],
        [{"text": "done"}, spent(1500, 1200, 20)],
    ]
    _, _, _, produced = _run(tmp_path, rounds)
    counted = [mark.tokens for mark in _progress(produced)]
    # It starts at nothing and never goes back down: what the screen shows is a total, not a round.
    assert counted[0] == 0
    assert counted[-1] == 4330
    assert counted == sorted(counted)


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


def test_a_stopped_answer_still_says_what_its_finished_rounds_spent(tmp_path):
    # A round that came back whole was paid for, and the stop landing just after it does not undo
    # that: the record keeps the figure, though the screen draws no cost under a stopped turn.
    rounds = [[spent(1200, 900, 5), {"text": "Half a "}]]
    chats, _, _, _ = _run(tmp_path, rounds, control=Cut())
    assert _kept(chats).text == ""
    assert _kept(chats).usage == Usage(1200, 900, 5)


def test_an_answer_stopped_before_the_counts_arrive_spent_nothing_it_knows_of(tmp_path):
    # Madde 76, and the honest record of a limit rather than a guard on a behaviour. The engine
    # reports once, in a frame just before the stream closes; an answer cut short never reaches it.
    # Since Madde 440 the cut round is thrown away whole, its figure with it.
    rounds = [[spent(1200, 900, 5), {"text": "Half a "}, CUT]]
    chats, _, _, _ = _run(tmp_path, rounds, control=Cut())
    assert _kept(chats).text == ""
    assert _kept(chats).usage == Usage()


# --- permission asked in the middle of a turn (Madde 99) -----------------------------------------


def test_a_call_the_mode_does_not_cover_is_asked_about(tmp_path):
    control = Answers(allowed())
    _gated(tmp_path, [_write_round(), [{"text": "done"}]], control=control)
    assert control.asked == 1


def test_the_question_carries_the_tool_and_its_arguments(tmp_path):
    # Raw, the way the model wrote them. Parsing here would be a second parser beside run_tool's,
    # and the two would drift on the first change to either.
    from backend.features.workspace.domain.permission import PermissionWanted

    _, _, _, produced = _gated(
        tmp_path, [_write_round(), [{"text": "done"}]], control=Answers(allowed())
    )
    asked = [piece for piece in produced if isinstance(piece, PermissionWanted)]
    assert asked == [
        PermissionWanted("create_file", json.dumps({"name": "plan.md", "content": "x"}))
    ]


def test_an_allowed_call_runs(tmp_path):
    _, files, _, _ = _gated(
        tmp_path, [_write_round(), [{"text": "done"}]], control=Answers(allowed())
    )
    assert files.list_names("p1") == ["plan.md"]


def test_an_allowed_call_changes_the_mode_for_the_rest_of_the_turn(tmp_path):
    # One answer for two writes. Measured by the control running out if it is asked twice, which
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
    control = Answers(allowed())
    _, files, _, _ = _gated(tmp_path, rounds, control=control)
    assert control.asked == 1
    assert sorted(files.list_names("p1")) == ["one.md", "two.md"]


def test_a_refused_call_does_not_run(tmp_path):
    _, files, _, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], control=Answers(refused())
    )
    assert files.list_names("p1") == []


def test_a_refused_call_tells_the_model_why(tmp_path):
    # A wall with nothing written on it is a wall the model walks into again.
    _, _, engine, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], control=Answers(refused())
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
        control=Answers(refused("that file is mine")),
    )
    refusal = [piece for piece in engine.seen[1] if piece["role"] == "tool"][-1]
    assert "that file is mine" in refusal["content"]


def test_a_refused_call_is_still_a_card(tmp_path):
    # Madde 84 and 85 do not bend for a refusal: what the turn did is what the chat shows. No file
    # name, because no file was touched.
    chats, _, _, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], control=Answers(refused())
    )
    assert chats.get("p1", "c1").messages[-1].calls == (ToolCall("create_file", "", "Not allowed"),)


def test_a_refusal_does_not_end_the_turn(tmp_path):
    _, _, engine, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], control=Answers(refused())
    )
    assert len(engine.seen) == 2


def test_a_stop_while_waiting_ends_the_turn(tmp_path):
    chats, files, engine, _ = _gated(
        tmp_path, [_write_round(), [{"text": "never"}]], control=StopsWhileWaiting()
    )
    assert files.list_names("p1") == []
    assert len(engine.seen) == 1
    assert chats.get("p1", "c1").messages[-1].stopped


def test_edit_mode_never_asks(tmp_path):
    # NEVER raises when it is asked, so this is measured rather than asserted.
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
        tmp_path, [_write_round(), [{"text": "done"}]], control=Answers(allowed())
    )
    kinds = [type(piece) for piece in produced]
    assert kinds.index(PermissionWanted) < kinds.index(FileStarted)


# --- what a mode decides (Madde 91, and Madde 99) ------------------------------------------------
#
# What the mode decided used to be which tools the request carried, and the test for that is gone:
# since Madde 99 every request carries all of them. Its replacement lives with this turn's own
# reds, as test_every_mode_is_offered_every_tool.


def _in_mode(tmp_path, rounds, mode):
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine(rounds)
    produced = _answer(chats, files, engine, mode)
    return chats, engine, produced


def test_a_turn_that_names_no_mode_carries_the_writing_tools(tmp_path):
    # The retry road sends no mode of its own, and neither does any caller written before this.
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "Hi"}]])
    list(run_turn(chats, files, engine, "p1", chats.get("p1", "c1"), NOW, NEVER))
    assert "create_file" in engine.tools[0]


def test_in_plan_mode_the_turn_ends_when_the_plan_is_written(tmp_path):
    # The plan is on disk and the next move is the user's: they read it, fix it in the file itself,
    # then run it in edit mode. A second round here would be the model running its own plan.
    #
    # Madde 207: the plan is an ordinary create_file now, and plan mode is what makes it a plan --
    # it runs without a question there, and it is what ends the turn. The file card is asserted as
    # well as the one request: a turn that stopped to ask permission also sends one, and would read
    # as green here.
    rounds = [
        [{"tool_calls": [call("create_file", name="bar-scene-plan.md", content="1. ...")]}],
        [{"text": "never reached"}],
    ]
    _, engine, produced = _in_mode(tmp_path, rounds, "plan")
    assert len(engine.seen) == 1
    assert [piece for piece in produced if isinstance(piece, FileWritten)]


# --- the line the turn is answering (Madde 195) --------------------------------------------------


def _branched(tmp_path, **edit):
    """The seeded chat, answered once, then edited back at its first message."""
    chats, files = _seeded(tmp_path)
    _said(chats,"Done.", NOW, role="ai")
    _said(chats,"hi again", NOW, branch_at=0, line_id="l2", **edit)
    return chats, files


def test_the_request_carries_the_open_line_and_not_the_one_left_behind(tmp_path):
    # The conversation the model is answering is the one the user is standing in. Sending the line
    # they walked away from would answer a question that was taken back, and it would do it while
    # the screen shows something else entirely.
    chats, files = _branched(tmp_path)
    engine = ScriptedEngine([[{"text": "Done again."}]])
    _answer(chats, files, engine)
    assert [
        message["content"] for message in engine.seen[0] if message["role"] in ("user", "ai")
    ] == ["hi again"]


def test_the_skill_comes_from_the_open_lines_newest_question(tmp_path):
    # Read by walking back from the end, and the end has to be the end of the open line --
    # otherwise a version runs under the skill of a turn nobody is looking at.
    from backend.features.workspace.domain.skills import instruction_for

    chats, files = _branched(tmp_path, skill="edit-prompts")
    engine = ScriptedEngine([[{"text": "Done again."}]])
    _answer(chats, files, engine)
    said = [message["content"] for message in engine.seen[0]]
    assert instruction_for("edit-prompts") in said


# --- a trimmed chat (Madde 345) ------------------------------------------------------------------


def test_a_trimmed_chat_sends_only_what_follows_the_cut(tmp_path):
    # The row's own words: in a trimmed chat only the newest part goes to the model, while every
    # message stays in the record.
    chats, files = _seeded(tmp_path)
    _said(chats,"Done.", NOW, role="ai")
    _said(chats,"again", NOW)
    chat = chats.get("p1", "c1")
    marked = replace(chat.messages[-1], trimmed=2)
    chats.replace("p1", replace(chat, messages=chat.messages[:-1] + (marked,)))
    engine = ScriptedEngine([[{"text": "Done again."}]])
    _answer(chats, files, engine)
    assert [
        message["content"] for message in engine.seen[0] if message["role"] in ("user", "ai")
    ] == ["again"]
    assert len(chats.get("p1", "c1").messages) == 4
