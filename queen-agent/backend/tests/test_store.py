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
    assert store.list_dir("files") == []


# Madde 59. A write that dies partway must leave what it was overwriting alone -- the first
# principle, and the one place the store broke it. The failure here is real rather than injected:
# "\ud800" is a lone surrogate, which cannot be encoded as utf-8 and raises inside handle.write.
BAD_TEXT = "\ud800"


def test_a_failed_write_leaves_the_old_file_alone(tmp_path):
    store = Store(str(tmp_path))
    store.write_text("a.txt", "body")

    with pytest.raises(UnicodeEncodeError):
        store.write_text("a.txt", BAD_TEXT)

    assert store.read_text("a.txt") == "body"


def test_a_failed_write_leaves_nothing_behind(tmp_path):
    # Half a file is rubbish beside the user's own, and a person opening the folder on Drive would
    # take it for one of theirs.
    store = Store(str(tmp_path))
    store.write_text("a.txt", "body")

    with pytest.raises(UnicodeEncodeError):
        store.write_text("a.txt", BAD_TEXT)
    assert store.list_dir("") == ["a.txt"]

    store.write_text("a.txt", "again")
    assert store.list_dir("") == ["a.txt"]


def test_the_temporary_file_is_written_beside_its_target(tmp_path, monkeypatch):
    """os.replace cannot cross a filesystem. On Colab the root is a Drive mount and /tmp is local
    disk, so a temporary written to the system's temp directory would fail every single move -- and
    never once on the machine this is developed on."""
    seen = []
    real = os.replace

    def watching(src, dst):
        seen.append((src, dst))
        return real(src, dst)

    monkeypatch.setattr(os, "replace", watching)
    Store(str(tmp_path)).write_text("deep/a.txt", "body")

    assert seen, "yazma os.replace kullanmıyor — hedef yerinde kesiliyor"
    src, dst = seen[-1]
    assert os.path.dirname(src) == os.path.dirname(dst)


def test_root_is_created_on_first_write_not_on_construction(tmp_path):
    root = tmp_path / "queenagent-root"
    store = Store(str(root))
    assert not os.path.exists(root)
    store.write_text("a.txt", "x")
    assert os.path.exists(root)


# Madde 447. On Drive every call is a round trip, and making a folder that is already there costs
# three of them; a folder is made only when the write finds it missing.


def _counting_makedirs(monkeypatch):
    made = []
    real = os.makedirs

    def counting(path, *args, **kwargs):
        made.append(path)
        return real(path, *args, **kwargs)

    monkeypatch.setattr(os, "makedirs", counting)
    return made


def test_a_write_into_a_folder_that_is_there_makes_no_folder(tmp_path, monkeypatch):
    store = Store(str(tmp_path))
    store.write_text("a/b.txt", "first")
    made = _counting_makedirs(monkeypatch)
    store.write_text("a/b.txt", "second")
    store.write_text("a/c.txt", "third")
    assert made == [], "Var olan klasöre yazmak klasör yarattı"
    assert store.read_text("a/b.txt") == "second"


def test_a_move_into_a_folder_that_is_there_makes_no_folder(tmp_path, monkeypatch):
    store = Store(str(tmp_path))
    store.write_text("files/one.md", "1")
    store.write_text("trash/old.md", "0")
    made = _counting_makedirs(monkeypatch)
    store.move("files/one.md", "trash/one.md")
    assert made == [], "Var olan klasöre taşımak klasör yarattı"
    assert store.list_dir("trash") == ["old.md", "one.md"]


def test_a_move_into_a_missing_folder_makes_it(tmp_path):
    store = Store(str(tmp_path))
    store.write_text("files/one.md", "1")
    store.move("files/one.md", "deep/trash/one.md")
    assert store.read_text("deep/trash/one.md") == "1"


def test_mtime_is_the_files_own_time(tmp_path):
    # Only 448's move of old projects reads one: the old layout kept the pin's moment and a file's
    # time nowhere else. It goes with 448.
    store = Store(str(tmp_path))
    store.write_text("p1/pinned", "")
    os.utime(tmp_path / "p1" / "pinned", (1_000_000_000, 1_000_000_000))
    assert store.mtime("p1/pinned") == 1_000_000_000


def test_a_move_of_something_that_is_not_there_still_fails(tmp_path):
    with pytest.raises(FileNotFoundError):
        Store(str(tmp_path)).move("ghost.md", "trash/ghost.md")
