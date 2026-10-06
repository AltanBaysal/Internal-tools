"""The composition root itself: proof that backend/main.py imports and serves.

Every other test builds its own object graph out of fakes, so main.py -- the one place concrete
classes are wired (CODE-STANDARD) -- was the file the suite never read. A name used above the line
that defines it broke Flask at import, the suite stayed green, and the break reached the user in
Colab instead (madde 309).

What is asserted is what the notebook waits for: the module comes up, and its app answers
/api/health. Nothing is faked because nothing in the graph reaches out at construction -- paths are
joined, weights are loaded on the first render, and torch is imported inside it.
"""
import base64
import importlib
import json
import os
import sys

import pytest
import requests

from backend import config
from backend.features.photo_generation.domain import layers
from backend.tests.test_deepseek_box import Answers, calling
from backend.tests.test_deepseek_client import FakeResponse, answering

VIDEO_MODEL = "QE_VIDEO_MODEL"


def _import_main(video_model):
    """backend.main, freshly imported under one video model.

    config reads the environment at import and main branches on what it read, so config is reloaded
    rather than re-imported: reload keeps the one module object every other importer already holds,
    and a second config object would leave two answers to the same question.
    """
    os.environ[VIDEO_MODEL] = video_model
    importlib.reload(config)
    sys.modules.pop("backend.main", None)
    return importlib.import_module("backend.main")


@pytest.fixture
def import_main():
    before = os.environ.get(VIDEO_MODEL)
    yield _import_main
    if before is None:
        os.environ.pop(VIDEO_MODEL, None)
    else:
        os.environ[VIDEO_MODEL] = before
    # The environment is what it was, so config is reloaded once more and the rest of the suite
    # reads the real one. main is dropped instead of re-imported: on a broken wiring importing it
    # again would raise out of a fixture, which reports as an error on top of the failure it
    # already has.
    sys.modules.pop("backend.main", None)
    importlib.reload(config)


@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_comes_up_and_answers_health(import_main, video_model):
    """Both video producers are wired at module level, each in its own branch, and Colab runs h3 --
    so one import would leave the branch the user actually runs unread."""
    main = import_main(video_model)

    response = main.app.test_client().get("/api/health")

    assert response.status_code == 200


@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_serves_referanstans_record(import_main, video_model):
    """Madde 317: the door's own tests wire it by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the door's words -- a door never hung would not."""
    main = import_main(video_model)

    response = main.app.test_client().get("/api/projects/m317-yok/reference-settings")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m317-yok"}


@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_hands_a_reference_run_to_the_use_case(import_main, video_model):
    """Madde 326: main.py hung this door with an argument queue_references does not take, and every
    press came back 500 -- the door's own tests wire it by hand. A missing project is the use case's
    first question, so its answer proves the call got in."""
    main = import_main(video_model)

    response = main.app.test_client().post("/api/projects/m326-yok/references/produce",
                                           json={"prompts": '["a"]', "variants": 1})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m326-yok"}


@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_serves_the_agents_chats(import_main, video_model):
    """Madde 417: the door's own tests wire it by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the door's words -- a door never hung would not."""
    main = import_main(video_model)

    response = main.app.test_client().get("/api/projects/m417-yok/chats")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m417-yok"}


@pytest.mark.parametrize("video_model", ["", "h3"])
@pytest.mark.parametrize("method, url", [("post", "/api/projects/m420-yok/chats/1/questions"),
                                         ("post", "/api/projects/m420-yok/chats/1/stop"),
                                         ("get", "/api/projects/m420-yok/chats/working")],
                         ids=["ask", "stop", "working"])
def test_the_app_serves_the_agents_doors(import_main, video_model, method, url):
    """Madde 420: the doors' own tests wire them by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the doors' words -- a door never hung would not."""
    main = import_main(video_model)

    response = getattr(main.app.test_client(), method)(url, json={"text": "Kaç kare var?"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m420-yok"}


@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_serves_the_projects_video_length(import_main, video_model):
    """Madde 422: the door's own tests wire it by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the door's words -- a door never hung would not."""
    main = import_main(video_model)

    response = main.app.test_client().get("/api/projects/m422-yok/video-length")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m422-yok"}


def test_an_h3_session_queues_its_videos_at_the_projects_length(import_main, monkeypatch,
                                                                tmp_path):
    """The queue's doors read the length the door saved: one store behind both."""
    (tmp_path / "düğün").mkdir()
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))
    main = import_main("h3")

    assert main._video_length("düğün") == 8
    main.app.test_client().put("/api/projects/düğün/video-length", json={"seconds": 12})
    assert main._video_length("düğün") == 12


def test_a_wan_session_queues_its_videos_with_no_length(import_main):
    """"h3e özel": a WAN video runs as long as its graph says."""
    main = import_main("")

    assert main._video_length is None


class FakeRun:
    """The question being answered: writes down what the agent writes to the chat."""

    def __init__(self):
        self.wrote = []

    def stopped(self):
        return False

    def add_step(self, running, done):
        self.wrote.append(("step", running, done))

    def finish_step(self):
        self.wrote.append(("stepDone",))

    def answer(self, text):
        self.wrote.append(("answer", text))

    def fail(self, text):
        self.wrote.append(("failure", text))


def test_the_agent_reads_the_open_project_through_the_box_and_changes_nothing(
        import_main, monkeypatch, tmp_path):
    """Madde 420, as main.py wires it: the agent reads the gallery's cards and a frame's photo out of
    the open project, asks Queen AI through the box -- the tool calls go unchecked, the words are
    checked -- and writes nothing into the project ("yani bir değişilik yapamasın"). requests.post is
    the one the client sends with, so no request leaves this machine."""
    project = tmp_path / "düğün"
    project.mkdir()
    (project / "P0_0.png").write_bytes(b"PNG")
    row = {"file": "P0_0.png", "frame": "P0_0", "layer": "photo", "status": "done",
           "prompt": "kırmızı elbiseli kadın"}
    (project / "photos.jsonl").write_text(json.dumps(row, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    before = {path.name: path.read_bytes() for path in project.iterdir()}
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "k-1")
    main = import_main("h3")
    read = {"id": "call_1", "type": "function",
            "function": {"name": "read_frame", "arguments": '{"frame": 1}'}}
    look = {"id": "call_2", "type": "function",
            "function": {"name": "look_at_frame", "arguments": '{"frame": 1}'}}
    http = Answers([calling(read, look), answering("Projede tek kare var: kırmızı elbiseli kadın."),
                    answering("APPROVED")])
    monkeypatch.setattr(requests, "post", http.post)
    run = FakeRun()

    main._agent(run, "düğün", [], "Projede ne var?")

    assert run.wrote[-1] == ("answer", "Projede tek kare var: kırmızı elbiseli kadın.")
    first, second, _check = http.calls
    assert [tool["function"]["name"] for tool in first["body"]["tools"]] == ["read_frame",
                                                                             "look_at_frame"]
    told = second["body"]["messages"]
    assert any(message["role"] == "tool" and "kırmızı elbiseli kadın" in message["content"]
               for message in told)
    pictures = [part["image_url"]["url"] for message in told
                if message["role"] == "user" and isinstance(message["content"], list)
                for part in message["content"] if part["type"] == "image_url"]
    assert pictures == ["data:image/png;base64," + base64.b64encode(b"PNG").decode()]
    assert {path.name: path.read_bytes() for path in project.iterdir()} == before


PHOTO = ("P0_0.png", b"PNG")


def _refusal(main, kind):
    """What the session's writer for `kind` says with no key -- the sentence of the model it would
    have asked. No request leaves: a missing key is refused before one is built."""
    with pytest.raises(RuntimeError) as refused:
        main._writers[kind].write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                                  "standard", source=PHOTO, scene="")
    return str(refused.value)


def test_an_h3_session_s_video_prompt_is_queen_ai_s(import_main, monkeypatch):
    """Madde 400: DeepSeek writes H3's prompt, looking at the photo."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "")
    main = import_main("h3")

    assert "DEEPSEEK_API_KEY" in _refusal(main, layers.VIDEO)


def test_a_wan_session_s_video_prompt_is_queen_ai_s(import_main, monkeypatch):
    """Madde 404: DeepSeek writes WAN's prompt too. With no key the sentence names the model the
    writer asks -- and no request leaves."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "")
    main = import_main("")

    assert "DEEPSEEK_API_KEY" in _refusal(main, layers.VIDEO)


@pytest.mark.parametrize("video_model", ["", "h3"])
def test_every_session_s_sound_prompt_is_queen_ai_s(import_main, monkeypatch, video_model):
    """Madde 404: the sound is written by Queen AI in a session of either video model."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "")
    main = import_main(video_model)

    assert "DEEPSEEK_API_KEY" in _refusal(main, layers.AUDIO)


def test_the_deepseek_key_comes_from_the_environment(import_main, monkeypatch):
    """The notebook hands it over as QE_DEEPSEEK_API_KEY, the way every setting of this app
    travels. The model and its address are DeepSeek's own, the ones QueenAgent speaks to."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "ds-1")
    import_main("h3")

    assert config.DEEPSEEK_API_KEY == "ds-1"
    assert config.DEEPSEEK_MODEL == "deepseek-flash"
    assert config.DEEPSEEK_URL == "https://api.deepseek.com/chat/completions"


@pytest.mark.parametrize("video_model, kind", [
    ("h3", layers.VIDEO), ("", layers.VIDEO), ("h3", layers.AUDIO), ("", layers.AUDIO),
], ids=["h3-video", "wan-video", "h3-sound", "wan-sound"])
def test_every_queen_ai_prompt_goes_through_the_box(import_main, monkeypatch, video_model, kind):
    """Madde 416 and 418: H3's, WAN's and the sound's writer, as main.py wires them, have a failed
    request sent again and the answer checked -- four HTTP errors, then the fifth try's answer and
    the check's approval, and that answer is the prompt. requests.post is the one the client sends
    with, so no request leaves this machine."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "k-1")
    main = import_main(video_model)
    http = Answers([FakeResponse(status_code=500, text="iç hata")] * 4
                   + [answering("she turns"), answering("APPROVED")])
    monkeypatch.setattr(requests, "post", http.post)

    written = main._writers[kind].write({"photo": "kırmızı elbiseli kadın",
                                         "video": "kadın dönüyor"},
                                        "standard", source=PHOTO, scene="")

    assert written == "she turns"
    assert len(http.calls) == 6
