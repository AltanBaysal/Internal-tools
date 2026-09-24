"""Referanstan's own record: what its boxes open with once the visit's draft is gone (madde 317).

The photo panel's settings.json is written when a photo batch is sent and this one when a reference
production is, so each keeps a file of its own (CODE-STANDARD, Separation of concerns).

The new modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
from functools import partial

import pytest

from backend.features.projects.data.settings_store import DriveSettingsStore
from backend.features.projects.domain.usecases.get_settings import ProjectMissing, get_settings
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

EMPTY = {"prompts": "", "variants": None}
URL = "/api/projects/düğün/reference-settings"


def store_at(path):
    from backend.features.projects.data.reference_settings_store import (
        DriveReferenceSettingsStore,
    )
    return DriveReferenceSettingsStore(DriveStorage(str(path)))


def save(*args):
    from backend.features.projects.domain.usecases.save_reference_settings import (
        save_reference_settings,
    )
    return save_reference_settings(*args)


def test_a_record_never_written_reads_empty(tmp_path):
    (tmp_path / "düğün").mkdir()
    assert store_at(tmp_path).read("düğün") == EMPTY


def test_what_is_written_reads_back_as_it_was_typed(tmp_path):
    # The box reopens looking the way it was left: a parsed list would come back reformatted.
    (tmp_path / "düğün").mkdir()
    store = store_at(tmp_path)
    typed = '[\n  "gotik kız",\n]'
    store.write("düğün", {"prompts": typed, "variants": 3})
    assert store.read("düğün") == {"prompts": typed, "variants": 3}


@pytest.mark.parametrize("raw", ["{ yarım", "[]", '{"prompts": 5, "variants": true}',
                                 '{"prompts": null, "variants": "4"}'])
def test_an_unreadable_record_reads_empty(tmp_path, raw):
    # The record only refills boxes: what cannot be read must not keep the tab from opening.
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "reference_settings.json").write_text(raw, encoding="utf-8")
    assert store_at(tmp_path).read("düğün") == EMPTY


def test_the_record_keeps_a_file_of_its_own(tmp_path):
    (tmp_path / "düğün").mkdir()
    store_at(tmp_path).write("düğün", {"prompts": '["a"]', "variants": 2})
    assert (tmp_path / "düğün" / "reference_settings.json").exists()
    assert not (tmp_path / "düğün" / "settings.json").exists()
    assert DriveSettingsStore(DriveStorage(str(tmp_path))).read("düğün")["prompts"] == ""


class FakeStore:
    def __init__(self):
        self.saved = {}

    def project_exists(self, project):
        return project == "düğün"

    def write(self, project, settings):
        self.saved[project] = settings


def test_saving_stores_what_it_was_given():
    store = FakeStore()
    save(store, "düğün", '["a"]', 3)
    assert store.saved == {"düğün": {"prompts": '["a"]', "variants": 3}}


def test_saving_refuses_a_project_that_is_not_there():
    store = FakeStore()
    with pytest.raises(ProjectMissing) as exc:
        save(store, "yok", '["a"]', 3)
    assert str(exc.value) == "Proje yok: yok"
    assert store.saved == {}


def make_client(tmp_path):
    """The door wired by hand over a temp folder -- the wiring main.py does."""
    from backend.features.projects.data.reference_settings_store import (
        DriveReferenceSettingsStore,
    )
    from backend.features.projects.domain.usecases.save_reference_settings import (
        save_reference_settings,
    )
    from backend.features.projects.presentation.reference_settings_routes import (
        make_reference_settings_blueprint,
    )
    drive = tmp_path / "drive"
    drive.mkdir()
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    store = DriveReferenceSettingsStore(DriveStorage(str(drive)))
    blueprint = make_reference_settings_blueprint(
        get_reference_settings=partial(get_settings, store),
        save_reference_settings=partial(save_reference_settings, store))
    return create_app(dist_dir=str(dist), blueprints=[blueprint]).test_client(), drive


def test_a_new_project_answers_with_an_empty_record(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün").mkdir()
    assert client.get(URL).get_json() == EMPTY


def test_a_record_put_down_comes_back(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün").mkdir()
    resp = client.put(URL, json={"prompts": '["a"]', "variants": 3})
    assert resp.status_code == 204
    assert client.get(URL).get_json() == {"prompts": '["a"]', "variants": 3}


def test_an_unknown_project_is_a_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/reference-settings").status_code == 404
    assert client.put("/api/projects/yok/reference-settings",
                      json={"prompts": "x", "variants": 1}).status_code == 404


def test_a_put_never_creates_a_project(tmp_path):
    # Every folder under the root is a project: a write to an unknown name must not conjure one.
    client, drive = make_client(tmp_path)
    client.put("/api/projects/yok/reference-settings", json={"prompts": "x", "variants": 1})
    assert not (drive / "yok").exists()


@pytest.mark.parametrize("variants", [True, "4", 2.5, None])
def test_fields_of_the_wrong_type_are_stored_empty(tmp_path, variants):
    # bool is an int in Python, and True would silently mean "1 variant".
    client, drive = make_client(tmp_path)
    (drive / "düğün").mkdir()
    client.put(URL, json={"prompts": 5, "variants": variants})
    assert client.get(URL).get_json() == EMPTY
