import pytest

from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.errors import FileNotFound
from backend.features.workspace.domain.project import Project
from backend.features.workspace.domain.usecases.read_file import read_file
from backend.services.store.store import Store


def _files(tmp_path):
    # A file lives in a project, and projects.json is what says it is there (Madde 447).
    store = Store(str(tmp_path))
    projects = FileProjectStore(store)
    projects.add(Project(id="p1", name="Thesis", created_at="2026-08-09T10:00:00+00:00"))
    return FileFileStore(store, projects)


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


def test_a_file_projects_json_does_not_name_is_not_read(tmp_path):
    # A name from the address becomes a path only once projects.json names it.
    files = _files(tmp_path)
    Store(str(tmp_path)).write_text("p1/files/stray.md", "nobody wrote me")
    with pytest.raises(FileNotFound):
        read_file(files, "p1", "stray.md")
    assert files.read("p1", "stray.md") is None


def test_a_row_whose_file_is_gone_reads_as_not_found(tmp_path):
    # Not found, not a crash: the row outlived its file (a delete a sudden death half finished).
    files = _files(tmp_path)
    files.write("p1", "plan.md", "body")
    Store(str(tmp_path)).move("p1/files/plan.md", "p1/trash/plan.md")
    with pytest.raises(FileNotFound):
        read_file(files, "p1", "plan.md")
    assert files.read("p1", "plan.md") is None


def test_one_reading_answers_both_questions(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "body")
    body = read_file(files, "p1", "plan.md")
    # The row and the text come back together, the row out of memory: one trip to the disk.
    assert body.file.name == "plan.md" and body.text == "body"
