import pytest

from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.usecases.edit_project import (
    InvalidProjectName,
    ProjectNotFound,
    edit_project,
)
from backend.services.store.store import Store


def _store(tmp_path):
    store = FileProjectStore(Store(str(tmp_path)))
    store.add(
        Project(
            id="pabc",
            name="Thesis",
            desc="Click to add a description.",
            hue=94,
            created_at="2026-08-09T10:00:00+00:00",
        )
    )
    return store


def test_the_name_changes_and_stays_changed(tmp_path):
    edit_project(_store(tmp_path), "pabc", name="Thesis research")
    assert FileProjectStore(Store(str(tmp_path))).get("pabc").name == "Thesis research"


def test_sending_only_a_description_leaves_the_name_alone(tmp_path):
    edited = edit_project(_store(tmp_path), "pabc", desc="Source summaries.")
    assert edited.name == "Thesis"
    assert edited.desc == "Source summaries."


def test_sending_only_a_name_leaves_the_description_alone(tmp_path):
    edited = edit_project(_store(tmp_path), "pabc", name="Renamed")
    assert edited.desc == "Click to add a description."


@pytest.mark.parametrize("bad", ["", "   ", "\n"])
def test_an_empty_name_is_rejected_and_the_old_one_survives(tmp_path, bad):
    store = _store(tmp_path)
    with pytest.raises(InvalidProjectName):
        edit_project(store, "pabc", name=bad)
    assert store.get("pabc").name == "Thesis"


def test_an_unknown_project_is_reported(tmp_path):
    with pytest.raises(ProjectNotFound):
        edit_project(_store(tmp_path), "nope", name="x")


def test_both_fields_are_trimmed(tmp_path):
    edited = edit_project(_store(tmp_path), "pabc", name="  Thesis  ", desc="  Notes.  ")
    assert (edited.name, edited.desc) == ("Thesis", "Notes.")


def test_the_hue_and_the_creation_time_are_never_touched(tmp_path):
    edited = edit_project(_store(tmp_path), "pabc", name="Renamed")
    assert edited.hue == 94
    assert edited.created_at == "2026-08-09T10:00:00+00:00"
