import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.domain.errors import FileNotFound
from backend.features.workspace.domain.ports import ChatStore
from backend.features.workspace.domain.usecases.delete_file import delete_file
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


def test_the_delete_chat_use_case_is_gone():
    # Madde 353: nothing on screen deletes a chat any more, so the rule that did is dead code.
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.delete_chat  # noqa: F401


def test_neither_the_chat_store_nor_its_port_can_delete():
    # Deleting the project still takes its chats, whole, with the directory (FileProjectStore).
    assert not hasattr(FileChatStore, "delete")
    assert not hasattr(ChatStore, "delete")
