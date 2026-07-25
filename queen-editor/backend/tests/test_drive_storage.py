import pytest

from backend.services.drive.storage import DriveStorage


def test_make_dir_creates_folder_and_returns_mtime(tmp_path):
    storage = DriveStorage(str(tmp_path))
    mtime = storage.make_dir("düğün")
    assert mtime is not None and mtime > 0
    assert (tmp_path / "düğün").is_dir()


def test_make_dir_returns_none_when_name_taken(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    assert storage.make_dir("düğün") is None


def test_list_dirs_returns_name_and_mtime(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    storage.make_dir("kapak çekimi")
    entries = storage.list_dirs()
    assert sorted(name for name, _ in entries) == ["düğün", "kapak çekimi"]
    assert all(mtime > 0 for _, mtime in entries)


def test_list_dirs_skips_files(tmp_path):
    (tmp_path / "not-a-project.txt").write_text("x", encoding="utf-8")
    assert DriveStorage(str(tmp_path)).list_dirs() == []


def test_list_dirs_raises_when_root_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        DriveStorage(str(tmp_path / "yok")).list_dirs()
