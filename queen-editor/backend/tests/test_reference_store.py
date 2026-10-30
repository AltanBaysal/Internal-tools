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


def put(pool, name, data):
    """An upload's two steps: the bytes under a hidden name, then their own (madde 523)."""
    pool.place("düğün", pool.stage("düğün", data), name)


def test_a_clip_is_measured_where_the_pool_keeps_it(tmp_path):
    """ffprobe reads the file on Drive itself, so the path it is handed comes from the door: the
    mount is checked and the names are held to the root before it is."""
    pool, lengths = pool_at(tmp_path)
    put(pool, "a.mp4", b"MP4")
    put(pool, "b.png", b"PNG")

    assert pool.items("düğün") == [("a.mp4", 4.0), ("b.png", None)]
    assert lengths.asked == [str(tmp_path / "düğün" / "referans" / "a.mp4")]


def test_the_pool_folder_is_opened_by_its_first_file(tmp_path):
    pool, _lengths = pool_at(tmp_path)

    put(pool, "a.png", b"PNG")

    assert (tmp_path / "düğün" / "referans" / "a.png").read_bytes() == b"PNG"
    assert pool.dir_path("düğün") == str(tmp_path / "düğün" / "referans")


def test_a_staged_file_is_in_no_listing_and_a_discarded_one_is_gone(tmp_path):
    pool, _lengths = pool_at(tmp_path)

    staged = pool.stage("düğün", b"PNG")
    assert pool.items("düğün") == []
    pool.discard("düğün", staged)

    assert list((tmp_path / "düğün" / "referans").iterdir()) == []


def test_discarding_never_raises(tmp_path):
    """It runs on the way out of a failed upload, whose own error is the one to tell."""
    pool, _lengths = pool_at(tmp_path)

    pool.discard("düğün", "..")


def test_a_project_that_is_not_there_is_never_opened_by_an_upload(tmp_path):
    pool, _lengths = pool_at(tmp_path)

    with pytest.raises(FileNotFoundError):
        pool.stage("yok", b"PNG")

    assert not (tmp_path / "yok").exists()


def test_a_reference_name_cannot_leave_the_pool(tmp_path):
    pool, _lengths = pool_at(tmp_path)
    (tmp_path / "düğün" / "plan.json").write_text("{}", encoding="utf-8")

    with pytest.raises(StorageError):
        pool.delete("düğün", "..")

    assert (tmp_path / "düğün" / "plan.json").exists()
