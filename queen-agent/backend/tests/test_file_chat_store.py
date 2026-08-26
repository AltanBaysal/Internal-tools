import json
from dataclasses import replace

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.domain.chat import Chat, Message, ToolCall, Usage
from backend.services.store.store import Store


def _chat(chat_id="c1", text="Hello"):
    return Chat(
        id=chat_id,
        title=text,
        created_at="2026-08-09T11:04:00+00:00",
        messages=(Message(role="user", at="2026-08-09T11:04:00+00:00", text=text),),
    )


def test_a_chat_survives_a_new_store_instance(tmp_path):
    FileChatStore(Store(str(tmp_path))).add("p1", _chat())
    assert FileChatStore(Store(str(tmp_path))).get("p1", "c1") == _chat()


def test_the_id_is_the_file_name_and_is_not_repeated_inside(tmp_path):
    raw = Store(str(tmp_path))
    FileChatStore(raw).add("p1", _chat())
    assert "c1" not in raw.read_text("p1/chats/c1.json")


def test_the_skill_a_chat_selected_is_written_and_read_back(tmp_path):
    FileChatStore(Store(str(tmp_path))).add("p1", replace(_chat(), skill="generate-prompts"))
    assert FileChatStore(Store(str(tmp_path))).get("p1", "c1").skill == "generate-prompts"


def test_the_skill_a_message_was_sent_with_survives_the_disk(tmp_path):
    written = replace(
        _chat(),
        messages=(Message(role="user", at="2026-08-09T11:04:00+00:00", text="hi", skill="verify"),),
    )
    FileChatStore(Store(str(tmp_path))).add("p1", written)
    assert FileChatStore(Store(str(tmp_path))).get("p1", "c1").messages[0].skill == "verify"


def test_a_chat_and_a_message_with_no_skill_write_no_field(tmp_path):
    raw = Store(str(tmp_path))
    FileChatStore(raw).add("p1", _chat())
    assert "skill" not in raw.read_text("p1/chats/c1.json")


def test_a_chat_written_before_skills_existed_still_reads(tmp_path):
    # There are records on disk already. They have no such field and must not need a migration.
    raw = Store(str(tmp_path))
    raw.write_text(
        "p1/chats/old.json",
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00", "messages": []}',
    )
    assert FileChatStore(raw).get("p1", "old").skill == ""


def test_a_chat_that_still_carries_a_model_on_disk_is_read_without_it(tmp_path):
    # Madde 82 took the field out. Every chat written before it has a model key sitting in its
    # JSON, and reading one must not fail over a word nothing asks about any more -- it simply
    # drops the next time the chat is written.
    raw = Store(str(tmp_path))
    raw.write_text(
        "p1/chats/old.json",
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00", "messages": [],'
        ' "model": "grok-4.3"}',
    )
    old = FileChatStore(raw).get("p1", "old")
    assert old.title == "Old"
    assert not hasattr(old, "model")


def test_an_unknown_chat_is_none(tmp_path):
    assert FileChatStore(Store(str(tmp_path))).get("p1", "nope") is None


def test_a_project_without_chats_lists_nothing(tmp_path):
    assert FileChatStore(Store(str(tmp_path))).list_for("p1") == []


def test_entries_that_are_not_chat_files_are_skipped(tmp_path):
    raw = Store(str(tmp_path))
    store = FileChatStore(raw)
    store.add("p1", _chat())
    raw.write_text("p1/chats/notes.txt", "stray")
    assert [chat.id for chat in store.list_for("p1")] == ["c1"]


# --- the calls a message carries (Madde 66) ------------------------------------------------------


def _answered(*calls):
    return replace(
        _chat(),
        messages=(
            Message(role="ai", at="2026-08-09T11:05:00+00:00", text="Read it.", calls=calls),
        ),
    )


def test_the_calls_an_answer_made_survive_a_round_trip(tmp_path):
    chat = _answered(ToolCall("read_file", "plan.md"), ToolCall("list_files", ""))
    FileChatStore(Store(str(tmp_path))).add("p1", chat)
    assert FileChatStore(Store(str(tmp_path))).get("p1", "c1") == chat


def test_a_message_that_called_nothing_writes_no_field(tmp_path):
    # An empty list is noise on disk, exactly as an empty file list is.
    raw = Store(str(tmp_path))
    FileChatStore(raw).add("p1", _chat())
    assert "calls" not in raw.read_text("p1/chats/c1.json")


def test_a_call_with_no_target_writes_no_target(tmp_path):
    raw = Store(str(tmp_path))
    FileChatStore(raw).add("p1", _answered(ToolCall("list_files", "")))
    assert "target" not in raw.read_text("p1/chats/c1.json")


def test_how_a_call_went_survives_a_round_trip(tmp_path):
    chat = _answered(ToolCall("read_file", "plan.md", "45 lines"))
    FileChatStore(Store(str(tmp_path))).add("p1", chat)
    assert FileChatStore(Store(str(tmp_path))).get("p1", "c1") == chat


def test_a_call_with_nothing_to_say_writes_no_outcome(tmp_path):
    # The same rule one field over: a call recorded before this existed carries none.
    raw = Store(str(tmp_path))
    FileChatStore(raw).add("p1", _answered(ToolCall("list_files", "")))
    assert "outcome" not in raw.read_text("p1/chats/c1.json")


def test_a_stopped_answer_survives_a_round_trip(tmp_path):
    chat = replace(
        _chat(),
        messages=(
            Message(role="ai", at="2026-08-09T11:05:00+00:00", text="Half a", stopped=True),
        ),
    )
    FileChatStore(Store(str(tmp_path))).add("p1", chat)
    assert FileChatStore(Store(str(tmp_path))).get("p1", "c1") == chat


def test_an_answer_that_was_not_stopped_writes_no_field(tmp_path):
    raw = Store(str(tmp_path))
    FileChatStore(raw).add("p1", _chat())
    assert "stopped" not in raw.read_text("p1/chats/c1.json")


def test_a_chat_written_before_calls_existed_reads_back_empty(tmp_path):
    # No migration: the field is absent, and absent is what empty means.
    raw = Store(str(tmp_path))
    raw.write_text(
        "p1/chats/c1.json",
        json.dumps(
            {
                "title": "Hello",
                "createdAt": "2026-08-09T11:04:00+00:00",
                "messages": [{"role": "ai", "at": "2026-08-09T11:04:00+00:00", "text": "hi"}],
            }
        ),
    )
    assert FileChatStore(raw).get("p1", "c1").messages[0].calls == ()
    # The same absence, one field over: nothing written before today was ever stopped.
    assert FileChatStore(raw).get("p1", "c1").messages[0].stopped is False
    # And one more: nothing written before today was ever measured.
    assert FileChatStore(raw).get("p1", "c1").messages[0].usage == Usage()


# --- what the answer spent (Madde 68) ------------------------------------------------------------


def test_what_an_answer_spent_survives_a_round_trip(tmp_path):
    chat = replace(
        _chat(),
        messages=(
            Message(
                role="ai",
                at="2026-08-09T11:05:00+00:00",
                text="Here it is.",
                usage=Usage(sent=12400, cached=9100, answered=842),
            ),
        ),
    )
    FileChatStore(Store(str(tmp_path))).add("p1", chat)
    assert FileChatStore(Store(str(tmp_path))).get("p1", "c1") == chat


def test_an_answer_nobody_measured_writes_no_field(tmp_path):
    # An all-zero object is noise on disk, exactly as an empty file list is.
    raw = Store(str(tmp_path))
    FileChatStore(raw).add("p1", _chat())
    assert "usage" not in raw.read_text("p1/chats/c1.json")
