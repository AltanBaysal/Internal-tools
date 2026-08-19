import json
from dataclasses import replace

import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.chat import Chat
from backend.features.workspace.domain.errors import ChatNotFound, EmptyMessage, EngineFailed
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.domain.tools import MAX_ROUNDS, FileStarted, FileWritten
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.start_chat import start_chat
from backend.features.workspace.domain.usecases.stream_answer import stream_answer
from backend.services.store.store import Store

NOW = "2026-08-09T11:06:00.000+00:00"

STRUCTURE = json.dumps(
    {
        "quality": "score_9_up",
        "characters": {"aylin": "1girl"},
        "locations": {"bedroom": "sunlit bedroom"},
        "shots": [
            {"characters": ["aylin"], "location": "bedroom", "action": "one", "camera": "wide"}
        ],
    }
)


def call(tool, call_id="t1", **arguments):
    return {"id": call_id, "function": {"name": tool, "arguments": json.dumps(arguments)}}


class ScriptedEngine:
    """Each round is a list of pieces the engine hands back."""

    def __init__(self, rounds, blow_up_after=None):
        self.rounds = list(rounds)
        self.blow_up_after = blow_up_after
        self.seen = []
        self.asked_for = "not asked"

    def stream(self, messages, tools=None, model=None):
        self.seen.append(list(messages))
        self.asked_for = model
        if self.blow_up_after is not None and len(self.seen) > self.blow_up_after:
            raise RuntimeError("connection dropped")
        pieces = self.rounds.pop(0) if self.rounds else []
        for piece in pieces:
            yield piece


def _seeded(tmp_path):
    store = Store(str(tmp_path))
    projects, chats, files = FileProjectStore(store), FileChatStore(store), FileFileStore(store)
    now = "2026-08-09T11:04:00.000+00:00"
    create_project(projects, new_id="p1", now=now)
    start_chat(chats, projects, "p1", "hi", "c1", now)
    return chats, files


def _run(tmp_path, rounds, **kwargs):
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine(rounds, **kwargs)
    produced = list(stream_answer(chats, files, engine, "p1", "c1", NOW))
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
    files.write("p1", "shots.json", STRUCTURE)
    rounds = [[{"tool_calls": [call("build_prompts", name="shots.json")]}], [{"text": "done"}]]
    produced = list(stream_answer(chats, files, ScriptedEngine(rounds), "p1", "c1", NOW))
    # A file is born here too, so it gets the same dashed card and the same filled one.
    assert isinstance(produced[0], FileStarted)
    assert produced[1] == FileWritten("shots.py")


def test_editing_a_file_announces_nothing(tmp_path):
    chats, files = _seeded(tmp_path)
    files.write("p1", "plan.md", "alpha")
    rounds = [
        [{"tool_calls": [call("edit_file", name="plan.md", old="alpha", new="beta")]}],
        [{"text": "done"}],
    ]
    produced = list(stream_answer(chats, files, ScriptedEngine(rounds), "p1", "c1", NOW))
    # An edit is not a birth: a card would claim a file the user already has is new.
    assert not any(isinstance(piece, (FileStarted, FileWritten)) for piece in produced)
    assert files.read("p1", "plan.md") == "beta"


def test_a_name_born_twice_in_one_turn_is_remembered_once(tmp_path):
    chats, files = _seeded(tmp_path)
    files.write("p1", "shots.json", STRUCTURE)
    rounds = [
        [
            {
                "tool_calls": [
                    call("build_prompts", call_id="a", name="shots.json"),
                    call("build_prompts", call_id="b", name="shots.json"),
                ]
            }
        ],
        [{"text": "done"}],
    ]
    list(stream_answer(chats, files, ScriptedEngine(rounds), "p1", "c1", NOW))
    # The card says a file exists, not how many times it was written.
    assert chats.get("p1", "c1").messages[-1].files == ("shots.py",)


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
    list(stream_answer(chats, files, engine, "p1", "c1", NOW))
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
    list(stream_answer(chats, files, engine, "p1", "c1", NOW))
    # Answers carry no skill, and letting them count would repeat the instruction every turn.
    assert _instructions(engine.seen[0]) == [instruction_for("create-scenario")]


def test_changing_the_skill_brings_the_new_one_in_once(tmp_path):
    _, conversation = _said_with(
        tmp_path, ("one", "create-scenario"), ("now split it", "split-into-shots")
    )
    assert _instructions(conversation) == [
        instruction_for("create-scenario"),
        instruction_for("split-into-shots"),
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
        list(stream_answer(chats, files, engine, "p1", "c1", NOW))
    assert [m.text for m in chats.get("p1", "c1").messages] == ["hi"]


def test_an_unknown_chat_is_reported_before_anything_streams(tmp_path):
    chats, files = _seeded(tmp_path)
    with pytest.raises(ChatNotFound):
        list(stream_answer(chats, files, ScriptedEngine([]), "p1", "nope", NOW))


def test_the_answer_is_asked_for_with_the_chats_own_model(tmp_path):
    chats, files = _seeded(tmp_path)
    chats.replace("p1", replace(chats.get("p1", "c1"), model="grok-4.3"))
    engine = ScriptedEngine([[{"text": "hi"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW))
    assert engine.asked_for == "grok-4.3"


def test_a_chat_that_chose_nothing_asks_for_nothing(tmp_path):
    # None, not a name: which model answers for a chat that never picked one is the engine's own
    # setting, and the domain has no business knowing what it says.
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "hi"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW))
    assert engine.asked_for is None
