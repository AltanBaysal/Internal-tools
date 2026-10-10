"""The chat's status and the running turn's snapshot (Madde 461): pure rules, no store, no thread."""
from dataclasses import replace

import pytest

from backend.features.workspace.domain.chat import Chat, Message, ToolCall, Version
from backend.features.workspace.domain.permission import PermissionWanted
from backend.features.workspace.domain.tools import FileStarted, FileWritten
from backend.features.workspace.domain.turn import (
    ANSWERED,
    FAILED,
    IDLE,
    RUNNING,
    STOPPED,
    UNANSWERED,
    WAITING,
    Progress,
    Question,
    Snapshot,
    applied,
    changed,
    status_of,
)

AT = "2026-10-10T10:00:00.000+00:00"


def _chat(*said):
    return Chat(id="c1", title="hi", created_at=AT, messages=tuple(said))


def _user(text="hi"):
    return Message(role="user", at=AT, text=text)


def _ai(text="Done.", **flags):
    return Message(role="ai", at=AT, text=text, **flags)


# --- what the record says, with no turn running ----------------------------------------------------


def test_an_answer_is_answered():
    assert status_of(_chat(_user(), _ai()), None) == ANSWERED


def test_a_question_with_nothing_after_it_is_unanswered():
    # An old chat file whose last word is the user's reads the same way as a turn that died with the
    # process: there is a question and no answer, and nothing is running to give one.
    assert status_of(_chat(_user()), None) == UNANSWERED
    assert status_of(_chat(_user(), _ai(), _user("and more")), None) == UNANSWERED


def test_a_failed_answer_is_failed_whatever_its_kind():
    assert status_of(_chat(_user(), _ai("HTTP 502", failed="technical")), None) == FAILED
    assert status_of(_chat(_user(), _ai("refused", failed="refused")), None) == FAILED


def test_a_stopped_answer_is_stopped():
    assert status_of(_chat(_user(), _ai("", stopped=True)), None) == STOPPED


def test_a_chat_with_no_message_is_idle():
    # One cannot be made through the door, but the rule must not read past the end of a list.
    assert status_of(_chat(), None) == IDLE


def test_the_status_is_read_off_the_open_line():
    # The first line was answered and the open one was not: reading the first would send the user's
    # newest question nowhere.
    chat = replace(
        _chat(_user(), _ai()),
        versions=(Version(id="l2", parent="", at=0, messages=(_user("hi again"),)),),
        active="l2",
    )
    assert status_of(chat, None) == UNANSWERED
    assert status_of(replace(chat, active=""), None) == ANSWERED


# --- a turn in memory ------------------------------------------------------------------------------


def test_a_live_turn_is_running_whatever_the_record_says():
    # The record ends on the question while its turn runs; running is not on disk anywhere.
    assert status_of(_chat(_user()), Snapshot(id="t1")) == RUNNING


def test_a_live_turn_on_a_question_is_waiting():
    asked = Snapshot(id="t1", permission=Question(1, "create_file", "{}"))
    assert status_of(_chat(_user()), asked) == WAITING


def test_a_live_turn_says_its_status_with_no_record_at_hand():
    # What the events door and Stop answer with (Madde 462): they read no chat, and need none.
    assert status_of(None, Snapshot(id="t1")) == RUNNING
    assert status_of(None, Snapshot(id="t1", permission=Question(1, "edit_file", "{}"))) == WAITING


def test_an_ended_turn_leaves_the_status_to_the_record():
    over = Snapshot(id="t1", ended=True)
    assert status_of(_chat(_user(), _ai()), over) == ANSWERED
    assert status_of(_chat(_user()), over) == UNANSWERED


# --- the snapshot a turn keeps of itself ----------------------------------------------------------


def test_every_change_moves_the_version_on():
    assert changed(Snapshot(id="t1"), creating=True) == Snapshot(id="t1", version=1, creating=True)


def test_progress_replaces_the_last():
    once = applied(Snapshot(id="t1"), Progress(1, 32, 0))
    twice = applied(once, Progress(2, 32, 140))
    assert (twice.progress, twice.version) == (Progress(2, 32, 140), 2)


def test_a_file_started_is_being_created_until_it_is_written_or_its_step_is_kept():
    started = applied(Snapshot(id="t1"), FileStarted())
    assert started.creating
    written = applied(started, FileWritten("plan.md"))
    assert (written.creating, written.files) == (False, ("plan.md",))
    # A write that made no new file -- an edit -- ends on its step alone.
    stepped = applied(started, ToolCall("edit_file", "plan.md", "Saved"))
    assert (stepped.creating, stepped.calls) == (False, (ToolCall("edit_file", "plan.md", "Saved"),))


def test_steps_and_files_are_kept_in_the_order_they_came():
    snapshot = Snapshot(id="t1")
    for piece in (ToolCall("read_file", "a.md"), FileWritten("b.md"), ToolCall("create_file", "b.md")):
        snapshot = applied(snapshot, piece)
    assert snapshot.calls == (ToolCall("read_file", "a.md"), ToolCall("create_file", "b.md"))
    assert snapshot.files == ("b.md",)


def test_a_question_is_named_by_the_version_that_asked_it():
    # So two questions of one turn never share a name, and a late answer to the first cannot settle
    # the second.
    first = applied(Snapshot(id="t1", version=4), PermissionWanted("create_file", '{"name": "a"}'))
    assert first.permission == Question(5, "create_file", '{"name": "a"}')
    second = applied(changed(first, permission=None), PermissionWanted("edit_file", "{}"))
    assert second.permission.wait == 7


def test_something_that_is_not_a_piece_of_a_turn_is_refused():
    with pytest.raises(TypeError):
        applied(Snapshot(id="t1"), "a word")
