import pytest

from backend.features.workspace.data.file_project_store import (
    PROJECT_FILE,
    FileProjectStore,
    ProjectIdTaken,
)
from backend.features.workspace.domain.project import Project
from backend.services.store.store import Store


def _store(tmp_path):
    return FileProjectStore(Store(str(tmp_path)))


def _project(pid="pabc", name="Thesis", created_at="2026-08-09T10:00:00+00:00"):
    return Project(id=pid, name=name, desc="Notes.", hue=94, created_at=created_at)


def test_project_survives_a_new_store_instance(tmp_path):
    _store(tmp_path).add(_project())
    # A second instance reads from disk only -- this is what "the app rebuilds itself from files"
    # means, and it is what a server restart does.
    assert _store(tmp_path).list_all() == [_project()]


def test_existing_id_is_not_overwritten(tmp_path):
    store = _store(tmp_path)
    store.add(_project(name="First"))
    with pytest.raises(ProjectIdTaken):
        store.add(_project(name="Second"))
    assert store.list_all()[0].name == "First"


def test_entries_without_a_project_file_are_ignored(tmp_path):
    raw = Store(str(tmp_path))
    raw.write_text("stray/notes.txt", "not a project")
    FileProjectStore(raw).add(_project())
    assert [p.id for p in FileProjectStore(raw).list_all()] == ["pabc"]


def test_empty_root_lists_nothing(tmp_path):
    assert _store(tmp_path).list_all() == []


def test_the_id_is_the_directory_name_and_is_not_repeated_in_the_file(tmp_path):
    raw = Store(str(tmp_path))
    FileProjectStore(raw).add(_project())
    assert "pabc" not in raw.read_text(f"pabc/{PROJECT_FILE}")


def test_counts_are_zero_when_the_subdirectories_do_not_exist(tmp_path):
    _store(tmp_path).add(_project())
    listed = _store(tmp_path).list_all()[0]
    assert (listed.chat_count, listed.file_count) == (0, 0)


def test_counts_come_from_the_directories(tmp_path):
    raw = Store(str(tmp_path))
    FileProjectStore(raw).add(_project())
    raw.write_text("pabc/chats/c1.json", "{}")
    raw.write_text("pabc/files/a.md", "a")
    raw.write_text("pabc/files/b.md", "b")
    listed = FileProjectStore(raw).list_all()[0]
    assert (listed.chat_count, listed.file_count) == (1, 2)


def test_counts_are_not_written_into_the_project_file(tmp_path):
    raw = Store(str(tmp_path))
    FileProjectStore(raw).add(_project())
    stored = raw.read_text(f"pabc/{PROJECT_FILE}")
    # A derived answer is never stored: the directory already answers it.
    assert "chat" not in stored and "file" not in stored
