from functools import partial
from io import BytesIO

from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.reference_store import DriveReferenceStore
from backend.features.photo_generation.domain.usecases.add_references import add_references
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.remove_reference import remove_reference
from backend.features.photo_generation.presentation.reference_routes import (
    make_reference_blueprint,
)
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app


def client_over(drive, dist):
    """A server over this Drive folder. A second one is what a restart looks like from here: the
    pool is a folder, not a session."""
    storage = DriveStorage(str(drive))
    store = DrivePhotoStore(storage)
    pool = DriveReferenceStore(storage)
    blueprint = make_reference_blueprint(
        add_references=partial(add_references, store, pool),
        list_references=partial(list_references, store, pool),
        remove_reference=partial(remove_reference, store, pool),
        reference_dir=pool.dir_path)
    return create_app(dist_dir=str(dist), blueprints=[blueprint]).test_client()


def make_client(tmp_path):
    drive = tmp_path / "drive"
    (drive / "düğün").mkdir(parents=True)
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("x", encoding="utf-8")
    return client_over(drive, dist), drive, dist


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
    assert names_of(added.get_json()) == ["kedi.png", "dans.mp4"]
    assert (drive / "düğün" / "referans" / "kedi.png").read_bytes() == b"PNG"

    listed = client.get("/api/projects/düğün/references")
    assert [(row["name"], row["kind"]) for row in listed.get_json()["references"]] == [
        ("kedi.png", "picture"), ("dans.mp4", "video")]

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


def test_a_pool_asked_of_a_project_that_does_not_exist_is_a_404(tmp_path):
    client, _drive, _dist = make_client(tmp_path)

    assert client.get("/api/projects/yok/references").status_code == 404
