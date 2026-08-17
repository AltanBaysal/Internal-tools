import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app


class FakeEngine:
    """No network in a test: the answer is whatever this says it is."""

    def __init__(self, answer="Done.", blow_up=None):
        self.answer = answer
        self.blow_up = blow_up

    def complete(self, messages, tools=None):
        if self.blow_up:
            raise RuntimeError(self.blow_up)
        return {"role": "assistant", "content": self.answer}

    def stream(self, messages, tools=None):
        if self.blow_up:
            raise RuntimeError(self.blow_up)
        yield {"text": self.answer}


def _client(tmp_path, engine=None):
    store = Store(str(tmp_path))
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                FileProjectStore(store),
                FileChatStore(store),
                FileFileStore(store),
                engine or FakeEngine(),
            ),
        ),
    )
    return app.test_client()


def _project(client):
    return client.post("/api/projects").get_json()["id"]


def _started(client, text="hello"):
    # Every chat is born inside a project now, so both ids come back together.
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/chats", json={"text": text}).get_json()["id"]
    return pid, cid


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


def test_a_chat_can_be_renamed_over_http(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/chats", json={"text": "hi"}).get_json()["id"]
    resp = client.patch(f"/api/projects/{pid}/chats/{cid}", json={"title": "The introduction"})
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "The introduction"
    assert client.get(f"/api/projects/{pid}/chats").get_json()[0]["title"] == "The introduction"


def test_an_empty_title_is_refused_over_http(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/chats", json={"text": "hi"}).get_json()["id"]
    assert client.patch(f"/api/projects/{pid}/chats/{cid}", json={"title": " "}).status_code == 400


def test_a_chat_can_be_deleted_and_stops_being_listed(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/chats", json={"text": "hi"}).get_json()["id"]
    assert client.delete(f"/api/projects/{pid}/chats/{cid}").status_code == 200
    assert client.get(f"/api/projects/{pid}/chats").get_json() == []
    assert client.get(f"/api/projects/{pid}/chats/{cid}").status_code == 404


def test_deleting_a_chat_leaves_the_project_its_files(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/chats", json={"text": "hi"}).get_json()["id"]
    FileFileStore(Store(str(tmp_path))).write(pid, "plan.md", "body")
    client.delete(f"/api/projects/{pid}/chats/{cid}")
    # A file belongs to the project; the chat that produced it going away changes nothing.
    assert [f["name"] for f in client.get(f"/api/projects/{pid}/files").get_json()] == ["plan.md"]


def test_deleting_a_chat_that_is_not_there_is_a_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    assert client.delete(f"/api/projects/{pid}/chats/nope").status_code == 404


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


def test_starting_a_chat_from_nowhere_is_gone(tmp_path):
    # A chat needs a project to live in, so there is no address that opens both at once. 405 rather
    # than 404: GET /api/chats still answers there.
    client = _client(tmp_path)
    assert client.post("/api/chats", json={"text": "Write the intro"}).status_code == 405
    assert client.get("/api/projects").get_json() == []


def test_opening_a_project_and_a_chat_together_is_gone():
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.start_chat_in_new_project  # noqa: F401


def test_a_message_is_appended_to_an_existing_chat(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client, "first")
    body = client.post(f"/api/projects/{pid}/chats/{cid}/messages", json={"text": "second"}).get_json()
    assert [m["text"] for m in body["messages"]] == ["first", "second"]


def test_appending_to_an_unknown_chat_is_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    assert (
        client.post(f"/api/projects/{pid}/chats/nope/messages", json={"text": "hi"}).status_code
        == 404
    )


def test_appending_nothing_is_400(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client, "first")
    assert (
        client.post(f"/api/projects/{pid}/chats/{cid}/messages", json={"text": " "}).status_code
        == 400
    )


def test_recent_chats_span_every_project_and_name_theirs(tmp_path):
    client = _client(tmp_path)
    older_pid, _ = _started(client, "older")
    newer_pid, _ = _started(client, "newer")
    recent = client.get("/api/chats").get_json()
    assert [row["title"] for row in recent] == ["newer", "older"]
    assert [row["projectId"] for row in recent] == [newer_pid, older_pid]


def test_the_answer_arrives_as_a_stream_of_events(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    resp = client.post(f"/api/projects/{pid}/chats/{cid}/answer")
    assert resp.mimetype == "text/event-stream"
    body = resp.get_data(as_text=True)
    assert body.index("event: chunk") < body.index("event: done")
    assert '"text": "Done."' in body
    # The record the browser ends up trusting is the one the server wrote.
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert [m["text"] for m in kept["messages"]] == ["hello", "Done."]


def test_a_broken_engine_speaks_inside_the_stream(tmp_path):
    client = _client(tmp_path, engine=FakeEngine(blow_up="401 bad key"))
    pid, cid = _started(client)
    body = client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data(as_text=True)
    # The status code was settled when the first byte left, so the fault travels as an event.
    assert "event: error" in body
    assert "401 bad key" in body
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert [m["text"] for m in kept["messages"]] == ["hello"]


def test_answering_an_unknown_chat_is_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/chats/nope/answer").status_code == 404


def test_a_new_chat_shows_up_in_the_project_count(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    client.post(f"/api/projects/{pid}/chats", json={"text": "hello"})
    assert client.get("/api/projects").get_json()[0]["chats"] == 1
