"""The storage door seen from HTTP (madde 472): what reaches the screen when the disk fails, and
names from a URL that would leave the root.

The tunnel is public and needs no login, so a project's name in a URL is anybody's. Before 472
`DELETE /api/projects/..` reached rmtree on the folder above the root -- all of MyDrive -- and
`/photos/../<file>` served the files beside the root. Every route here is wired the way main.py
wires it, over a temp folder whose parent holds something that must not be touched.
"""
import pytest
from flask import Blueprint

from backend.tests.test_photo_routes import make_client as photo_client
from backend.tests.test_projects_routes import make_client as projects_client
from backend.tests.test_reference_routes import make_client as reference_client
from backend.web.app import create_app


def test_a_failure_of_the_disk_reaches_the_screen_in_its_own_words(tmp_path):
    """One handler for every route: the screen prints body.error, so a 500 page with no sentence
    was what a failed save looked like wherever a route did not catch the error itself."""
    blueprint = Blueprint("broken", __name__)

    @blueprint.get("/api/broken")
    def broken():
        raise OSError(107, "Transport endpoint is not connected")

    (tmp_path / "index.html").write_text("x", encoding="utf-8")
    client = create_app(dist_dir=str(tmp_path), blueprints=[blueprint]).test_client()

    response = client.get("/api/broken")

    assert response.status_code == 503
    assert response.get_json() == {"error": "[Errno 107] Transport endpoint is not connected"}


def test_a_dropped_mount_reaches_the_screen_when_a_save_is_asked(tmp_path):
    client, drive = projects_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    (drive / "düğün" / "settings.json").write_text("{}", encoding="utf-8")
    moved = tmp_path / "kopuk"
    drive.rename(moved)

    response = client.put("/api/projects/düğün/settings", json={"prompts": "a"})

    assert response.status_code == 503
    # Which root it was is the OS's own words: the projects' and the exports' are two doors with one
    # sentence (madde 494).
    assert "Kök klasöre ulaşılamıyor" in response.get_json()["error"]
    assert repr(str(drive)) in response.get_json()["error"]
    # Nothing was written anywhere: no root was opened again, and the old file is untouched.
    assert not drive.exists()
    assert (moved / "düğün" / "settings.json").read_text(encoding="utf-8") == "{}"


def refused(response, name):
    """The storage door turned `name` away: a client's error, and the door's own sentence -- which
    is also the proof that the request got as far as the door with that very name."""
    assert response.status_code == 400
    assert response.get_json() == {"error": f"Geçersiz ad: {name!r}"}


SECRET = "kökün dışında"


def beside_the_root(tmp_path):
    """A file next to the root -- what a name that leaves the root would reach."""
    planted = tmp_path / "sır.txt"
    planted.write_text(SECRET, encoding="utf-8")
    return planted


@pytest.mark.parametrize("name, said", [("..", ".."), ("%2E%2E", ".."), (".", ".")])
def test_deleting_a_project_named_to_leave_the_root_deletes_nothing(tmp_path, name, said):
    client, drive = projects_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    planted = beside_the_root(tmp_path)

    response = client.delete(f"/api/projects/{name}")

    refused(response, said)
    assert (drive / "düğün").is_dir()
    assert planted.read_text(encoding="utf-8") == SECRET


def test_archiving_a_project_named_to_leave_the_root_is_refused(tmp_path):
    client, _drive = projects_client(tmp_path)

    response = client.post("/api/projects/../archive")

    refused(response, "..")
    assert not (tmp_path / "drive" / "arsiv.json").exists()


def test_restoring_a_project_named_to_leave_the_root_finds_nothing(tmp_path):
    """Restoring never turns the name into a path -- it only looks for it among the marks -- so the
    answer is the ordinary one for a name the archive does not hold."""
    client, _drive = projects_client(tmp_path)

    response = client.post("/api/projects/../restore")

    assert response.status_code == 404


def test_renaming_a_project_named_to_leave_the_root_moves_nothing(tmp_path):
    client, drive = projects_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})

    response = client.post("/api/projects/../rename", json={"name": "kaçış"})

    refused(response, "..")
    assert not (drive / "kaçış").exists()
    assert (drive / "düğün").is_dir()


@pytest.mark.parametrize("project", ["..", "%2E%2E"])
def test_a_photo_url_cannot_serve_a_file_beside_the_root(tmp_path, project):
    client, _drive = photo_client(tmp_path)
    planted = beside_the_root(tmp_path)

    response = client.get(f"/photos/{project}/sır.txt")

    refused(response, "..")
    assert SECRET not in response.get_data(as_text=True)
    assert planted.exists()


def test_a_photo_url_cannot_name_the_folder_above_a_project(tmp_path):
    client, drive = photo_client(tmp_path)
    (drive / "düğün" / "plan.json").write_text("{}", encoding="utf-8")

    response = client.get("/photos/düğün/..")

    assert response.status_code == 404


def test_a_photo_is_still_served(tmp_path):
    client, drive = photo_client(tmp_path)
    (drive / "düğün" / "P0_0.png").write_bytes(b"PNG")

    response = client.get("/photos/düğün/P0_0.png")

    assert response.status_code == 200
    assert response.data == b"PNG"


@pytest.mark.parametrize("project", ["..", "%2E%2E"])
def test_a_reference_url_cannot_serve_a_file_beside_the_root(tmp_path, project):
    client, _drive, _dist = reference_client(tmp_path)
    planted = beside_the_root(tmp_path)

    response = client.get(f"/references/{project}/sır.txt")

    refused(response, "..")
    assert SECRET not in response.get_data(as_text=True)
    assert planted.exists()


def test_a_reference_name_cannot_delete_outside_the_pool(tmp_path):
    client, drive, _dist = reference_client(tmp_path)
    (drive / "düğün" / "plan.json").write_text("{}", encoding="utf-8")

    response = client.post("/api/projects/düğün/references/../delete")

    refused(response, "..")
    assert (drive / "düğün" / "plan.json").exists()
