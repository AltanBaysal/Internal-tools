import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.errors import ChatNotFound, FileNotFound
from backend.features.workspace.domain.usecases.delete_chat import delete_chat
from backend.features.workspace.domain.usecases.delete_file import delete_file
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.services.store.store import Store


def _files(tmp_path):
    return FileFileStore(Store(str(tmp_path)))


def test_deleting_takes_the_file_out_of_the_list(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "body")
    assert delete_file(files, "p1", "plan.md") == "plan.md"
    assert files.list_names("p1") == []


def test_a_deleted_file_is_moved_rather_than_destroyed(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "body")
    delete_file(files, "p1", "plan.md")
    assert Store(str(tmp_path)).list_dir("p1/trash") == ["plan.md"]


def test_a_second_delete_of_the_same_name_does_not_lose_the_first(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "first")
    delete_file(files, "p1", "plan.md")
    files.write("p1", "plan.md", "second")
    # The trash keeps both; the answer says which one the second became.
    assert delete_file(files, "p1", "plan.md") == "plan-2.md"
    assert sorted(Store(str(tmp_path)).list_dir("p1/trash")) == ["plan-2.md", "plan.md"]


def test_deleting_a_file_that_is_not_there_is_reported(tmp_path):
    with pytest.raises(FileNotFound):
        delete_file(_files(tmp_path), "p1", "ghost.md")


# Restoring is gone by karar 16: every deletion asks first, and none of them offers a way back. The
# disk still keeps the file -- what went is the offer, not the trash.


def _seeded(tmp_path):
    store = Store(str(tmp_path))
    projects, chats = FileProjectStore(store), FileChatStore(store)
    now = "2026-08-09T11:04:00.000+00:00"
    create_project(projects, new_id="p1", now=now)
    # Naming no chat is what asks for one, since Madde 87.
    append_message(chats, "p1", "", "hi", now, project_store=projects, new_id="c1")
    return chats


def test_a_deleted_chat_is_gone(tmp_path):
    chats = _seeded(tmp_path)
    delete_chat(chats, "p1", "c1")
    assert chats.get("p1", "c1") is None
    assert chats.list_for("p1") == []


def test_deleting_a_chat_leaves_its_files_alone(tmp_path):
    chats = _seeded(tmp_path)
    files = _files(tmp_path)
    files.write("p1", "plan.md", "body")
    delete_chat(chats, "p1", "c1")
    # A file belongs to the project, never to the chat that happened to produce it.
    assert files.list_names("p1") == ["plan.md"]


def test_deleting_a_chat_that_is_not_there_is_reported(tmp_path):
    with pytest.raises(ChatNotFound):
        delete_chat(_seeded(tmp_path), "p1", "nope")


def test_a_deleted_chat_is_moved_rather_than_destroyed(tmp_path):
    # It used to be removed outright, on the grounds that files got Undo and chats got a question.
    # Karar 16 took the Undo, and what was left was the user's own sentences being destroyed while
    # QueenAgent's file sat in the trash. A chat is the most personal thing in the project.
    chats = _seeded(tmp_path)
    delete_chat(chats, "p1", "c1")
    assert Store(str(tmp_path)).list_dir("p1/trash") == ["c1.json"]


def test_the_same_chat_id_deleted_twice_does_not_lose_the_first(tmp_path):
    chats = _seeded(tmp_path)
    delete_chat(chats, "p1", "c1")
    append_message(
        chats,
        "p1",
        "",
        "again",
        "2026-08-09T12:00:00.000+00:00",
        project_store=FileProjectStore(Store(str(tmp_path))),
        new_id="c1",
    )
    delete_chat(chats, "p1", "c1")
    # The same rule the files follow: the trash keeps everything it is handed.
    assert sorted(Store(str(tmp_path)).list_dir("p1/trash")) == ["c1-2.json", "c1.json"]
