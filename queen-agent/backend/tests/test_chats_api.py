import json
import threading

import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.data.live_turns import LiveTurns
from backend.features.workspace.domain.black_box import REFUSED_SAID
from backend.features.workspace.domain.chat import Chat, Message, ToolCall
from backend.features.workspace.domain.permission import PermissionWanted
from backend.features.workspace.domain.prompt import APPROVED
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.domain.tools import FileStarted, FileWritten
from backend.features.workspace.domain.turn import Progress
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app


class FakeEngine:
    """No network in a test: the answer is whatever this says it is."""

    def __init__(self, answer="Done.", blow_up=None, check=APPROVED):
        self.answer = answer
        self.blow_up = blow_up
        # What the black box's check says of every answer (Madde 445).
        self.check = check
        self.seen = None

    def complete(self, messages, tools=None):
        if self.blow_up:
            raise RuntimeError(self.blow_up)
        return {"role": "assistant", "content": self.answer}

    # No model (Madde 358): the engine answers with the one config.py names, so a route that still
    # handed one down would die here.
    def stream(self, messages, tools=None, on_open=None):
        if self.blow_up:
            raise RuntimeError(self.blow_up)
        self.seen = [dict(message) for message in messages]
        yield {"text": self.answer}

    def stream_alone(self, system, text, on_open=None):
        yield {"text": self.check}


class ScriptedEngine:
    """An engine whose rounds are written out, so a turn can call tools and never speak.

    FakeEngine answers in one piece and cannot reach for a tool, and a silent turn is exactly the
    shape it cannot make. Kept here rather than shared with the use case's tests: a test that
    imports another test's fixture makes the two move together for no reason.
    """

    def __init__(self, rounds):
        self.rounds = list(rounds)
        # Which tools each round was offered. Since Madde 91 that is what a mode turns into.
        self.tools = []

    def stream(self, messages, tools=None, on_open=None):
        self.tools.append([spec["function"]["name"] for spec in tools or []])
        pieces = self.rounds.pop(0) if self.rounds else []
        for piece in pieces:
            yield piece

    def stream_alone(self, system, text, on_open=None):
        yield {"text": APPROVED}


class FailsThenAnswers:
    """An engine whose first `times` tries fail with these words, and whose next one answers.

    Five failures are one turn's failed answer (Madde 440), so this is how a test writes one through
    the door rather than onto the disk.
    """

    def __init__(self, times, words="HTTP 502", answer="Done."):
        self.left = times
        self.words = words
        self.answer = answer

    def stream(self, messages, tools=None, on_open=None):
        if self.left:
            self.left -= 1
            raise RuntimeError(self.words)
        yield {"text": self.answer}

    def stream_alone(self, system, text, on_open=None):
        yield {"text": APPROVED}


def _tool_call(tool, **arguments):
    return {"id": "t1", "function": {"name": tool, "arguments": json.dumps(arguments)}}


def _app(tmp_path, engine=None, store=None, files=None):
    """The app, its chat store and its live turns -- fresh per app, like the stores: one test's turn
    must not hold another's chat. The chat store is for a test that lays a chat down the way the
    routes would; the turns for one that watches a turn run."""
    store = store or Store(str(tmp_path))
    projects = FileProjectStore(store)
    chats = FileChatStore(store, projects)
    turns = LiveTurns()
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                projects,
                chats,
                (files or FileFileStore)(store, projects),
                engine or FakeEngine(),
                turns,
            ),
        ),
    )
    return app, chats, turns


def _wired(tmp_path, engine=None):
    app, chats, _turns = _app(tmp_path, engine)
    return app.test_client(), chats


def _client(tmp_path, engine=None):
    return _wired(tmp_path, engine)[0]


def _project(client):
    return client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]


def _chunks(response):
    for chunk in response.response:
        yield chunk.decode() if isinstance(chunk, bytes) else chunk


def _data(chunks):
    """What the frames said, in order: a beat carries no data and is dropped, as EventSource does."""
    said = []
    for chunk in chunks:
        said += [json.loads(line[len("data: ") :]) for line in chunk.splitlines() if line.startswith("data: ")]
    return said


def _listen(client, pid, cid):
    """The events door, opened and not yet read: the turn it hears is the one running now."""
    return client.get(f"/api/projects/{pid}/chats/{cid}/events")


def _heard(client, pid, cid):
    """The events door read to its end -- which is the end of the turn running in the chat, or at
    once when none is. Since Madde 462 the door that starts a turn answers before it ends, so this
    is how a test waits for what the turn wrote."""
    return _data(_chunks(_listen(client, pid, cid)))


def _sent(client, pid, **body):
    """A message through the one door, its turn waited for. The door's own answer, handed back."""
    answer = client.post(f"/api/projects/{pid}/messages", json=body)
    if answer.status_code == 202:
        _heard(client, pid, answer.get_json()["id"])
    return answer


def _retried(client, pid, cid, **body):
    """Try again, and whatever turn it started or found, waited for."""
    answer = client.post(f"/api/projects/{pid}/chats/{cid}/retry", json=body)
    if answer.status_code in (200, 202):
        _heard(client, pid, cid)
    return answer


def _started(client, text="hello"):
    # Every chat is born inside a project, so both ids come back together, the first turn over.
    pid = _project(client)
    return pid, _sent(client, pid, text=text).get_json()["id"]


def _record(client, project_id, chat_id):
    return client.get(f"/api/projects/{project_id}/chats/{chat_id}").get_json()


def _texts(client, pid, cid):
    return [message["text"] for message in _record(client, pid, cid)["messages"]]


def test_the_one_door_creates_a_chat_when_none_is_named(tmp_path):
    # Madde 87: one address for every sentence a user says. No chat in the body means there is no
    # chat yet, so the server makes one -- a chat is still born with its first message.
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    made = _record(client, pid, cid)
    assert made["title"] == "Write the intro"
    assert made["id"].startswith("c")
    assert [(m["role"], m["text"]) for m in made["messages"]][0] == ("user", "Write the intro")


def test_the_one_door_appends_when_a_chat_is_named(tmp_path):
    # The same address, and the only difference is one field in the body.
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    _sent(client, pid, chat=cid, text="and more")
    kept = _record(client, pid, cid)
    assert [m["text"] for m in kept["messages"]][:3] == ["Write the intro", "Done.", "and more"]
    # The title belongs to the message that started the chat and never moves.
    assert kept["title"] == "Write the intro"


def test_the_separate_answering_door_is_gone(tmp_path):
    # 405 rather than 404: the SPA fallback claims every path for GET, so an address with no rule
    # of its own still exists -- it just does not know POST.
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert client.post(f"/api/projects/{pid}/chats/{cid}/answer").status_code == 405


def test_a_body_with_no_text_is_a_blank_message(tmp_path):
    # One door, one meaning (Madde 462): Try again has its own door now, so a message without text
    # is a message with nothing in it, and nothing is answered.
    client = _client(tmp_path, engine=FailsThenAnswers(5))
    pid, cid = _started(client)
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid})
    assert (refused.status_code, refused.get_json()) == (400, {"error": "a message needs text"})
    assert [m["failed"] for m in _record(client, pid, cid)["messages"]] == ["", "technical"]


def test_a_null_sentence_is_refused_and_nothing_is_answered(tmp_path):
    # Null is a sentence that is not one. It breaks as it did before Madde 461, and nothing is
    # written or answered.
    client = _client(tmp_path, engine=FailsThenAnswers(5))
    pid, cid = _started(client)
    assert client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": None}).status_code == 500
    assert [m["failed"] for m in _record(client, pid, cid)["messages"]] == ["", "technical"]


def test_a_body_with_neither_a_chat_nor_text_is_400(tmp_path):
    # There is nothing to write and nothing to answer, so there is nothing this request means.
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/messages", json={}).status_code == 400


def test_a_blank_sentence_is_refused(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "   "})
    assert refused.status_code == 400


def test_the_old_creating_door_is_gone(tmp_path):
    # That address is a list of chats and answers GET, so Flask's answer is not 404 -- it is that
    # this address does not know this method. The rule table is what says the door went; a status
    # code alone cannot, because the SPA fallback answers GET for every path there is.
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/chats", json={"text": "hi"}).status_code == 405


def test_the_old_appending_door_is_gone(tmp_path):
    # 405 rather than 404, and for the same reason the creating door gives one.
    client = _client(tmp_path)
    pid, cid = _started(client)
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


def test_an_empty_first_sentence_is_refused_and_makes_no_chat(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/messages", json={"text": "   "}).status_code == 400
    assert client.get(f"/api/projects/{pid}/chats").get_json() == []


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


def test_a_chat_cannot_be_deleted(tmp_path):
    # Madde 353: its one place on screen was the project screen, and that screen is gone -- so is
    # the door. The address still answers GET, which is why a DELETE is refused rather than unknown.
    client = _client(tmp_path)
    pid, cid = _started(client, "hi")
    assert client.delete(f"/api/projects/{pid}/chats/{cid}").status_code == 405
    assert [row["id"] for row in client.get(f"/api/projects/{pid}/chats").get_json()] == [cid]
    assert client.get(f"/api/projects/{pid}/chats/{cid}").status_code == 200


def test_the_list_comes_newest_first_and_carries_no_messages(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    _sent(client, pid, text="first")
    _sent(client, pid, text="second")
    listed = client.get(f"/api/projects/{pid}/chats").get_json()
    assert [row["title"] for row in listed] == ["second", "first"]
    # The list screen does not draw messages, so sending them would be for nothing.
    assert all("messages" not in row for row in listed)


def test_one_chat_carries_its_messages(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    body = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert [m["text"] for m in body["messages"]] == ["hello", "Done."]


def test_an_unknown_chat_is_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    assert client.get(f"/api/projects/{pid}/chats/nope").status_code == 404


def test_there_is_no_workspace_wide_chat_address(tmp_path):
    # A chat needs a project to live in, and the sidebar lists that project's own chats, so
    # the workspace has no rule for this path at all. The status is 405 rather than 404 because the
    # SPA fallback still claims every GET; the rule table is what actually says it is gone.
    client = _client(tmp_path)
    assert client.post("/api/chats", json={"text": "Write the intro"}).status_code == 405
    rules = {rule.rule for rule in client.application.url_map.iter_rules()}
    assert "/api/chats" not in rules
    assert client.get("/api/projects").get_json() == []


def test_the_chat_store_offers_no_workspace_wide_listing(tmp_path):
    # Every chat is asked for through its project now, so the port shrank with the use case.
    assert not hasattr(_wired(tmp_path)[1], "list_all")


def test_the_recent_chats_use_case_is_gone():
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.list_recent_chats  # noqa: F401


def test_opening_a_project_and_a_chat_together_is_gone():
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.start_chat_in_new_project  # noqa: F401


def test_a_projects_chats_come_back_newest_first(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    _sent(client, pid, text="older")
    _sent(client, pid, text="newer")
    listed = client.get(f"/api/projects/{pid}/chats").get_json()
    assert [row["title"] for row in listed] == ["newer", "older"]


def test_an_engine_that_keeps_failing_ends_the_turn_in_a_failed_answer(tmp_path):
    # Madde 440: the black box does not throw, so the turn ends as any turn does, and the
    # failure's own words are the record's answer -- there for the card on every reload.
    client = _client(tmp_path, engine=FakeEngine(blow_up="401 bad key"))
    pid, cid = _started(client)
    kept = _record(client, pid, cid)
    assert [(m["text"], m["failed"]) for m in kept["messages"]] == [
        ("hello", ""),
        ("401 bad key", "technical"),
    ]
    assert kept["status"] == "failed"


def test_an_answer_refused_five_times_ends_the_turn_in_the_refusal_message(tmp_path):
    # Madde 445: the refusal's own words never reach the record. The general message stands as the
    # answer, written like any answer so it stays on a reload.
    client = _client(tmp_path, engine=FakeEngine(answer="I cannot help.", check="REFUSAL"))
    pid, cid = _started(client, "x" * 100)
    record = _record(client, pid, cid)
    assert [(m["text"], m["failed"]) for m in record["messages"]] == [
        ("x" * 100, ""),
        (REFUSED_SAID, "refused"),
    ]
    # It weighs nothing: the chat is as full as its question alone makes it.
    assert record["context"]["sent"] == 100 * 3 // 10


def test_every_message_says_whether_it_failed(tmp_path):
    # Always present, like `stopped`: the browser draws from what it is handed.
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert [m["failed"] for m in _record(client, pid, cid)["messages"]] == ["", ""]


def test_a_failed_answer_followed_by_a_message_stays_in_the_record(tmp_path):
    client = _client(tmp_path, engine=FailsThenAnswers(5))
    pid, cid = _started(client)
    _sent(client, pid, chat=cid, text="again")
    said = _record(client, pid, cid)["messages"]
    assert [(m["text"], m["failed"]) for m in said] == [
        ("hello", ""),
        ("HTTP 502", "technical"),
        ("again", ""),
        ("Done.", ""),
    ]


def _silent_with_a_file():
    return ScriptedEngine([[{"tool_calls": [_tool_call("create_file", name="plan.md", content="x")]}], []])


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
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    # Every field, always present -- the browser draws what it is handed, and an absent one would
    # make each reader check before drawing. Madde 78 adds the third.
    assert kept["messages"][-1]["calls"] == [
        {"tool": "create_file", "target": "plan.md", "outcome": "Saved"}
    ]


def test_stopping_a_chat_that_is_not_there_is_a_404(tmp_path):
    client = _client(tmp_path)
    pid, _ = _started(client)
    assert client.post(f"/api/projects/{pid}/chats/nope/stop", json={"turn": "t1"}).status_code == 404


def test_the_stored_chat_says_which_answer_was_stopped(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    # This one ran to the end, so the field is there and it is false.
    assert kept["messages"][-1]["stopped"] is False


def test_the_stored_chat_says_what_the_answer_spent(tmp_path):
    engine = ScriptedEngine(
        [[{"text": "Done."}, {"usage": {"sent": 12400, "cached": 9100, "answered": 842}}]]
    )
    client = _client(tmp_path, engine=engine)
    pid, cid = _started(client)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert kept["messages"][-1]["usage"] == {"sent": 12400, "cached": 9100, "answered": 842}


def test_an_unmeasured_answer_still_carries_the_field(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert kept["messages"][-1]["usage"] == {"sent": 0, "cached": 0, "answered": 0}


def test_the_record_keeps_the_silent_answer(tmp_path):
    # Madde 38, kept through Madde 440: a turn that wrote a file and then said nothing is finished,
    # not a failure.
    client = _client(tmp_path, engine=_silent_with_a_file())
    pid, cid = _started(client)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    assert [m["text"] for m in kept] == ["hello", ""]
    assert kept[-1]["files"] == ["plan.md"]
    assert kept[-1]["failed"] == ""


def test_a_turn_that_produced_nothing_ends_in_a_failed_answer(tmp_path):
    # Neither a word nor a file five times over. Since Madde 440 it is said on the record.
    client = _client(tmp_path, engine=ScriptedEngine([[]]))
    pid, cid = _started(client)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    assert [(m["text"], m["failed"]) for m in kept] == [
        ("hello", ""),
        ("The model returned nothing.", "technical"),
    ]


def test_a_new_chat_shows_up_in_the_project_count(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    _sent(client, pid, text="hello")
    assert client.get("/api/projects").get_json()[0]["chats"] == 1


# --- one model, and the server names it (Madde 82, Madde 358) ------------------------------------


def test_the_model_endpoint_is_gone(tmp_path):
    assert _client(tmp_path).get("/api/model").status_code == 404


def test_a_chat_carries_no_model(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert "model" not in client.get(f"/api/projects/{pid}/chats/{cid}").get_json()


def test_a_chat_cannot_be_patched(tmp_path):
    # Madde 86 took the route out: a chat carries nothing that changes. The address still answers
    # GET, so Flask's answer is not 404 -- it is that this address does not know this method.
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert client.patch(f"/api/projects/{pid}/chats/{cid}", json={"skill": "verify"}).status_code == 405
    assert client.patch(f"/api/projects/{pid}/chats/{cid}", json={"title": "Else"}).status_code == 405
    assert client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["title"] == "hello"


def test_a_model_sent_with_a_message_is_not_kept(tmp_path):
    # Madde 358. The server names the model every turn goes to, so a field a browser still sends is
    # read by nothing and written nowhere.
    client = _client(tmp_path)
    pid = _project(client)
    cid = _sent(client, pid, text="hello", model="deepseek-v4-pro").get_json()["id"]
    assert "model" not in _record(client, pid, cid)["messages"][0]


def test_a_message_on_the_wire_names_no_model_even_when_its_record_does(tmp_path):
    # Madde 146 to 357 wrote the model onto the message. The record keeps it; the screen shows no
    # model, so nothing sends it there.
    client, chats = _wired(tmp_path)
    pid = _project(client)
    chats.add(
        pid,
        Chat(
            id="c1",
            title="Old",
            created_at="2026-09-02T10:00:00+00:00",
            messages=(
                Message(
                    role="user", at="2026-09-02T10:00:00+00:00", text="hi", model="deepseek-v4-pro"
                ),
            ),
        ),
    )
    assert "model" not in _record(client, pid, "c1")["messages"][0]


def test_a_chat_carries_no_skill(tmp_path):
    # Madde 86: the field is gone from the record, so it is gone from the wire too. What the skill
    # was sent with keeps it -- that is the message, not the chat.
    client = _client(tmp_path)
    pid = _project(client)
    cid = _sent(client, pid, text="hello", skill="create-scenario").get_json()["id"]
    born = _record(client, pid, cid)
    assert "skill" not in born
    assert born["messages"][0]["skill"] == "create-scenario"


def test_a_message_carries_the_skill_it_was_sent_with(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    _sent(client, pid, chat=cid, text="more", skill="verify")
    # The first turn's pair carries none; the sentence just sent carries the one it was sent with.
    assert [m["skill"] for m in _record(client, pid, cid)["messages"]][:3] == ["", "", "verify"]


def test_a_selected_skill_reaches_the_engine_as_an_instruction(tmp_path):
    # The road from the composer to the engine is one road, and this is where it is checked end to
    # end.
    plain, with_skill = FakeEngine(), FakeEngine()
    client = _client(tmp_path, engine=plain)
    _started(client)

    other = _client(tmp_path / "second", engine=with_skill)
    opid = _project(other)
    _sent(other, opid, text="hello", skill="edit-prompts")

    # No instruction with no skill selected. The file names are not one: since Madde 127 they ride
    # in every request either way, so they are dropped before the count.
    assert not [
        piece
        for piece in plain.seen
        if piece["role"] == "system" and "project" not in piece["content"]
    ]
    # At the end since Madde 93.
    assert with_skill.seen[-1] == {
        "role": "system",
        "content": instruction_for("edit-prompts"),
    }


# --- the ceiling on a chat's context (Madde 92; the messages alone since Madde 337) -------------

# 170,000 characters: 51,000 tokens by the chat's measure, past the ceiling.
LONG = "a" * 170_000


def _answering(tmp_path, answer, sent=0):
    """A client whose one answer says this, and reports having sent this many tokens."""
    engine = ScriptedEngine(
        [[{"text": answer}, {"usage": {"sent": sent, "cached": 0, "answered": 5}}]]
    )
    return _client(tmp_path, engine)


def test_a_full_chat_refuses_a_new_sentence(tmp_path):
    # The ceiling stops the turn before anything is written: a refused sentence that reached the
    # disk would leave the chat waiting for an answer nobody can give it.
    client = _answering(tmp_path, LONG)
    pid, cid = _started(client)
    before = len(_record(client, pid, cid)["messages"])
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "and more"})
    assert refused.status_code == 400
    assert "ceiling" in refused.get_json()["error"]
    assert len(_record(client, pid, cid)["messages"]) == before


def test_a_full_chat_refuses_a_second_attempt_too(tmp_path):
    # The reason has to be the ceiling rather than whatever else the door might have said first --
    # otherwise the screen tells the user something true and useless.
    client = _answering(tmp_path, LONG)
    pid, cid = _started(client)
    refused = client.post(f"/api/projects/{pid}/chats/{cid}/retry", json={})
    assert refused.status_code == 400
    assert "ceiling" in refused.get_json()["error"]


def test_a_turn_that_spent_a_lot_but_said_little_does_not_fill_the_chat(tmp_path):
    # Madde 337. Sixty thousand is what the old ceiling read: the whole last request, with its
    # instructions, its tool steps and its opened files. None of that is the conversation.
    client = _answering(tmp_path, "Done.", sent=60_000)
    pid, cid = _started(client)
    kept = _sent(client, pid, chat=cid, text="and more")
    assert kept.status_code == 202
    said = [message["text"] for message in _record(client, pid, cid)["messages"]]
    assert said[:3] == ["hello", "Done.", "and more"]


def test_the_record_says_how_much_of_the_ceiling_it_has_used(tmp_path):
    from backend.features.workspace.domain.chat import CONTEXT_CEILING

    client = _answering(tmp_path, "a" * 995, sent=41_000)
    pid, cid = _started(client)
    assert _record(client, pid, cid)["context"] == {"sent": 300, "ceiling": CONTEXT_CEILING}


# --- trimming a full chat from the start (Madde 345) ---------------------------------------------

# 20,000 characters: 6,000 tokens. Nine such answers fill a chat; eight do not.
PAGE = "a" * 20_000


def _filled(tmp_path):
    """A client and a chat of nine turns that has just filled, with one more answer left to give."""
    engine = ScriptedEngine([[{"text": PAGE}]] * 9 + [[{"text": "Done."}]])
    client = _client(tmp_path, engine)
    pid, cid = _started(client)
    for _ in range(8):
        _sent(client, pid, chat=cid, text="go on")
    return client, pid, cid


def test_a_full_chat_is_trimmed_from_the_start_and_keeps_every_message(tmp_path):
    client, pid, cid = _filled(tmp_path)
    trimmed = client.post(f"/api/projects/{pid}/chats/{cid}/trim")
    assert trimmed.status_code == 200
    assert trimmed.get_json() == {}
    record = _record(client, pid, cid)
    assert record["trimmed"] == 16
    assert len(record["messages"]) == 18
    assert record["context"]["sent"] == 6001


def test_a_trimmed_chat_takes_turns_again(tmp_path):
    client, pid, cid = _filled(tmp_path)
    client.post(f"/api/projects/{pid}/chats/{cid}/trim")
    assert _sent(client, pid, chat=cid, text="and more").status_code == 202
    said = [message["text"] for message in _record(client, pid, cid)["messages"]]
    assert said[-2:] == ["and more", "Done."]


def test_a_chat_that_is_not_full_is_not_trimmed(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    refused = client.post(f"/api/projects/{pid}/chats/{cid}/trim")
    assert refused.status_code == 400
    assert refused.get_json() == {"error": "this chat is not full"}
    assert _record(client, pid, cid)["trimmed"] == 0


def test_trimming_a_chat_that_is_not_there_is_a_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    refused = client.post(f"/api/projects/{pid}/chats/nope/trim")
    assert refused.status_code == 404
    assert refused.get_json() == {"error": "chat not found"}


def test_a_chat_nobody_trimmed_says_so(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert _record(client, pid, cid)["trimmed"] == 0


# --- whether the chat is full, said by the server (Madde 352) ------------------------------------


def test_a_chat_below_the_ceiling_says_it_is_not_full(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert _record(client, pid, cid)["full"] is False


def test_a_full_chat_says_so_before_anything_is_refused(tmp_path):
    client = _answering(tmp_path, LONG)
    pid, cid = _started(client)
    assert _record(client, pid, cid)["full"] is True


def test_a_trimmed_chat_is_not_full_any_more(tmp_path):
    client, pid, cid = _filled(tmp_path)
    assert _record(client, pid, cid)["full"] is True
    client.post(f"/api/projects/{pid}/chats/{cid}/trim")
    assert _record(client, pid, cid)["full"] is False


# --- the mode a turn was sent in (Madde 91) ------------------------------------------------------


def test_every_mode_is_offered_every_tool(tmp_path):
    from backend.features.workspace.domain.tools import TOOL_SPECS

    engine = ScriptedEngine([[{"text": "Done."}]])
    client = _client(tmp_path, engine)
    pid = _project(client)
    _sent(client, pid, text="hello", mode="ask")
    assert engine.tools == [[spec["function"]["name"] for spec in TOOL_SPECS]]


def test_the_mode_is_not_written_to_the_record(tmp_path):
    # Nothing ever reads a mode back, and a field nothing reads is a question every later reader
    # has to answer for themselves. Until Madde 463.
    client = _client(tmp_path)
    pid = _project(client)
    cid = _sent(client, pid, text="hello", mode="plan").get_json()["id"]
    kept = _record(client, pid, cid)
    assert not any("mode" in message for message in kept["messages"])
    assert "mode" not in kept


# --- versions of one conversation (Madde 195) ----------------------------------------------------


def _edited(client, pid, chat_id, text, at):
    return _sent(client, pid, chat=chat_id, text=text, **{"from": at})


def test_the_transcript_that_comes_back_is_the_open_line(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    _edited(client, pid, cid, "Write a shorter intro", 0)
    assert _texts(client, pid, cid) == ["Write a shorter intro", "Done."]


def test_every_message_carries_the_options_it_stands_among(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    _edited(client, pid, cid, "Write a shorter intro", 0)
    said = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    standing = said[0]["variants"]
    assert (standing["index"], standing["of"]) == (1, 2)
    assert standing["versions"][0] == ""
    assert standing["versions"][1]
    assert said[1]["variants"]["of"] == 1


def test_the_answer_to_an_edited_message_is_written_into_its_own_line(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    _edited(client, pid, cid, "Write a shorter intro", 0)
    stored = json.loads((tmp_path / pid / "chats" / f"{cid}.json").read_text(encoding="utf-8"))
    assert [m["text"] for m in stored["messages"]] == ["Write the intro", "Done."]
    assert [m["text"] for m in stored["versions"][0]["messages"]] == [
        "Write a shorter intro",
        "Done.",
    ]


def test_the_door_that_changes_which_version_is_open(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    _edited(client, pid, cid, "Write a shorter intro", 0)
    back = client.post(f"/api/projects/{pid}/chats/{cid}/version", json={"version": ""})
    assert back.status_code == 200
    assert _texts(client, pid, cid) == ["Write the intro", "Done."]


def test_a_version_nobody_wrote_is_refused_and_changes_nothing(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    _edited(client, pid, cid, "Write a shorter intro", 0)
    refused = client.post(f"/api/projects/{pid}/chats/{cid}/version", json={"version": "ghost"})
    assert refused.status_code == 404
    assert refused.get_json() == {"error": "version not found"}
    assert _texts(client, pid, cid) == ["Write a shorter intro", "Done."]


def test_editing_in_a_chat_that_does_not_exist_is_refused(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    refused = client.post(
        f"/api/projects/{pid}/messages", json={"chat": "ghost", "text": "hi", "from": 0}
    )
    assert refused.status_code == 404
    assert refused.get_json() == {"error": "chat not found"}


# --- one turn at a time in a chat, running on its own (Madde 461; 458's tests carried) -----------

BUSY = "this chat is still answering -- try again once it has finished"
PROJECT_BUSY = "a chat in this project is still answering -- try again once it has finished"


class GatedEngine:
    """An engine one of whose answers waits until the test opens the gate, so a turn can be held
    running while other requests arrive. Only the call after hold_next waits: the chat is born
    first, and another chat is answered while the held one still waits."""

    def __init__(self):
        self.gate = threading.Event()
        self.entered = threading.Event()
        self._hold = False

    def hold_next(self):
        self._hold = True

    def stream(self, messages, tools=None, on_open=None):
        if self._hold:
            self._hold = False
            self.entered.set()
            self.gate.wait(5)
        yield {"text": "Done."}

    def stream_alone(self, system, text, on_open=None):
        yield {"text": APPROVED}


def _running(tmp_path, store=None):
    """A chat whose second turn is held inside the model's request: the client, the ids, the
    engine whose gate releases the turn, the door's answer to the message, and the live turns."""
    engine = GatedEngine()
    app, _chats, turns = _app(tmp_path, engine, store=store)
    client = app.test_client()
    pid, cid = _started(client)
    engine.hold_next()
    sent = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "more"})
    assert engine.entered.wait(5)
    return client, pid, cid, engine, sent, turns


def _until_ended(turn):
    """Wait for a turn's end the way a listener does, by its snapshot."""
    seen = turn.snapshot()
    while not seen.ended:
        seen = turn.changed_since(seen.version, 5)
    return seen


def test_a_message_is_answered_at_once_with_the_chat_and_its_running_turn(tmp_path):
    # Madde 462: the door answers as soon as the question is written and the turn has started --
    # the chat as reading it gives it, so the screen draws the question and listens to the turn.
    client, pid, cid, engine, sent, turns = _running(tmp_path)
    assert sent.status_code == 202
    answer = sent.get_json()
    assert answer["id"] == cid
    assert [m["text"] for m in answer["messages"]] == ["hello", "Done.", "more"]
    assert answer["status"] == "running"
    assert answer["turn"]["id"] == turns.get(pid, cid).id
    assert answer["turn"]["status"] == "running"
    engine.gate.set()
    _heard(client, pid, cid)


def test_a_draft_is_answered_with_the_chat_it_was_born_as(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    sent = _sent(client, pid, text="hello")
    assert sent.status_code == 202
    assert sent.get_json()["id"].startswith("c")
    assert [row["id"] for row in client.get(f"/api/projects/{pid}/chats").get_json()] == [
        sent.get_json()["id"]
    ]


def test_while_a_turn_runs_every_request_that_would_write_its_chat_is_refused(tmp_path):
    # A new sentence and an edit advance the chat; a version and Continue here write it; deleting
    # the project would move it from under the turn. All wait for the turn's end. A refused message
    # says which turn is running, so the screen follows it.
    client, pid, cid, engine, _sent_, turns = _running(tmp_path)
    running = turns.get(pid, cid).id
    for body in ({"chat": cid, "text": "again"}, {"chat": cid, "text": "x", "from": 0}):
        refused = client.post(f"/api/projects/{pid}/messages", json=body)
        assert refused.status_code == 409
        assert refused.get_json()["error"] == BUSY
        assert refused.get_json()["turn"]["id"] == running
    for door in ("version", "trim"):
        refused = client.post(f"/api/projects/{pid}/chats/{cid}/{door}", json={"version": ""})
        assert (refused.status_code, refused.get_json()) == (409, {"error": BUSY})
    refused = client.delete(f"/api/projects/{pid}")
    assert (refused.status_code, refused.get_json()) == (409, {"error": PROJECT_BUSY})
    assert _texts(client, pid, cid) == ["hello", "Done.", "more"]
    engine.gate.set()
    _heard(client, pid, cid)
    assert _texts(client, pid, cid) == ["hello", "Done.", "more", "Done."]


def test_a_message_refused_while_a_turn_runs_hands_back_the_chat_as_it_stands(tmp_path):
    # A tab that was out of date sends into another tab's turn: it draws the chat the turn holds --
    # the other tab's question under the turn -- not the record it had, and it reads no disk for it.
    store = CountingStore(str(tmp_path))
    client, pid, cid, engine, _sent_, turns = _running(tmp_path, store)
    store.counted()
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "again"})
    said = refused.get_json()
    assert refused.status_code == 409
    assert said["error"] == BUSY
    assert [m["text"] for m in said["messages"]] == ["hello", "Done.", "more"]
    assert (said["status"], said["turn"]["id"]) == ("running", turns.get(pid, cid).id)
    assert store.counted() == (0, 0)
    engine.gate.set()
    _heard(client, pid, cid)


def test_once_the_turn_ends_the_next_request_is_answered(tmp_path):
    client, pid, cid, engine, _sent_, _turns = _running(tmp_path)
    engine.gate.set()
    _heard(client, pid, cid)
    assert _sent(client, pid, chat=cid, text="next").status_code == 202
    assert _texts(client, pid, cid) == ["hello", "Done.", "more", "Done.", "next", "Done."]


def test_a_chat_with_a_turn_running_does_not_hold_another_chat(tmp_path):
    client, pid, cid, engine, _sent_, _turns = _running(tmp_path)
    assert _sent(client, pid, text="elsewhere").status_code == 202
    engine.gate.set()
    _heard(client, pid, cid)


def test_a_draft_is_held_by_the_chat_it_is_born_as(tmp_path):
    engine = GatedEngine()
    app, _chats, _turns = _app(tmp_path, engine)
    client = app.test_client()
    pid = _project(client)
    engine.hold_next()
    born = client.post(f"/api/projects/{pid}/messages", json={"text": "hello"}).get_json()["id"]
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": born, "text": "more"})
    assert (refused.status_code, refused.get_json()["error"]) == (409, BUSY)
    engine.gate.set()
    _heard(client, pid, born)


def test_a_turn_keeps_running_with_nobody_listening(tmp_path):
    # The tab closed, or the tunnel dropped the stream: the turn ends on its own and writes its
    # answer, which the next visit reads.
    client, pid, cid, engine, _sent_, turns = _running(tmp_path)
    live = turns.get(pid, cid)
    listening = _listen(client, pid, cid)
    assert _data([next(_chunks(listening))])[0]["turn"]["id"] == live.id
    listening.close()
    engine.gate.set()
    assert _until_ended(live).error == ""
    assert _texts(client, pid, cid) == ["hello", "Done.", "more", "Done."]


def _asking_engine():
    """An engine whose second turn wants to write, and a first turn to be born in."""
    return ScriptedEngine(
        [
            [{"text": "hi"}],
            [{"tool_calls": [_tool_call("create_file", name="plan.md", content="x")]}],
            [{"text": "ok"}],
        ]
    )


def _asking_app(tmp_path):
    app, _chats, turns = _app(tmp_path, _asking_engine())
    return app.test_client(), turns


def _until_asked(frames):
    """Read the stream frame by frame until its turn asks; the turn as it asks. Frame by frame: the
    question waits for ever, so a stream read to its end would never end."""
    for chunk in frames:
        for frame in _data([chunk]):
            if frame["turn"] and frame["turn"]["permission"]:
                return frame["turn"]
    raise AssertionError("the turn never asked")


def _asked(client, pid, cid):
    """A turn in Ask, sent and listened to until its question stands: the turn as it asks, and the
    rest of the stream, still unread."""
    client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "write it", "mode": "ask"})
    frames = _chunks(_listen(client, pid, cid))
    return _until_asked(frames), frames


def test_a_waiting_turn_names_its_question_with_the_tool_and_its_arguments(tmp_path):
    client, _turns = _asking_app(tmp_path)
    pid, cid = _started(client)
    turn, _rest = _asked(client, pid, cid)
    assert turn["status"] == "waiting"
    asked = turn["permission"]
    assert asked["tool"] == "create_file"
    assert json.loads(asked["arguments"]) == {"name": "plan.md", "content": "x"}
    assert isinstance(asked["wait"], int)
    client.post(
        f"/api/projects/{pid}/chats/{cid}/permission",
        json={"turn": turn["id"], "wait": asked["wait"], "allowed": False},
    )
    _heard(client, pid, cid)


def test_an_allow_naming_the_turn_and_its_question_lets_the_turn_finish(tmp_path):
    client, _turns = _asking_app(tmp_path)
    pid, cid = _started(client)
    turn, rest = _asked(client, pid, cid)
    answered = client.post(
        f"/api/projects/{pid}/chats/{cid}/permission",
        json={"turn": turn["id"], "wait": turn["permission"]["wait"], "allowed": True},
    )
    assert answered.status_code == 200
    # The card goes with the answer: the turn the door hands back no longer asks.
    assert answered.get_json()["turn"]["permission"] is None
    assert _data(rest)[-1] == {"turn": None}
    assert [file["name"] for file in client.get(f"/api/projects/{pid}/files").get_json()] == ["plan.md"]


def test_a_refusal_at_the_door_writes_no_file_and_the_turn_still_ends(tmp_path):
    client, _turns = _asking_app(tmp_path)
    pid, cid = _started(client)
    turn, rest = _asked(client, pid, cid)
    client.post(
        f"/api/projects/{pid}/chats/{cid}/permission",
        json={"turn": turn["id"], "wait": turn["permission"]["wait"], "allowed": False, "reason": "no"},
    )
    _data(rest)
    assert client.get(f"/api/projects/{pid}/files").get_json() == []
    assert _record(client, pid, cid)["messages"][-1]["calls"][0]["outcome"] == "Not allowed"


def test_an_answer_naming_another_turn_or_another_question_settles_nothing(tmp_path):
    # Gap 1 of Madde 461, closed: a late press names what it was meant for, and reaches nothing else.
    client, turns = _asking_app(tmp_path)
    pid, cid = _started(client)
    turn, _rest = _asked(client, pid, cid)
    wait = turn["permission"]["wait"]
    for stale in ({"turn": "t-earlier", "wait": wait}, {"turn": turn["id"], "wait": wait - 1}, {}):
        late = client.post(
            f"/api/projects/{pid}/chats/{cid}/permission", json={**stale, "allowed": True}
        )
        assert late.status_code == 200
        assert late.get_json()["turn"]["permission"]["wait"] == wait
    client.post(
        f"/api/projects/{pid}/chats/{cid}/permission",
        json={"turn": turn["id"], "wait": wait, "allowed": False},
    )
    _heard(client, pid, cid)
    assert client.get(f"/api/projects/{pid}/files").get_json() == []


def test_a_question_waits_with_no_browser_and_is_answered_later(tmp_path):
    # The user: "sonsuza kadar beklesin". The browser goes; the question stands in memory, and an
    # answer arriving later lets the turn finish.
    client, turns = _asking_app(tmp_path)
    pid, cid = _started(client)
    turn, _rest = _asked(client, pid, cid)
    live = turns.get(pid, cid)
    client.post(
        f"/api/projects/{pid}/chats/{cid}/permission",
        json={"turn": turn["id"], "wait": turn["permission"]["wait"], "allowed": True},
    )
    _until_ended(live)
    assert [file["name"] for file in client.get(f"/api/projects/{pid}/files").get_json()] == ["plan.md"]
    assert _texts(client, pid, cid)[-1] == "ok"


def test_answering_a_chat_that_is_not_there_is_a_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    answered = client.post(f"/api/projects/{pid}/chats/nope/permission", json={"allowed": True})
    assert answered.status_code == 404
    assert answered.get_json() == {"error": "chat not found"}


def test_a_permission_with_nothing_running_does_nothing(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    answered = client.post(f"/api/projects/{pid}/chats/{cid}/permission", json={"allowed": True})
    assert (answered.status_code, answered.get_json()) == (200, {"turn": None})


# --- Stop, bound to the turn it names (Madde 462) --------------------------------------------------


def test_a_stop_naming_the_running_turn_stops_it(tmp_path):
    client, pid, cid, engine, sent, _turns = _running(tmp_path)
    stopped = client.post(
        f"/api/projects/{pid}/chats/{cid}/stop", json={"turn": sent.get_json()["turn"]["id"]}
    )
    assert stopped.status_code == 200
    # Asked for, not done: the turn stops at its next chance, and is still running as it answers.
    assert stopped.get_json()["turn"]["id"] == sent.get_json()["turn"]["id"]
    engine.gate.set()
    _heard(client, pid, cid)
    last = _record(client, pid, cid)["messages"][-1]
    assert (last["text"], last["stopped"]) == ("", True)


def test_a_stop_naming_another_turn_does_nothing(tmp_path):
    # A press meant for the turn before this one: the running turn finishes and is not stopped.
    client, pid, cid, engine, _sent_, _turns = _running(tmp_path)
    for late in ({"turn": "t-earlier"}, {}):
        assert client.post(f"/api/projects/{pid}/chats/{cid}/stop", json=late).status_code == 200
    engine.gate.set()
    _heard(client, pid, cid)
    last = _record(client, pid, cid)["messages"][-1]
    assert (last["text"], last["stopped"]) == ("Done.", False)


def test_a_stop_with_nothing_running_reaches_nothing(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    stopped = client.post(f"/api/projects/{pid}/chats/{cid}/stop", json={"turn": "t1"})
    assert (stopped.status_code, stopped.get_json()) == (200, {"turn": None})
    _sent(client, pid, chat=cid, text="more")
    last = _record(client, pid, cid)["messages"][-1]
    assert (last["text"], last["stopped"]) == ("Done.", False)


# --- reading a chat says its status and its running turn (Madde 462) -------------------------------


def _laid(tmp_path, *said):
    """A chat laid on disk with these messages, and the client that reads it."""
    client, chats = _wired(tmp_path)
    pid = _project(client)
    chats.add(pid, Chat(id="c1", title="go", created_at="2026-10-09T10:00:00+00:00", messages=said))
    return client, pid


AT = "2026-10-09T10:00:00+00:00"


@pytest.mark.parametrize(
    ("said", "status"),
    [
        ((), "idle"),
        ((Message("user", AT, "go"),), "unanswered"),
        ((Message("user", AT, "go"), Message("ai", AT, "Done.")), "answered"),
        ((Message("user", AT, "go"), Message("ai", AT, "", stopped=True)), "stopped"),
        ((Message("user", AT, "go"), Message("ai", AT, "HTTP 502", failed="technical")), "failed"),
        ((Message("user", AT, "go"), Message("ai", AT, REFUSED_SAID, failed="refused")), "failed"),
    ],
)
def test_reading_a_chat_says_its_status_from_the_record(tmp_path, said, status):
    client, pid = _laid(tmp_path, *said)
    record = _record(client, pid, "c1")
    assert (record["status"], record["turn"]) == (status, None)


def test_reading_a_chat_while_its_turn_runs_says_so_and_hands_the_turn(tmp_path):
    client, pid, cid, engine, _sent_, turns = _running(tmp_path)
    record = _record(client, pid, cid)
    assert record["status"] == "running"
    assert record["turn"] == {
        "id": turns.get(pid, cid).id,
        "status": "running",
        "calls": [],
        "files": [],
        "creating": False,
        "progress": {"round": 1, "of": 32, "tokens": 0},
        "permission": None,
    }
    engine.gate.set()
    _heard(client, pid, cid)
    assert (_record(client, pid, cid)["status"], _record(client, pid, cid)["turn"]) == ("answered", None)


def test_reading_a_chat_while_its_turn_waits_draws_the_question_again(tmp_path):
    # Gap 3 of Madde 461: a reload during a waiting permission draws the card and Stop from here.
    client, _turns = _asking_app(tmp_path)
    pid, cid = _started(client)
    turn, _rest = _asked(client, pid, cid)
    record = _record(client, pid, cid)
    assert record["status"] == "waiting"
    assert record["turn"]["id"] == turn["id"]
    assert record["turn"]["permission"] == turn["permission"]
    client.post(
        f"/api/projects/{pid}/chats/{cid}/permission",
        json={"turn": turn["id"], "wait": turn["permission"]["wait"], "allowed": False},
    )
    _heard(client, pid, cid)


# --- the events door: the running turn, as it moves (Madde 462) ------------------------------------


def _laid_turn(tmp_path):
    """A chat on disk and a turn held on it by hand, so a test moves the turn one piece at a time."""
    app, chats, turns = _app(tmp_path)
    client = app.test_client()
    pid = _project(client)
    chats.add(pid, Chat(id="c1", title="go", created_at=AT, messages=(Message("user", AT, "go"),)))
    return client, pid, turns, turns.reserve(pid, "c1")


def test_with_nothing_running_the_door_says_so_and_closes(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    listening = _listen(client, pid, cid)
    assert listening.mimetype == "text/event-stream"
    assert listening.headers["Cache-Control"] == "no-cache"
    assert listening.headers["X-Accel-Buffering"] == "no"
    assert _data(_chunks(listening)) == [{"turn": None}]


def test_the_first_frame_is_the_turn_as_it_stands_and_every_change_is_a_frame(tmp_path):
    client, pid, turns, turn = _laid_turn(tmp_path)
    turn.apply(Progress(1, 32, 0))
    frames = _chunks(_listen(client, pid, "c1"))
    first = _data([next(frames)])[0]["turn"]
    assert (first["id"], first["status"], first["progress"]) == (
        turn.id,
        "running",
        {"round": 1, "of": 32, "tokens": 0},
    )
    turn.apply(FileStarted())
    assert _data([next(frames)])[0]["turn"]["creating"] is True
    turn.apply(FileWritten("plan.md"))
    turn.apply(ToolCall("create_file", "plan.md", "Saved"))
    # Whole snapshots: a listener that wakes after two changes lands where the turn is, with nothing
    # to add up.
    said = _data([next(frames)])[0]["turn"]
    assert (said["files"], said["creating"]) == (["plan.md"], False)
    assert said["calls"] == [{"tool": "create_file", "target": "plan.md", "outcome": "Saved"}]
    turn.apply(PermissionWanted("edit_file", "{}"))
    said = _data([next(frames)])[0]["turn"]
    assert said["status"] == "waiting"
    assert said["calls"] == [{"tool": "create_file", "target": "plan.md", "outcome": "Saved"}]
    assert said["permission"] == {"wait": turn.snapshot().permission.wait, "tool": "edit_file", "arguments": "{}"}
    turns.release(pid, "c1", turn)
    assert _data(frames) == [{"turn": None}]


def test_the_door_beats_while_nothing_moves(monkeypatch, tmp_path):
    # A comment line: EventSource drops it, and a tunnel sees bytes on a connection gone quiet.
    # Shortened here: a real beat costs fifteen seconds of waiting.
    from backend.features.workspace.presentation import routes

    monkeypatch.setattr(routes, "BEAT_SECONDS", 0.01)
    client, pid, turns, turn = _laid_turn(tmp_path)
    frames = _chunks(_listen(client, pid, "c1"))
    next(frames)
    assert next(frames) == ": beat\n\n"
    turns.release(pid, "c1", turn)
    assert _data(frames) == [{"turn": None}]


def test_a_turn_whose_own_code_broke_ends_with_its_words(tmp_path):
    client, pid, turns, turn = _laid_turn(tmp_path)
    frames = _chunks(_listen(client, pid, "c1"))
    next(frames)
    turns.release(pid, "c1", turn, "the disk went away")
    assert _data(frames) == [{"turn": None, "error": "the disk went away"}]


def test_two_listeners_hear_the_same_turn(tmp_path):
    # Two tabs on one chat: one condition wakes both.
    client, pid, turns, turn = _laid_turn(tmp_path)
    first, second = _chunks(_listen(client, pid, "c1")), _chunks(_listen(client, pid, "c1"))
    assert _data([next(first)]) == _data([next(second)])
    turn.apply(Progress(2, 32, 140))
    assert _data([next(first)]) == _data([next(second)])
    turns.release(pid, "c1", turn)
    assert _data(first) == _data(second) == [{"turn": None}]


def test_a_reload_during_a_version_switch_hears_the_hold_end(tmp_path):
    # The hold is a turn too, for that one read and write (Madde 461's gap 4): its listener hears it
    # end rather than waiting on it for ever.
    client, pid, turns, _turn = _laid_turn(tmp_path)
    turns.release(pid, "c1", _turn)
    held = turns.reserve(pid, "c1")
    frames = _chunks(_listen(client, pid, "c1"))
    next(frames)
    turns.release(pid, "c1", held)
    assert _data(frames) == [{"turn": None}]


def test_a_turn_whose_own_code_breaks_leaves_its_question_unanswered(tmp_path):
    # The black box answers for the model, so what is left is a tool or the disk: the last frame
    # carries its words, and nothing is written -- the question stays, unanswered.
    listening = threading.Event()

    class NoDisk(FileFileStore):
        def list_names(self, project_id):
            listening.wait(5)
            raise OSError("the disk went away")

    app, _chats, _turns = _app(tmp_path, files=NoDisk)
    client = app.test_client()
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": "hello"}).get_json()["id"]
    frames = _chunks(_listen(client, pid, cid))
    listening.set()
    assert _data(frames)[-1] == {"turn": None, "error": "the disk went away"}
    record = _record(client, pid, cid)
    assert ([m["text"] for m in record["messages"]], record["status"]) == (["hello"], "unanswered")


# --- Try again, decided by the chat's status (Madde 461, its own door since 462) -----------------


def test_try_again_on_a_failed_answer_replaces_it_and_never_writes_the_question_twice(tmp_path):
    client = _client(tmp_path, engine=FailsThenAnswers(5, answer="Here it is."))
    pid, cid = _started(client)
    assert _record(client, pid, cid)["status"] == "failed"
    again = client.post(f"/api/projects/{pid}/chats/{cid}/retry", json={})
    assert again.status_code == 202
    # The failed answer is already gone from what comes back: the card goes when the door answers.
    assert [m["text"] for m in again.get_json()["messages"]] == ["hello"]
    _heard(client, pid, cid)
    assert _texts(client, pid, cid) == ["hello", "Here it is."]


def test_try_again_on_an_unanswered_question_answers_it_once(tmp_path):
    # A chat whose last word is the user's: an old file, or a turn that died with the server.
    client, pid = _laid(tmp_path, Message("user", AT, "go"))
    assert _retried(client, pid, "c1").status_code == 202
    assert _texts(client, pid, "c1") == ["go", "Done."]


@pytest.mark.parametrize(
    "said",
    [
        (Message("user", AT, "go"), Message("ai", AT, "Done.")),
        (Message("user", AT, "go"), Message("ai", AT, "", stopped=True)),
        (),
    ],
)
def test_try_again_on_an_answered_stopped_or_empty_chat_runs_nothing(tmp_path, said):
    # Nothing is waiting, so answering anyway would write a second reply to a question that has one.
    # The answer comes back with the door's reply, and the screen shows it.
    client, pid = _laid(tmp_path, *said)
    again = client.post(f"/api/projects/{pid}/chats/c1/retry", json={})
    assert again.status_code == 200
    assert (again.get_json()["turn"], len(again.get_json()["messages"])) == (None, len(said))
    assert len(_texts(client, pid, "c1")) == len(said)


def test_try_again_on_a_running_turn_only_hands_it_back(tmp_path):
    # Reconnecting: the screen lost the turn, and the door says which one runs, writing nothing.
    client, pid, cid, engine, sent, _turns = _running(tmp_path)
    again = client.post(f"/api/projects/{pid}/chats/{cid}/retry", json={})
    assert again.status_code == 200
    assert again.get_json()["turn"]["id"] == sent.get_json()["turn"]["id"]
    assert [m["text"] for m in again.get_json()["messages"]] == ["hello", "Done.", "more"]
    engine.gate.set()
    _heard(client, pid, cid)
    assert _retried(client, pid, cid).status_code == 200
    assert _texts(client, pid, cid) == ["hello", "Done.", "more", "Done."]


def test_try_again_in_a_chat_that_is_not_there_is_a_404(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    refused = client.post(f"/api/projects/{pid}/chats/nope/retry", json={})
    assert (refused.status_code, refused.get_json()) == (404, {"error": "chat not found"})


def test_try_again_in_a_project_that_is_not_there_says_so(tmp_path):
    # The same words the message door says: the project is what is missing, not the chat.
    refused = _client(tmp_path).post("/api/projects/nope/chats/c1/retry", json={})
    assert (refused.status_code, refused.get_json()) == (404, {"error": "project not found"})


def _failed_in_a_full_chat(tmp_path):
    """A chat whose last question filled it and whose answer then failed, written to disk."""
    return _laid(
        tmp_path,
        Message(role="user", at="2026-10-09T10:00:00+00:00", text="go"),
        Message(role="ai", at="2026-10-09T10:01:00+00:00", text="a" * 100_000),
        Message(role="user", at="2026-10-09T10:02:00+00:00", text="b" * 70_000),
        Message(role="ai", at="2026-10-09T10:03:00+00:00", text="HTTP 502", failed="technical"),
    )


def test_try_again_in_a_full_chat_meets_the_ceiling_and_the_failed_answer_stays(tmp_path):
    client, pid = _failed_in_a_full_chat(tmp_path)
    refused = client.post(f"/api/projects/{pid}/chats/c1/retry", json={})
    assert refused.status_code == 400
    assert "ceiling" in refused.get_json()["error"]
    assert _record(client, pid, "c1")["messages"][-1]["failed"] == "technical"


def test_try_again_after_continue_here_keeps_the_trim(tmp_path):
    # Continue here marks the line's last message, which here is the failed answer. Taking it out
    # must not take the trim with it: the mark moves to the question in front of it.
    client, pid = _failed_in_a_full_chat(tmp_path)
    assert client.post(f"/api/projects/{pid}/chats/c1/trim").status_code == 200
    _retried(client, pid, "c1")
    record = _record(client, pid, "c1")
    assert record["trimmed"] == 2
    assert [m["failed"] for m in record["messages"]] == ["", "", "", ""]
    assert record["messages"][-1]["text"] == "Done."


def test_try_again_carries_the_mode_until_the_chat_holds_one(tmp_path):
    # Madde 463 moves it onto the chat; until then the request says it, as a message does. Asked in
    # Ask, the write stops at its question.
    engine = ScriptedEngine(
        [[{"tool_calls": [_tool_call("create_file", name="plan.md", content="x")]}], [{"text": "ok"}]]
    )
    app, chats, _turns = _app(tmp_path, engine)
    client = app.test_client()
    pid = _project(client)
    chats.add(pid, Chat(id="c1", title="go", created_at=AT, messages=(Message("user", AT, "go"),)))
    assert client.post(f"/api/projects/{pid}/chats/c1/retry", json={"mode": "ask"}).status_code == 202
    turn = _until_asked(_chunks(_listen(client, pid, "c1")))
    assert turn["permission"]["tool"] == "create_file"
    client.post(
        f"/api/projects/{pid}/chats/c1/permission",
        json={"turn": turn["id"], "wait": turn["permission"]["wait"], "allowed": False},
    )
    _heard(client, pid, "c1")


def test_a_request_refused_for_another_reason_lets_the_chat_go(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": " "}).status_code == 400
    _retried(client, pid, cid)
    assert _sent(client, pid, chat=cid, text="more").status_code == 202


def test_a_request_that_breaks_before_its_turn_lets_the_chat_go(tmp_path):
    client, chats = _wired(tmp_path)
    pid, cid = _started(client)
    reading = chats.get

    def broken(project_id, chat_id):
        raise OSError("Drive went away")

    chats.get = broken
    assert client.post(f"/api/projects/{pid}/chats/{cid}/retry", json={}).status_code == 500
    chats.get = reading
    assert _sent(client, pid, chat=cid, text="more").status_code == 202


# --- what a turn costs the chat file (Madde 461, 462) ----------------------------------------------


class CountingStore(Store):
    """The disk, counting reads and writes of chat files alone: projects.json is queued apart."""

    def __init__(self, root):
        super().__init__(root)
        self.reads = 0
        self.writes = 0

    def read_text(self, rel):
        if "/chats/" in rel:
            self.reads += 1
        return super().read_text(rel)

    def write_text(self, rel, text):
        if "/chats/" in rel:
            self.writes += 1
        return super().write_text(rel, text)

    def counted(self):
        reads, writes, self.reads, self.writes = self.reads, self.writes, 0, 0
        return reads, writes


def _counted(tmp_path, engine=None):
    store = CountingStore(str(tmp_path))
    app, _chats, _turns = _app(tmp_path, engine, store=store)
    return app.test_client(), store


def test_a_message_reads_its_chat_once_and_writes_it_twice(tmp_path):
    # Once to check it, once for the question, once for the answer. Listening to it reads nothing.
    client, store = _counted(tmp_path)
    pid, cid = _started(client)
    store.counted()
    _sent(client, pid, chat=cid, text="more")
    assert store.counted() == (1, 2)


def test_a_first_message_reads_nothing(tmp_path):
    client, store = _counted(tmp_path)
    pid = _project(client)
    _sent(client, pid, text="hello")
    assert store.counted() == (0, 2)


def test_try_again_on_a_failed_answer_drops_it_and_answers_in_two_writes(tmp_path):
    client, store = _counted(tmp_path, FailsThenAnswers(5))
    pid, cid = _started(client)
    store.counted()
    _retried(client, pid, cid)
    assert store.counted() == (1, 2)


def test_try_again_on_an_answered_chat_writes_nothing(tmp_path):
    client, store = _counted(tmp_path)
    pid, cid = _started(client)
    store.counted()
    _retried(client, pid, cid)
    assert store.counted() == (1, 0)


def test_stop_and_permission_touch_no_chat_file(tmp_path):
    client, store = _counted(tmp_path)
    pid, cid = _started(client)
    store.counted()
    client.post(f"/api/projects/{pid}/chats/{cid}/stop", json={"turn": "t1"})
    client.post(f"/api/projects/{pid}/chats/{cid}/permission", json={"allowed": True})
    assert store.counted() == (0, 0)


def test_while_a_turn_runs_reading_listening_and_trying_again_touch_no_disk(tmp_path):
    # A reload during a turn is a read and a listen; a reconnect is a Try again. None goes to Drive.
    store = CountingStore(str(tmp_path))
    client, pid, cid, engine, _sent_, turns = _running(tmp_path, store)
    store.counted()
    assert _texts(client, pid, cid) == ["hello", "Done.", "more"]
    listening = _chunks(_listen(client, pid, cid))
    next(listening)
    client.post(f"/api/projects/{pid}/chats/{cid}/retry", json={})
    assert store.counted() == (0, 0)
    engine.gate.set()
    _data(listening)
