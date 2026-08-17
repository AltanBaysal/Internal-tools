from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app


class FakeEngine:
    def stream(self, messages, tools=None):
        yield {"text": "Done."}


def _client(tmp_path):
    store = Store(str(tmp_path))
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                FileProjectStore(store),
                FileChatStore(store),
                FileFileStore(store),
                FakeEngine(),
            ),
        ),
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


def test_two_projects_get_different_ids(tmp_path):
    # The id is all that tells them apart now: two projects are told apart by name, not by colour.
    client = _client(tmp_path)
    first = client.post("/api/projects").get_json()
    second = client.post("/api/projects").get_json()
    assert first["id"] != second["id"]


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
    body = client.patch(f"/api/projects/{created['id']}", json={"name": "Thesis"}).get_json()
    assert body["chats"] == 0
    assert body["files"] == 0


def test_a_description_in_the_body_is_simply_not_a_field(tmp_path):
    # PATCH sends what changed; a key the project has no room for is not an error, it is nothing.
    client = _client(tmp_path)
    created = client.post("/api/projects").get_json()
    resp = client.patch(f"/api/projects/{created['id']}", json={"desc": "Notes."})
    assert resp.status_code == 200
    assert "desc" not in resp.get_json()


def test_the_answer_carries_neither_a_description_nor_a_colour(tmp_path):
    created = _client(tmp_path).post("/api/projects").get_json()
    assert set(created) == {"id", "name", "createdAt", "chats", "files"}


def test_a_project_can_be_deleted(tmp_path):
    client = _client(tmp_path)
    created = client.post("/api/projects").get_json()
    resp = client.delete(f"/api/projects/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["trashed"] == created["id"]
    assert client.get("/api/projects").get_json() == []


def test_deleting_a_project_that_is_not_there_says_so(tmp_path):
    resp = _client(tmp_path).delete("/api/projects/nope")
    assert resp.status_code == 404
    assert "not found" in resp.get_json()["error"]


def test_there_is_no_way_to_bring_a_project_back(tmp_path):
    # Undo is gone (karar 16): the confirmation is what protects the user, and the disk keeps the
    # directory. The rule table is what proves no such address exists. The file's own restore is
    # still here -- that one goes in Madde 19.
    client = _client(tmp_path)
    addresses = [str(rule) for rule in client.application.url_map.iter_rules()]
    assert "/api/projects/<project_id>/restore" not in addresses
    assert not [address for address in addresses if address.startswith("/api/trash")]
