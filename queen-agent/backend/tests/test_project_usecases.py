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


def _born(store, pid="pabc"):
    return create_project(store, new_id=pid, now="2026-08-09T10:00:00+00:00")


def _named(store, name):
    """A project already sitting in the store under a name of its own."""
    store.add(Project(id=name, name=name, created_at="2026-08-09T09:00:00+00:00"))


def test_new_project_is_born_with_the_default_name():
    store = FakeProjectStore()
    project = _born(store)
    # Madde 191: numbered from the first one. An unnumbered first would stay special forever, and
    # the day it was renamed it would leave a hole nobody could see.
    assert project.name == f"{NEW_PROJECT_NAME} 1"
    assert project.id == "pabc"
    assert project.created_at == "2026-08-09T10:00:00+00:00"


def test_three_in_a_row_count_up():
    store = FakeProjectStore()
    assert [_born(store, pid).name for pid in ("p1", "p2", "p3")] == [
        "New project 1",
        "New project 2",
        "New project 3",
    ]


def test_a_deleted_number_is_taken_again():
    # The next free one rather than the next one along: three projects called New project 1, 3 and
    # 4 is a sidebar that reads like something went missing.
    store = FakeProjectStore()
    for pid in ("p1", "p2", "p3"):
        _born(store, pid)
    # Asserted before anything is removed: without it this test passes on a store that never
    # numbered anything, which is what it does today.
    assert [project.name for project in store.projects] == [
        "New project 1",
        "New project 2",
        "New project 3",
    ]

    store.projects = [p for p in store.projects if p.name != "New project 2"]
    assert _born(store, "p4").name == "New project 2"


def test_a_renamed_project_gives_its_number_back():
    # The number tells apart the ones still called New project. Rename one and there is nobody
    # left on the screen for that number to tell apart.
    store = FakeProjectStore()
    for pid in ("p1", "p2"):
        _born(store, pid)
    assert [project.name for project in store.projects] == ["New project 1", "New project 2"]

    store.projects[0] = Project(id="p1", name="Thesis", created_at="2026-08-09T10:00:00+00:00")
    assert _born(store, "p3").name == "New project 1"


def test_a_project_with_a_name_of_its_own_holds_no_number():
    store = FakeProjectStore()
    _named(store, "Thesis")
    _named(store, "Bar scene")
    assert _born(store).name == "New project 1"


def test_a_number_somebody_typed_by_hand_is_still_taken():
    # Two projects under one name is the one thing the number exists to prevent, and it does not
    # matter which of them got there first.
    store = FakeProjectStore()
    _named(store, "New project 1")
    _named(store, "New project 3")
    assert _born(store).name == "New project 2"
    store.projects.append(Project(id="x", name="New project 2", created_at="now"))
    assert _born(store, "p9").name == "New project 4"


def test_the_number_is_separated_by_a_space():
    # naming.unique_name is the precedent and this parts from it on purpose: a hyphen is a file
    # name's mark, and what the user reads in the sidebar is a title.
    store = FakeProjectStore()
    assert "-" not in _born(store).name
    assert _born(store, "p2").name.startswith(f"{NEW_PROJECT_NAME} ")


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
