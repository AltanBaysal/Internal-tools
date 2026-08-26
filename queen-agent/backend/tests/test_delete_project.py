import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.errors import ProjectNotFound
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.delete_project import delete_project
from backend.features.workspace.domain.usecases.append_message import append_message
from backend.services.store.store import Store


def _project_with_contents(tmp_path, project_id="p1"):
    store = Store(str(tmp_path))
    projects = FileProjectStore(store)
    create_project(projects, new_id=project_id, now="2026-08-09T10:00:00+00:00")
    # Naming no chat is what asks for one, since Madde 87.
    append_message(
        FileChatStore(store),
        project_id,
        "",
        "hello",
        "2026-08-09T11:04:00+00:00",
        project_store=projects,
        new_id="c1",
    )
    FileFileStore(store).write(project_id, "plan.md", "body")
    return projects, store


def test_a_deleted_project_leaves_the_list(tmp_path):
    projects, _ = _project_with_contents(tmp_path)
    delete_project(projects, "p1")
    assert projects.list_all() == []


def test_the_project_is_moved_rather_than_destroyed(tmp_path):
    projects, store = _project_with_contents(tmp_path)
    assert delete_project(projects, "p1") == "p1"
    # Whole and intact: the chats and the files go with the directory rather than being deleted one
    # by one, and nothing on disk is lost.
    assert sorted(store.list_dir("trash/p1")) == ["chats", "files", "project.json"]
    assert store.list_dir("trash/p1/files") == ["plan.md"]
    assert store.list_dir("trash/p1/chats") == ["c1.json"]


def test_the_trash_is_not_a_project(tmp_path):
    # The root listing is one directory per live project. The trash has no project.json of its own,
    # which is exactly what the store already skips.
    projects, _ = _project_with_contents(tmp_path)
    delete_project(projects, "p1")
    assert [project.id for project in projects.list_all()] == []


def test_the_same_id_deleted_twice_does_not_lose_the_first(tmp_path):
    projects, store = _project_with_contents(tmp_path)
    delete_project(projects, "p1")
    create_project(projects, new_id="p1", now="2026-08-10T10:00:00+00:00")
    assert delete_project(projects, "p1") == "p1-2"
    assert sorted(store.list_dir("trash")) == ["p1", "p1-2"]


def test_deleting_a_project_that_is_not_there_is_reported(tmp_path):
    projects = FileProjectStore(Store(str(tmp_path)))
    with pytest.raises(ProjectNotFound):
        delete_project(projects, "nope")


def test_the_other_projects_are_untouched(tmp_path):
    projects, store = _project_with_contents(tmp_path)
    _project_with_contents(tmp_path, project_id="p2")
    delete_project(projects, "p1")
    assert [project.id for project in projects.list_all()] == ["p2"]
    assert store.list_dir("p2/files") == ["plan.md"]
