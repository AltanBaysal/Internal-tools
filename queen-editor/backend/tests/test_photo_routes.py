import json
from functools import partial

from backend.features.photo_generation.data.order_store import DriveOrderStore
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.usecases.copy_frames import copy_frames
from backend.features.photo_generation.domain.usecases.remove_frames import remove_frames
from backend.features.photo_generation.domain.usecases.export_summary import export_summary
from backend.features.photo_generation.domain.usecases.run_export import start_export
from backend.features.photo_generation.export_runner import MODES, ExportRunner
from backend.features.photo_generation.domain.usecases.cancel_generation import cancel_generation
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.list_models import list_models
from backend.features.photo_generation.domain.usecases.queue_layer import queue_layer
from backend.features.photo_generation.domain.usecases.regenerate import regenerate
from backend.features.photo_generation.domain.usecases.remove_layer import remove_layer
from backend.features.photo_generation.domain.usecases.retry_failed import retry_failed
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

    def generate(self, prompt, negative, seed, model="", source=None, end=None):
        self.calls.append((prompt, negative, seed, model))
        return b"PNGDATA"


class StopsAfter:
    """Renders `count` frames, then acts like the session that died: the run pauses and the rest of
    the queue stays owed, with no line in the log. Raise `count` to bring the machine back."""

    def __init__(self, runner, count):
        self.runner = runner
        self.count = count
        self.calls = 0

    def generate(self, prompt, negative, seed, model="", source=None, end=None):
        self.calls += 1
        if self.calls > self.count:
            self.runner.request_stop()
            raise RuntimeError("kesildi")
        return b"PNGDATA"


class RecordingExporter:
    """Writes nothing: what the endpoint tests care about is that the run was started at all."""

    def __init__(self):
        self.pieces = []

    def piece(self, video, audio, target):
        self.pieces.append(target)

    def merge(self, pieces, target):
        self.pieces.append(target)


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
    export_runner = ExportRunner(spawn=lambda fn: fn())
    exporter = RecordingExporter()
    generator = generator or FakeGenerator()
    producers = {layers.PHOTO: generator}
    blueprint = make_photo_generation_blueprint(
        start_batch=partial(start_batch, runner, store, record, plan_store,
                            producers, lambda: 42,
                            lambda: "2026-08-03T14:32:11+00:00"),
        get_status=partial(get_status, runner),
        stop_generation=partial(stop_generation, runner, lambda: None),
        resume_batch=partial(resume_batch, runner, store, record, plan_store, producers,
                             lambda: "2026-08-03T14:32:11+00:00"),
        cancel_generation=partial(cancel_generation, runner, store, record, plan_store,
                                  lambda: "2026-08-05T10:00:00+00:00"),
        retry_frame=partial(retry_frame, runner, store, record, plan_store,
                            producers, lambda: "2026-08-03T14:32:11+00:00"),
        retry_failed=partial(retry_failed, runner, store, record, plan_store,
                             producers, lambda: "2026-08-03T14:32:11+00:00"),
        queue_layer=partial(queue_layer, runner, store, record, plan_store, order_store,
                            producers, lambda: "2026-08-03T14:32:11+00:00"),
        regenerate=partial(regenerate, runner, store, record, plan_store, order_store,
                           producers, lambda: 42, lambda: "2026-08-03T14:32:11+00:00"),
        remove_layer=partial(remove_layer, record, store, plan_store, order_store,
                             lambda: "2026-08-05T10:00:00+00:00"),
        list_frames=partial(list_frames, record, store, plan_store, order_store),
        list_models=partial(list_models, generator),
        save_order=partial(save_order, record, store, plan_store, order_store),
        export_summary=partial(export_summary, record, store, plan_store, order_store,
                               lambda: 5),
        export_state=export_runner.state,
        run_export=partial(start_export, export_runner, store, record, plan_store, order_store,
                           exporter, lambda: "2026-08-12 14-32"),
        cancel_export=lambda: [export_runner.cancel(mode) for mode in MODES],
        remove_frames=partial(remove_frames, record, store, plan_store, order_store,
                              lambda: "2026-08-05T10:00:00+00:00"),
        copy_frames=partial(copy_frames, record, store, plan_store, order_store,
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
        "P0_0.png", "P0_1.png", "P1_0.png", "P1_1.png"]


def test_queueing_answers_with_the_gallery_it_just_made(tmp_path):
    # Otherwise the screen has to ask for the gallery in a second round-trip, and the frames it was
    # just told about are nowhere until that lands.
    client, _ = make_client(tmp_path)

    resp = generate(client, prompts='["a"]', variants=1)

    body = resp.get_json()
    assert body["added"] == 1
    assert [frame["id"] for frame in body["frames"]] == ["P0_0"]


def test_queueing_a_layer_answers_with_the_gallery_too(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = client.post("/api/projects/düğün/layers/video", json={})

    assert resp.status_code == 202
    assert [frame["id"] for frame in resp.get_json()["frames"]] == ["P0_0"]


def test_a_refused_batch_answers_with_the_error_alone(tmp_path):
    client, _ = make_client(tmp_path)

    resp = generate(client, prompts="")

    assert resp.status_code == 400
    assert "frames" not in resp.get_json()


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
    assert (drive / "düğün" / "P0_0.png").exists()


def test_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    resp = generate(client, project="yok")
    assert resp.status_code == 404
    assert "yok" in resp.get_json()["error"]


def test_generate_reports_how_many_frames_the_queue_took(tmp_path):
    client, _ = make_client(tmp_path)

    resp = generate(client, prompts='["a", "b"]', variants=3)

    assert resp.status_code == 202
    body = resp.get_json()
    # The count is its own answer, not something the screen derives by measuring the gallery.
    assert body["job"] == "running" and body["added"] == 6


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
        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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
    assert files == ["P1_0.png", "P0_0.png"]


def test_files_without_a_record_row_are_not_listed(tmp_path):
    # The plan and the record are the gallery's list: a file no run produced is not part of it.
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "9_a.png").write_bytes(b"x")
    assert client.get("/api/projects/düğün/frames").get_json() == {"frames": []}


def test_a_listed_frame_carries_the_prompt_behind_it(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["kraliçe tahtta"]', variants=1)
    row = client.get("/api/projects/düğün/frames").get_json()["frames"][0]
    assert row["file"] == "P0_0.png" and row["prompt"] == "kraliçe tahtta"
    assert row["status"] == "done"


def test_frames_of_an_unknown_project_return_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/frames").status_code == 404


def test_photo_is_served_from_the_project_folder(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "P0_0.png").write_bytes(b"PNGDATA")
    assert client.get("/photos/düğün/P0_0.png").data == b"PNGDATA"
    assert client.get("/photos/düğün/yok.png").status_code == 404


def test_photo_response_is_immutably_cacheable(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "P0_0.png").write_bytes(b"PNGDATA")
    resp = client.get("/photos/düğün/P0_0.png")
    assert resp.status_code == 200
    assert resp.headers["Cache-Control"] == "public, max-age=31536000, immutable"


def files_of(client, project="düğün"):
    return [row["file"] for row in client.get(f"/api/projects/{project}/frames").get_json()["frames"]]


def test_saved_order_decides_how_photos_are_listed(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    assert files_of(client) == ["P1_0.png", "P0_0.png"]

    resp = client.put("/api/projects/düğün/order", json={"order": ["P0_0", "P1_0"]})
    assert resp.status_code == 200
    # Identities in, identities out: one picture can stand under two frames.
    assert resp.get_json() == {"order": ["P0_0", "P1_0"]}
    assert files_of(client) == ["P0_0.png", "P1_0.png"]


def test_photos_produced_after_a_sort_land_on_top(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    client.put("/api/projects/düğün/order", json={"order": ["P0_0", "P1_0"]})

    generate(client, prompts='["c"]', variants=1)

    assert files_of(client) == ["P2_0.png", "P0_0.png", "P1_0.png"]


def test_order_keeps_only_the_names_the_record_knows(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    resp = client.put("/api/projects/düğün/order", json={"order": ["hayalet", "P0_0"]})
    assert resp.get_json() == {"order": ["P0_0"]}


def test_order_that_is_not_a_list_of_names_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.put("/api/projects/düğün/order", json={"order": "P0_0.png"})
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

    assert statuses_of(client) == [("P1_0.png", "pending"), ("P0_0.png", "done")]


class RenderFailed(RuntimeError):
    """ComfyUI answered and said the graph failed -- the frame's problem, not the run's."""

    frame_level = True


def test_the_gallery_keeps_a_red_frame_after_the_worker_is_gone(tmp_path):
    class BlowsUpOnTheFirstPrompt:
        """Drops the same job every time it is offered -- three attempts, then red."""

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
            if prompt == "a":
                raise RenderFailed("node 41: OOM")
            return b"PNGDATA"

    client, _ = make_client(tmp_path, generator=BlowsUpOnTheFirstPrompt())
    generate(client, prompts='["a", "b"]', variants=1)

    # Nothing is left in memory: this answer is the plan and the log alone. And the failed frame is
    # drawn once, in its own place -- not as a red tile and a dashed one at the same time.
    assert statuses_of(client) == [("P1_0.png", "done"), ("P0_0.png", "failed")]


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

    delete_photos_request(client, ["P1_0"])

    assert statuses_of(client) == [("P0_0.png", "done")]


def test_retry_produces_only_the_named_frame(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    delete_photos_request(client, ["P0_0"])

    resp = client.post("/api/projects/düğün/retry", json={"frame": "P0_0"})

    assert resp.status_code == 202
    assert (drive / "düğün" / "P0_0.png").exists()
    # It comes back where it was, not on top: a frame's place in the gallery is its own.
    assert files_of(client) == ["P1_0.png", "P0_0.png"]


def test_retry_without_a_file_puts_every_red_frame_back(tmp_path):
    class BlowsUpUntilItIsForgiven:
        """Drops every job of the first batch, then renders whatever is offered again."""

        def __init__(self):
            self.forgiving = False

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
            if not self.forgiving:
                raise RenderFailed("node 41: OOM")
            return b"PNGDATA"

    generator = BlowsUpUntilItIsForgiven()
    client, drive = make_client(tmp_path, generator=generator)
    generate(client, prompts='["a", "b"]', variants=1)
    assert statuses_of(client) == [("P1_0.png", "failed"), ("P0_0.png", "failed")]
    generator.forgiving = True

    resp = client.post("/api/projects/düğün/retry", json={})

    assert resp.status_code == 202
    assert (drive / "düğün" / "P0_0.png").exists()
    assert (drive / "düğün" / "P1_0.png").exists()


def test_the_videos_endpoint_carries_the_variant_count(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = client.post("/api/projects/düğün/layers/video", json={"variants": 2})

    assert resp.status_code == 202
    # One video on the frame itself and one on the copy it just gained.
    assert resp.get_json()["added"] == 2


def test_the_videos_endpoint_refuses_an_impossible_variant_count(tmp_path):
    client, _ = make_client(tmp_path)

    resp = client.post("/api/projects/düğün/layers/video", json={"variants": 0})

    assert resp.status_code == 400
    assert resp.get_json()["field"] == "variants"


def video_jobs(drive, project="düğün"):
    plan = json.loads((drive / project / "plan.json").read_text(encoding="utf-8"))
    return [frame for frame in plan["frames"] if frame["type"] == "video"]


def test_the_videos_endpoint_carries_the_production_mode(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = client.post("/api/projects/düğün/layers/video", json={"mode": "loop"})

    assert resp.status_code == 202
    # The plan line is where the mode has to land: the renderer reads it hours later, long after
    # the panel that chose it is gone.
    assert [job["mode"] for job in video_jobs(drive)] == ["loop"]


def test_a_layer_queued_with_no_mode_is_a_plain_one(tmp_path):
    # A client older than the row asks for exactly what it always asked for -- the same reading the
    # variant count already gets.
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    client.post("/api/projects/düğün/layers/video", json={})

    assert [job["mode"] for job in video_jobs(drive)] == ["standard"]


def test_the_videos_endpoint_refuses_a_mode_nobody_knows(tmp_path):
    client, _ = make_client(tmp_path)

    resp = client.post("/api/projects/düğün/layers/video", json={"mode": "kelebek"})

    assert resp.status_code == 400
    assert resp.get_json()["field"] == "mode"


def test_a_sound_cannot_be_asked_to_end_anywhere(tmp_path):
    # Only a video ends on a picture. Letting the word through would hide the mistake behind a
    # sound that came out fine.
    client, _ = make_client(tmp_path)

    resp = client.post("/api/projects/düğün/layers/audio", json={"mode": "loop"})

    assert resp.status_code == 400
    assert resp.get_json()["field"] == "mode"


def test_an_unknown_layer_is_not_a_place_to_queue_anything(tmp_path):
    client, _ = make_client(tmp_path)

    assert client.post("/api/projects/düğün/layers/foto", json={}).status_code == 404


def test_a_copy_frame_shares_its_sources_photo_file(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    client.post("/api/projects/düğün/layers/video", json={"variants": 3})

    rows = client.get("/api/projects/düğün/frames").get_json()["frames"]
    assert [row["id"] for row in rows] == ["P0_2", "P0_1", "P0_0"]
    # Three frames, one picture on disk.
    assert {row["file"] for row in rows} == {"P0_0.png"}


def regenerate_request(client, frame, layer="photo", prompt="a", project="düğün", mode=None):
    body = {"frame": frame, "layer": layer, "prompt": prompt}
    if mode is not None:
        # Left out rather than sent as null: what the older screen sends is a body with no mode at
        # all, and that shape has to keep working.
        body["mode"] = mode
    return client.post(f"/api/projects/{project}/regenerate", json=body)


def test_regenerate_answers_with_the_new_frames_name(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = regenerate_request(client, "P0_0")

    assert resp.status_code == 202
    assert resp.get_json() == {"job": "running", "frame": "P0_1"}


def test_a_frame_made_again_joins_the_gallery_beside_its_source(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    regenerate_request(client, "P0_0", prompt="başka")

    rows = client.get("/api/projects/düğün/frames").get_json()["frames"]
    assert [(row["id"], row["file"]) for row in rows] == [("P1_0", "P1_0.png"),
                                                          ("P0_0", "P0_0.png")]
    assert (drive / "düğün" / "P1_0.png").exists()


def test_a_regenerate_mode_nobody_knows_is_refused(tmp_path):
    """Proof that the body's mode reaches the rule at all: an unknown one could not be refused if
    the route were dropping the field."""
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = regenerate_request(client, "P0_0", layer="video", mode="kelebek")

    assert resp.status_code == 400
    assert resp.get_json()["error"]


def test_linking_a_frame_with_nothing_after_it_is_refused_with_a_reason(tmp_path):
    """One frame in the gallery, so it is the film's last. The screen never sends this; the answer
    still has to be a refusal rather than a job that will fail later."""
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = regenerate_request(client, "P0_0", layer="video", mode="linked")

    assert resp.status_code == 400
    assert resp.get_json()["error"]


def test_regenerating_a_frame_the_gallery_does_not_know_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    assert regenerate_request(client, "P9_9").status_code == 404


def test_regenerating_a_layer_the_frame_cannot_carry_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = regenerate_request(client, "P0_0", layer="audio", prompt="ses")

    assert resp.status_code == 400
    assert resp.get_json()["error"]


def test_regenerating_a_layer_that_does_not_exist_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    assert regenerate_request(client, "P0_0", layer="foto").status_code == 404


def delete_layer_request(client, frame, layer="video", project="düğün"):
    return client.post(f"/api/projects/{project}/layers/{layer}/delete", json={"frame": frame})


def give_it_a_video(drive, frame="P0_0", project="düğün"):
    """Put a produced video on a frame, the way the engine would.

    By hand because no video producer runs in these tests -- the graph is not in the repo. A second
    DrivePhotoRecord over the same folder is the same log: the record is a file, not a session.
    """
    name = f"{frame}_V1_0.mp4"
    (drive / project / name).write_bytes(b"MP4")
    DrivePhotoRecord(DriveStorage(str(drive))).append(project, {
        "file": name, "frame": frame, "layer": "video", "status": "done",
        "prompt": "kadın dönüyor"})
    return name


def test_deleting_a_video_leaves_the_frame_in_the_gallery(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    give_it_a_video(drive)

    resp = delete_layer_request(client, "P0_0")

    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": ["P0_0_V1_0.mp4"]}
    assert not (drive / "düğün" / "P0_0_V1_0.mp4").exists()
    assert files_of(client) == ["P0_0.png"]
    assert (drive / "düğün" / "P0_0.png").exists()


def test_the_photo_layer_is_not_deleted_this_way(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    assert delete_layer_request(client, "P0_0", layer="photo").status_code == 404


def test_deleting_a_layer_of_an_unknown_frame_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    assert delete_layer_request(client, "P9_9").status_code == 404


def test_retry_of_a_frame_the_plan_does_not_know_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    assert client.post("/api/projects/düğün/retry", json={"frame": "P9_9"}).status_code == 404


def test_resume_produces_only_what_the_run_never_got_to(tmp_path):
    runner = PhotoRunner(spawn=lambda fn: fn())
    generator = StopsAfter(runner, 1)
    client, drive = make_client(tmp_path, generator=generator, runner=runner)
    generate(client, prompts='["a", "b"]', variants=1)
    assert not (drive / "düğün" / "P1_0.png").exists()

    generator.count = 10                       # the machine is back
    resp = client.post("/api/projects/düğün/resume")

    assert resp.status_code == 202
    assert (drive / "düğün" / "P1_0.png").exists()


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
    assert (drive / "düğün" / "P0_0.png").exists()
    assert client.post("/api/projects/düğün/resume").status_code == 409


def copy_frames_request(client, frames, project="düğün"):
    return client.post(f"/api/projects/{project}/frames/copy", json={"frames": frames})


def delete_photos_request(client, frames, project="düğün"):
    return client.post(f"/api/projects/{project}/frames/delete", json={"frames": frames})


def test_the_copy_route_answers_with_the_twins_and_the_gallery_they_landed_in(tmp_path):
    client, _drive = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)

    answer = copy_frames_request(client, ["P0_0"])

    assert answer.status_code == 200
    body = answer.get_json()
    assert body["copies"] == ["C1_P0_0"]
    # The gallery comes back with it: the screen would ask for exactly this in a second round-trip.
    assert [f["id"] for f in body["frames"]] == ["P1_0", "C1_P0_0", "P0_0"]


def test_deleting_one_twin_leaves_the_others_picture_on_the_disk(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    copy_frames_request(client, ["P0_0"])

    delete_photos_request(client, ["C1_P0_0"])

    # One picture, two frames holding it: the last of them to let go is what unlinks it.
    assert (drive / "düğün" / "P0_0.png").exists()
    gallery = client.get("/api/projects/düğün/frames").get_json()["frames"]
    assert [f["id"] for f in gallery] == ["P0_0"]


def test_a_copy_body_that_is_not_a_list_of_identities_is_refused(tmp_path):
    client, _drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    answer = copy_frames_request(client, "P0_0")

    assert answer.status_code == 400
    assert "metin dizisi" in answer.get_json()["error"]


def test_deleting_photos_removes_them_from_the_gallery_and_the_folder(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a", "b", "c"]', variants=1)

    resp = delete_photos_request(client, ["P0_0", "P2_0"])

    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": ["P0_0", "P2_0"], "removed": []}
    assert files_of(client) == ["P1_0.png"]
    assert not (drive / "düğün" / "P0_0.png").exists()


def test_pulling_pending_frames_out_leaves_the_photos_alone(tmp_path):
    runner = PhotoRunner(spawn=lambda fn: fn())
    client, drive = make_client(tmp_path, generator=StopsAfter(runner, 1), runner=runner)
    generate(client, prompts='["a", "b", "c"]', variants=1)

    resp = delete_photos_request(client, ["P2_0", "P1_0"])

    assert resp.get_json() == {"deleted": [], "removed": ["P2_0", "P1_0"]}
    assert statuses_of(client) == [("P0_0.png", "done")]
    assert (drive / "düğün" / "P0_0.png").exists()


def test_a_photo_produced_after_a_delete_does_not_reuse_the_number(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    delete_photos_request(client, ["P0_0"])

    generate(client, prompts='["b"]', variants=1)

    assert files_of(client) == ["P1_0.png"]


def test_deleting_a_photo_drops_it_from_the_saved_order(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    client.put("/api/projects/düğün/order", json={"order": ["P0_0", "P1_0"]})

    delete_photos_request(client, ["P0_0"])

    assert files_of(client) == ["P1_0.png"]


def test_deleting_an_unknown_photo_reports_nothing_deleted(tmp_path):
    client, _ = make_client(tmp_path)
    resp = delete_photos_request(client, ["yok"])
    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": [], "removed": []}


def test_a_delete_body_that_is_not_a_list_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    assert delete_photos_request(client, "P0_0").status_code == 400


def test_deleting_photos_of_an_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert delete_photos_request(client, ["P0_0"], project="yok").status_code == 404


def test_the_export_summary_is_json_not_a_download(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    give_it_a_video(drive)

    resp = client.get("/api/projects/düğün/export/summary")

    assert resp.status_code == 200
    body = resp.get_json()
    assert (body["videos"], body["seconds"]) == (1, 5)
    assert body["folder"].endswith("export")


def test_the_summary_of_a_project_with_no_video_is_zero(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    assert client.get("/api/projects/düğün/export/summary").get_json()["videos"] == 0


def test_the_old_export_download_is_gone(tmp_path):
    client, _ = make_client(tmp_path)

    resp = client.get("/api/projects/düğün/export")

    # No rule answers that address any more, so the SPA fallback takes it: whatever comes back, it
    # is not a data file.
    assert resp.mimetype != "application/json"
    assert "attachment" not in resp.headers.get("Content-Disposition", "")


def test_the_summary_of_an_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/export/summary").status_code == 404


def test_an_export_runs_and_says_where_it_wrote(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    give_it_a_video(drive)

    resp = client.post("/api/projects/düğün/export/separate")

    assert resp.status_code == 202
    state = client.get("/api/projects/düğün/export/status").get_json()["separate"]
    assert (state["state"], state["written"], state["total"]) == ("done", 1, 1)
    assert state["target"].endswith("2026-08-12 14-32")


def test_an_export_of_an_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.post("/api/projects/yok/export/separate").status_code == 404


def test_an_export_mode_that_does_not_exist_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.post("/api/projects/düğün/export/yarım").status_code == 404


def test_cancelling_an_export_is_accepted(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.post("/api/projects/düğün/export/cancel").status_code == 202


def test_a_broken_order_file_does_not_hide_the_gallery(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    (drive / "düğün" / "order.json").write_text("{yarım", encoding="utf-8")
    assert files_of(client) == ["P0_0.png"]
