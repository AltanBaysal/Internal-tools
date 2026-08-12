"""The producers endpoints over a real Flask app, with fake models on disk."""
from functools import partial

from backend.features.producers.data.comfy_models import ComfyModelFiles
from backend.features.producers.domain.usecases.cancel_install import cancel_install
from backend.features.producers.domain.usecases.install_producer import install_producer
from backend.features.producers.domain.usecases.list_producers import list_producers
from backend.features.producers.presentation.routes import make_producers_blueprint
from backend.features.producers.runner import InstallRunner
from backend.web.app import create_app

GROUPS = {"photo": [], "video": [{"folder": "vae", "name": "v.safetensors", "url": "u1"}],
          "audio": []}


class FakeFetcher:
    def __init__(self):
        self.fetched = []

    def fetch(self, url, path, headers=None, on_progress=None, cancelled=None):
        self.fetched.append(url)


def make_client(tmp_path, runner=None):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    files = ComfyModelFiles(str(tmp_path / "comfy"))
    runner = runner or InstallRunner(spawn=lambda fn: fn())
    fetcher = FakeFetcher()
    blueprint = make_producers_blueprint(
        list_producers=lambda: list_producers(GROUPS, files, running=runner.status()),
        install_producer=partial(install_producer, GROUPS, files, fetcher, runner, {}),
        cancel_install=partial(cancel_install, runner),
    )
    app = create_app(dist_dir=str(dist), blueprints=[blueprint])
    return app.test_client(), fetcher


def test_the_panel_reads_three_rows(tmp_path):
    client, _ = make_client(tmp_path)

    body = client.get("/api/producers").get_json()

    assert [row["id"] for row in body["producers"]] == ["photo", "video", "audio"]
    assert body["producers"][1]["installed"] is False


def test_installing_starts_the_download(tmp_path):
    client, fetcher = make_client(tmp_path)

    response = client.post("/api/producers/video/install")

    assert response.status_code == 202
    assert fetcher.fetched == ["u1"]


def test_a_second_install_while_one_runs_is_refused(tmp_path):
    # A runner that never finishes: the first request claims it and keeps it.
    client, _ = make_client(tmp_path, runner=InstallRunner(spawn=lambda fn: None))
    client.post("/api/producers/video/install")

    assert client.post("/api/producers/video/install").status_code == 409


def test_cancelling_answers_with_nothing_to_say(tmp_path):
    client, _ = make_client(tmp_path, runner=InstallRunner(spawn=lambda fn: None))
    client.post("/api/producers/video/install")

    assert client.post("/api/producers/video/install/cancel").status_code == 204
