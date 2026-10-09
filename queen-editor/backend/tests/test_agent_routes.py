"""The agent at the door (madde 420): a question asked, the agent stopped, and which chats' agents
are working -- the doors the screen (425) calls.

Wired by hand over a temp folder, the wiring main.py does: the real chat record, the real runner, the
real loop, and a fake box. The gallery's cards come from a fake, the way main.py hands the photo
feature's answer in. The work runs inline where only its end matters, and is held back where the
test has to look while the agent is at work.

The new modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
import copy
from functools import partial

import pytest

from backend.services.deepseek.box import Answer
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

ASKED = "2026-10-06T10:00:00+00:00"
CHATS = "/api/projects/düğün/chats"
QUESTIONS = f"{CHATS}/1/questions"
STOP = f"{CHATS}/1/stop"
WORKING = f"{CHATS}/working"
REFUSED = "Model hata döndü, farklı şekilde dene."
NO_FRAMES = ("Projede henüz kare yok. Prompt'ları yazıp kuyruğa eklediğinde kareler galeride "
             "belirir; sonra sorularını kareler üzerinden cevaplayabilirim.")
# düğün's gallery, top first: P0_0 is frame 1, P1_0 is frame 2.
CARDS = [
    {"id": "P1_0", "status": "done", "layers": {"photo": "P1_0.png"}, "owed": [], "failed": [],
     "errors": {}, "scene": "", "prompts": {"photo": "yeşil elbiseli kadın"}},
    {"id": "P0_0", "status": "done", "layers": {"photo": "P0_0.png"}, "owed": [], "failed": [],
     "errors": {}, "scene": "", "prompts": {"photo": "kırmızı elbiseli kadın"}},
]


def finished(running, done):
    return {"running": running, "done": done, "finished": True}


LOOKED = finished("Projeye bakıyor…", "Projeye baktı")
READ_2 = finished("2 numaralı kareyi okuyor…", "2 numaralı kareyi okudu")
LOOKED_AT_1 = finished("1 numaralı karenin görseline bakıyor…",
                       "1 numaralı karenin görseline baktı")


def call(name, frame, call_id="call_1"):
    return {"id": call_id, "type": "function",
            "function": {"name": name, "arguments": f'{{"frame": {frame}}}'}}


def calling(*calls):
    return Answer("", tool_calls=list(calls))


class FakeBox:
    """Answers each request with the next of `answers`; an entry may be a function, which runs while
    the request is out and returns the answer. Keeps every request as it was sent."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.asked = []

    def converse(self, messages, tools=()):
        self.asked.append((copy.deepcopy(messages), tools))
        answer = self.answers.pop(0)
        return answer() if callable(answer) else answer


def app_over(drive, dist, box, cards=CARDS, hold=False):
    """(client, held) over `drive`, wired the way main.py wires it -- built again over the same
    folder, it is a restart. With `hold`, the work started waits in `held` until the test runs it."""
    from backend.features.agent.data.chat_record import DriveChatRecord
    from backend.features.agent.domain.usecases import chats
    from backend.features.agent.domain.usecases.answer_question import answer_question
    from backend.features.agent.presentation.routes import (
        make_agent_blueprint,
        make_chats_blueprint,
    )
    from backend.features.agent.runner import AgentRunner
    record = DriveChatRecord(DriveStorage(str(drive)))
    held = []
    runner = AgentRunner(record, spawn=held.append if hold else lambda work: work())
    agent = partial(answer_question, box, lambda project: copy.deepcopy(cards),
                    lambda project, file: b"PNG")
    app = create_app(dist_dir=str(dist), blueprints=[
        make_chats_blueprint(new_chat=partial(chats.new_chat, record),
                             list_chats=partial(chats.list_chats, record),
                             open_chat=partial(chats.open_chat, record)),
        make_agent_blueprint(ask_question=partial(chats.ask_question, record, runner, agent,
                                                  lambda: ASKED),
                             stop_agent=partial(chats.stop_agent, record, runner),
                             working_chats=partial(chats.working_chats, record, runner)),
    ])
    return app.test_client(), held


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


def opened(client, chat=1):
    return client.get(f"{CHATS}/{chat}").get_json()


def test_a_question_is_answered_by_reading_the_project(drive, dist):
    box = FakeBox(calling(call("read_frame", 2, "call_1"), call("look_at_frame", 1, "call_2")),
                  Answer("2 numaralı karede yeşil elbiseli bir kadın var."))
    client, _held = app_over(drive, dist, box)
    client.post(CHATS)

    response = client.post(QUESTIONS, json={"text": "2 numaralı karede ne var?"})

    whole = {"id": 1, "questions": [{
        "text": "2 numaralı karede ne var?", "askedAt": ASKED,
        "steps": [LOOKED, READ_2, LOOKED_AT_1],
        "outcome": {"kind": "answer", "text": "2 numaralı karede yeşil elbiseli bir kadın var."}}]}
    assert response.status_code == 200
    assert response.get_json() == whole
    assert opened(client) == whole


def test_the_door_returns_at_once_and_the_answer_lands_later(drive, dist):
    """The agent runs on the server: the page that asked can close, reload or go elsewhere."""
    client, held = app_over(drive, dist, FakeBox(Answer("Projede 2 kare var.")), hold=True)
    client.post(CHATS)

    response = client.post(QUESTIONS, json={"text": "Kaç kare var?"})

    assert response.status_code == 200
    assert response.get_json()["questions"][0]["outcome"] is None
    assert client.get(WORKING).get_json() == {"working": [1]}
    # The page reloaded: the chat is read again, and the agent is still at it.
    assert opened(client)["questions"][0]["outcome"] is None

    held.pop()()

    question = opened(client)["questions"][0]
    assert question["steps"] == [LOOKED]
    assert question["outcome"] == {"kind": "answer", "text": "Projede 2 kare var."}
    assert client.get(WORKING).get_json() == {"working": []}


def test_a_working_chat_takes_no_second_question(drive, dist):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "Kaç kare var?"})

    response = client.post(QUESTIONS, json={"text": "Peki 7?"})

    assert response.status_code == 409
    assert response.get_json() == {"error": "Bu sohbette agent hâlâ çalışıyor."}
    assert [question["text"] for question in opened(client)["questions"]] == ["Kaç kare var?"]


def test_two_chats_work_at_once(drive, dist):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "Birinci"})
    # Chat 1 has a question now, so a new chat is a new one.
    assert client.post(CHATS).get_json()["id"] == 2

    assert client.post(f"{CHATS}/2/questions", json={"text": "İkinci"}).status_code == 200

    assert client.get(WORKING).get_json() == {"working": [1, 2]}


def test_a_stop_keeps_the_finished_steps_and_says_stopped_with_no_half_answer(drive, dist):
    """The model read frame 2 and was reading what it brought when ■ was pressed: that step was going
    on and drops, the look at the project stays, and the words of the round that was out are never
    written (BEHAVIOUR.md, Agent panel)."""
    stops = []

    def pressed_while_out():
        stops.append(client.post(STOP))
        return Answer("Yarım kalan cevap.")

    box = FakeBox(calling(call("read_frame", 2)), pressed_while_out)
    client, held = app_over(drive, dist, box, hold=True)
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "2 numaralı karede ne var?"})

    held.pop()()

    question = opened(client)["questions"][0]
    assert question["steps"] == [LOOKED]
    assert question["outcome"] == {"kind": "stopped"}
    assert stops[0].status_code == 200
    assert stops[0].get_json()["questions"][0] == question
    assert len(box.asked) == 2
    assert client.get(WORKING).get_json() == {"working": []}


def test_a_stopped_chat_takes_a_new_question_at_once(drive, dist):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "Kaç kare var?"})
    client.post(STOP)

    assert client.post(QUESTIONS, json={"text": "Peki 7?"}).status_code == 200


def test_stopping_a_chat_that_is_not_working_changes_nothing(drive, dist):
    client, _held = app_over(drive, dist, FakeBox(Answer("Projede 2 kare var.")))
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "Kaç kare var?"})
    before = opened(client)

    response = client.post(STOP)

    assert response.status_code == 200
    assert response.get_json() == before
    assert opened(client) == before


@pytest.mark.parametrize("failure", [
    Answer(REFUSED, failed=True, refused=True),
    Answer("DeepSeek HTTP 503\nmeşgul", failed=True),
], ids=["refusal", "technical"])
def test_a_refusal_and_a_technical_failure_land_as_failures(drive, dist, failure):
    """One card on the screen, its words the box's (BEHAVIOUR.md, Agent panel)."""
    client, _held = app_over(drive, dist, FakeBox(failure))
    client.post(CHATS)

    question = client.post(QUESTIONS, json={"text": "Kaç kare var?"}).get_json()["questions"][0]

    assert question["steps"] == [LOOKED]
    assert question["outcome"] == {"kind": "failure", "text": failure.text}


def test_a_project_with_no_frames_is_told_so(drive, dist):
    box = FakeBox()
    client, _held = app_over(drive, dist, box, cards=[])
    client.post(CHATS)

    question = client.post(QUESTIONS, json={"text": "Kaç kare var?"}).get_json()["questions"][0]

    assert question["steps"] == [LOOKED]
    assert question["outcome"] == {"kind": "answer", "text": NO_FRAMES}
    assert box.asked == []


def test_after_a_restart_an_unanswered_question_is_not_working_and_takes_a_new_one(drive, dist):
    """What works lives in the process; a restart leaves the question with no outcome and invents
    nothing about why."""
    client, _held = app_over(drive, dist, FakeBox(), hold=True)
    client.post(CHATS)
    client.post(QUESTIONS, json={"text": "Kaç kare var?"})

    restarted, _held = app_over(drive, dist, FakeBox(), hold=True)

    assert restarted.get(WORKING).get_json() == {"working": []}
    assert opened(restarted)["questions"][0]["outcome"] is None
    assert restarted.post(QUESTIONS, json={"text": "Peki 7?"}).status_code == 200


@pytest.mark.parametrize("body", [{"text": ""}, {"text": "   \n"}, {}, {"text": 7}],
                         ids=["empty", "spaces", "no-text", "a-number"])
def test_an_empty_question_is_refused(drive, dist, body):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)
    client.post(CHATS)

    response = client.post(QUESTIONS, json=body)

    assert response.status_code == 400
    assert response.get_json() == {"error": "Soru boş."}
    assert opened(client) == {"id": 1, "questions": []}


@pytest.mark.parametrize("method, url", [("post", "/api/projects/yok/chats/1/questions"),
                                         ("post", "/api/projects/yok/chats/1/stop"),
                                         ("get", "/api/projects/yok/chats/working")])
def test_an_unknown_project_is_a_404_and_no_folder_is_made(drive, dist, method, url):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)

    response = getattr(client, method)(url, json={"text": "Kaç kare var?"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: yok"}
    assert not (drive / "yok").exists()


@pytest.mark.parametrize("url", [f"{CHATS}/7/questions", f"{CHATS}/7/stop"])
def test_an_unknown_chat_is_a_404(drive, dist, url):
    client, _held = app_over(drive, dist, FakeBox(), hold=True)

    response = client.post(url, json={"text": "Kaç kare var?"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Sohbet yok: 7"}


def broken_drive(*_args):
    raise OSError("[Errno 107] Transport endpoint is not connected")


@pytest.mark.parametrize("method, url", [("post", QUESTIONS), ("post", STOP), ("get", WORKING)])
def test_a_disk_error_answers_in_the_systems_own_words(dist, method, url):
    from backend.features.agent.presentation.routes import make_agent_blueprint
    client = create_app(dist_dir=str(dist), blueprints=[
        make_agent_blueprint(ask_question=broken_drive, stop_agent=broken_drive,
                             working_chats=broken_drive)]).test_client()

    response = getattr(client, method)(url, json={"text": "Kaç kare var?"})

    assert response.status_code == 500
    assert response.get_json() == {"error": "[Errno 107] Transport endpoint is not connected"}
