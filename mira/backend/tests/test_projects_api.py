from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app


def _client(tmp_path):
    store = Store(str(tmp_path))
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(make_workspace_bp(FileProjectStore(store), FileChatStore(store)),),
    )
    return app.test_client()


def test_empty_root_returns_an_empty_list(tmp_path):
    resp = _client(tmp_path).get("/api/projects")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_created_project_appears_in_the_list(tmp_path):
    client = _client(tmp_path)
    created = client.post("/api/projects")
    assert created.status_code == 201
    body = created.get_json()
    assert body["name"] == "New project"
    assert body["id"].startswith("p")
    assert client.get("/api/projects").get_json() == [body]


def test_projects_survive_a_fresh_app(tmp_path):
    _client(tmp_path).post("/api/projects")
    assert len(_client(tmp_path).get("/api/projects").get_json()) == 1


def test_project_payload_carries_zero_counts_before_anything_exists(tmp_path):
    body = _client(tmp_path).post("/api/projects").get_json()
    assert body["chats"] == 0
    assert body["files"] == 0


def test_two_projects_get_different_ids_and_hues(tmp_path):
    client = _client(tmp_path)
    first = client.post("/api/projects").get_json()
    second = client.post("/api/projects").get_json()
    assert first["id"] != second["id"]
    assert first["hue"] != second["hue"]


def test_patch_renames_a_project(tmp_path):
    client = _client(tmp_path)
    created = client.post("/api/projects").get_json()
    resp = client.patch(f"/api/projects/{created['id']}", json={"name": "Thesis"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Thesis"
    assert client.get("/api/projects").get_json()[0]["name"] == "Thesis"


def test_patch_rejects_an_empty_name(tmp_path):
    client = _client(tmp_path)
    created = client.post("/api/projects").get_json()
    assert client.patch(f"/api/projects/{created['id']}", json={"name": "  "}).status_code == 400


def test_patch_on_an_unknown_project_is_404(tmp_path):
    assert _client(tmp_path).patch("/api/projects/nope", json={"name": "x"}).status_code == 404


def test_patch_keeps_the_counts_in_the_answer(tmp_path):
    client = _client(tmp_path)
    created = client.post("/api/projects").get_json()
    body = client.patch(f"/api/projects/{created['id']}", json={"desc": "Notes."}).get_json()
    assert body["chats"] == 0
    assert body["files"] == 0
