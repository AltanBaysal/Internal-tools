import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.errors import ChatNotFound, FileNotFound, NameTaken
from backend.features.workspace.domain.usecases.delete_chat import delete_chat
from backend.features.workspace.domain.usecases.delete_file import delete_file
from backend.features.workspace.domain.usecases.list_files import list_files
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.restore_file import restore_file
from backend.features.workspace.domain.usecases.start_chat import start_chat
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


def test_restoring_puts_the_file_back_with_its_contents(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "body")
    restore_file(files, "p1", delete_file(files, "p1", "plan.md"), "plan.md")
    assert files.read("p1", "plan.md") == "body"


def test_restoring_keeps_the_time_so_the_row_goes_back_where_it_was(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "old.md", "a")
    before = list_files(files, "p1")[0].modified_at
    restore_file(files, "p1", delete_file(files, "p1", "old.md"), "old.md")
    # Moving is not rewriting: the file returns to its old place in the list rather than the top.
    assert list_files(files, "p1")[0].modified_at == before


def test_restoring_onto_a_name_that_was_taken_again_refuses(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "first")
    trashed = delete_file(files, "p1", "plan.md")
    files.write("p1", "plan.md", "second")
    with pytest.raises(NameTaken):
        restore_file(files, "p1", trashed, "plan.md")
    # Refused, not guessed at: both files are still where they were.
    assert files.read("p1", "plan.md") == "second"
    assert Store(str(tmp_path)).list_dir("p1/trash") == ["plan.md"]


def test_restoring_something_the_trash_does_not_hold_is_reported(tmp_path):
    with pytest.raises(FileNotFound):
        restore_file(_files(tmp_path), "p1", "ghost.md", "ghost.md")


def _seeded(tmp_path):
    store = Store(str(tmp_path))
    projects, chats = FileProjectStore(store), FileChatStore(store)
    now = "2026-08-09T11:04:00.000+00:00"
    create_project(projects, new_id="p1", now=now)
    start_chat(chats, projects, "p1", "hi", "c1", now)
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
