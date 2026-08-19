import os

import pytest

from backend.services.store.store import PathOutsideRoot, Store


@pytest.mark.parametrize(
    "rel", ["../escape.txt", "a/../../escape.txt", "/etc/passwd", "C:\\Windows\\x"]
)
def test_paths_escaping_the_root_are_rejected(tmp_path, rel):
    store = Store(str(tmp_path))
    with pytest.raises(PathOutsideRoot):
        store.write_text(rel, "no")


def test_write_creates_missing_parent_directories(tmp_path):
    store = Store(str(tmp_path))
    store.write_text("a/b/c.txt", "hello")
    assert store.read_text("a/b/c.txt") == "hello"


def test_missing_directory_lists_as_empty(tmp_path):
    assert Store(str(tmp_path)).list_dir("nothing/here") == []


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        Store(str(tmp_path)).read_text("nothing.txt")


def test_move_keeps_the_content_and_clears_the_old_place(tmp_path):
    store = Store(str(tmp_path))
    store.write_text("files/note.md", "body")
    store.move("files/note.md", "trash/note.md")
    assert store.read_text("trash/note.md") == "body"
    assert not store.exists("files/note.md")


def test_root_is_created_on_first_write_not_on_construction(tmp_path):
    root = tmp_path / "queenagent-root"
    store = Store(str(root))
    assert not os.path.exists(root)
    store.write_text("a.txt", "x")
    assert os.path.exists(root)
