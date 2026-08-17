from dataclasses import fields

from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.usecases.create_project import (
    HUE_STEP,
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
    return Project(id=pid, name=pid, hue=0, created_at=created_at)


def test_a_project_carries_no_description():
    # The design removed it as a data field, not only as a paragraph on screen.
    assert "desc" not in {field.name for field in fields(Project)}


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


def test_hue_steps_with_the_number_of_existing_projects():
    store = FakeProjectStore([_project("p1", "2026-08-01T00:00:00+00:00")])
    project = create_project(store, new_id="p2", now="2026-08-09T10:00:00+00:00")
    assert project.hue == HUE_STEP


def test_hue_wraps_around_the_colour_wheel():
    existing = [_project(f"p{i}", "2026-08-01T00:00:00+00:00") for i in range(8)]
    project = create_project(
        FakeProjectStore(existing), new_id="p9", now="2026-08-09T10:00:00+00:00"
    )
    assert 0 <= project.hue < 360


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
