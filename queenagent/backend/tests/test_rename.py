import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.errors import (
    ChatNotFound,
    FileNotFound,
    InvalidChatTitle,
)
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.list_files import list_files
from backend.features.workspace.domain.usecases.rename_chat import rename_chat
from backend.features.workspace.domain.usecases.rename_file import rename_file
from backend.features.workspace.domain.usecases.start_chat import start_chat
from backend.services.store.store import Store


def _files(tmp_path):
    return FileFileStore(Store(str(tmp_path)))


def _chats(tmp_path):
    store = Store(str(tmp_path))
    projects, chats = FileProjectStore(store), FileChatStore(store)
    now = "2026-08-09T11:04:00.000+00:00"
    create_project(projects, new_id="p1", now=now)
    start_chat(chats, projects, "p1", "hi", "c1", now)
    return chats


def test_a_chat_takes_the_new_title(tmp_path):
    chats = _chats(tmp_path)
    assert rename_chat(chats, "p1", "c1", "The introduction").title == "The introduction"
    assert chats.get("p1", "c1").title == "The introduction"


def test_renaming_a_chat_leaves_what_was_said_alone(tmp_path):
    chats = _chats(tmp_path)
    rename_chat(chats, "p1", "c1", "Something else")
    assert [message.text for message in chats.get("p1", "c1").messages] == ["hi"]


def test_an_empty_title_is_refused(tmp_path):
    chats = _chats(tmp_path)
    with pytest.raises(InvalidChatTitle):
        rename_chat(chats, "p1", "c1", "   ")
    assert chats.get("p1", "c1").title == "hi"


def test_renaming_a_chat_that_is_not_there_is_reported(tmp_path):
    with pytest.raises(ChatNotFound):
        rename_chat(_chats(tmp_path), "p1", "nope", "x")


def test_a_file_takes_the_new_name_and_keeps_its_contents(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "the body")
    assert rename_file(files, "p1", "plan.md", "outline.md").name == "outline.md"
    assert files.read("p1", "outline.md") == "the body"
    assert files.list_names("p1") == ["outline.md"]


def test_renaming_keeps_the_time_so_the_row_does_not_jump(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "a")
    before = list_files(files, "p1")[0].modified_at
    rename_file(files, "p1", "plan.md", "outline.md")
    # Moving is not rewriting: the row stays where it was in the list.
    assert list_files(files, "p1")[0].modified_at == before


def test_a_taken_name_is_numbered_rather_than_refused(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "first")
    files.write("p1", "outline.md", "second")
    # Undo promises the old name back and refuses; renaming promises a name and gives the free one.
    assert rename_file(files, "p1", "plan.md", "outline.md").name == "outline-2.md"
    assert files.read("p1", "outline.md") == "second"


def test_the_name_a_person_types_is_cleaned_like_any_other(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "a")
    assert rename_file(files, "p1", "plan.md", "../../secret").name == "secret.md"


def test_renaming_to_the_same_name_changes_nothing(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "a")
    # Without this the file would be numbered against itself and become plan-2.md.
    assert rename_file(files, "p1", "plan.md", "plan.md").name == "plan.md"


def test_the_answer_carries_the_chip_and_the_time(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "a")
    renamed = rename_file(files, "p1", "plan.md", "notes.txt")
    assert renamed.ext == "txt"
    assert renamed.modified_at.startswith("20")


def test_renaming_a_file_that_is_not_there_is_reported(tmp_path):
    with pytest.raises(FileNotFound):
        rename_file(_files(tmp_path), "p1", "ghost.md", "x.md")
