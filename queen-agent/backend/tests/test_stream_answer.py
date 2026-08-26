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

    # No model since Madde 82: the engine is built knowing which one. A use case that still passed
    # one would die here rather than quietly working.
    def stream(self, messages, tools=None, on_open=None):
        self.seen.append(list(messages))
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
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine(rounds, **kwargs)
    produced = list(stream_answer(chats, files, engine, "p1", "c1", NOW, stops))
    return chats, files, engine, produced


def test_a_round_without_tools_ends_the_loop(tmp_path):
    chats, _, engine, produced = _run(tmp_path, [[{"text": "He"}, {"text": "llo"}]])
    assert produced[:-1] == ["He", "llo"]
    assert isinstance(produced[-1], Chat)
    assert len(engine.seen) == 1


def test_a_tool_call_is_run_and_the_answer_goes_back_to_the_model(tmp_path):
    rounds = [[{"tool_calls": [call("list_files")]}], [{"text": "Nothing yet."}]]
    _, _, engine, _ = _run(tmp_path, rounds)
    assert len(engine.seen) == 2
    second = engine.seen[1]
    assert second[-2]["role"] == "assistant"
    assert second[-2]["tool_calls"][0]["id"] == "t1"
    assert second[-1] == {
        "role": "tool",
        "tool_call_id": "t1",
        "content": "This project has no files yet.",
    }


def test_two_calls_in_one_round_are_both_run(tmp_path):
    rounds = [
        [
            {
                "tool_calls": [
                    call("create_file", call_id="a", name="plan.md", content="x"),
                    call("create_file", call_id="b", name="plan.md", content="y"),
                ]
            }
        ],
        [{"text": "done"}],
    ]
    _, files, _, _ = _run(tmp_path, rounds)
    assert sorted(files.list_names("p1")) == ["plan-2.md", "plan.md"]


def test_text_from_every_round_becomes_one_message(tmp_path):
    rounds = [[{"text": "Looking. "}, {"tool_calls": [call("list_files")]}], [{"text": "Nothing."}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    stored = chats.get("p1", "c1").messages
    assert [(m.role, m.text) for m in stored] == [("user", "hi"), ("ai", "Looking. Nothing.")]


def test_the_tool_traffic_is_never_written_to_the_chat(tmp_path):
    rounds = [[{"tool_calls": [call("list_files")]}], [{"text": "done"}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    # The chat is what the user reads, not the model's bookkeeping.
    assert [m.role for m in chats.get("p1", "c1").messages] == ["user", "ai"]


def test_the_loop_stops_at_the_round_limit_and_still_writes(tmp_path):
    forever = [[{"text": "."}, {"tool_calls": [call("list_files")]}] for _ in range(MAX_ROUNDS + 3)]
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
    produced = list(stream_answer(chats, files, ScriptedEngine(rounds), "p1", "c1", NOW, NEVER))
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
    produced = list(stream_answer(chats, files, ScriptedEngine(rounds), "p1", "c1", NOW, NEVER))
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
    list(stream_answer(chats, files, ScriptedEngine(rounds), "p1", "c1", NOW, NEVER))
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
    forever = [[{"tool_calls": [call("list_files")]}] for _ in range(MAX_ROUNDS + 3)]
    with pytest.raises(EmptyMessage):
        _run(tmp_path, forever)


def _said_with(tmp_path, *turns):
    """Run one answer over a chat whose messages were sent with the given skills."""
    chats, files = _seeded(tmp_path)
    for number, (text, skill) in enumerate(turns):
        append_message(chats, "p1", "c1", text, f"2026-08-09T12:0{number}:00.000+00:00", skill=skill)
    engine = ScriptedEngine([[{"text": "ok"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER))
    return chats, engine.seen[0]


def _instructions(conversation):
    return [piece["content"] for piece in conversation if piece["role"] == "system"]


def test_a_skill_puts_its_instruction_right_before_the_message(tmp_path):
    _, conversation = _said_with(tmp_path, ("write me a scenario", "create-scenario"))
    assert conversation[-2] == {
        "role": "system",
        "content": instruction_for("create-scenario"),
    }
    assert conversation[-1]["content"] == "write me a scenario"


def test_the_same_skill_twice_running_says_it_once(tmp_path):
    _, conversation = _said_with(
        tmp_path, ("one", "create-scenario"), ("and again", "create-scenario")
    )
    # Resending the same text every turn would break the conversation and pay for it twice.
    assert _instructions(conversation) == [instruction_for("create-scenario")]


def test_a_reply_in_between_does_not_bring_it_back(tmp_path):
    chats, files = _seeded(tmp_path)
    append_message(chats, "p1", "c1", "one", NOW, skill="create-scenario")
    append_message(chats, "p1", "c1", "here it is", NOW, role="ai")
    append_message(chats, "p1", "c1", "again", NOW, skill="create-scenario")
    engine = ScriptedEngine([[{"text": "ok"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER))
    # Answers carry no skill, and letting them count would repeat the instruction every turn.
    assert _instructions(engine.seen[0]) == [instruction_for("create-scenario")]


def test_changing_the_skill_brings_the_new_one_in_once(tmp_path):
    _, conversation = _said_with(
        tmp_path, ("one", "create-scenario"), ("now split it", "split-into-frames")
    )
    assert _instructions(conversation) == [
        instruction_for("create-scenario"),
        instruction_for("split-into-frames"),
    ]


def test_a_skill_left_and_taken_up_again_is_said_again(tmp_path):
    _, conversation = _said_with(
        tmp_path,
        ("one", "create-scenario"),
        ("just chatting", ""),
        ("another scenario", "create-scenario"),
    )
    # The rule fades the further back it sits, so coming back to it says it again.
    assert _instructions(conversation) == [
        instruction_for("create-scenario"),
        instruction_for("create-scenario"),
    ]


def test_a_chat_without_a_skill_is_told_nothing_extra(tmp_path):
    _, conversation = _said_with(tmp_path, ("hello", ""))
    assert _instructions(conversation) == []


def test_a_skill_nobody_knows_adds_nothing_and_still_answers(tmp_path):
    chats, conversation = _said_with(tmp_path, ("hello", "web-search"))
    assert _instructions(conversation) == []
    assert chats.get("p1", "c1").messages[-1].text == "ok"


def test_the_instruction_is_never_written_to_the_chat(tmp_path):
    chats, _ = _said_with(tmp_path, ("write me a scenario", "create-scenario"))
    # The transcript is what the user reads: user sentences and answers, nothing else.
    assert [m.role for m in chats.get("p1", "c1").messages] == ["user", "user", "ai"]


def test_a_stream_that_breaks_writes_nothing(tmp_path):
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "half"}]], blow_up_after=0)
    with pytest.raises(EngineFailed):
        list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER))
    assert [m.text for m in chats.get("p1", "c1").messages] == ["hi"]


def test_an_unknown_chat_is_reported_before_anything_streams(tmp_path):
    chats, files = _seeded(tmp_path)
    with pytest.raises(ChatNotFound):
        list(stream_answer(chats, files, ScriptedEngine([]), "p1", "nope", NOW, NEVER))


def test_the_engine_is_asked_without_a_model(tmp_path):
    # Madde 82: which model answers belongs to the wiring, not to the chat. ScriptedEngine.stream
    # refuses one, so a use case that passed a model would die here.
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "hi"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER))
    assert len(engine.seen) == 1


# --- the calls a turn made, seen and kept (Madde 66) ---------------------------------------------


def _lines(produced):
    return [piece for piece in produced if isinstance(piece, ToolCall)]


def test_each_call_leaves_a_line_as_it_happens(tmp_path):
    rounds = [[{"tool_calls": [call("list_files")]}], [{"text": "Nothing yet."}]]
    _, _, _, produced = _run(tmp_path, rounds)
    assert _lines(produced) == [ToolCall("list_files", "", "No files")]


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
    rounds = [[{"tool_calls": [call("list_files")]}], [{"text": "done"}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert chats.get("p1", "c1").messages[-1].calls == (ToolCall("list_files", "", "No files"),)


def test_an_answer_that_called_nothing_remembers_none(tmp_path):
    chats, _, _, _ = _run(tmp_path, [[{"text": "Hello"}]])
    assert chats.get("p1", "c1").messages[-1].calls == ()


def test_the_kept_call_says_how_it_went(tmp_path):
    # Madde 78. The tests above pin the tool and the file; none of them asks whether the line under
    # the call survived, and that is the half a reader a week later is looking at.
    rounds = [[{"tool_calls": [call("list_files")]}], [{"text": "done"}]]
    chats, _, _, _ = _run(tmp_path, rounds)
    assert chats.get("p1", "c1").messages[-1].calls[0].outcome == "No files"


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

TWO_ROUNDS = [[{"text": "Half a "}, {"tool_calls": [call("list_files")]}], [{"text": "sentence."}]]


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
        [{"tool_calls": [call("list_files")]}, spent(1000, 600, 10)],
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
