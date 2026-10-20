"""The reference pool over the one storage door: a folder of its own inside the project."""
import pytest

from backend.features.photo_generation.data.reference_store import DriveReferenceStore
from backend.services.storage.storage import Storage, StorageError


class Lengths:
    """ffprobe's answer, and where it was asked: the test machine has no ffprobe."""

    def __init__(self):
        self.asked = []

    def seconds_at(self, path):
        self.asked.append(path)
        return 4.0


def pool_at(path):
    (path / "düğün").mkdir()
    lengths = Lengths()
    return DriveReferenceStore(Storage(str(path)), lengths), lengths


def test_a_clip_is_measured_where_the_pool_keeps_it(tmp_path):
    """ffprobe reads the file on Drive itself, so the path it is handed comes from the door: the
    mount is checked and the names are held to the root before it is."""
    pool, lengths = pool_at(tmp_path)
    pool.save("düğün", "a.mp4", b"MP4")
    pool.save("düğün", "b.png", b"PNG")

    assert pool.items("düğün") == [("a.mp4", 4.0), ("b.png", None)]
    assert lengths.asked == [str(tmp_path / "düğün" / "referans" / "a.mp4")]


def test_the_pool_folder_is_opened_by_its_first_file(tmp_path):
    pool, _lengths = pool_at(tmp_path)

    pool.save("düğün", "a.png", b"PNG")

    assert (tmp_path / "düğün" / "referans" / "a.png").read_bytes() == b"PNG"
    assert pool.dir_path("düğün") == str(tmp_path / "düğün" / "referans")


def test_a_project_that_is_not_there_is_never_opened_by_an_upload(tmp_path):
    pool, _lengths = pool_at(tmp_path)

    with pytest.raises(FileNotFoundError):
        pool.save("yok", "a.png", b"PNG")

    assert not (tmp_path / "yok").exists()


def test_a_reference_name_cannot_leave_the_pool(tmp_path):
    pool, _lengths = pool_at(tmp_path)
    (tmp_path / "düğün" / "plan.json").write_text("{}", encoding="utf-8")

    with pytest.raises(StorageError):
        pool.delete("düğün", "..")

    assert (tmp_path / "düğün" / "plan.json").exists()
