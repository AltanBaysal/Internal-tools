from functools import partial
from io import BytesIO

from backend.features.photo_generation.data.ffmpeg_clips import FfmpegClips
from backend.features.photo_generation.data.order_store import DriveOrderStore
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.reference_order_store import (
    DriveReferenceOrderStore,
)
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.data.reference_store import DriveReferenceStore
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.usecases.add_references import add_references
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.queue_references import queue_references
from backend.features.photo_generation.domain.usecases.remove_reference import remove_reference
from backend.features.photo_generation.domain.usecases.save_reference_order import (
    save_reference_order,
)
from backend.features.photo_generation.presentation.reference_routes import (
    make_reference_blueprint,
)
from backend.features.photo_generation.runner import PhotoRunner
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app


class FakeGenerator:
    """A video engine that answers with bytes. What H3 really does with references is madde 304's;
    this file is about the door."""

    def generate(self, *_args, **_kwargs):
        return b"MP4"


def fixed_length(seconds=4.0):
    """ffprobe's answer, without ffprobe: the test machine has no such tool, and how long a clip
    runs is the clip tool's own test to make (test_ffmpeg_clips)."""
    return FfmpegClips(run=lambda args, **_kwargs: type(
        "Done", (), {"returncode": 0, "stdout": f"{seconds}\n", "stderr": ""})())


def client_over(drive, dist, clips=None, has_h3=True):
    """A server over this Drive folder. A second one is what a restart looks like from here: the
    pool is a folder, not a session."""
    storage = DriveStorage(str(drive))
    store = DrivePhotoStore(storage)
    record = DrivePhotoRecord(storage)
    plan_store = DrivePlanStore(storage)
    gallery = DriveOrderStore(storage)
    runner = PhotoRunner(spawn=lambda fn: fn())
    clips = clips or fixed_length()
    pool = DriveReferenceStore(storage, clips)
    orders = DriveReferenceOrderStore(storage)
    blueprint = make_reference_blueprint(
        add_references=partial(add_references, store, pool, orders, clips),
        list_references=partial(list_references, store, pool, orders),
        remove_reference=partial(remove_reference, store, pool, orders),
        save_reference_order=partial(save_reference_order, store, pool, orders),
        queue_references=partial(queue_references, runner, store, record, plan_store, gallery,
                                 pool, orders, {layers.VIDEO: FakeGenerator()}, lambda: 7,
                                 lambda: "t", has_h3),
        reference_dir=pool.dir_path)
    return create_app(dist_dir=str(dist), blueprints=[blueprint]).test_client()


def make_client(tmp_path, clips=None):
    drive = tmp_path / "drive"
    (drive / "düğün").mkdir(parents=True)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    return client_over(drive, dist, clips), drive, dist


def upload(client, *files, project="düğün"):
    return client.post(f"/api/projects/{project}/references",
                       data={"files": [(BytesIO(data), name) for name, data in files]},
                       content_type="multipart/form-data")


def names_of(body):
    return [row["name"] for row in body["references"]]


def test_two_references_are_uploaded_listed_and_one_is_deleted(tmp_path):
    """Madde 297 end to end, over a real folder: the pool is what is on the disk, and nothing about
    it lives in the process."""
    client, drive, dist = make_client(tmp_path)

    added = upload(client, ("kedi.png", b"PNG"), ("dans.mp4", b"MP4"))

    assert added.status_code == 200
    # A row at a time, and by name inside a row while nobody has dragged anything: the order they
    # were picked in is not on the disk to be read back (madde 297), and a slot is a place inside
    # one kind's row (madde 300).
    assert names_of(added.get_json()) == ["kedi.png", "dans.mp4"]
    assert (drive / "düğün" / "referans" / "kedi.png").read_bytes() == b"PNG"

    listed = client.get("/api/projects/düğün/references")
    assert [(row["name"], row["kind"], row["seconds"])
            for row in listed.get_json()["references"]] == [
        ("kedi.png", "picture", None), ("dans.mp4", "video", 4.0)]

    gone = client.post("/api/projects/düğün/references/kedi.png/delete")
    assert gone.status_code == 200
    assert names_of(gone.get_json()) == ["dans.mp4"]
    assert not (drive / "düğün" / "referans" / "kedi.png").exists()

    # The restart: a second server over the same folder, and the pool is still what it was.
    again = client_over(drive, dist).get("/api/projects/düğün/references")
    assert names_of(again.get_json()) == ["dans.mp4"]


def test_a_reference_is_served_from_the_server(tmp_path):
    """The browser cannot reach Drive (FOUNDATION 4), so every byte of the pool comes through
    here."""
    client, _drive, _dist = make_client(tmp_path)
    upload(client, ("kedi.png", b"PNG"))

    resp = client.get("/references/düğün/kedi.png")

    assert resp.status_code == 200
    assert resp.data == b"PNG"
    # Not a photo's forever cache: a deleted name can be given to another file, and stale bytes in
    # the browser would be the wrong thumbnail.
    assert "immutable" not in resp.headers.get("Cache-Control", "")


def test_a_file_the_pool_cannot_read_is_refused(tmp_path):
    client, drive, _dist = make_client(tmp_path)

    resp = upload(client, ("notlar.txt", b"..."))

    assert resp.status_code == 400
    assert "notlar.txt" in resp.get_json()["error"]
    assert not (drive / "düğün" / "referans").exists()


def test_the_order_is_saved_and_read_back(tmp_path):
    """The order is a document of its own, so it outlives the session that dragged it."""
    client, drive, dist = make_client(tmp_path)
    upload(client, ("kedi.png", b"ONE"), ("kuş.png", b"TWO"))

    saved = client.put("/api/projects/düğün/references/order",
                       json={"order": {"picture": ["kuş.png", "kedi.png"]}})

    assert saved.status_code == 200
    assert names_of(saved.get_json()) == ["kuş.png", "kedi.png"]

    again = client_over(drive, dist).get("/api/projects/düğün/references")
    assert names_of(again.get_json()) == ["kuş.png", "kedi.png"]


def test_a_deleted_reference_leaves_its_slot_where_it_was(tmp_path):
    client, _drive, _dist = make_client(tmp_path)
    upload(client, ("bir.png", b"1"), ("iki.png", b"2"), ("üç.png", b"3"))
    client.put("/api/projects/düğün/references/order",
               json={"order": {"picture": ["bir.png", "iki.png", "üç.png"]}})

    left = client.post("/api/projects/düğün/references/iki.png/delete")

    assert [(row["name"], row["slot"]) for row in left.get_json()["references"]] == [
        ("bir.png", 1), ("üç.png", 3)]


def test_a_reference_that_passes_a_limit_is_a_400(tmp_path):
    """The app counts and refuses: H3's own complaint would land in a Colab log nobody opens."""
    client, drive, _dist = make_client(tmp_path, clips=fixed_length(20.0))

    resp = upload(client, ("uzun.mp4", b"MP4"))

    assert resp.status_code == 400
    assert "uzun.mp4" in resp.get_json()["error"]
    assert not (drive / "düğün" / "referans" / "uzun.mp4").exists()


def test_a_pool_asked_of_a_project_that_does_not_exist_is_a_404(tmp_path):
    client, _drive, _dist = make_client(tmp_path)

    assert client.get("/api/projects/yok/references").status_code == 404


def produce(client, prompts='["gotik kız"]', variants=1, project="düğün"):
    return client.post(f"/api/projects/{project}/references/produce",
                       json={"prompts": prompts, "variants": variants})


def test_a_refused_reference_run_is_a_400_with_its_reason(tmp_path):
    """Nothing is on the pool yet, so there is nothing to make a video out of."""
    client, _drive, _dist = make_client(tmp_path)

    resp = produce(client)

    assert resp.status_code == 400
    assert "referans" in resp.get_json()["error"].lower()


def test_a_reference_run_that_can_go_ahead_answers_with_what_it_took(tmp_path):
    client, _drive, _dist = make_client(tmp_path)
    upload(client, ("kedi.png", b"PNG"))

    resp = produce(client, variants=2)

    assert resp.status_code == 202
    # One prompt, two variants: two cards, and the answer has the shape every other production
    # answers in.
    assert resp.get_json() == {"added": 2}
