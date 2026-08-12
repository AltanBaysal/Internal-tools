import json
from functools import partial

from backend.features.photo_generation.data.order_store import DriveOrderStore
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.domain.usecases.remove_frames import remove_frames
from backend.features.photo_generation.domain.usecases.export_project import export_project
from backend.features.photo_generation.domain.usecases.cancel_generation import cancel_generation
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.list_models import list_models
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.features.photo_generation.domain.usecases.resume_batch import resume_batch
from backend.features.photo_generation.domain.usecases.save_order import save_order
from backend.features.photo_generation.domain.usecases.start_batch import start_batch
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
from backend.features.photo_generation.presentation.routes import make_photo_generation_blueprint
from backend.features.photo_generation.runner import PhotoRunner
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app


class FakeGenerator:
    def __init__(self, installed=("nova.safetensors",)):
        self.installed = list(installed)
        self.calls = []

    def models(self):
        return list(self.installed)

    def generate(self, prompt, negative, seed, model=""):
        self.calls.append((prompt, negative, seed, model))
        return b"PNGDATA"


class StopsAfter:
    """Renders `count` frames, then acts like the session that died: the run pauses and the rest of
    the queue stays owed, with no line in the log. Raise `count` to bring the machine back."""

    def __init__(self, runner, count):
        self.runner = runner
        self.count = count
        self.calls = 0

    def generate(self, prompt, negative, seed, model=""):
        self.calls += 1
        if self.calls > self.count:
            self.runner.request_stop()
            raise RuntimeError("kesildi")
        return b"PNGDATA"


def make_client(tmp_path, generator=None, runner=None):
    drive = tmp_path / "drive"
    (drive / "düğün").mkdir(parents=True)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")

    storage = DriveStorage(str(drive))
    store = DrivePhotoStore(storage)
    record = DrivePhotoRecord(storage)
    plan_store = DrivePlanStore(storage)
    order_store = DriveOrderStore(storage)
    runner = runner or PhotoRunner(spawn=lambda fn: fn())
    generator = generator or FakeGenerator()
    blueprint = make_photo_generation_blueprint(
        start_batch=partial(start_batch, runner, store, record, plan_store,
                            generator, lambda: 42,
                            lambda: "2026-08-03T14:32:11+00:00"),
        get_status=partial(get_status, runner),
        stop_generation=partial(stop_generation, runner, lambda: None),
        resume_batch=partial(resume_batch, runner, store, record, plan_store, generator,
                             lambda: "2026-08-03T14:32:11+00:00"),
        cancel_generation=partial(cancel_generation, runner, store, record, plan_store,
                                  lambda: "2026-08-05T10:00:00+00:00"),
        retry_frame=partial(retry_frame, runner, store, record, plan_store,
                            generator, lambda: "2026-08-03T14:32:11+00:00"),
        list_frames=partial(list_frames, record, store, plan_store, order_store),
        list_models=partial(list_models, generator),
        save_order=partial(save_order, record, store, plan_store, order_store),
        export_project=partial(export_project, record, store, plan_store, order_store),
        remove_frames=partial(remove_frames, record, store, plan_store, order_store,
                              lambda: "2026-08-05T10:00:00+00:00"),
        photo_dir=store.photo_dir,
    )
    app = create_app(dist_dir=str(dist), blueprints=[blueprint])
    return app.test_client(), drive


def generate(client, project="düğün", **body):
    payload = {"prompts": '["kraliçe tahtta"]', "negative": "blurry", "variants": 1, **body}
    return client.post(f"/api/projects/{project}/generate", json=payload)


def test_generate_returns_202_and_writes_every_frame(tmp_path):
    client, drive = make_client(tmp_path)
    resp = generate(client, prompts='["a", "b"]', variants=2)
    assert resp.status_code == 202
    assert sorted(p.name for p in (drive / "düğün").glob("*.png")) == [
        "0_a.png", "0_b.png", "1_a.png", "1_b.png"]


def test_status_reports_the_counts(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=2)
    assert client.get("/api/status").get_json() == {
        "status": "done", "project": "düğün", "done": 4, "failed": 0, "total": 4, "failures": []}


def test_status_is_idle_before_anything_runs(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/status").get_json() == {"status": "idle"}


def test_unreadable_prompt_list_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = generate(client, prompts="tek prompt")
    assert resp.status_code == 400
    assert "liste" in resp.get_json()["error"].lower()


def test_bad_variants_return_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = generate(client, variants=0)
    assert resp.status_code == 400
    assert "Varyant" in resp.get_json()["error"]


def test_missing_variants_return_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post("/api/projects/düğün/generate", json={"prompts": '["a"]'})
    assert resp.status_code == 400


def test_missing_negative_generates_without_one(tmp_path):
    client, drive = make_client(tmp_path)
    resp = client.post("/api/projects/düğün/generate",
                       json={"prompts": '["a"]', "variants": 1})
    assert resp.status_code == 202
    assert (drive / "düğün" / "0_a.png").exists()


def test_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    resp = generate(client, project="yok")
    assert resp.status_code == 404
    assert "yok" in resp.get_json()["error"]


def test_generate_reports_how_many_frames_the_queue_took(tmp_path):
    client, _ = make_client(tmp_path)

    resp = generate(client, prompts='["a", "b"]', variants=3)

    assert resp.status_code == 202
    assert resp.get_json() == {"job": "running", "added": 6}


def test_a_worker_held_by_another_project_returns_409(tmp_path):
    runner = PhotoRunner(spawn=lambda fn: None)
    client, _ = make_client(tmp_path, runner=runner)
    runner.start("başka", lambda: None)

    resp = generate(client)

    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Zaten bir üretim sürüyor."


def test_adding_to_the_running_projects_own_queue_is_accepted(tmp_path):
    client, _ = make_client(tmp_path, runner=PhotoRunner(spawn=lambda fn: None))
    generate(client)
    assert generate(client).status_code == 202


def test_failed_batch_shows_the_real_error_in_status(tmp_path):
    class Broken:
        def generate(self, prompt, negative, seed, model=""):
            raise RuntimeError("node 9 (CheckpointLoaderSimple): dosya yok")

    client, _ = make_client(tmp_path, generator=Broken())
    generate(client, prompts='["a", "b", "c"]', variants=1)
    state = client.get("/api/status").get_json()
    assert state["status"] == "error" and "CheckpointLoaderSimple" in state["error"]


def test_stop_returns_the_current_status(tmp_path):
    client, _ = make_client(tmp_path, runner=PhotoRunner(spawn=lambda fn: None))
    generate(client)
    resp = client.post("/api/stop")
    assert resp.status_code == 200 and resp.get_json()["status"] == "running"


def test_frames_are_listed_newest_first(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    files = [row["file"] for row in
             client.get("/api/projects/düğün/frames").get_json()["frames"]]
    assert files == ["1_a.png", "0_a.png"]


def test_files_without_a_record_row_are_not_listed(tmp_path):
    # The plan and the record are the gallery's list: a file no run produced is not part of it.
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "9_a.png").write_bytes(b"x")
    assert client.get("/api/projects/düğün/frames").get_json() == {"frames": []}


def test_a_listed_frame_carries_the_prompt_behind_it(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["kraliçe tahtta"]', variants=1)
    row = client.get("/api/projects/düğün/frames").get_json()["frames"][0]
    assert row["file"] == "0_a.png" and row["prompt"] == "kraliçe tahtta"
    assert row["status"] == "done"


def test_frames_of_an_unknown_project_return_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/frames").status_code == 404


def test_photo_is_served_from_the_project_folder(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "0_a.png").write_bytes(b"PNGDATA")
    assert client.get("/photos/düğün/0_a.png").data == b"PNGDATA"
    assert client.get("/photos/düğün/yok.png").status_code == 404


def test_photo_response_is_immutably_cacheable(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "0_a.png").write_bytes(b"PNGDATA")
    resp = client.get("/photos/düğün/0_a.png")
    assert resp.status_code == 200
    assert resp.headers["Cache-Control"] == "public, max-age=31536000, immutable"


def files_of(client, project="düğün"):
    return [row["file"] for row in client.get(f"/api/projects/{project}/frames").get_json()["frames"]]


def test_saved_order_decides_how_photos_are_listed(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    assert files_of(client) == ["1_a.png", "0_a.png"]

    resp = client.put("/api/projects/düğün/order", json={"order": ["0_a.png", "1_a.png"]})
    assert resp.status_code == 200
    # The screen sends file names; what is stored and echoed back is the frame's identity.
    assert resp.get_json() == {"order": ["0_a", "1_a"]}
    assert files_of(client) == ["0_a.png", "1_a.png"]


def test_photos_produced_after_a_sort_land_on_top(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    client.put("/api/projects/düğün/order", json={"order": ["0_a.png", "1_a.png"]})

    generate(client, prompts='["c"]', variants=1)

    assert files_of(client) == ["2_a.png", "0_a.png", "1_a.png"]


def test_order_keeps_only_the_names_the_record_knows(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    resp = client.put("/api/projects/düğün/order", json={"order": ["hayalet.png", "0_a.png"]})
    assert resp.get_json() == {"order": ["0_a"]}


def test_order_that_is_not_a_list_of_names_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.put("/api/projects/düğün/order", json={"order": "0_a.png"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Sıra listesi metin dizisi olmalı."


def test_order_of_an_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.put("/api/projects/yok/order", json={"order": []}).status_code == 404


def statuses_of(client, project="düğün"):
    return [(row["file"], row["status"])
            for row in client.get(f"/api/projects/{project}/frames").get_json()["frames"]]


def test_the_gallery_keeps_a_dead_sessions_frames_in_place(tmp_path):
    runner = PhotoRunner(spawn=lambda fn: fn())
    client, _ = make_client(tmp_path, generator=StopsAfter(runner, 1), runner=runner)
    generate(client, prompts='["a", "b"]', variants=1)

    assert statuses_of(client) == [("1_a.png", "pending"), ("0_a.png", "done")]


class RenderFailed(RuntimeError):
    """ComfyUI answered and said the graph failed -- the frame's problem, not the run's."""

    frame_level = True


def test_the_gallery_keeps_a_red_frame_after_the_worker_is_gone(tmp_path):
    class BlowsUpOnce:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed, model=""):
            self.calls += 1
            if self.calls == 1:
                raise RenderFailed("node 41: OOM")
            return b"PNGDATA"

    client, _ = make_client(tmp_path, generator=BlowsUpOnce())
    generate(client, prompts='["a", "b"]', variants=1)

    # Nothing is left in memory: this answer is the plan and the log alone. And the failed frame is
    # drawn once, in its own place -- not as a red tile and a dashed one at the same time.
    assert statuses_of(client) == [("1_a.png", "done"), ("0_a.png", "failed")]


def test_the_models_endpoint_lists_what_the_renderer_has(tmp_path):
    client, _ = make_client(tmp_path,
                            generator=FakeGenerator(installed=["nova.safetensors", "b.safetensors"]))

    resp = client.get("/api/models")

    assert resp.status_code == 200
    assert resp.get_json() == {"models": ["nova.safetensors", "b.safetensors"]}


def test_an_unreachable_renderer_answers_with_its_own_words(tmp_path):
    class Unreachable(FakeGenerator):
        def models(self):
            raise RuntimeError("Connection refused: 127.0.0.1:8188")

    client, _ = make_client(tmp_path, generator=Unreachable())

    resp = client.get("/api/models")

    assert resp.status_code == 502
    assert resp.get_json()["error"] == "Connection refused: 127.0.0.1:8188"


def test_every_frame_of_a_batch_carries_the_chosen_model(tmp_path):
    generator = FakeGenerator()
    client, drive = make_client(tmp_path, generator=generator)

    generate(client, prompts='["a", "b"]', variants=2, model="başka.safetensors")

    assert [model for _p, _n, _s, model in generator.calls] == ["başka.safetensors"] * 4
    plan = json.loads((drive / "düğün" / "plan.json").read_text(encoding="utf-8"))
    assert {frame["model"] for frame in plan["frames"]} == {"başka.safetensors"}


def test_a_batch_sent_without_a_model_renders_with_the_graphs_own(tmp_path):
    generator = FakeGenerator()
    client, _ = make_client(tmp_path, generator=generator)

    generate(client, prompts='["a"]', variants=1)

    assert generator.calls == [("a", "blurry", 42, "")]


def test_a_project_without_a_plan_has_an_empty_gallery(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/düğün/frames").get_json() == {"frames": []}


def test_a_deleted_photo_leaves_the_gallery_for_good(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)

    delete_photos_request(client, ["1_a.png"])

    assert statuses_of(client) == [("0_a.png", "done")]


def test_retry_produces_only_the_named_frame(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    delete_photos_request(client, ["0_a.png"])

    resp = client.post("/api/projects/düğün/retry", json={"file": "0_a.png"})

    assert resp.status_code == 202
    assert (drive / "düğün" / "0_a.png").exists()
    # It comes back where it was, not on top: a frame's place in the gallery is its own.
    assert files_of(client) == ["1_a.png", "0_a.png"]


def test_retry_of_a_frame_the_plan_does_not_know_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    assert client.post("/api/projects/düğün/retry", json={"file": "9_z.png"}).status_code == 404


def test_resume_produces_only_what_the_run_never_got_to(tmp_path):
    runner = PhotoRunner(spawn=lambda fn: fn())
    generator = StopsAfter(runner, 1)
    client, drive = make_client(tmp_path, generator=generator, runner=runner)
    generate(client, prompts='["a", "b"]', variants=1)
    assert not (drive / "düğün" / "1_a.png").exists()

    generator.count = 10                       # the machine is back
    resp = client.post("/api/projects/düğün/resume")

    assert resp.status_code == 202
    assert (drive / "düğün" / "1_a.png").exists()


def test_resume_with_nothing_left_returns_409(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = client.post("/api/projects/düğün/resume")

    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Devam edilecek kare yok."


def test_resume_of_an_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.post("/api/projects/yok/resume").status_code == 404


def test_cancel_empties_the_queue_and_leaves_the_photos(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = client.post("/api/projects/düğün/cancel")

    assert resp.status_code == 204
    assert client.get("/api/status").get_json() == {"status": "idle"}
    assert (drive / "düğün" / "0_a.png").exists()
    assert client.post("/api/projects/düğün/resume").status_code == 409


def delete_photos_request(client, files, project="düğün"):
    return client.post(f"/api/projects/{project}/frames/delete", json={"files": files})


def test_deleting_photos_removes_them_from_the_gallery_and_the_folder(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a", "b", "c"]', variants=1)

    resp = delete_photos_request(client, ["0_a.png", "2_a.png"])

    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": ["0_a.png", "2_a.png"], "removed": []}
    assert files_of(client) == ["1_a.png"]
    assert not (drive / "düğün" / "0_a.png").exists()


def test_pulling_pending_frames_out_leaves_the_photos_alone(tmp_path):
    runner = PhotoRunner(spawn=lambda fn: fn())
    client, drive = make_client(tmp_path, generator=StopsAfter(runner, 1), runner=runner)
    generate(client, prompts='["a", "b", "c"]', variants=1)

    resp = delete_photos_request(client, ["2_a.png", "1_a.png"])

    assert resp.get_json() == {"deleted": [], "removed": ["2_a.png", "1_a.png"]}
    assert statuses_of(client) == [("0_a.png", "done")]
    assert (drive / "düğün" / "0_a.png").exists()


def test_a_photo_produced_after_a_delete_does_not_reuse_the_number(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    delete_photos_request(client, ["0_a.png"])

    generate(client, prompts='["b"]', variants=1)

    assert files_of(client) == ["1_a.png"]


def test_deleting_a_photo_drops_it_from_the_saved_order(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    client.put("/api/projects/düğün/order", json={"order": ["0_a.png", "1_a.png"]})

    delete_photos_request(client, ["0_a.png"])

    assert files_of(client) == ["1_a.png"]


def test_deleting_an_unknown_photo_reports_nothing_deleted(tmp_path):
    client, _ = make_client(tmp_path)
    resp = delete_photos_request(client, ["yok.png"])
    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": [], "removed": []}


def test_a_delete_body_that_is_not_a_list_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    assert delete_photos_request(client, "0_a.png").status_code == 400


def test_deleting_photos_of_an_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert delete_photos_request(client, ["0_a.png"], project="yok").status_code == 404


def test_export_reads_the_gallery_from_the_bottom_up(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    client.put("/api/projects/düğün/order", json={"order": ["0_a.png", "1_a.png"]})

    resp = client.get("/api/projects/düğün/export")

    assert resp.status_code == 200
    assert resp.mimetype == "application/json"
    assert "attachment" in resp.headers["Content-Disposition"]
    body = json.loads(resp.data)
    # The gallery reads 0_a above 1_a; the video starts at the bottom one.
    assert body["photos"] == [{"file": "1_a.png", "prompt": "b"},
                              {"file": "0_a.png", "prompt": "a"}]
    assert body["folder"].endswith("düğün")


def test_export_of_an_empty_project_is_still_a_file(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.get("/api/projects/düğün/export")
    assert resp.status_code == 200
    assert json.loads(resp.data)["photos"] == []


def test_export_of_an_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/export").status_code == 404


def test_a_broken_order_file_does_not_hide_the_gallery(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    (drive / "düğün" / "order.json").write_text("{yarım", encoding="utf-8")
    assert files_of(client) == ["0_a.png"]
