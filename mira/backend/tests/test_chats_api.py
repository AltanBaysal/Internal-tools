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


def _project(client):
    return client.post("/api/projects").get_json()["id"]


def test_a_chat_is_created_with_its_first_message(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    resp = client.post(f"/api/projects/{pid}/chats", json={"text": "Write the intro"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "Write the intro"
    assert body["id"].startswith("c")
    assert [(m["role"], m["text"]) for m in body["messages"]] == [("user", "Write the intro")]


def test_an_empty_message_is_refused(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/chats", json={"text": "   "}).status_code == 400
    assert client.get(f"/api/projects/{pid}/chats").get_json() == []


def test_an_unknown_project_is_404(tmp_path):
    client = _client(tmp_path)
    assert client.post("/api/projects/nope/chats", json={"text": "hi"}).status_code == 404


def test_the_list_comes_newest_first_and_carries_no_messages(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    client.post(f"/api/projects/{pid}/chats", json={"text": "first"})
    client.post(f"/api/projects/{pid}/chats", json={"text": "second"})
    listed = client.get(f"/api/projects/{pid}/chats").get_json()
    assert [row["title"] for row in listed] == ["second", "first"]
    # The list screen does not draw messages, so sending them would be for nothing.
    assert all("messages" not in row for row in listed)


def test_one_chat_carries_its_messages(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/chats", json={"text": "hello"}).get_json()["id"]
    body = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert [m["text"] for m in body["messages"]] == ["hello"]


def test_an_unknown_chat_is_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    assert client.get(f"/api/projects/{pid}/chats/nope").status_code == 404


def test_a_new_chat_shows_up_in_the_project_count(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    client.post(f"/api/projects/{pid}/chats", json={"text": "hello"})
    assert client.get("/api/projects").get_json()[0]["chats"] == 1
