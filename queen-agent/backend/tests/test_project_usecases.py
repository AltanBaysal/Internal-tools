from dataclasses import fields

import pytest

from backend.features.workspace.domain.errors import InvalidProjectName
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.usecases import create_project as create_project_module
from backend.features.workspace.domain.usecases.create_project import create_project


class FakeProjectStore:
    """A stand-in port: the use cases are tested with no disk and no clock."""

    def __init__(self, projects=()):
        self.projects = list(projects)

    def add(self, project):
        self.projects.append(project)

    def list_all(self):
        return list(self.projects)


def test_a_project_carries_neither_a_description_nor_a_colour():
    # Both were data fields, and both are gone: one accent marks the primary action and nothing
    # else, so a project has no colour of its own to store.
    named = {field.name for field in fields(Project)}
    assert "desc" not in named
    assert "hue" not in named


def _born(store, pid="pabc", name="Harbour"):
    return create_project(store, new_id=pid, name=name, now="2026-08-09T10:00:00+00:00")


def test_a_new_project_is_born_with_the_name_it_was_given():
    # Madde 361: every + New project asks for the name first, so the project is born with it --
    # trimmed, as a rename trims it.
    store = FakeProjectStore()
    project = _born(store, name="  Harbour at dusk  ")
    assert project.name == "Harbour at dusk"
    assert project.id == "pabc"
    assert project.created_at == "2026-08-09T10:00:00+00:00"


def test_a_project_is_not_born_without_a_name():
    # The screen sends nothing for a blank field, but that is a convenience; the rule lives here.
    store = FakeProjectStore()
    for blank in ("", "   ", None):
        with pytest.raises(InvalidProjectName):
            _born(store, name=blank)
    assert store.projects == []


def test_the_numbering_is_gone():
    # Madde 191 numbered a project born with no name -- New project 1, 2, 3. No road makes one any
    # more, so the stem that numbering hung off is not kept either.
    assert not hasattr(create_project_module, "NEW_PROJECT_NAME")


def test_created_project_is_handed_to_the_store():
    store = FakeProjectStore()
    project = _born(store)
    assert store.projects == [project]
