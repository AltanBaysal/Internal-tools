from dataclasses import fields

from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.usecases.create_project import (
    NEW_PROJECT_NAME,
    create_project,
)
from backend.features.workspace.domain.usecases.list_projects import list_projects


class FakeProjectStore:
    """A stand-in port: the use cases are tested with no disk and no clock."""

    def __init__(self, projects=()):
        self.projects = list(projects)

    def add(self, project):
        self.projects.append(project)

    def list_all(self):
        return list(self.projects)


def _project(pid, created_at):
    return Project(id=pid, name=pid, created_at=created_at)


def test_a_project_carries_neither_a_description_nor_a_colour():
    # Both were data fields, and both are gone: one accent marks the primary action and nothing
    # else, so a project has no colour of its own to store.
    named = {field.name for field in fields(Project)}
    assert "desc" not in named
    assert "hue" not in named


def test_new_project_is_born_with_the_default_name():
    store = FakeProjectStore()
    project = create_project(store, new_id="pabc", now="2026-08-09T10:00:00+00:00")
    assert project.name == NEW_PROJECT_NAME
    assert project.id == "pabc"
    assert project.created_at == "2026-08-09T10:00:00+00:00"


def test_created_project_is_handed_to_the_store():
    store = FakeProjectStore()
    project = create_project(store, new_id="pabc", now="2026-08-09T10:00:00+00:00")
    assert store.projects == [project]


def test_projects_come_back_oldest_first():
    # The ids are deliberately in reverse alphabetical order: this is the only way to prove the
    # order comes from createdAt rather than from the directory name.
    store = FakeProjectStore(
        [
            _project("zzz", "2026-08-05T00:00:00+00:00"),
            _project("aaa", "2026-08-01T00:00:00+00:00"),
        ]
    )
    assert [p.id for p in list_projects(store)] == ["aaa", "zzz"]
