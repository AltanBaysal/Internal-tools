import os
from types import SimpleNamespace

import pytest

from backend.services.store.store import PathOutsideRoot, RootUnreachable, Store


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


# Madde 490. The root is stat'ed before every operation, and never made: when Colab's Drive drops,
# a write that made its folders would make them on Colab's own disk and say it succeeded.

# Every public operation, called on a root holding p1/a.txt. A method added to Store and not here
# fails test_every_operation_is_checked.
CALLS = {
    "read_text": lambda store: store.read_text("p1/a.txt"),
    "write_text": lambda store: store.write_text("p1/b.txt", "new"),
    "list_dir": lambda store: store.list_dir("p1"),
    "move": lambda store: store.move("p1/a.txt", "trash/a.txt"),
}

DROPPED = "Transport endpoint is not connected"


def _root_stat(monkeypatch, root, answer):
    """os.stat with the root's own answer given by `answer(real_stat, path)`; every other path
    stats as it does. Returns the list of times the root was asked."""
    real = os.stat
    asked = []

    def stat(path, *args, **kwargs):
        if os.path.abspath(path) == os.path.abspath(root):
            asked.append(path)
            return answer(real, path)
        return real(path, *args, **kwargs)

    monkeypatch.setattr(os, "stat", stat)
    return asked


def _dropped(real, path):
    raise OSError(107, DROPPED, path)


def _tree(root):
    """Every folder and file under the root, with each file's text."""
    seen = []
    for folder, _dirs, files in os.walk(root):
        seen.append((os.path.relpath(folder, root), None))
        for name in files:
            with open(os.path.join(folder, name), encoding="utf-8") as handle:
                seen.append((os.path.relpath(os.path.join(folder, name), root), handle.read()))
    return sorted(seen, key=lambda entry: entry[0])


def _laid(root):
    os.mkdir(root)
    store = Store(str(root))
    store.write_text("p1/a.txt", "body")
    return store


def test_every_operation_is_checked():
    public = {name for name in vars(Store) if not name.startswith("_")}
    assert public == set(CALLS), "Store'un bir açık yöntemi bağlantı testlerinde yok"


@pytest.mark.parametrize("operation", sorted(CALLS))
def test_a_dropped_connection_stops_every_operation_and_writes_nothing(tmp_path, monkeypatch, operation):
    root = tmp_path / "root"
    store = _laid(root)
    before = _tree(root)
    _root_stat(monkeypatch, root, _dropped)
    with pytest.raises(RootUnreachable) as refused:
        CALLS[operation](store)
    # Not "not found": the callers' except FileNotFoundError would turn it into an empty answer.
    assert not isinstance(refused.value, FileNotFoundError)
    assert DROPPED in str(refused.value), "Hata işletim sisteminin cümlesini taşımıyor"
    assert _tree(root) == before


@pytest.mark.parametrize("operation", sorted(CALLS))
def test_a_missing_root_stops_every_operation_and_is_never_made(tmp_path, operation):
    root = tmp_path / "root"
    with pytest.raises(RootUnreachable) as refused:
        CALLS[operation](Store(str(root)))
    assert not isinstance(refused.value, FileNotFoundError)
    assert not root.exists(), "Kök açıldı"


def test_a_root_on_another_device_is_refused(tmp_path, monkeypatch):
    # Drive gone and a folder of the same name made on Colab's own disk: the stat succeeds, the
    # device is what tells them apart.
    store = _laid(tmp_path / "root")
    first = os.stat(tmp_path / "root").st_dev
    _root_stat(monkeypatch, tmp_path / "root", lambda real, path: SimpleNamespace(st_dev=first + 1))
    with pytest.raises(RootUnreachable) as refused:
        store.read_text("p1/a.txt")
    assert f"device {first}, now {first + 1}" in str(refused.value)


def test_construction_stats_nothing_and_each_operation_stats_the_root_once(tmp_path, monkeypatch):
    asked = _root_stat(monkeypatch, tmp_path, lambda real, path: real(path))
    store = Store(str(tmp_path))
    assert asked == [], "Kurulum diske dokundu"
    store.write_text("p1/a.txt", "body")
    assert len(asked) == 1
    for operation in sorted(CALLS):
        CALLS[operation](store)
        store.write_text("p1/a.txt", "body")
    assert len(asked) == 1 + 2 * len(CALLS), "Bir işlem kökü birden çok kez yokladı"


def test_a_root_gone_after_the_check_is_still_never_made(tmp_path, monkeypatch):
    # The connection drops between the check and the write: the write fails on its own, and the
    # folders it would make stop at the root.
    root = tmp_path / "root"
    _root_stat(monkeypatch, root, lambda real, path: real(str(tmp_path)))
    store = Store(str(root))
    with pytest.raises(FileNotFoundError):
        store.write_text("p1/chats/c1.json", "{}")
    with pytest.raises(FileNotFoundError):
        store.write_text("projects.json", "{}")
    with pytest.raises(FileNotFoundError):
        store.move("p1", "trash/p1")
    assert not root.exists(), "Kök açıldı"


# Madde 447. On Drive every call is a round trip, and making a folder that is already there costs
# one; a folder is made only when the write finds it missing.


def _counting_folder_makes(monkeypatch):
    made = []
    for name in ("makedirs", "mkdir"):
        real = getattr(os, name)

        def counting(path, *args, real=real, **kwargs):
            made.append(path)
            return real(path, *args, **kwargs)

        monkeypatch.setattr(os, name, counting)
    return made


def test_a_write_into_a_folder_that_is_there_makes_no_folder(tmp_path, monkeypatch):
    store = Store(str(tmp_path))
    store.write_text("a/b.txt", "first")
    made = _counting_folder_makes(monkeypatch)
    store.write_text("a/b.txt", "second")
    store.write_text("a/c.txt", "third")
    assert made == [], "Var olan klasöre yazmak klasör yarattı"
    assert store.read_text("a/b.txt") == "second"


def test_a_move_into_a_folder_that_is_there_makes_no_folder(tmp_path, monkeypatch):
    store = Store(str(tmp_path))
    store.write_text("files/one.md", "1")
    store.write_text("trash/old.md", "0")
    made = _counting_folder_makes(monkeypatch)
    store.move("files/one.md", "trash/one.md")
    assert made == [], "Var olan klasöre taşımak klasör yarattı"
    assert store.list_dir("trash") == ["old.md", "one.md"]


def test_a_move_into_a_missing_folder_makes_it(tmp_path):
    store = Store(str(tmp_path))
    store.write_text("files/one.md", "1")
    store.move("files/one.md", "deep/trash/one.md")
    assert store.read_text("deep/trash/one.md") == "1"


def test_a_write_into_a_new_project_makes_each_missing_folder_once(tmp_path, monkeypatch):
    store = Store(str(tmp_path))
    made = _counting_folder_makes(monkeypatch)
    store.write_text("p1/chats/c1.json", "{}")
    assert made == [str(tmp_path / "p1"), str(tmp_path / "p1" / "chats")]


def test_a_move_of_something_that_is_not_there_still_fails(tmp_path):
    with pytest.raises(FileNotFoundError):
        Store(str(tmp_path)).move("ghost.md", "trash/ghost.md")
