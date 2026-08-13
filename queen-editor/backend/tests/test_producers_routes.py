"""The producers endpoint over a real Flask app, with fake models on disk."""
from backend.features.producers.data.comfy_models import ComfyModelFiles
from backend.features.producers.domain.usecases.list_producers import list_producers
from backend.features.producers.presentation.routes import make_producers_blueprint
from backend.web.app import create_app

GROUPS = {"photo": [], "video": [{"folder": "vae", "name": "v.safetensors"}], "audio": []}


def make_client(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    files = ComfyModelFiles(str(tmp_path / "comfy"))
    blueprint = make_producers_blueprint(
        list_producers=lambda: list_producers(GROUPS, files))
    app = create_app(dist_dir=str(dist), blueprints=[blueprint])
    return app.test_client()


def test_the_panel_reads_three_rows(tmp_path):
    body = make_client(tmp_path).get("/api/producers").get_json()

    assert [row["id"] for row in body["producers"]] == ["photo", "video", "audio"]
    assert body["producers"][1]["installed"] is False


def test_there_is_no_way_to_start_an_install_over_http(tmp_path):
    """The app installs nothing, so the endpoints that used to are gone rather than answering.

    405 rather than 404: the single-page fallback answers any unclaimed path for GET, so what is
    left of these two is a path that accepts no POST at all.
    """
    client = make_client(tmp_path)

    assert client.post("/api/producers/video/install").status_code == 405
    assert client.post("/api/producers/video/install/cancel").status_code == 405
