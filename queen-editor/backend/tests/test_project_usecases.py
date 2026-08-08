import pytest

from backend.features.projects.domain.project import Project
from backend.features.projects.domain.usecases.create_project import (
    InvalidName,
    NameTaken,
    create_project,
)
from backend.features.projects.domain.usecases.get_settings import ProjectMissing, get_settings
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.domain.usecases.save_settings import save_settings


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


class FakeSettingsStore:
    def __init__(self, projects=("düğün",)):
        self.projects = list(projects)
        self.saved = {}

    def project_exists(self, project):
        return project in self.projects

    def read(self, project):
        return self.saved.get(project, {"prompts": "", "negative": "", "variants": None})

    def write(self, project, settings):
        self.saved[project] = settings


def test_get_settings_passes_the_store_through():
    store = FakeSettingsStore()
    store.saved["düğün"] = {"prompts": '["a"]', "negative": "neg", "variants": 4}
    assert get_settings(store, "düğün") == {"prompts": '["a"]', "negative": "neg", "variants": 4}


def test_get_settings_rejects_a_missing_project():
    with pytest.raises(ProjectMissing) as exc:
        get_settings(FakeSettingsStore(), "yok")
    assert str(exc.value) == "Proje yok: yok"


def test_save_settings_stores_what_it_was_given():
    store = FakeSettingsStore()
    save_settings(store, "düğün", '["a"]', "neg", 4, "nova.safetensors")
    assert store.saved["düğün"] == {"prompts": '["a"]', "negative": "neg", "variants": 4,
                                    "model": "nova.safetensors"}


def test_save_settings_keeps_text_the_server_would_reject():
    # A list that fails to parse is still what the user typed; losing it would punish the mistake
    # twice.
    store = FakeSettingsStore()
    save_settings(store, "düğün", "[ yarım", "", None)
    assert store.saved["düğün"]["prompts"] == "[ yarım"


def test_save_settings_rejects_a_missing_project():
    store = FakeSettingsStore()
    with pytest.raises(ProjectMissing):
        save_settings(store, "yok", '["a"]', "", 4)
    assert store.saved == {}
