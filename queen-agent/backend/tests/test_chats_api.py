import json

import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.data.memory_stops import MemoryStops
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app


class FakeEngine:
    """No network in a test: the answer is whatever this says it is."""

    def __init__(self, answer="Done.", blow_up=None):
        self.answer = answer
        self.blow_up = blow_up
        self.seen = None

    def complete(self, messages, tools=None):
        if self.blow_up:
            raise RuntimeError(self.blow_up)
        return {"role": "assistant", "content": self.answer}

    # No model since Madde 82: there is one, and the client is built knowing it. A caller that
    # still passed one would die here rather than quietly working.
    def stream(self, messages, tools=None):
        if self.blow_up:
            raise RuntimeError(self.blow_up)
        self.seen = [dict(message) for message in messages]
        yield {"text": self.answer}


class ScriptedEngine:
    """An engine whose rounds are written out, so a turn can call tools and never speak.

    FakeEngine answers in one piece and cannot reach for a tool, and a silent turn is exactly the
    shape it cannot make. Kept here rather than shared with the use case's tests: a test that
    imports another test's fixture makes the two move together for no reason.
    """

    def __init__(self, rounds):
        self.rounds = list(rounds)

    def stream(self, messages, tools=None):
        pieces = self.rounds.pop(0) if self.rounds else []
        for piece in pieces:
            yield piece


def _tool_call(tool, **arguments):
    return {"id": "t1", "function": {"name": tool, "arguments": json.dumps(arguments)}}


def _client(tmp_path, engine=None):
    # A fresh registry per client, like the stores: one test's stop must not reach another's answer.
    store = Store(str(tmp_path))
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                FileProjectStore(store),
                FileChatStore(store),
                FileFileStore(store),
                engine or FakeEngine(),
                MemoryStops(),
            ),
        ),
    )
    return app.test_client()


def _project(client):
    return client.post("/api/projects").get_json()["id"]


def _started(client, text="hello"):
    # Every chat is born inside a project now, so both ids come back together.
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": text}).get_json()["id"]
    return pid, cid


def test_the_one_door_creates_a_chat_when_none_is_named(tmp_path):
    # Madde 87: one address for every sentence a user says. No chat in the body means there is no
    # chat yet, so the server makes one -- a chat is still born with its first message.
    client = _client(tmp_path)
    pid = _project(client)
    resp = client.post(f"/api/projects/{pid}/messages", json={"text": "Write the intro"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "Write the intro"
    assert body["id"].startswith("c")
    assert [(m["role"], m["text"]) for m in body["messages"]] == [("user", "Write the intro")]


def test_the_one_door_appends_when_a_chat_is_named(tmp_path):
    # The same address, and the only difference is one field in the body.
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": "Write the intro"}).get_json()[
        "id"
    ]
    resp = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "and more"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert [m["text"] for m in body["messages"]] == ["Write the intro", "and more"]
    # The title belongs to the message that started the chat and never moves.
    assert body["title"] == "Write the intro"


def test_the_old_creating_door_is_gone(tmp_path):
    # That address is a list of chats and answers GET, so Flask's answer is not 404 -- it is that
    # this address does not know this method. The rule table is what says the door went; a status
    # code alone cannot, because the SPA fallback answers GET for every path there is.
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/chats", json={"text": "hi"}).status_code == 405


def test_the_old_appending_door_is_gone(tmp_path):
    # 405 rather than 404, and for the same reason the creating door gives one: the SPA fallback
    # claims every path for GET, so an address with no rule of its own still exists -- it just does
    # not know POST.
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": "hi"}).get_json()["id"]
    sent = client.post(f"/api/projects/{pid}/chats/{cid}/messages", json={"text": "more"})
    assert sent.status_code == 405


def test_a_chat_that_is_not_there_is_404_and_nothing_is_created(tmp_path):
    # Empty means there is no chat yet. A name that is simply wrong is not the same thing, and
    # creating one here would turn a typo into a second chat nobody asked for.
    client = _client(tmp_path)
    pid = _project(client)
    sent = client.post(f"/api/projects/{pid}/messages", json={"chat": "nope", "text": "hi"})
    assert sent.status_code == 404
    assert client.get(f"/api/projects/{pid}/chats").get_json() == []


def test_an_empty_message_is_refused(tmp_path):
    # Both ways in: with nothing to append to, and with a chat waiting for it.
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/messages", json={"text": "   "}).status_code == 400
    assert client.get(f"/api/projects/{pid}/chats").get_json() == []
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": "hi"}).get_json()["id"]
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": " "})
    assert refused.status_code == 400


def test_an_unknown_project_is_404(tmp_path):
    assert (
        _client(tmp_path).post("/api/projects/nope/messages", json={"text": "hi"}).status_code == 404
    )


def test_the_chat_rename_use_case_is_gone():
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.rename_chat  # noqa: F401


def test_the_start_chat_use_case_is_gone():
    # append_message took creating over: one rule for a message arriving, whether or not there is a
    # chat to put it in. The same shape as the rename use case that went before it.
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.start_chat  # noqa: F401




def test_a_chat_can_be_deleted_and_stops_being_listed(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": "hi"}).get_json()["id"]
    assert client.delete(f"/api/projects/{pid}/chats/{cid}").status_code == 200
    assert client.get(f"/api/projects/{pid}/chats").get_json() == []
    assert client.get(f"/api/projects/{pid}/chats/{cid}").status_code == 404


def test_deleting_a_chat_leaves_the_project_its_files(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": "hi"}).get_json()["id"]
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
    client.post(f"/api/projects/{pid}/messages", json={"text": "first"})
    client.post(f"/api/projects/{pid}/messages", json={"text": "second"})
    listed = client.get(f"/api/projects/{pid}/chats").get_json()
    assert [row["title"] for row in listed] == ["second", "first"]
    # The list screen does not draw messages, so sending them would be for nothing.
    assert all("messages" not in row for row in listed)


def test_one_chat_carries_its_messages(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": "hello"}).get_json()["id"]
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


def test_a_projects_chats_come_back_newest_first(tmp_path):
    # The sidebar and the project screen read this one list; there is no wider one to read.
    client = _client(tmp_path)
    pid = _project(client)
    client.post(f"/api/projects/{pid}/messages", json={"text": "older"})
    client.post(f"/api/projects/{pid}/messages", json={"text": "newer"})
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


def _silent_with_a_file():
    return ScriptedEngine([[{"tool_calls": [_tool_call("create_file", name="plan.md", content="x")]}], []])


def test_a_call_travels_as_its_own_event(tmp_path):
    # Madde 66: the line has to arrive while the answer is still running, not only with the record.
    client = _client(tmp_path, engine=ScriptedEngine([[{"tool_calls": [_tool_call("list_files")]}], [{"text": "none"}]]))
    pid, cid = _started(client)
    body = client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data(as_text=True)
    assert "event: call" in body
    assert '"tool": "list_files"' in body
    assert body.index("event: call") < body.index("event: done")


def test_the_stored_chat_hands_back_the_calls(tmp_path):
    client = _client(
        tmp_path,
        engine=ScriptedEngine(
            [
                [{"tool_calls": [_tool_call("create_file", name="plan.md", content="x")]}],
                [{"text": "Saved."}],
            ]
        ),
    )
    pid, cid = _started(client)
    # Read rather than fired: the answer is written by the generator, and nothing runs until the
    # body is consumed.
    client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data(as_text=True)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    # Every field, always present -- the browser draws what it is handed, and an absent one would
    # make each reader check before drawing. Madde 78 adds the third.
    assert kept["messages"][-1]["calls"] == [
        {"tool": "create_file", "target": "plan.md", "outcome": "Saved"}
    ]


def test_a_running_answer_can_be_asked_to_stop(tmp_path):
    # Madde 67. The request arrives on its own connection while the answer is still streaming --
    # which it can, because the server handles requests concurrently.
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert client.post(f"/api/projects/{pid}/chats/{cid}/stop").status_code == 200


def test_stopping_a_chat_that_is_not_there_is_a_404(tmp_path):
    client = _client(tmp_path)
    pid, _ = _started(client)
    assert client.post(f"/api/projects/{pid}/chats/nope/stop").status_code == 404


def test_the_stored_chat_says_which_answer_was_stopped(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data(as_text=True)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    # This one ran to the end, so the field is there and it is false -- the browser draws from what
    # it is handed and should not have to check whether a field exists.
    assert kept["messages"][-1]["stopped"] is False


def test_the_stored_chat_says_what_the_answer_spent(tmp_path):
    engine = ScriptedEngine(
        [[{"text": "Done."}, {"usage": {"sent": 12400, "cached": 9100, "answered": 842}}]]
    )
    client = _client(tmp_path, engine=engine)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data(as_text=True)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert kept["messages"][-1]["usage"] == {"sent": 12400, "cached": 9100, "answered": 842}


def test_an_unmeasured_answer_still_carries_the_field(tmp_path):
    # Always present, unlike on disk: the browser draws from what it is handed, and an absent field
    # would make every reader check for it first.
    client = _client(tmp_path)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data(as_text=True)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert kept["messages"][-1]["usage"] == {"sent": 0, "cached": 0, "answered": 0}


def test_a_silent_turn_that_made_a_file_closes_the_stream_cleanly(tmp_path):
    # What the user reported as a network error: the model worked without speaking and the stream
    # broke instead of ending.
    client = _client(tmp_path, engine=_silent_with_a_file())
    pid, cid = _started(client)
    body = client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data(as_text=True)
    assert "event: file" in body
    assert "event: done" in body
    assert "event: error" not in body


def test_the_record_keeps_the_silent_answer(tmp_path):
    client = _client(tmp_path, engine=_silent_with_a_file())
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data()
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    assert [m["text"] for m in kept] == ["hello", ""]
    assert kept[-1]["files"] == ["plan.md"]


def test_a_turn_that_produced_nothing_says_so_inside_the_stream(tmp_path):
    # Neither a word nor a file, so there is no answer -- and saying so is the server's job, not
    # the browser's guess about the connection.
    client = _client(tmp_path, engine=ScriptedEngine([[]]))
    pid, cid = _started(client)
    body = client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data(as_text=True)
    assert "event: error" in body
    assert "The model returned nothing." in body


def test_a_turn_that_produced_nothing_writes_nothing(tmp_path):
    client = _client(tmp_path, engine=ScriptedEngine([[]]))
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data()
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    assert [m["text"] for m in kept] == ["hello"]


def test_answering_an_unknown_chat_is_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/chats/nope/answer").status_code == 404


def test_a_new_chat_shows_up_in_the_project_count(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    client.post(f"/api/projects/{pid}/messages", json={"text": "hello"})
    assert client.get("/api/projects").get_json()[0]["chats"] == 1


# --- one model, and nothing on a chat says which (Madde 82) --------------------------------------


def test_the_model_endpoint_is_gone(tmp_path):
    # One model, so there is nothing to ask about. Flask answers a route nobody registered, and
    # that answer is the test.
    assert _client(tmp_path).get("/api/model").status_code == 404


def test_a_chat_carries_no_model(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert "model" not in client.get(f"/api/projects/{pid}/chats/{cid}").get_json()


def test_a_chat_cannot_be_patched(tmp_path):
    # Madde 86 took the route out: a chat carries nothing that changes. The address still answers
    # GET, so Flask's answer is not 404 -- it is that this address does not know this method.
    #
    # This is also where renaming a chat is refused, which used to need a test of its own: while
    # PATCH existed the refusal had to be about the body it did not understand. Now the method is
    # simply absent, and one answer covers both.
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert client.patch(f"/api/projects/{pid}/chats/{cid}", json={"skill": "verify"}).status_code == 405
    assert client.patch(f"/api/projects/{pid}/chats/{cid}", json={"title": "Else"}).status_code == 405
    assert client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["title"] == "hello"


def test_the_engine_is_asked_without_a_model(tmp_path):
    # There is one model and the wiring names it once, in config.py. Nothing on the way to the
    # engine gets to say otherwise -- FakeEngine.stream refuses one, so a route that passed a model
    # would die here rather than quietly working.
    engine = FakeEngine()
    client = _client(tmp_path, engine=engine)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/answer").get_data()
    assert engine.seen is not None


def test_a_chat_carries_no_skill(tmp_path):
    # Madde 86: the field is gone from the record, so it is gone from the wire too. What the skill
    # was sent with keeps it -- that is the message, not the chat.
    client = _client(tmp_path)
    pid = _project(client)
    born = client.post(
        f"/api/projects/{pid}/messages", json={"text": "hello", "skill": "create-scenario"}
    ).get_json()
    assert "skill" not in born
    assert born["messages"][0]["skill"] == "create-scenario"


def test_a_message_carries_the_skill_it_was_sent_with(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    chat = client.post(
        f"/api/projects/{pid}/messages", json={"chat": cid, "text": "more", "skill": "verify"}
    ).get_json()
    assert [m["skill"] for m in chat["messages"]] == ["", "verify"]


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
        f"/api/projects/{opid}/messages", json={"text": "hello", "skill": "create-scenario"}
    ).get_json()["id"]
    other.post(f"/api/projects/{opid}/chats/{ocid}/answer").get_data()

    assert not [piece for piece in plain.seen if piece["role"] == "system"]
    assert with_skill.seen[0] == {
        "role": "system",
        "content": instruction_for("create-scenario"),
    }
