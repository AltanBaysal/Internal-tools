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


def _archive():
    """The archive use cases, reached where they are used rather than at the top of the file: the
    module does not exist yet in the test tour, and an import up there would fail collection and
    take every other question in this file down with it."""
    from backend.features.projects.domain.usecases import archive_project
    return archive_project


def archive_project(store, name):
    return _archive().archive_project(store, name)


def restore_project(store, name):
    return _archive().restore_project(store, name)


def list_archived_projects(store):
    return _archive().list_archived_projects(store)


class FakeStore:
    """In-memory ProjectStore -- no Drive, no filesystem."""

    def __init__(self, projects=()):
        self.projects = list(projects)
        self.archived = []

    def list(self):
        return list(self.projects)

    def list_archived(self):
        return list(self.archived)

    def is_archived(self, name):
        return any(p.name == name for p in self.archived)

    def create(self, name):
        # A name the archive holds is taken too (madde 223): without this the project that owns it
        # has no way back, because the archived card offers the way back and nothing else.
        if any(p.name == name for p in self.projects) or self.is_archived(name):
            return None
        project = Project(name, 100.0)
        self.projects.append(project)
        return project

    def rename(self, old, new):
        """The renamed project, None when the new name is taken, False when the old one is gone."""
        if any(p.name == new for p in self.projects) or self.is_archived(new):
            return None
        found = next((p for p in self.projects if p.name == old), None)
        if found is None:
            return False
        self.projects = [Project(new, p.modified_at) if p.name == old else p
                         for p in self.projects]
        return next(p for p in self.projects if p.name == new)


class RecordingStore(FakeStore):
    """A store that writes down when it was asked to delete or archive, so order can be asserted."""

    def __init__(self, log, projects=("düğün",), archived=()):
        super().__init__([Project(name, 100.0) for name in projects])
        self.log = log
        self.archived = [Project(name, 100.0) for name in archived]

    def delete(self, name):
        self.log.append(f"delete:{name}")
        gone = [p for p in self.projects if p.name == name]
        self.projects = [p for p in self.projects if p.name != name]
        return bool(gone)

    def archive(self, name):
        """The marked project, or False when there is no such project. Nothing can collide any more
        (madde 227): the mark says which list the project is drawn in, and the project itself does
        not go anywhere."""
        self.log.append(f"archive:{name}")
        found = next((p for p in self.projects if p.name == name), None)
        if found is None:
            return False
        self.projects = [p for p in self.projects if p.name != name]
        self.archived.append(found)
        return found

    def restore(self, name):
        self.log.append(f"restore:{name}")
        found = next((p for p in self.archived if p.name == name), None)
        if found is None:
            return False
        self.archived = [p for p in self.archived if p.name != name]
        self.projects.append(found)
        return found


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


def test_archiving_a_project_leaves_its_production_alone():
    """Madde 227. Halting was the moving archive's debt: a worker writing into a folder on its way
    somewhere else left half a project here and half there. Nothing moves now, and the project is
    meant to go on working -- so there is nothing to stop, and no port to stop it with."""
    log = []
    store = RecordingStore(log)

    archive_project(store, "düğün")

    assert log == ["archive:düğün"]


def test_archiving_something_that_is_not_there_says_so():
    with pytest.raises(ProjectMissing) as exc:
        archive_project(RecordingStore([]), "yok")
    assert str(exc.value) == "Proje yok: yok"


def test_restoring_something_the_archive_does_not_hold():
    with pytest.raises(ProjectMissing) as exc:
        restore_project(RecordingStore([], projects=()), "yok")
    assert str(exc.value) == "Proje yok: yok"


def test_creating_onto_a_name_the_archive_holds_is_refused():
    """Madde 223, and what the user hit: the name went to a new project, and the archived one could
    never come back out."""
    store = RecordingStore([], projects=(), archived=("düğün",))

    with pytest.raises(NameTaken):
        create_project(store, "düğün")

    assert [p.name for p in store.list()] == []


def test_the_refusal_says_the_name_is_in_the_archive():
    """Not the usual sentence: someone reading "bu ad zaten kullanılıyor" would go looking for it
    among their projects, where it is not."""
    store = RecordingStore([], projects=(), archived=("düğün",))

    with pytest.raises(NameTaken) as exc:
        create_project(store, "düğün")

    assert "arşiv" in str(exc.value).lower()
    assert "düğün" in str(exc.value)


def test_renaming_onto_a_name_the_archive_holds_says_the_same_thing():
    """One situation, one sentence -- the rule rename already follows for a name a project holds."""
    store = RecordingStore([], projects=("nikah",), archived=("düğün",))

    with pytest.raises(NameTaken) as renaming_says:
        rename_project(store, straight, "nikah", "düğün")
    with pytest.raises(NameTaken) as creating_says:
        create_project(store, "düğün")

    assert str(renaming_says.value) == str(creating_says.value)


def test_a_name_a_live_project_holds_keeps_the_sentence_it_had():
    """The new sentence belongs to the archive alone: sending someone to the archive over a name
    that is sitting on their own screen would read worse than the old wording."""
    store = RecordingStore([], projects=("düğün",), archived=())

    with pytest.raises(NameTaken) as exc:
        create_project(store, "düğün")

    assert str(exc.value) == "Bu ad zaten kullanılıyor. Başka bir ad dene."


def test_restoring_puts_it_back_among_the_projects():
    store = RecordingStore([], projects=(), archived=("düğün",))

    restore_project(store, "düğün")

    assert [p.name for p in store.list()] == ["düğün"]
    assert store.archived == []


def test_the_archive_list_is_newest_change_first_too():
    """One screen, one order: the archive is read with the same use case the projects are."""
    store = FakeStore()
    store.archived = [Project("eski", 100.0), Project("yeni", 300.0)]

    assert [p.name for p in list_archived_projects(store)] == ["yeni", "eski"]


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
    save_settings(store, "düğün", '["a"]', "neg", 4, "nova3dcg", "slime")
    assert store.saved["düğün"] == {"prompts": '["a"]', "negative": "neg", "variants": 4,
                                    "model": "nova3dcg", "lora": "slime"}


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
