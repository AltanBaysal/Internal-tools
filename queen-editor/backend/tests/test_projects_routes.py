import os
from functools import partial

from backend.features.projects.data.project_store import DriveProjectStore
from backend.features.projects.data.settings_store import DriveSettingsStore
from backend.features.projects.domain import name_rules
from backend.features.projects.domain.usecases.check_name import check_name
from backend.features.projects.domain.usecases.create_project import create_project
from backend.features.projects.domain.usecases.delete_project import delete_project
from backend.features.projects.domain.usecases.get_settings import get_settings
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.domain.usecases.save_settings import save_settings
from backend.features.projects.presentation.routes import make_projects_blueprint
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app


def client_for(drive_root, dist_dir, halted=None):
    """Wire the feature by hand -- the same wiring main.py does, but over a temp folder.

    The halt port stands in for the photo worker: this feature never knows what is behind it, so a
    list that writes down the name is the whole of it here.
    """
    storage = DriveStorage(str(drive_root))
    store = DriveProjectStore(storage)
    settings_store = DriveSettingsStore(storage)
    blueprint = make_projects_blueprint(
        list_projects=partial(list_projects, store),
        create_project=partial(create_project, store),
        check_name=check_name,
        delete_project=partial(delete_project, store,
                               lambda project: (halted if halted is not None else []).append(
                                   project)),
        get_settings=partial(get_settings, settings_store),
        save_settings=partial(save_settings, settings_store),
    )
    return create_app(dist_dir=str(dist_dir), blueprints=[blueprint]).test_client()


def make_client(tmp_path, halted=None):
    drive = tmp_path / "drive"
    drive.mkdir()
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    return client_for(drive, dist, halted), drive


def test_deleting_a_project_removes_the_folder_with_everything_in_it(tmp_path):
    client, drive = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    (drive / "düğün" / "0_a.png").write_bytes(b"PNG")

    resp = client.delete("/api/projects/düğün")

    assert resp.status_code == 204
    assert not (drive / "düğün").exists()
    assert client.get("/api/projects").get_json()["projects"] == []


def test_deleting_a_project_asks_for_its_production_to_stop(tmp_path):
    halted = []
    client, _ = make_client(tmp_path, halted)
    client.post("/api/projects", json={"name": "düğün"})

    client.delete("/api/projects/düğün")

    assert halted == ["düğün"]


def test_deleting_an_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.delete("/api/projects/yok").status_code == 404


def test_a_usable_name_checks_out_clean(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.get("/api/projects/name-check?name=kapak çekimi")
    assert resp.status_code == 200
    assert resp.get_json() == {"error": None}


def test_the_check_answers_with_the_rules_own_sentence(tmp_path):
    client, _ = make_client(tmp_path)
    # Not a second wording of the rule: whatever name_rules says is what the box prints.
    assert client.get("/api/projects/name-check?name=a:b").get_json()["error"] == (
        name_rules.validate("a:b"))
    assert client.get("/api/projects/name-check?name=").get_json()["error"] == (
        name_rules.validate(""))


def test_checking_a_name_creates_nothing(tmp_path):
    client, drive = make_client(tmp_path)
    client.get("/api/projects/name-check?name=düğün")
    assert client.get("/api/projects").get_json()["projects"] == []
    assert not (drive / "düğün").exists()


def test_get_projects_empty(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    assert resp.get_json() == {"projects": []}


def test_post_creates_folder_and_returns_201(tmp_path):
    client, drive = make_client(tmp_path)
    resp = client.post("/api/projects", json={"name": "kapak çekimi"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "kapak çekimi"
    assert isinstance(body["modifiedAt"], int)
    assert (drive / "kapak çekimi").is_dir()


def test_get_projects_newest_change_first(tmp_path):
    client, drive = make_client(tmp_path)
    client.post("/api/projects", json={"name": "eski"})
    client.post("/api/projects", json={"name": "yeni"})
    os.utime(drive / "eski", (1000, 1000))
    os.utime(drive / "yeni", (2000, 2000))
    names = [p["name"] for p in client.get("/api/projects").get_json()["projects"]]
    assert names == ["yeni", "eski"]


def test_post_invalid_name_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post("/api/projects", json={"name": "foto/deneme"})
    assert resp.status_code == 400
    assert "kullanılamaz" in resp.get_json()["error"]


def test_post_duplicate_name_returns_409(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    resp = client.post("/api/projects", json={"name": "düğün"})
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Bu ad zaten kullanılıyor. Başka bir ad dene."


def test_post_without_name_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post("/api/projects", json={})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Proje adı boş olamaz."


def test_get_projects_reports_the_real_error_when_root_missing(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    client = client_for(tmp_path / "olmayan-kok", dist)
    resp = client.get("/api/projects")
    assert resp.status_code == 500
    assert "olmayan-kok" in resp.get_json()["error"]


def test_health_still_works(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/health").get_json() == {"status": "ok"}


def test_settings_start_empty_for_a_new_project(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    assert client.get("/api/projects/düğün/settings").get_json() == {
        "prompts": "", "negative": "", "variants": None, "model": ""}


def test_settings_survive_a_put_and_come_back(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    resp = client.put("/api/projects/düğün/settings",
                      json={"prompts": '["a"]', "negative": "neg", "variants": 4,
                            "model": "nova.safetensors"})
    assert resp.status_code == 204
    assert client.get("/api/projects/düğün/settings").get_json() == {
        "prompts": '["a"]', "negative": "neg", "variants": 4, "model": "nova.safetensors"}


def test_settings_of_an_unknown_project_return_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/settings").status_code == 404
    assert client.put("/api/projects/yok/settings", json={"prompts": "x"}).status_code == 404


def test_putting_settings_never_creates_a_project(tmp_path):
    # Every folder under the root is a project: a settings write to an unknown name must not
    # conjure one.
    client, drive = make_client(tmp_path)
    client.put("/api/projects/yok/settings", json={"prompts": "x"})
    assert not (drive / "yok").exists()
    assert client.get("/api/projects").get_json() == {"projects": []}


def test_settings_of_the_wrong_type_are_coerced(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    client.put("/api/projects/düğün/settings",
               json={"prompts": 5, "negative": None, "variants": "4", "model": 7})
    assert client.get("/api/projects/düğün/settings").get_json() == {
        "prompts": "", "negative": "", "variants": None, "model": ""}
