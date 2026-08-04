from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.services.drive.storage import DriveStorage


def store_at(path):
    return DrivePhotoStore(DriveStorage(str(path)))


def test_project_exists_follows_the_folder(tmp_path):
    store = store_at(tmp_path)
    (tmp_path / "düğün").mkdir()
    assert store.project_exists("düğün") is True
    assert store.project_exists("yok") is False


def test_next_number_starts_at_zero(tmp_path):
    (tmp_path / "düğün").mkdir()
    assert store_at(tmp_path).next_number("düğün") == 0


def test_delete_removes_the_photo_from_the_project_folder(tmp_path):
    storage = DriveStorage(str(tmp_path))
    store = DrivePhotoStore(storage)
    store.save("düğün", 0, "a", b"PNG")

    store.delete("düğün", "0_a.png")

    assert storage.list_files("düğün") == []


def test_next_number_is_highest_plus_one(tmp_path):
    project = tmp_path / "düğün"
    project.mkdir()
    for name in ("0_a.png", "7_c.png", "3_b.png", "notlar.txt", "_bozuk.png"):
        (project / name).write_bytes(b"x")
    assert store_at(tmp_path).next_number("düğün") == 8


def test_save_writes_the_file_and_returns_its_name(tmp_path):
    (tmp_path / "düğün").mkdir()
    assert store_at(tmp_path).save("düğün", 4, "a", b"PNG") == "4_a.png"
    assert (tmp_path / "düğün" / "4_a.png").read_bytes() == b"PNG"


def test_photo_dir_is_the_project_folder(tmp_path):
    assert store_at(tmp_path).photo_dir("düğün") == str(tmp_path / "düğün")
