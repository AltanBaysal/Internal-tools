import pytest

from backend.services.drive.storage import DriveStorage


def test_a_stamp_changes_when_the_file_does(tmp_path):
    # What a caller holding a parsed copy checks before trusting it. Length as well as time: an
    # append inside the same second still has to read as a change.
    storage = DriveStorage(str(tmp_path))
    storage.append_line("düğün", "photos.jsonl", "bir")
    before = storage.stamp("düğün", "photos.jsonl")

    storage.append_line("düğün", "photos.jsonl", "iki")

    assert before is not None
    assert storage.stamp("düğün", "photos.jsonl") != before


def test_a_file_that_is_not_there_has_no_stamp(tmp_path):
    assert DriveStorage(str(tmp_path)).stamp("düğün", "yok.jsonl") is None


def test_deleting_a_file_removes_it(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.write_bytes("düğün", "0_a.png", b"PNG")
    storage.delete_file("düğün", "0_a.png")
    assert storage.list_files("düğün") == []


def test_deleting_a_file_that_is_already_gone_is_not_an_error(tmp_path):
    DriveStorage(str(tmp_path)).delete_file("düğün", "yok.png")


def test_make_dir_creates_folder_and_returns_mtime(tmp_path):
    storage = DriveStorage(str(tmp_path))
    mtime = storage.make_dir("düğün")
    assert mtime is not None and mtime > 0
    assert (tmp_path / "düğün").is_dir()


def test_make_dir_returns_none_when_name_taken(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    assert storage.make_dir("düğün") is None


def test_renaming_a_folder_takes_everything_in_it(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    storage.write_text("düğün", "plan.jsonl", "bir satır")

    assert storage.rename_dir("düğün", "nikah") is not False

    assert storage.read_text("nikah", "plan.jsonl") == "bir satır"
    assert not storage.dir_exists("düğün")


def test_renaming_onto_a_name_that_is_taken_moves_nothing(tmp_path):
    # Two answers because the caller has two different sentences for them: None is a clash, False is
    # a folder that was not there. The mtime that comes back on success is what make_dir answers.
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    storage.make_dir("nikah")

    assert storage.rename_dir("düğün", "nikah") is None
    assert storage.rename_dir("yok", "başka") is False

    assert storage.dir_exists("düğün")
    assert storage.dir_exists("nikah")


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


def test_dir_exists(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    assert storage.dir_exists("düğün") is True
    assert storage.dir_exists("yok") is False


def test_write_bytes_then_list_files(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    storage.write_bytes("düğün", "0_a.png", b"PNG")
    assert (tmp_path / "düğün" / "0_a.png").read_bytes() == b"PNG"
    assert storage.list_files("düğün") == ["0_a.png"]


def test_list_files_skips_directories(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    storage.make_dir("düğün/altklasör")
    storage.write_bytes("düğün", "0_a.png", b"PNG")
    assert storage.list_files("düğün") == ["0_a.png"]


def test_list_files_returns_empty_for_missing_dir(tmp_path):
    assert DriveStorage(str(tmp_path)).list_files("yok") == []


def test_dir_path_joins_root_and_subdir(tmp_path):
    storage = DriveStorage(str(tmp_path))
    assert storage.dir_path("düğün") == str(tmp_path / "düğün")


def test_read_text_returns_none_when_the_file_is_not_there(tmp_path):
    assert DriveStorage(str(tmp_path)).read_text("düğün", "settings.json") is None


def test_write_text_creates_the_folder_and_round_trips(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.write_text("düğün", "settings.json", '{"negatif": "bulanık"}')
    assert storage.read_text("düğün", "settings.json") == '{"negatif": "bulanık"}'


def test_write_text_replaces_what_was_there(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.write_text("düğün", "settings.json", "eski")
    storage.write_text("düğün", "settings.json", "yeni")
    assert storage.read_text("düğün", "settings.json") == "yeni"


def test_append_line_creates_the_file_and_keeps_earlier_lines(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.append_line("düğün", "photos.jsonl", '{"file": "0_a.png"}')
    storage.append_line("düğün", "photos.jsonl", '{"file": "0_b.png"}')
    assert storage.read_lines("düğün", "photos.jsonl") == [
        '{"file": "0_a.png"}', '{"file": "0_b.png"}']


def test_read_lines_is_empty_when_the_file_is_not_there(tmp_path):
    assert DriveStorage(str(tmp_path)).read_lines("düğün", "photos.jsonl") == []


def test_read_lines_skips_blank_lines(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.write_text("düğün", "photos.jsonl", "ilk\n\n   \nikinci\n")
    assert storage.read_lines("düğün", "photos.jsonl") == ["ilk", "ikinci"]
