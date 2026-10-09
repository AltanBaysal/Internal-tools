import json

import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.data.memory_permissions import MemoryPermissions
from backend.features.workspace.data.memory_stops import MemoryStops
from backend.features.workspace.domain.black_box import REFUSED_SAID
from backend.features.workspace.domain.chat import Chat, Message
from backend.features.workspace.domain.prompt import APPROVED
from backend.features.workspace.domain.skills import instruction_for
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
                MemoryPermissions(),
            ),
        ),
    )
    return app.test_client()


def _project(client):
    return client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]


def _frames(body):
    # The event names in order, so a test can say what the stream said without matching bytes.
    return [line[len("event: ") :] for line in body.splitlines() if line.startswith("event: ")]


def _steps(body):
    """The same list with the turn's heartbeat taken out (Madde 194).

    A progress frame goes out at the top of every round and again whenever the count moves, so it
    lands between any two frames a test might be comparing. Where it lands is its own test's
    question, not every other test's.
    """
    return [name for name in _frames(body) if name != "progress"]


def _named(body):
    # The chat the stream's first frame named.
    return json.loads(body.split("data: ", 1)[1].splitlines()[0])["chat"]


def _started(client, text="hello"):
    # Every chat is born inside a project, so both ids come back together. And since Madde 88 it is
    # born answered too: there is no way to write a message without the answer following it down
    # the same connection.
    pid = _project(client)
    body = client.post(f"/api/projects/{pid}/messages", json={"text": text}).get_data(as_text=True)
    return pid, _named(body)


def _first_turn(client, text="hello"):
    # The chat, and the stream its first turn produced. Since Madde 88 those are one request, so a
    # test that wants to look at a stream sends a sentence rather than asking for an answer.
    pid = _project(client)
    body = client.post(f"/api/projects/{pid}/messages", json={"text": text}).get_data(as_text=True)
    return pid, _named(body), body


def _record(client, project_id, chat_id):
    # What the turn wrote. Asked for separately since Madde 89: the stream says a turn is over, and
    # the record has one home.
    return client.get(f"/api/projects/{project_id}/chats/{chat_id}").get_json()


def test_the_one_door_creates_a_chat_when_none_is_named(tmp_path):
    # Madde 87: one address for every sentence a user says. No chat in the body means there is no
    # chat yet, so the server makes one -- a chat is still born with its first message. Madde 88
    # made the answer to that request a stream, so the record is read off the closing frame.
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
    client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "and more"}).get_data()
    kept = _record(client, pid, cid)
    # The first turn answered itself, so the new sentence is the third thing in the record.
    assert [m["text"] for m in kept["messages"]][:3] == ["Write the intro", "Done.", "and more"]
    # The title belongs to the message that started the chat and never moves.
    assert kept["title"] == "Write the intro"


def test_a_sentence_is_answered_in_the_same_request(tmp_path):
    # Madde 88: one request. The message is written and the answer streams back down the
    # connection that brought it -- nothing opens a second one.
    client = _client(tmp_path)
    pid = _project(client)
    resp = client.post(f"/api/projects/{pid}/messages", json={"text": "hello"})
    assert resp.mimetype == "text/event-stream"
    body = resp.get_data(as_text=True)
    assert _frames(body)[-1] == "done"
    assert [m["text"] for m in _record(client, pid, _named(body))["messages"]] == ["hello", "Done."]


def test_the_first_frame_names_the_chat_that_was_born(tmp_path):
    # The id cannot come back as a field any more, because the body is a sequence of events. It
    # comes first, and the server knows it before the model has said a word.
    client = _client(tmp_path)
    pid = _project(client)
    body = client.post(f"/api/projects/{pid}/messages", json={"text": "hello"}).get_data(
        as_text=True
    )
    assert _frames(body)[0] == "chat"
    assert json.loads(body.split("data: ", 1)[1].splitlines()[0])["chat"].startswith("c")


def test_the_first_frame_names_the_chat_on_a_follow_up_too(tmp_path):
    # Sent every time rather than only when it is news: no condition on the server, and the browser
    # changes the address only when what it hears differs from what it holds.
    client = _client(tmp_path)
    pid, cid = _started(client)
    body = client.post(
        f"/api/projects/{pid}/messages", json={"chat": cid, "text": "more"}
    ).get_data(as_text=True)
    assert _frames(body)[0] == "chat"
    assert _named(body) == cid


def test_the_separate_answering_door_is_gone(tmp_path):
    # 405 rather than 404: the SPA fallback claims every path for GET, so an address with no rule
    # of its own still exists -- it just does not know POST.
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert client.post(f"/api/projects/{pid}/chats/{cid}/answer").status_code == 405


def test_a_body_with_no_text_asks_again_without_writing_the_sentence_twice(tmp_path):
    # Try again. Since Madde 440 a turn the model failed on leaves a failed answer behind, and
    # asking again takes it out and answers the same question -- written once.
    client = _client(tmp_path, engine=FailsThenAnswers(5))
    pid = _project(client)
    first = client.post(f"/api/projects/{pid}/messages", json={"text": "hello"}).get_data(
        as_text=True
    )
    cid = _named(first)
    again = client.post(f"/api/projects/{pid}/messages", json={"chat": cid})
    assert again.mimetype == "text/event-stream"
    again.get_data()
    said = _record(client, pid, cid)["messages"]
    assert [(m["text"], m["failed"]) for m in said] == [("hello", ""), ("Done.", "")]


def test_a_body_with_neither_a_chat_nor_text_is_400(tmp_path):
    # There is nothing to write and nothing to answer, so there is nothing this request means.
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/messages", json={}).status_code == 400


def test_asking_again_for_a_chat_that_was_already_answered_is_400(tmp_path):
    # Nothing is waiting, so answering anyway would write a second reply to a question that has
    # one. The rule the browser used to hold, in the one place a request has to pass.
    client = _client(tmp_path)
    pid, cid = _started(client)
    again = client.post(f"/api/projects/{pid}/messages", json={"chat": cid})
    assert again.status_code == 400
    assert len(client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]) == 2


def test_a_blank_sentence_is_refused_before_the_stream_starts(tmp_path):
    # Blank is not the same as absent, and no stream begins for it.
    client = _client(tmp_path)
    pid, cid = _started(client)
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "   "})
    assert refused.status_code == 400
    assert refused.mimetype != "text/event-stream"


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
    # The other half of this -- a blank sentence sent into a chat that exists -- is its own test
    # since Madde 88, because what it must not do is start a stream.
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
    client.post(f"/api/projects/{pid}/messages", json={"text": "first"})
    client.post(f"/api/projects/{pid}/messages", json={"text": "second"})
    listed = client.get(f"/api/projects/{pid}/chats").get_json()
    assert [row["title"] for row in listed] == ["second", "first"]
    # The list screen does not draw messages, so sending them would be for nothing.
    assert all("messages" not in row for row in listed)


def test_one_chat_carries_its_messages(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    body = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    # A chat is born answered since Madde 88: one request wrote both of these.
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


def test_the_words_do_not_travel_down_the_stream(tmp_path):
    # Madde 440: the answer comes back whole and the screen shows it once the turn has ended, so the
    # words are read off the record and nothing of them crosses while the turn runs.
    client = _client(tmp_path)
    pid, cid, body = _first_turn(client)
    assert "chunk" not in _frames(body)
    assert "Done." not in body
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert [m["text"] for m in kept["messages"]] == ["hello", "Done."]


def test_the_closing_frame_carries_nothing(tmp_path):
    # Madde 89: the record has one home, and it is the read endpoint. The stream says a turn is
    # over; what the turn wrote is a question asked separately.
    client = _client(tmp_path)
    _pid, _cid, body = _first_turn(client)
    closing = [block for block in body.split("\n\n") if block.startswith("event: done")]
    assert closing == ["event: done\ndata: {}"]


def test_no_frame_in_the_stream_carries_the_record(tmp_path):
    # Not only the last one: a shape that leaks anywhere is a second place it can drift from.
    client = _client(tmp_path)
    _pid, _cid, body = _first_turn(client)
    assert "messages" not in body


def test_an_engine_that_keeps_failing_ends_the_turn_in_a_failed_answer(tmp_path):
    # Madde 440: the black box does not throw, so the stream ends as any turn does, and the
    # failure's own words are the record's answer -- there for the card on every reload.
    client = _client(tmp_path, engine=FakeEngine(blow_up="401 bad key"))
    pid, cid, body = _first_turn(client)
    assert _frames(body)[-1] == "done"
    assert "event: error" not in body
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert [(m["text"], m["failed"]) for m in kept["messages"]] == [
        ("hello", ""),
        ("401 bad key", "technical"),
    ]


def test_an_answer_refused_five_times_ends_the_turn_in_the_refusal_message(tmp_path):
    # Madde 445: the refusal's own words never reach the record. The general message stands as the
    # answer, written like any answer so it stays on a reload, and the stream ends as any turn does.
    client = _client(tmp_path, engine=FakeEngine(answer="I cannot help.", check="REFUSAL"))
    pid, cid, body = _first_turn(client, "x" * 100)
    assert _frames(body)[-1] == "done"
    assert "event: error" not in body
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


def test_try_again_after_a_failed_answer_replaces_it(tmp_path):
    client = _client(tmp_path, engine=FailsThenAnswers(5, answer="Here it is."))
    pid, cid = _started(client)
    assert _record(client, pid, cid)["messages"][-1]["failed"] == "technical"
    body = client.post(f"/api/projects/{pid}/messages", json={"chat": cid}).get_data(as_text=True)
    assert _frames(body)[-1] == "done"
    said = _record(client, pid, cid)["messages"]
    assert [m["text"] for m in said] == ["hello", "Here it is."]


def test_a_failed_answer_followed_by_a_message_stays_in_the_record(tmp_path):
    client = _client(tmp_path, engine=FailsThenAnswers(5))
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "again"}).get_data()
    said = _record(client, pid, cid)["messages"]
    assert [(m["text"], m["failed"]) for m in said] == [
        ("hello", ""),
        ("HTTP 502", "technical"),
        ("again", ""),
        ("Done.", ""),
    ]


def _failed_in_a_full_chat(tmp_path):
    """A chat whose last question filled it and whose answer then failed, written to disk.

    30,000 tokens of answer and 21,000 of question: full, and the trim's cut stands before that
    question.
    """
    client = _client(tmp_path)
    pid = _project(client)
    FileChatStore(Store(str(tmp_path))).add(
        pid,
        Chat(
            id="c1",
            title="go",
            created_at="2026-10-09T10:00:00+00:00",
            messages=(
                Message(role="user", at="2026-10-09T10:00:00+00:00", text="go"),
                Message(role="ai", at="2026-10-09T10:01:00+00:00", text="a" * 100_000),
                Message(role="user", at="2026-10-09T10:02:00+00:00", text="b" * 70_000),
                Message(
                    role="ai", at="2026-10-09T10:03:00+00:00", text="HTTP 502", failed="technical"
                ),
            ),
        ),
    )
    return client, pid


def test_try_again_in_a_full_chat_meets_the_ceiling_and_the_failed_answer_stays(tmp_path):
    client, pid = _failed_in_a_full_chat(tmp_path)
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": "c1"})
    assert refused.status_code == 400
    assert "ceiling" in refused.get_json()["error"]
    assert _record(client, pid, "c1")["messages"][-1]["failed"] == "technical"


def test_try_again_after_continue_here_keeps_the_trim(tmp_path):
    # Continue here marks the line's last message, which here is the failed answer. Taking it out
    # must not take the trim with it: the mark moves to the question in front of it.
    client, pid = _failed_in_a_full_chat(tmp_path)
    assert client.post(f"/api/projects/{pid}/chats/c1/trim").status_code == 200
    client.post(f"/api/projects/{pid}/messages", json={"chat": "c1"}).get_data()
    record = _record(client, pid, "c1")
    assert record["trimmed"] == 2
    assert [m["failed"] for m in record["messages"]] == ["", "", "", ""]
    assert record["messages"][-1]["text"] == "Done."


def _silent_with_a_file():
    return ScriptedEngine([[{"tool_calls": [_tool_call("create_file", name="plan.md", content="x")]}], []])


def test_a_call_travels_as_its_own_event(tmp_path):
    # Madde 66: the line has to arrive while the answer is still running, not only with the record.
    engine = ScriptedEngine(
        [[{"tool_calls": [_tool_call("read_file", name="ghost.md")]}], [{"text": "none"}]]
    )
    client = _client(tmp_path, engine=engine)
    _pid, _cid, body = _first_turn(client)
    assert "event: call" in body
    assert '"tool": "read_file"' in body
    assert body.index("event: call") < body.index("event: done")


def test_a_running_turn_reaches_the_browser_as_progress(tmp_path):
    # Madde 194. The turn already knew which round it was on and what it had spent; nothing carried
    # that out to the screen, so a long turn showed three blinking dots and nothing else.
    engine = ScriptedEngine(
        [[{"tool_calls": [_tool_call("read_file", name="ghost.md")]}], [{"text": "none"}]]
    )
    client = _client(tmp_path, engine=engine)
    _pid, _cid, body = _first_turn(client)
    assert "event: progress" in body
    said = json.loads(body.split("event: progress\ndata: ", 1)[1].splitlines()[0])
    assert said == {"round": 1, "of": 32, "tokens": 0}
    # Ahead of the work it is reporting on, or the first thing the screen hears is that a round it
    # never saw begin has ended.
    assert body.index("event: progress") < body.index("event: call")


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
    # Read rather than fired: the answer is written by the generator, and nothing runs until the
    # body is consumed -- which _first_turn does.
    pid, cid, _body = _first_turn(client)
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
    pid, cid, _body = _first_turn(client)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    # This one ran to the end, so the field is there and it is false -- the browser draws from what
    # it is handed and should not have to check whether a field exists.
    assert kept["messages"][-1]["stopped"] is False


def test_the_stored_chat_says_what_the_answer_spent(tmp_path):
    engine = ScriptedEngine(
        [[{"text": "Done."}, {"usage": {"sent": 12400, "cached": 9100, "answered": 842}}]]
    )
    client = _client(tmp_path, engine=engine)
    pid, cid, _body = _first_turn(client)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert kept["messages"][-1]["usage"] == {"sent": 12400, "cached": 9100, "answered": 842}


def test_an_unmeasured_answer_still_carries_the_field(tmp_path):
    # Always present, unlike on disk: the browser draws from what it is handed, and an absent field
    # would make every reader check for it first.
    client = _client(tmp_path)
    pid, cid, _body = _first_turn(client)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()
    assert kept["messages"][-1]["usage"] == {"sent": 0, "cached": 0, "answered": 0}


def test_a_silent_turn_that_made_a_file_closes_the_stream_cleanly(tmp_path):
    # What the user reported as a network error: the model worked without speaking and the stream
    # broke instead of ending.
    client = _client(tmp_path, engine=_silent_with_a_file())
    pid, cid, body = _first_turn(client)
    assert "event: file" in body
    assert "event: done" in body
    assert "event: error" not in body


def test_the_record_keeps_the_silent_answer(tmp_path):
    # Madde 38, kept through Madde 440: a turn that wrote a file and then said nothing is finished,
    # not a failure.
    client = _client(tmp_path, engine=_silent_with_a_file())
    pid, cid, _body = _first_turn(client)
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    assert [m["text"] for m in kept] == ["hello", ""]
    assert kept[-1]["files"] == ["plan.md"]
    assert kept[-1]["failed"] == ""


def test_a_turn_that_produced_nothing_ends_in_a_failed_answer(tmp_path):
    # Neither a word nor a file five times over. Saying so is the server's job, not the browser's
    # guess about the connection, and since Madde 440 it is said on the record.
    client = _client(tmp_path, engine=ScriptedEngine([[]]))
    pid, cid, body = _first_turn(client)
    assert "event: error" not in body
    kept = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    assert [(m["text"], m["failed"]) for m in kept] == [
        ("hello", ""),
        ("The model returned nothing.", "technical"),
    ]


def test_answering_an_unknown_chat_is_400(tmp_path):
    # A chat that is not there cannot be waiting for anything, so this is not a missing address --
    # it is a request that means nothing. Since Madde 88 the door decides that before it streams.
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/messages", json={"chat": "nope"}).status_code == 400


def test_a_new_chat_shows_up_in_the_project_count(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    client.post(f"/api/projects/{pid}/messages", json={"text": "hello"})
    assert client.get("/api/projects").get_json()[0]["chats"] == 1


# --- one model, and the server names it (Madde 82, Madde 358) ------------------------------------


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


def test_a_model_sent_with_a_message_is_not_kept(tmp_path):
    # Madde 358. The server names the model every turn goes to, so a field a browser still sends is
    # read by nothing and written nowhere.
    client = _client(tmp_path)
    pid = _project(client)
    cid = _named(
        client.post(
            f"/api/projects/{pid}/messages", json={"text": "hello", "model": "deepseek-v4-pro"}
        ).get_data(as_text=True)
    )
    assert "model" not in _record(client, pid, cid)["messages"][0]


def test_a_message_on_the_wire_names_no_model_even_when_its_record_does(tmp_path):
    # Madde 146 to 357 wrote the model onto the message. The record keeps it; the screen shows no
    # model, so nothing sends it there.
    client = _client(tmp_path)
    pid = _project(client)
    FileChatStore(Store(str(tmp_path))).add(
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
    cid = _named(
        client.post(
            f"/api/projects/{pid}/messages", json={"text": "hello", "skill": "create-scenario"}
        ).get_data(as_text=True)
    )
    born = _record(client, pid, cid)
    assert "skill" not in born
    assert born["messages"][0]["skill"] == "create-scenario"


def test_a_message_carries_the_skill_it_was_sent_with(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client)
    client.post(
        f"/api/projects/{pid}/messages", json={"chat": cid, "text": "more", "skill": "verify"}
    ).get_data()
    # The first turn's pair carries none; the sentence just sent carries the one it was sent with.
    assert [m["skill"] for m in _record(client, pid, cid)["messages"]][:3] == ["", "", "verify"]


def test_a_selected_skill_reaches_the_engine_as_an_instruction(tmp_path):
    # Madde 27 proved the opposite here -- the choice was recorded and nothing read it. Madde 29
    # lifts that boundary, so the proof moves rather than disappearing: the road from the composer
    # to the engine is one road, and this is where it is checked end to end.
    plain, with_skill = FakeEngine(), FakeEngine()
    client = _client(tmp_path, engine=plain)
    pid, cid, _body = _first_turn(client)

    other = _client(tmp_path / "second", engine=with_skill)
    opid = _project(other)
    other.post(
        f"/api/projects/{opid}/messages", json={"text": "hello", "skill": "edit-prompts"}
    ).get_data()

    # No instruction with no skill selected. The file names are not one: since Madde 127 they ride
    # in every request either way, so they are dropped before the count.
    assert not [
        piece
        for piece in plain.seen
        if piece["role"] == "system" and "project" not in piece["content"]
    ]
    # At the end since Madde 93, where it used to be in front of the message it governed. The
    # claim is unchanged -- the road from the composer to the engine is one road.
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
    # Trying again is sending the same oversized request a second time. The reason has to be the
    # ceiling rather than whatever else the door might have said first -- otherwise the screen
    # tells the user something true and useless.
    client = _answering(tmp_path, LONG)
    pid, cid = _started(client)
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid})
    assert refused.status_code == 400
    assert "ceiling" in refused.get_json()["error"]


def test_a_turn_that_spent_a_lot_but_said_little_does_not_fill_the_chat(tmp_path):
    # Madde 337. Sixty thousand is what the old ceiling read: the whole last request, with its
    # instructions, its tool steps and its opened files. None of that is the conversation.
    client = _answering(tmp_path, "Done.", sent=60_000)
    pid, cid = _started(client)
    kept = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "and more"})
    assert kept.status_code == 200
    kept.get_data()
    said = [message["text"] for message in _record(client, pid, cid)["messages"]]
    assert said[:3] == ["hello", "Done.", "and more"]


def test_the_record_says_how_much_of_the_ceiling_it_has_used(tmp_path):
    # Both numbers, because the gauge draws a share and a share needs its denominator. A second
    # copy of the ceiling living in the browser is the thing that would go stale. "hello" and 995
    # characters of answer are a thousand characters: 300 tokens.
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
        client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "go on"}).get_data()
    return client, pid, cid


def test_a_full_chat_is_trimmed_from_the_start_and_keeps_every_message(tmp_path):
    # "hello" and "go on" are five characters, so each turn is 20,005: nine are 54,013 and full. One
    # turn is 6,001 and two are 12,003, so the cut stands before the ninth question -- message 16 --
    # and the ring reads the one turn still sent.
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
    kept = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "and more"})
    assert kept.status_code == 200
    kept.get_data()
    said = [message["text"] for message in _record(client, pid, cid)["messages"]]
    assert said[-2:] == ["and more", "Done."]


def test_a_chat_that_is_not_full_is_not_trimmed(tmp_path):
    # Continue here is offered only on a full chat (the owner's decision, 28 September), and the rule
    # lives here rather than in the button.
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
    # Always present, like the messages' calls: the line on screen (v9-1d) reads it, and a field
    # that comes and goes makes every reader check for it first.
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert _record(client, pid, cid)["trimmed"] == 0


# --- whether the chat is full, said by the server (Madde 352) ------------------------------------


def test_a_chat_below_the_ceiling_says_it_is_not_full(tmp_path):
    # The notice stands on this field alone: the screen counts nothing (FOUNDATION, Decision 4).
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
    # Until Madde 99 the mode was the request's tool list. Now everything is offered and the mode
    # decides what runs without asking -- so the word's consequence moved, and this is where it is
    # no longer visible.
    from backend.features.workspace.domain.tools import TOOL_SPECS

    engine = ScriptedEngine([[{"text": "Done."}]])
    client = _client(tmp_path, engine)
    pid = _project(client)
    client.post(f"/api/projects/{pid}/messages", json={"text": "hello", "mode": "ask"}).get_data()
    assert engine.tools == [[spec["function"]["name"] for spec in TOOL_SPECS]]


def test_the_mode_is_not_written_to_the_record(tmp_path):
    # Unlike the skill, which the record keeps because a later turn rebuilds its instruction from
    # it. Nothing ever reads a mode back, and a field nothing reads is a question every later
    # reader has to answer for themselves.
    client = _client(tmp_path)
    pid = _project(client)
    body = client.post(
        f"/api/projects/{pid}/messages", json={"text": "hello", "mode": "plan"}
    ).get_data(as_text=True)
    kept = _record(client, pid, _named(body))
    assert not any("mode" in message for message in kept["messages"])


# --- the door the answer comes in by (Madde 99) --------------------------------------------------


def _asking(tmp_path):
    """A client whose second turn wants to write, and a first turn to be born in.

    The chat has to exist before an answer can be left at its door, and a chat is born by being
    answered -- so the first round is an ordinary sentence with no tool in it.
    """
    engine = ScriptedEngine(
        [
            [{"text": "hi"}],
            [{"tool_calls": [_tool_call("create_file", name="plan.md", content="x")]}],
            [{"text": "ok"}],
        ]
    )
    return _client(tmp_path, engine)


def _write(client, pid, cid):
    return client.post(
        f"/api/projects/{pid}/messages", json={"chat": cid, "text": "write it", "mode": "ask"}
    ).get_data(as_text=True)


def test_the_answer_left_at_the_door_lets_the_turn_finish(tmp_path):
    # Answered before the question is asked, on purpose: the registry carries that race already,
    # and the alternative here is a second thread whose timing decides whether the test passes.
    client = _asking(tmp_path)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/permission", json={"allowed": True})
    body = _write(client, pid, cid)
    # Madde 194's progress frames are dropped: this test is about the order of the door, the work
    # and the answer, and a signal that fires every round says nothing about that order.
    assert _steps(body) == ["chat", "permission", "file-start", "file", "call", "done"]
    assert [file["name"] for file in client.get(f"/api/projects/{pid}/files").get_json()] == [
        "plan.md"
    ]


def test_the_question_names_the_tool_and_its_arguments(tmp_path):
    client = _asking(tmp_path)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/permission", json={"allowed": True})
    body = _write(client, pid, cid)
    asked = json.loads(body.split("event: permission\ndata: ", 1)[1].splitlines()[0])
    assert asked["tool"] == "create_file"
    assert json.loads(asked["arguments"]) == {"name": "plan.md", "content": "x"}


def test_a_refusal_at_the_door_writes_no_file_and_the_turn_still_ends(tmp_path):
    client = _asking(tmp_path)
    pid, cid = _started(client)
    client.post(
        f"/api/projects/{pid}/chats/{cid}/permission",
        json={"allowed": False, "reason": "not that one"},
    )
    body = _write(client, pid, cid)
    assert _steps(body) == ["chat", "permission", "call", "done"]
    assert client.get(f"/api/projects/{pid}/files").get_json() == []


def test_answering_a_chat_that_is_not_there_is_a_404(tmp_path):
    # The words as well as the number: an address nobody serves answers 404 too, and without the
    # body this test would pass today for a reason that has nothing to do with the item.
    client = _client(tmp_path)
    pid = _project(client)
    answered = client.post(f"/api/projects/{pid}/chats/nope/permission", json={"allowed": True})
    assert answered.status_code == 404
    assert answered.get_json() == {"error": "chat not found"}


# --- versions of one conversation (Madde 195) ----------------------------------------------------


def _edited(client, pid, chat_id, text, at):
    return client.post(
        f"/api/projects/{pid}/messages", json={"chat": chat_id, "text": text, "from": at}
    ).get_data(as_text=True)


def test_the_transcript_that_comes_back_is_the_open_line(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    _edited(client, pid, cid, "Write a shorter intro", 0)
    said = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    assert [message["text"] for message in said] == ["Write a shorter intro", "Done."]


def test_every_message_carries_the_options_it_stands_among(tmp_path):
    # Always present, like calls: the browser draws from what it is handed, and a field that comes
    # and goes makes every reader check for it first.
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    _edited(client, pid, cid, "Write a shorter intro", 0)
    said = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    standing = said[0]["variants"]
    # The name of a version is minted, so what is pinned is the shape: the first line is the empty
    # name and comes first, and the open one is the second of two.
    assert (standing["index"], standing["of"]) == (1, 2)
    assert standing["versions"][0] == ""
    assert standing["versions"][1]
    assert said[1]["variants"]["of"] == 1


def test_the_answer_to_an_edited_message_is_written_into_its_own_line(tmp_path):
    # The whole reason the edit goes through this door: the turn runs exactly as it always did, and
    # what changes is only which line it lands on.
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    body = _edited(client, pid, cid, "Write a shorter intro", 0)
    assert _frames(body)[-1] == "done"
    stored = json.loads(
        (tmp_path / pid / "chats" / f"{cid}.json").read_text(encoding="utf-8")
    )
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
    said = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    assert [message["text"] for message in said] == ["Write the intro", "Done."]


def test_a_version_nobody_wrote_is_refused_and_changes_nothing(tmp_path):
    client = _client(tmp_path)
    pid, cid = _started(client, "Write the intro")
    _edited(client, pid, cid, "Write a shorter intro", 0)
    refused = client.post(f"/api/projects/{pid}/chats/{cid}/version", json={"version": "ghost"})
    assert refused.status_code == 404
    assert refused.get_json() == {"error": "version not found"}
    said = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    assert [message["text"] for message in said] == ["Write a shorter intro", "Done."]


def test_editing_in_a_chat_that_does_not_exist_is_refused(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    refused = client.post(
        f"/api/projects/{pid}/messages", json={"chat": "ghost", "text": "hi", "from": 0}
    )
    assert refused.status_code == 404
    assert refused.get_json() == {"error": "chat not found"}


def test_the_beat_is_a_frame_the_browser_drops(tmp_path):
    # parseFrame keeps only what carries an event line, so a beat has to carry none. Measured on
    # this side because the front end is Madde 102's work and nothing here touches it. Reached
    # through _sse rather than over HTTP: a real beat costs fifteen seconds of waiting.
    from backend.features.workspace.domain.permission import Waiting
    from backend.features.workspace.presentation.routes import _sse

    written = "".join(_sse("c1", iter([Waiting()])))
    beat = written.split("\n\n")[1]
    assert beat and not beat.startswith("event:")
