from dataclasses import replace

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.domain.chat import Chat, Message
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


def test_the_model_a_chat_chose_is_written_and_read_back(tmp_path):
    FileChatStore(Store(str(tmp_path))).add("p1", replace(_chat(), model="grok-4.3"))
    assert FileChatStore(Store(str(tmp_path))).get("p1", "c1").model == "grok-4.3"


def test_a_chat_that_chose_nothing_writes_no_model(tmp_path):
    # An empty field is noise on disk, exactly as an empty file list is.
    raw = Store(str(tmp_path))
    FileChatStore(raw).add("p1", _chat())
    assert "model" not in raw.read_text("p1/chats/c1.json")


def test_a_chat_written_before_models_existed_still_reads(tmp_path):
    # There are records on disk already. They have no such field and must not need a migration.
    raw = Store(str(tmp_path))
    raw.write_text(
        "p1/chats/old.json",
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00", "messages": []}',
    )
    assert FileChatStore(raw).get("p1", "old").model == ""


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
