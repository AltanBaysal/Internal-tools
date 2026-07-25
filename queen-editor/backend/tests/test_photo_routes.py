from functools import partial

from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.start_generation import start_generation
from backend.features.photo_generation.presentation.routes import make_photo_generation_blueprint
from backend.features.photo_generation.runner import PhotoRunner
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app


class FakeGenerator:
    def generate(self, prompt, seed):
        return b"PNGDATA"


def make_client(tmp_path, generator=None, runner=None):
    drive = tmp_path / "drive"
    (drive / "düğün").mkdir(parents=True)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")

    store = DrivePhotoStore(DriveStorage(str(drive)))
    runner = runner or PhotoRunner(spawn=lambda fn: fn())
    blueprint = make_photo_generation_blueprint(
        start_generation=partial(start_generation, runner, store,
                                 generator or FakeGenerator(), lambda: 42),
        get_status=partial(get_status, runner),
        photo_dir=store.photo_dir,
    )
    app = create_app(dist_dir=str(dist), blueprints=[blueprint])
    return app.test_client(), drive


def test_generate_returns_202_and_writes_the_photo(tmp_path):
    client, drive = make_client(tmp_path)
    resp = client.post("/api/projects/düğün/generate", json={"prompt": "kraliçe tahtta"})
    assert resp.status_code == 202
    assert (drive / "düğün" / "0_a.png").read_bytes() == b"PNGDATA"


def test_status_reports_done_with_the_file(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects/düğün/generate", json={"prompt": "kraliçe"})
    assert client.get("/api/status").get_json() == {
        "status": "done", "project": "düğün", "file": "0_a.png"}


def test_status_is_idle_before_anything_runs(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/status").get_json() == {"status": "idle"}


def test_empty_prompt_returns_400(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post("/api/projects/düğün/generate", json={"prompt": "  "})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Prompt boş olamaz."


def test_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    resp = client.post("/api/projects/yok/generate", json={"prompt": "kraliçe"})
    assert resp.status_code == 404
    assert "yok" in resp.get_json()["error"]


def test_busy_runner_returns_409(tmp_path):
    client, _ = make_client(tmp_path, runner=PhotoRunner(spawn=lambda fn: None))
    client.post("/api/projects/düğün/generate", json={"prompt": "kraliçe"})
    resp = client.post("/api/projects/düğün/generate", json={"prompt": "kraliçe"})
    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Zaten bir üretim sürüyor."


def test_failed_generation_shows_the_real_error_in_status(tmp_path):
    class Broken:
        def generate(self, prompt, seed):
            raise RuntimeError("node 9 (CheckpointLoaderSimple): dosya yok")

    client, _ = make_client(tmp_path, generator=Broken())
    client.post("/api/projects/düğün/generate", json={"prompt": "kraliçe"})
    state = client.get("/api/status").get_json()
    assert state["status"] == "error" and "CheckpointLoaderSimple" in state["error"]


def test_photo_is_served_from_the_project_folder(tmp_path):
    client, drive = make_client(tmp_path)
    (drive / "düğün" / "0_a.png").write_bytes(b"PNGDATA")
    assert client.get("/photos/düğün/0_a.png").data == b"PNGDATA"
    assert client.get("/photos/düğün/yok.png").status_code == 404
