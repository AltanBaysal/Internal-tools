import os
from functools import partial

from backend.features.projects.data.project_store import DriveProjectStore
from backend.features.projects.domain.usecases.create_project import create_project
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.presentation.routes import make_projects_blueprint
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app


def client_for(drive_root, dist_dir):
    """Wire the feature by hand -- the same wiring main.py does, but over a temp folder."""
    store = DriveProjectStore(DriveStorage(str(drive_root)))
    blueprint = make_projects_blueprint(
        list_projects=partial(list_projects, store),
        create_project=partial(create_project, store),
    )
    return create_app(dist_dir=str(dist_dir), blueprints=[blueprint]).test_client()


def make_client(tmp_path):
    drive = tmp_path / "drive"
    drive.mkdir()
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    return client_for(drive, dist), drive


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
