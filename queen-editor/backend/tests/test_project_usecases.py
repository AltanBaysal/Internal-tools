import pytest

from backend.features.projects.domain.project import Project
from backend.features.projects.domain.usecases.create_project import (
    InvalidName,
    NameTaken,
    create_project,
)
from backend.features.projects.domain.usecases.delete_project import delete_project
from backend.features.projects.domain.usecases.get_settings import ProjectMissing, get_settings
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.domain.usecases.rename_project import rename_project
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

    def rename(self, old, new):
        """The renamed project, None when the new name is taken, False when the old one is gone."""
        if any(p.name == new for p in self.projects):
            return None
        found = next((p for p in self.projects if p.name == old), None)
        if found is None:
            return False
        self.projects = [Project(new, p.modified_at) if p.name == old else p
                         for p in self.projects]
        return next(p for p in self.projects if p.name == new)


class RecordingStore(FakeStore):
    """A store that writes down when it was asked to delete, so order can be asserted."""

    def __init__(self, log, projects=("düğün",)):
        super().__init__([Project(name, 100.0) for name in projects])
        self.log = log

    def delete(self, name):
        self.log.append(f"delete:{name}")
        gone = [p for p in self.projects if p.name == name]
        self.projects = [p for p in self.projects if p.name != name]
        return bool(gone)


def test_deleting_a_project_stops_its_production_before_the_folder_goes():
    """The other order is the bug: a worker writing into a folder that is being removed is exactly
    the error the confirm promises the user will not see."""
    log = []
    store = RecordingStore(log)

    delete_project(store, lambda project: log.append(f"halt:{project}"), "düğün")

    assert log == ["halt:düğün", "delete:düğün"]


def test_deleting_an_unknown_project_still_says_so():
    log = []
    with pytest.raises(ProjectMissing) as exc:
        delete_project(RecordingStore(log), lambda project: log.append("halt"), "yok")
    assert str(exc.value) == "Proje yok: yok"


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


# The port the projects feature knows nothing behind: production follows the folder there
# (photo_generation's own use case). Here it only has to run what it was handed.
def straight(old, new, do):
    return do()


def test_rename_moves_the_project_and_leaves_the_rest_alone():
    store = FakeStore([Project("düğün", 100.0), Project("nikah", 200.0)])

    rename_project(store, straight, "düğün", "kına")

    assert sorted(p.name for p in store.list()) == ["kına", "nikah"]


def test_rename_rejects_a_name_that_breaks_a_rule_without_touching_the_store():
    store = FakeStore([Project("düğün", 100.0)])
    with pytest.raises(InvalidName) as exc:
        rename_project(store, straight, "düğün", "foto/deneme")
    assert "kullanılamaz" in str(exc.value)
    assert [p.name for p in store.list()] == ["düğün"]


def test_rename_says_the_same_sentence_creating_says_when_the_name_is_taken():
    # One sentence for one situation: the user meets the same words whichever window they are in.
    store = FakeStore([Project("düğün", 100.0), Project("nikah", 200.0)])
    with pytest.raises(NameTaken) as exc:
        rename_project(store, straight, "düğün", "nikah")
    assert str(exc.value) == "Bu ad zaten kullanılıyor. Başka bir ad dene."


def test_saving_a_project_under_its_own_name_is_not_a_clash():
    # The design says so outright: the window closes and nothing moves.
    store = FakeStore([Project("düğün", 100.0)])

    rename_project(store, straight, "düğün", "düğün")

    assert [p.name for p in store.list()] == ["düğün"]


def test_renaming_a_project_that_is_not_there_says_so():
    with pytest.raises(ProjectMissing) as exc:
        rename_project(FakeStore(), straight, "yok", "başka")
    assert str(exc.value) == "Proje yok: yok"


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
