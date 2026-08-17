import pytest

from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.domain.errors import FileNotFound
from backend.features.workspace.domain.usecases.read_file import read_file
from backend.services.store.store import Store


def _files(tmp_path):
    return FileFileStore(Store(str(tmp_path)))


def test_reading_gives_the_text_with_its_chip_and_time(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "the body")
    body = read_file(files, "p1", "plan.md")
    assert (body.file.name, body.file.ext, body.text) == ("plan.md", "md", "the body")
    assert body.file.modified_at.startswith("20")


def test_size_counts_bytes_not_characters(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "note.md", "ü")
    # One character, two bytes -- which is why the browser is not asked to count it.
    assert read_file(files, "p1", "note.md").size == 2


def test_an_empty_file_has_no_size(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "empty.md", "")
    assert read_file(files, "p1", "empty.md").size == 0


def test_a_file_that_is_not_there_is_reported(tmp_path):
    with pytest.raises(FileNotFound):
        read_file(_files(tmp_path), "p1", "ghost.md")


def test_one_reading_answers_both_questions(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "body")
    body = read_file(files, "p1", "plan.md")
    # The stat and the text come out of the same call: split in two, a file deleted in between
    # would answer one question and not the other.
    assert body.file.name == "plan.md" and body.text == "body"
