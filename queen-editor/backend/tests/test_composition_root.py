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
import sys

import pytest
import requests

from backend import config
from backend.features.photo_generation.data.comfy_h3_video_generator import ComfyH3VideoGenerator
from backend.features.photo_generation.data.prompt_writer import H3VideoPromptWriter
from backend.features.photo_generation.domain import layers
from backend.tests.test_deepseek_box import Answers, calling
from backend.tests.test_deepseek_client import FakeResponse, answering


def _import_main():
    """backend.main, freshly imported under the environment the test set.

    config reads the environment at import, so config is reloaded rather than re-imported: reload
    keeps the one module object every other importer already holds, and a second config object would
    leave two answers to the same question.
    """
    importlib.reload(config)
    sys.modules.pop("backend.main", None)
    return importlib.import_module("backend.main")


@pytest.fixture
def import_main():
    yield _import_main
    # Every test asks for this fixture before monkeypatch, so the environment is put back first and
    # the config reloaded here is the real one the rest of the suite reads. main is dropped instead of
    # re-imported: on a broken wiring importing it again would raise out of a fixture, which reports
    # as an error on top of the failure it already has.
    sys.modules.pop("backend.main", None)
    importlib.reload(config)


def test_the_app_comes_up_and_answers_health(import_main):
    main = import_main()

    response = main.app.test_client().get("/api/health")

    assert response.status_code == 200


def test_the_queue_tells_the_watch_when_it_starts_and_ends_and_nothing_else_does(import_main):
    """Madde 509 and 518: the queue's worker tells the watch its starts and its endings -- an export
    brings nothing, and the agent has nothing to say to the watch either."""
    from backend.features.agent.runner import _thread_spawn as agent_spawn
    from backend.features.photo_generation.export_runner import _thread_spawn as export_spawn
    main = import_main()

    assert main._photo_runner._started == main._queue_watch.started
    assert main._photo_runner._ended == main._queue_watch.ended
    assert main._export_runner._spawn is export_spawn
    assert main._agent_runner._spawn is agent_spawn


def test_the_app_comes_up_with_the_queue_never_started_nor_ended(import_main):
    main = import_main()

    response = main.app.test_client().get("/api/queue/watch")

    assert response.get_json() == {"started": 0, "ended": 0, "last": None}


def test_a_root_that_is_not_there_is_nobodys_business_until_it_is_asked(import_main, monkeypatch,
                                                                         tmp_path):
    """Madde 472: building the storage door touches no disk, so the app comes up whatever the mount
    is doing -- and the first question asked of a missing root answers with the OS's own words."""
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path / "yok"))
    main = import_main()

    response = main.app.test_client().get("/api/projects")

    assert not (tmp_path / "yok").exists()
    assert response.status_code == 503
    assert "Kök klasöre ulaşılamıyor" in response.get_json()["error"]


@pytest.fixture
def root(monkeypatch, tmp_path):
    """A Drive root that is there and holds nothing: since madde 472 every question is asked of the
    root first, so a door's own answer about a missing project needs a root to stand on."""
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))


def test_the_app_serves_referanstans_record(import_main, root):
    """Madde 317: the door's own tests wire it by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the door's words -- a door never hung would not."""
    main = import_main()

    response = main.app.test_client().get("/api/projects/m317-yok/reference-settings")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m317-yok"}


def test_the_app_hands_a_reference_run_to_the_use_case(import_main, root):
    """Madde 326: main.py hung this door with an argument queue_references does not take, and every
    press came back 500 -- the door's own tests wire it by hand. A missing project is the use case's
    first question, so its answer proves the call got in."""
    main = import_main()

    response = main.app.test_client().post("/api/projects/m326-yok/references/produce",
                                           json={"prompts": '["a"]', "variants": 1})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m326-yok"}


def test_the_app_serves_the_agents_chats(import_main, root):
    """Madde 417: the door's own tests wire it by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the door's words -- a door never hung would not."""
    main = import_main()

    response = main.app.test_client().get("/api/projects/m417-yok/chats")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m417-yok"}


@pytest.mark.parametrize("method, url", [("post", "/api/projects/m420-yok/chats/1/questions"),
                                         ("post", "/api/projects/m420-yok/chats/1/stop"),
                                         ("get", "/api/projects/m420-yok/chats/working"),
                                         ("post", "/api/projects/m420-yok/chats/1/permission")],
                         ids=["ask", "stop", "working", "permission"])
def test_the_app_serves_the_agents_doors(import_main, root, method, url):
    """Madde 420: the doors' own tests wire them by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the doors' words -- a door never hung would not."""
    main = import_main()

    response = getattr(main.app.test_client(), method)(url, json={"text": "Kaç kare var?"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m420-yok"}


def test_the_app_serves_the_projects_video_length(import_main, root):
    """Madde 422: the door's own tests wire it by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the door's words -- a door never hung would not."""
    main = import_main()

    response = main.app.test_client().get("/api/projects/m422-yok/video-length")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m422-yok"}


def test_the_queue_reads_the_projects_video_length(import_main, monkeypatch, tmp_path):
    """The queue's doors read the length the door saved: one store behind both."""
    (tmp_path / "düğün").mkdir()
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))
    main = import_main()

    assert main._video_length("düğün") == 8
    main.app.test_client().put("/api/projects/düğün/video-length", json={"seconds": 12})
    assert main._video_length("düğün") == 12


def test_the_app_serves_the_projects_happy_ending(import_main, root):
    """Madde 426: the door's own tests wire it by hand, so only this one reads main.py's wiring."""
    main = import_main()

    response = main.app.test_client().get("/api/projects/m426-yok/happy-ending")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m426-yok"}


def test_the_queue_reads_the_projects_happy_ending(import_main, monkeypatch, tmp_path):
    """The queue's doors read the switch the door saved: one store behind both."""
    (tmp_path / "düğün").mkdir()
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))
    main = import_main()

    assert main._happy_ending("düğün") is False
    main.app.test_client().put("/api/projects/düğün/happy-ending", json={"on": True})
    assert main._happy_ending("düğün") is True


def test_the_app_serves_the_projects_turned_off_sounds(import_main, root):
    """Madde 510: the door's own tests wire it by hand, so only this one reads main.py's wiring."""
    main = import_main()

    response = main.app.test_client().get("/api/projects/m510-yok/muted")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m510-yok"}


def test_the_export_and_its_summary_read_the_sounds_the_door_turned_off(import_main, monkeypatch,
                                                                        tmp_path):
    """One store behind the door, the export and its summary. The summary is reached through its own
    door: a list it cannot read is a list it read."""
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "muted.json").write_text("{bozuk", encoding="utf-8")
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))
    main = import_main()

    assert main._start_export.keywords["mutes"] is main._mutes
    response = main.app.test_client().get("/api/projects/düğün/export/summary")
    assert response.status_code == 503
    assert "düğün/muted.json okunamıyor" in response.get_json()["error"]


def test_exports_land_in_the_root_the_notebook_hands_over(import_main, monkeypatch, tmp_path):
    """Madde 494: exports have a root of their own beside the projects', which the notebook opens
    and passes as QE_EXPORT_ROOT -- and nothing of theirs goes among the projects."""
    (tmp_path / "projeler").mkdir()
    (tmp_path / "export").mkdir()
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path / "projeler"))
    monkeypatch.setenv("QE_EXPORT_ROOT", str(tmp_path / "export"))
    main = import_main()

    assert main._photo_store.export_dir() == str(tmp_path / "export")


def test_every_session_makes_its_videos_with_h3(import_main, monkeypatch, tmp_path):
    """Madde 435: "wan modelini kaldıralım queen editorden direkt kullanımıyor zaten". The notebook
    names no video model any more, and the app wires H3's producer, H3's writer and the project's
    length in every session -- one with no video installed included, where the producers panel says
    what is missing."""
    (tmp_path / "düğün").mkdir()
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))
    main = import_main()

    assert isinstance(main._producers[layers.VIDEO], ComfyH3VideoGenerator)
    assert isinstance(main._writers[layers.VIDEO], H3VideoPromptWriter)
    assert main._video_length("düğün") == 8


def test_a_krea_frame_reaches_krea_s_graph_and_any_other_the_photo_graph(import_main, monkeypatch,
                                                                         tmp_path):
    """Madde 482: the queue's one photo producer sends each frame to its model's graph. Read off
    the graph ComfyUI is sent, since that is what decides what is drawn."""
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))
    main = import_main()
    sent = []
    monkeypatch.setattr(main._comfy_client, "submit", lambda workflow: sent.append(workflow) or "p1")
    monkeypatch.setattr(main._comfy_client, "wait", lambda prompt_id, timeout: {"outputs": {}})
    monkeypatch.setattr(main._comfy_client, "fetch_output", lambda history: b"PNG")
    photo = main._producers[layers.PHOTO]

    photo.generate("kraliçe tahtta", "", 1, "krea2", "usnr")
    photo.generate("kraliçe tahtta", "", 1, "qwen21turbo", "none")
    photo.generate("kraliçe tahtta", "", 1, "nova3dcg", "usnr")

    krea, qwen, nova = sent
    assert krea["53:19"]["inputs"]["value"] == "kraliçe tahtta"
    # Madde 508: Qwen has no graph any more. A line queued before it left is a value the catalog
    # does not know, so it reaches the photo graph as a file name, which ComfyUI refuses.
    assert qwen["45"]["inputs"]["ckpt_name"] == "qwen21turbo"
    assert nova["45"]["inputs"]["ckpt_name"] == "nova3DCGXL_ilV90.safetensors"


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
    main = import_main()
    read = {"id": "call_1", "type": "function",
            "function": {"name": "read_frame", "arguments": '{"frame": 1}'}}
    look = {"id": "call_2", "type": "function",
            "function": {"name": "look_at_frame", "arguments": '{"frame": 1}'}}
    # Madde 479: the mix-up check is a question of its own through the same box, checked like any
    # words, and its verdict comes back to the conversation as words.
    check = {"id": "call_3", "type": "function",
             "function": {"name": "check_frame", "arguments": '{"frame": 1}'}}
    http = Answers([calling(read, look, check), answering("OK"), answering("APPROVED"),
                    answering("Projede tek kare var: kırmızı elbiseli kadın."),
                    answering("APPROVED")])
    monkeypatch.setattr(requests, "post", http.post)
    run = FakeRun()

    main._agent(run, "düğün", [], "Projede ne var?")

    assert run.wrote[-1] == ("answer", "Projede tek kare var: kırmızı elbiseli kadın.")
    first, checked, _approved, second, _check = http.calls
    assert [tool["function"]["name"] for tool in first["body"]["tools"]] == [
        "read_frame", "look_at_frame", "check_frame", "fix_frame"]
    asked = checked["body"]["messages"][1]["content"]
    assert asked == [{"type": "image_url", "image_url": {
                          "url": "data:image/png;base64," + base64.b64encode(b"PNG").decode()}},
                     {"type": "text", "text": "Prompt: kırmızı elbiseli kadın"}]
    told = second["body"]["messages"]
    assert {"role": "tool", "tool_call_id": "call_3", "content": "Frame 1: OK"} in told
    assert any(message["role"] == "tool" and "kırmızı elbiseli kadın" in message["content"]
               for message in told)
    pictures = [part["image_url"]["url"] for message in told
                if message["role"] == "user" and isinstance(message["content"], list)
                for part in message["content"] if part["type"] == "image_url"]
    assert pictures == ["data:image/png;base64," + base64.b64encode(b"PNG").decode()]
    assert {path.name: path.read_bytes() for path in project.iterdir()} == before


class AllowingRun(FakeRun):
    """A run whose user presses İzin ver on every change (madde 480)."""

    def permit(self, change):
        self.wrote.append(("permit", change))
        return True


def test_the_agent_fixes_a_frame_through_the_photo_feature(import_main, monkeypatch, tmp_path):
    """Madde 481, as main.py wires it: fix_frame reaches the photo feature's fix over the very
    stores the gallery reads. The new line goes into the plan with the frame's seed, model and
    orientation, stands in the old frame's place, the old photo leaves the disk, and the queue is
    started -- held here, so no render leaves this machine."""
    project = tmp_path / "düğün"
    project.mkdir()
    (project / "P0_0.png").write_bytes(b"PNG")
    planned = {"id": "P0_0", "type": "photo", "number": 0, "variant": 0,
               "prompt": "1girl, white hair", "negative": "lowres", "seed": 42,
               "model": "nova.safetensors", "lora": "", "orientation": "yatay"}
    (project / "plan.json").write_text(json.dumps({"frames": [planned]}), encoding="utf-8")
    row = {"file": "P0_0.png", "frame": "P0_0", "layer": "photo", "status": "done",
           "prompt": "1girl, white hair", "negative": "lowres", "seed": 42}
    (project / "photos.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "k-1")
    main = import_main()
    started = []
    monkeypatch.setattr(main._photo_runner, "start",
                        lambda name, job: started.append(name) or True)
    fix = {"id": "call_1", "type": "function",
           "function": {"name": "fix_frame", "arguments": json.dumps(
               {"frame": 1, "prompt": "1girl, black hair", "negative": "lowres, white hair"})}}
    http = Answers([calling(fix), answering("1 düzeltildi."), answering("APPROVED")])
    monkeypatch.setattr(requests, "post", http.post)
    run = AllowingRun()

    main._agent(run, "düğün", [], "düzelt")

    assert run.wrote[-1] == ("answer", "1 düzeltildi.")
    assert ("permit", {"title": "1 numaralı kare düzeltilecek", "details": [
        {"label": "Prompt", "before": "1girl, white hair", "after": "1girl, black hair"},
        {"label": "Negatif prompt", "before": "lowres", "after": "lowres, white hair"},
        {"label": "Fotoğraf", "text": "Eski fotoğraf silinecek; yenisi aynı yerde üretilecek."},
    ]}) in run.wrote
    plan = json.loads((project / "plan.json").read_text(encoding="utf-8"))["frames"]
    assert plan[-1] == {"id": "P1_0", "type": "photo", "number": 1, "variant": 0,
                        "prompt": "1girl, black hair", "negative": "lowres, white hair",
                        "seed": 42, "model": "nova.safetensors", "lora": "",
                        "orientation": "yatay"}
    assert json.loads((project / "order.json").read_text(encoding="utf-8")) == {"order": ["P1_0"]}
    assert not (project / "P0_0.png").exists()
    last = json.loads((project / "photos.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert (last["frame"], last["layer"], last["status"]) == ("P0_0", "photo", "deleted")
    assert started == ["düğün"]


PHOTO = ("P0_0.png", b"PNG")


def _refusal(main, kind):
    """What the session's writer for `kind` says with no key -- the sentence of the model it would
    have asked. No request leaves: a missing key is refused before one is built."""
    with pytest.raises(RuntimeError) as refused:
        main._writers[kind].write({"photo": "kırmızı elbiseli kadın", "video": "kadın dönüyor"},
                                  "standard", source=PHOTO, scene="")
    return str(refused.value)


def test_the_video_prompt_is_queen_ai_s(import_main, monkeypatch):
    """Madde 400: DeepSeek writes H3's prompt, looking at the photo."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "")
    main = import_main()

    assert "DEEPSEEK_API_KEY" in _refusal(main, layers.VIDEO)


def test_nothing_makes_a_sound_any_more(import_main):
    """Madde 514, the user's words: "mmaudio zaten silenecek roadmape ekle sil". No producer and no
    prompt writer for a sound: the sounds already made stay, and no new one is made."""
    main = import_main()

    assert set(main._producers) == {layers.PHOTO, layers.VIDEO}
    assert set(main._writers) == {layers.VIDEO}


class _OwedSound:
    """A project whose frame has its photo and video, and a sound the queue still owes -- the
    plan, the record and the runner make_job asks of, and nothing else. A line written is kept, so
    the test can say none was."""

    def __init__(self):
        from backend.features.photo_generation.domain.running_name import RunningName
        self.named = RunningName("düğün")
        self.written = []

    def read(self, _project):
        return {"frames": [{"id": "P0_0", "type": "audio", "number": 0, "variant": 0,
                            "prompt": "", "negative": "", "seed": None, "model": ""}]}

    def slots(self, _project):
        return {"P0_0": {"photo": {"status": "done", "file": "P0_0.png"},
                         "video": {"status": "done", "file": "P0_0_V1_0.mp4"}}}

    def append(self, *line):
        self.written.append(line)

    def mark(self, *line, **_said):
        self.written.append(line)

    def stop_requested(self):
        return False

    def report(self, _state):
        pass


def test_a_sound_still_owed_stops_the_queue_and_asks_nobody(import_main, monkeypatch):
    """Madde 514: a sound queued before MMAudio went waits as any job whose producer is not here --
    run_loop's own rule, and the ending 509's notification names. Its prompt is not written: no
    request leaves for DeepSeek, and no line is written, so the job stays owed until the user takes
    it out (Sesleri sil, or clearing the queue)."""
    from backend.features.photo_generation.domain.run_loop import make_job
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "k-1")
    main = import_main()
    monkeypatch.setattr(requests, "post", lambda *a, **k: pytest.fail("DeepSeek'e istek gitti"))
    project = _OwedSound()

    state = make_job(project, None, project, project, main._producers, lambda: "now",
                     writers=main._writers)()

    assert (state["status"], state["waitingFor"]) == ("waiting", layers.AUDIO)
    assert project.written == []


def test_the_deepseek_key_comes_from_the_environment(import_main, monkeypatch):
    """The notebook hands it over as QE_DEEPSEEK_API_KEY, the way every setting of this app
    travels. The model and its address are DeepSeek's own, the ones QueenAgent speaks to."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "ds-1")
    import_main()

    assert config.DEEPSEEK_API_KEY == "ds-1"
    assert config.DEEPSEEK_MODEL == "deepseek-flash"
    assert config.DEEPSEEK_URL == "https://api.deepseek.com/chat/completions"


def test_every_queen_ai_prompt_goes_through_the_box(import_main, monkeypatch):
    """Madde 416 and 418: H3's writer, as main.py wires it, has a failed request sent again and the
    answer checked -- four HTTP errors, then the fifth try's answer and the check's approval, and
    that answer is the prompt. requests.post is the one the client sends with, so no request leaves
    this machine."""
    monkeypatch.setenv("QE_DEEPSEEK_API_KEY", "k-1")
    main = import_main()
    http = Answers([FakeResponse(status_code=500, text="iç hata")] * 4
                   + [answering("she turns"), answering("APPROVED")])
    monkeypatch.setattr(requests, "post", http.post)

    written = main._writers[layers.VIDEO].write({"photo": "kırmızı elbiseli kadın",
                                         "video": "kadın dönüyor"},
                                        "standard", source=PHOTO, scene="")

    assert written == "she turns"
    assert len(http.calls) == 6
