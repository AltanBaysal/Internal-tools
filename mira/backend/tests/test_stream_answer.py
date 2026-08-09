import json

import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.chat import Chat
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.tools import MAX_ROUNDS, FileStarted, FileWritten
from backend.features.workspace.domain.usecases.start_chat_in_new_project import (
    start_chat_in_new_project,
)
from backend.features.workspace.domain.usecases.stream_answer import stream_answer
from backend.services.store.store import Store

NOW = "2026-08-09T11:06:00.000+00:00"


def call(tool, call_id="t1", **arguments):
    return {"id": call_id, "function": {"name": tool, "arguments": json.dumps(arguments)}}


class ScriptedEngine:
    """Each round is a list of pieces the engine hands back."""

    def __init__(self, rounds, blow_up_after=None):
        self.rounds = list(rounds)
        self.blow_up_after = blow_up_after
        self.seen = []

    def stream(self, messages, tools=None):
        self.seen.append(list(messages))
        if self.blow_up_after is not None and len(self.seen) > self.blow_up_after:
            raise RuntimeError("connection dropped")
        pieces = self.rounds.pop(0) if self.rounds else []
        for piece in pieces:
            yield piece


def _seeded(tmp_path):
    store = Store(str(tmp_path))
    projects, chats, files = FileProjectStore(store), FileChatStore(store), FileFileStore(store)
    start_chat_in_new_project(projects, chats, "hi", "p1", "c1", "2026-08-09T11:04:00.000+00:00")
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
