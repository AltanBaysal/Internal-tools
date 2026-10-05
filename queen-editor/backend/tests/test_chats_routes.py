"""The agent's chats over HTTP (madde 417): a new chat, the list, one chat opened -- and no delete.

The door is wired by hand over a temp folder, the wiring main.py does. What 420's agent will write
-- a question, its steps, its outcome -- the tests write through the record itself: no door takes
them yet.

The new modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
from functools import partial

import pytest

from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

ASKED = "2026-10-06T10:00:00+00:00"
CHATS = "/api/projects/düğün/chats"
READING = ("3 numaralı kareyi okuyor…", "3 numaralı kareyi okudu")
LOOKING = ("Bir görsele bakıyor…", "Bir görsele baktı")
WHOLE = {"id": 1, "questions": [{
    "text": "Kaç kare var?", "askedAt": ASKED,
    "steps": [{"running": READING[0], "done": READING[1], "finished": True},
              {"running": LOOKING[0], "done": LOOKING[1], "finished": True}],
    "outcome": {"kind": "answer", "text": "Projede 12 kare var."}}]}
ROW = {"id": 1, "firstQuestion": "Kaç kare var?", "lastAskedAt": ASKED}


def client_with(dist, blueprint):
    return create_app(dist_dir=str(dist), blueprints=[blueprint]).test_client()


def app_over(drive, dist):
    """(client, record) over `drive` -- built again over the same folder, it is a restart."""
    from backend.features.agent.data.chat_record import DriveChatRecord
    from backend.features.agent.domain.usecases.chats import list_chats, new_chat, open_chat
    from backend.features.agent.presentation.routes import make_chats_blueprint
    record = DriveChatRecord(DriveStorage(str(drive)))
    blueprint = make_chats_blueprint(new_chat=partial(new_chat, record),
                                     list_chats=partial(list_chats, record),
                                     open_chat=partial(open_chat, record))
    return client_with(dist, blueprint), record


@pytest.fixture
def dist(tmp_path):
    folder = tmp_path / "dist"
    folder.mkdir()
    (folder / "index.html").write_text("x", encoding="utf-8")
    return folder


@pytest.fixture
def drive(tmp_path):
    """A root holding one project, düğün."""
    root = tmp_path / "drive"
    (root / "düğün").mkdir(parents=True)
    return root


@pytest.fixture
def server(drive, dist):
    return app_over(drive, dist)


def answered(record, project="düğün", chat=1):
    """What 420's agent will write: a question, two finished steps, an answer."""
    record.add_question(project, chat, "Kaç kare var?", ASKED)
    for running, done in (READING, LOOKING):
        record.add_step(project, chat, running, done)
        record.finish_step(project, chat)
    record.answer(project, chat, "Projede 12 kare var.")


def test_a_new_chat_comes_back_empty(server):
    client, _record = server

    response = client.post(CHATS)

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "questions": []}


def test_asking_for_a_new_chat_twice_gives_the_waiting_one(server):
    client, _record = server

    assert client.post(CHATS).get_json()["id"] == 1
    assert client.post(CHATS).get_json()["id"] == 1
    # An empty chat is never listed.
    assert client.get(CHATS).get_json() == {"chats": []}


def test_a_chat_with_a_question_is_listed_and_opens_whole(server):
    client, record = server
    client.post(CHATS)
    answered(record)

    assert client.get(CHATS).get_json() == {"chats": [ROW]}
    response = client.get(f"{CHATS}/1")
    assert response.status_code == 200
    assert response.get_json() == WHOLE


def test_a_new_chat_after_a_question_is_a_new_one(server):
    client, record = server
    client.post(CHATS)
    record.add_question("düğün", 1, "Kaç kare var?", ASKED)

    assert client.post(CHATS).get_json() == {"id": 2, "questions": []}


def test_the_chats_are_still_there_after_a_restart(server, drive, dist):
    client, record = server
    client.post(CHATS)
    answered(record)

    restarted, _record = app_over(drive, dist)

    assert restarted.get(CHATS).get_json() == {"chats": [ROW]}
    assert restarted.get(f"{CHATS}/1").get_json() == WHOLE


def test_another_projects_chats_are_never_visible(server, drive):
    client, record = server
    (drive / "kına").mkdir()
    client.post(CHATS)
    answered(record)

    assert client.get("/api/projects/kına/chats").get_json() == {"chats": []}
    response = client.get("/api/projects/kına/chats/1")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Sohbet yok: 1"}


@pytest.mark.parametrize("method, url", [("post", "/api/projects/yok/chats"),
                                         ("get", "/api/projects/yok/chats"),
                                         ("get", "/api/projects/yok/chats/1")])
def test_an_unknown_project_is_a_404(server, method, url):
    client, _record = server

    response = getattr(client, method)(url)

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: yok"}


def test_a_new_chat_never_creates_a_project(server, drive):
    # Every folder under the root is a project: a write to an unknown name must not conjure one.
    client, _record = server

    client.post("/api/projects/yok/chats")

    assert not (drive / "yok").exists()


def test_an_unknown_chat_is_a_404(server):
    client, _record = server

    response = client.get(f"{CHATS}/7")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Sohbet yok: 7"}


def test_there_is_no_door_to_delete_a_chat(server):
    """A chat is never deleted (madde 417)."""
    client, record = server
    client.post(CHATS)
    answered(record)

    assert client.delete(f"{CHATS}/1").status_code == 405
    assert client.get(f"{CHATS}/1").get_json() == WHOLE


def broken_drive(*_args):
    raise OSError("[Errno 107] Transport endpoint is not connected")


@pytest.mark.parametrize("method, url", [("post", CHATS), ("get", CHATS), ("get", f"{CHATS}/1")])
def test_a_disk_error_answers_in_the_systems_own_words(dist, method, url):
    from backend.features.agent.presentation.routes import make_chats_blueprint
    client = client_with(dist, make_chats_blueprint(new_chat=broken_drive, list_chats=broken_drive,
                                                    open_chat=broken_drive))

    response = getattr(client, method)(url)

    assert response.status_code == 500
    assert response.get_json() == {"error": "[Errno 107] Transport endpoint is not connected"}
