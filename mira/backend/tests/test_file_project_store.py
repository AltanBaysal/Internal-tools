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
