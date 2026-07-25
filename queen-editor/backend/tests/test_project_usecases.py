import pytest

from backend.features.projects.domain.project import Project
from backend.features.projects.domain.usecases.create_project import (
    InvalidName,
    NameTaken,
    create_project,
)
from backend.features.projects.domain.usecases.list_projects import list_projects


class FakeStore:
    """In-memory ProjectStore -- no Drive, no filesystem."""

    def __init__(self, projects=()):
        self.projects = list(projects)

    def list(self):
        return list(self.projects)

    def create(self, name):
        if any(p.name == name for p in self.projects):
            return None
        project = Project(name, 100.0)
        self.projects.append(project)
        return project


def test_list_projects_newest_change_first():
    store = FakeStore([Project("eski", 100.0), Project("yeni", 300.0), Project("orta", 200.0)])
    assert [p.name for p in list_projects(store)] == ["yeni", "orta", "eski"]


def test_list_projects_returns_empty_list():
    assert list_projects(FakeStore()) == []


def test_create_project_returns_created_project():
    store = FakeStore()
    project = create_project(store, "kapak çekimi")
    assert project.name == "kapak çekimi"
    assert [p.name for p in store.list()] == ["kapak çekimi"]


def test_create_project_rejects_invalid_name_without_touching_store():
    store = FakeStore()
    with pytest.raises(InvalidName) as exc:
        create_project(store, "foto/deneme")
    assert "kullanılamaz" in str(exc.value)
    assert store.list() == []


def test_create_project_raises_when_name_taken():
    store = FakeStore([Project("düğün", 100.0)])
    with pytest.raises(NameTaken) as exc:
        create_project(store, "düğün")
    assert str(exc.value) == "Bu ad zaten kullanılıyor. Başka bir ad dene."
