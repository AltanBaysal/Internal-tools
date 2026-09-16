from backend.features.projects.data.project_store import DriveProjectStore
from backend.services.drive.storage import DriveStorage


def store_at(path):
    return DriveProjectStore(DriveStorage(str(path)))


def test_list_archived_on_a_root_that_never_archived_anything(tmp_path):
    """A fresh install has no archive folder, and that is not an error -- it is an empty archive."""
    assert store_at(tmp_path).list_archived() == []


def test_create_makes_folder_and_returns_project(tmp_path):
    created = store_at(tmp_path).create("kapak çekimi")
    assert created.name == "kapak çekimi"
    assert created.modified_at > 0
    assert (tmp_path / "kapak çekimi").is_dir()


def test_create_returns_none_when_folder_exists(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    assert store.create("düğün") is None


def test_list_returns_projects_for_every_folder(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    store.create("test")
    assert sorted(p.name for p in store.list()) == ["düğün", "test"]
    assert all(p.modified_at > 0 for p in store.list())


def test_the_archive_folder_is_not_a_project(tmp_path):
    """It sits under the same root as the projects, and the root's folders ARE the projects -- so
    without this the archive shows up on the projects screen as a project called arsiv."""
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")

    assert [p.name for p in store.list()] == []


def test_the_archive_lists_what_was_put_in_it(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    store.create("test")
    store.archive("düğün")

    archived = store.list_archived()

    assert [p.name for p in archived] == ["düğün"]
    assert all(p.modified_at > 0 for p in archived)
    assert [p.name for p in store.list()] == ["test"]


def test_archiving_moves_the_folder_out_of_the_root(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    (tmp_path / "düğün" / "0_a.png").write_bytes(b"PNG")

    store.archive("düğün")

    assert not (tmp_path / "düğün").exists()
    # Everything the project knows lives in its folder, so everything travels with it.
    assert (tmp_path / "arsiv" / "düğün" / "0_a.png").read_bytes() == b"PNG"


def test_restoring_brings_it_back(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")

    store.restore("düğün")

    assert [p.name for p in store.list()] == ["düğün"]
    assert store.list_archived() == []


def test_an_archived_project_is_not_there_any_more(tmp_path):
    """What the decision buys for free. Generation and export reach a project by name through
    dir_exists, so a project that has been moved is closed to both -- and no second rule anywhere
    had to be written to say so."""
    storage = DriveStorage(str(tmp_path))
    store = DriveProjectStore(storage)
    store.create("düğün")

    store.archive("düğün")

    assert storage.dir_exists("düğün") is False


def test_archiving_the_same_name_twice_is_refused(tmp_path):
    """Archive one, make another with the same name, archive that: the first one must not be
    overwritten, and a project's own folder is the only copy of its work."""
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")
    store.create("düğün")

    assert store.archive("düğün") is None


def test_archiving_something_that_is_not_there_says_so(tmp_path):
    assert store_at(tmp_path).archive("yok") is False


def test_restoring_onto_a_live_name_is_refused(tmp_path):
    store = store_at(tmp_path)
    store.create("düğün")
    store.archive("düğün")
    store.create("düğün")

    assert store.restore("düğün") is None


def test_restoring_something_the_archive_does_not_hold_says_so(tmp_path):
    assert store_at(tmp_path).restore("yok") is False
