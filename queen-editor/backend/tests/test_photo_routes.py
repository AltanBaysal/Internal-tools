import json
from functools import partial

from backend.features.photo_generation.data.order_store import DriveOrderStore
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.domain.usecases.export_project import export_project
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.list_photos import list_photos
from backend.features.photo_generation.domain.usecases.save_order import save_order
from backend.features.photo_generation.domain.usecases.start_batch import start_batch
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
from backend.features.photo_generation.presentation.routes import make_photo_generation_blueprint
from backend.features.photo_generation.runner import PhotoRunner
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app


class FakeGenerator:
    def generate(self, prompt, negative, seed):
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
    blueprint = make_photo_generation_blueprint(
        start_batch=partial(start_batch, runner, store, record, plan_store,
                            generator or FakeGenerator(), lambda: 42,
                            lambda: "2026-08-03T14:32:11+00:00"),
        get_status=partial(get_status, runner),
        stop_generation=partial(stop_generation, runner, lambda: None),
        list_photos=partial(list_photos, record, store, order_store),
        save_order=partial(save_order, record, store, order_store),
        export_project=partial(export_project, record, store, order_store),
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
        "status": "done", "project": "düğün", "done": 4, "failed": 0, "total": 4}


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


def test_busy_runner_returns_409(tmp_path):
    client, _ = make_client(tmp_path, runner=PhotoRunner(spawn=lambda fn: None))
    generate(client)
    resp = generate(client)
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Zaten bir üretim sürüyor."


def test_failed_batch_shows_the_real_error_in_status(tmp_path):
    class Broken:
        def generate(self, prompt, negative, seed):
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


def test_photos_are_listed_newest_first(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    files = [row["file"] for row in
             client.get("/api/projects/düğün/photos").get_json()["photos"]]
    assert files == ["1_a.png", "0_a.png"]


def test_files_without_a_record_row_are_not_listed(tmp_path):
    # The record is the gallery's list: a file no run produced is not part of the project.
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "9_a.png").write_bytes(b"x")
    assert client.get("/api/projects/düğün/photos").get_json() == {"photos": []}


def test_a_listed_photo_carries_the_prompt_that_made_it(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["kraliçe tahtta"]', variants=1)
    row = client.get("/api/projects/düğün/photos").get_json()["photos"][0]
    assert row["file"] == "0_a.png" and row["prompt"] == "kraliçe tahtta"


def test_photos_of_an_unknown_project_return_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/photos").status_code == 404


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
    return [row["file"] for row in client.get(f"/api/projects/{project}/photos").get_json()["photos"]]


def test_saved_order_decides_how_photos_are_listed(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    assert files_of(client) == ["1_a.png", "0_a.png"]

    resp = client.put("/api/projects/düğün/order", json={"order": ["0_a.png", "1_a.png"]})
    assert resp.status_code == 200
    assert resp.get_json() == {"order": ["0_a.png", "1_a.png"]}
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
    assert resp.get_json() == {"order": ["0_a.png"]}


def test_order_that_is_not_a_list_of_names_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.put("/api/projects/düğün/order", json={"order": "0_a.png"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Sıra listesi metin dizisi olmalı."


def test_order_of_an_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.put("/api/projects/yok/order", json={"order": []}).status_code == 404


def test_export_downloads_a_json_file_in_gallery_order(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    client.put("/api/projects/düğün/order", json={"order": ["0_a.png", "1_a.png"]})

    resp = client.get("/api/projects/düğün/export")

    assert resp.status_code == 200
    assert resp.mimetype == "application/json"
    assert "attachment" in resp.headers["Content-Disposition"]
    body = json.loads(resp.data)
    assert body["photos"] == [{"file": "0_a.png", "prompt": "a"},
                              {"file": "1_a.png", "prompt": "b"}]
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
