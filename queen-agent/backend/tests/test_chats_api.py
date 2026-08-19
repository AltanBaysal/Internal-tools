import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app


class FakeEngine:
    """No network in a test: the answer is whatever this says it is."""

    def __init__(self, answer="Done.", blow_up=None):
        self.answer = answer
        self.blow_up = blow_up
        self.asked_for = "not asked"
        self.seen = None

    def complete(self, messages, tools=None):
        if self.blow_up:
            raise RuntimeError(self.blow_up)
        return {"role": "assistant", "content": self.answer}

    def stream(self, messages, tools=None, model=None):
        if self.blow_up:
            raise RuntimeError(self.blow_up)
        self.asked_for = model
        self.seen = [dict(message) for message in messages]
        yield {"text": self.answer}


def _client(tmp_path, engine=None, default_model="grok-4.5"):
    store = Store(str(tmp_path))
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                FileProjectStore(store),
                FileChatStore(store),
                FileFileStore(store),
                engine or FakeEngine(),
                default_model,
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


def test_a_chat_cannot_be_renamed(tmp_path):
    # Renaming lives on the project alone. PATCH exists now -- it is how the model and the skill are
    # changed -- so the refusal has to be in what it understands rather than in the method being
    # absent.
    client = _client(tmp_path)
    pid, cid = _started(client)
    resp = client.patch(f"/api/projects/{pid}/chats/{cid}", json={"title": "Something else"})
    assert resp.status_code == 400
    assert client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["title"] == "hello"


def test_the_chat_rename_use_case_is_gone():
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.rename_chat  # noqa: F401




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


def test_there_is_no_workspace_wide_chat_address(tmp_path):
    # A chat needs a project to live in, and Recent chats now lists that project's own chats, so
    # the workspace has no rule for this path at all. The status is 405 rather than 404 because the
    # SPA fallback still claims every GET; the rule table is what actually says it is gone.
    client = _client(tmp_path)
    assert client.post("/api/chats", json={"text": "Write the intro"}).status_code == 405
    rules = {rule.rule for rule in client.application.url_map.iter_rules()}
    assert "/api/chats" not in rules
    assert client.get("/api/projects").get_json() == []


def test_the_chat_store_offers_no_workspace_wide_listing(tmp_path):
    # Every chat is asked for through its project now, so the port shrank with the use case.
    store = FileChatStore(Store(str(tmp_path)))
    assert not hasattr(store, "list_all")


def test_the_recent_chats_use_case_is_gone():
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.list_recent_chats  # noqa: F401


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


def test_a_projects_chats_come_back_newest_first(tmp_path):
    # The sidebar and the project screen read this one list; there is no wider one to read.
    client = _client(tmp_path)
    pid = _project(client)
    client.post(f"/api/projects/{pid}/chats", json={"text": "older"})
    client.post(f"/api/projects/{pid}/chats", json={"text": "newer"})
    listed = client.get(f"/api/projects/{pid}/chats").get_json()
    assert [row["title"] for row in listed] == ["newer", "older"]


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


def test_a_chat_is_born_with_the_model_it_was_sent(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    born = client.post(
        f"/api/projects/{pid}/chats", json={"text": "hello", "model": "grok-4.3"}
    ).get_json()
    assert born["model"] == "grok-4.3"


def test_a_chat_that_picked_nothing_answers_with_the_default(tmp_path):
    # Resolved on the way out: the client always has a name to draw, and the record on disk is
    # still free to follow the setting.
    client = _client(tmp_path, default_model="grok-4.5")
    pid, cid = _started(client)
    assert client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["model"] == "grok-4.5"


def test_the_model_can_be_changed_mid_conversation(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    changed = client.patch(f"/api/projects/{pid}/chats/{cid}", json={"model": "grok-build-0.1"})
    assert changed.status_code == 200
    assert changed.get_json()["model"] == "grok-build-0.1"
    # And it stays: the next reader sees the pick, not the default.
    assert client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["model"] == "grok-build-0.1"


def test_changing_the_model_of_a_chat_that_is_not_there_is_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    assert client.patch(f"/api/projects/{pid}/chats/nope", json={"model": "grok-4.3"}).status_code == 404


def test_the_answer_is_asked_for_with_the_chats_own_model(tmp_path):
    engine = FakeEngine()
    client = _client(tmp_path, engine=engine)
    pid, cid = _started(client)
    client.patch(f"/api/projects/{pid}/chats/{cid}", json={"model": "grok-4.3"})
    client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data()
    assert engine.asked_for == "grok-4.3"


def test_a_chat_that_picked_nothing_lets_the_engine_decide(tmp_path):
    engine = FakeEngine()
    client = _client(tmp_path, engine=engine)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data()
    assert engine.asked_for is None


def test_a_chat_is_born_with_the_skill_it_was_sent(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    born = client.post(
        f"/api/projects/{pid}/chats", json={"text": "hello", "skill": "create-scenario"}
    ).get_json()
    assert born["skill"] == "create-scenario"
    assert born["messages"][0]["skill"] == "create-scenario"


def test_a_message_carries_the_skill_it_was_sent_with(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    chat = client.post(
        f"/api/projects/{pid}/chats/{cid}/messages", json={"text": "more", "skill": "verify"}
    ).get_json()
    assert [m["skill"] for m in chat["messages"]] == ["", "verify"]


def test_the_skill_can_be_changed_and_cleared(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    chosen = client.patch(f"/api/projects/{pid}/chats/{cid}", json={"skill": "verify"})
    assert chosen.get_json()["skill"] == "verify"
    # Pressing the selected one again clears it -- a skill may be absent, a model may not.
    cleared = client.patch(f"/api/projects/{pid}/chats/{cid}", json={"skill": ""})
    assert cleared.get_json()["skill"] == ""


def test_changing_one_choice_leaves_the_other_alone(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    client.patch(f"/api/projects/{pid}/chats/{cid}", json={"model": "grok-4.3"})
    changed = client.patch(f"/api/projects/{pid}/chats/{cid}", json={"skill": "verify"}).get_json()
    assert changed["model"] == "grok-4.3"
    assert changed["skill"] == "verify"


def test_a_selected_skill_reaches_the_engine_as_an_instruction(tmp_path):
    # Madde 27 proved the opposite here -- the choice was recorded and nothing read it. Madde 29
    # lifts that boundary, so the proof moves rather than disappearing: the road from the composer
    # to the engine is one road, and this is where it is checked end to end.
    plain, with_skill = FakeEngine(), FakeEngine()
    client = _client(tmp_path, engine=plain)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data()

    other = _client(tmp_path / "second", engine=with_skill)
    opid = _project(other)
    ocid = other.post(
        f"/api/projects/{opid}/chats", json={"text": "hello", "skill": "create-scenario"}
    ).get_json()["id"]
    other.post(f"/api/projects/{opid}/chats/{ocid}/answer").get_data()

    assert not [piece for piece in plain.seen if piece["role"] == "system"]
    assert with_skill.seen[0] == {
        "role": "system",
        "content": instruction_for("create-scenario"),
    }
