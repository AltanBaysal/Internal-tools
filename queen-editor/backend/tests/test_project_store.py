from backend.features.projects.data.project_store import DriveProjectStore
from backend.services.drive.storage import DriveStorage


def store_at(path):
    return DriveProjectStore(DriveStorage(str(path)))


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
