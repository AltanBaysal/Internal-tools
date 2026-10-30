"""Madde 523: two writes of one file at the same moment lose neither.

The user, 30 Ekim -- "bu hatalarıda çöz istersen". 512's coder found two files still read, changed
and written back whole with no lock: the reference pool's order (an upload, a removal, a drag) and
the archive marks (arsiv.json: archive, restore, delete, rename). Each test lets the second write in
between the first's read and its write, over a real folder: a fake that keeps no file could not lose
a write.
"""
import os
import threading
import time
from functools import partial

import pytest

from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.data.reference_order_store import DriveReferenceOrderStore
from backend.features.photo_generation.data.reference_store import DriveReferenceStore
from backend.features.photo_generation.domain import layers, references
from backend.features.photo_generation.domain.usecases.add_references import add_references
from backend.features.photo_generation.domain.usecases.follow_delete import follow_delete
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.remove_reference import remove_reference
from backend.features.photo_generation.domain.usecases.save_reference_order import (
    save_reference_order,
)
from backend.features.photo_generation.domain.usecases.start_batch import (
    ProjectMissing,
    start_batch,
)
from backend.features.photo_generation.runner import PhotoRunner
from backend.features.projects.data.project_store import DriveProjectStore
from backend.features.projects.domain.usecases.delete_project import delete_project
from backend.services.storage import storage as storage_module
from backend.services.storage.storage import TEMP_PREFIX, Storage
from backend.tests.test_photo_usecases import FakeGenerator

# How long the first party waits for the second to get in: long enough for a few steps over a
# temporary folder. A second write made to wait for a lock does not finish in it, and the first goes
# on.
WINDOW = 0.2


class Meanwhile:
    """Lets a second party in, in a thread of its own, right after the first answer of a method."""

    def __init__(self):
        self.thread = None
        self.failure = None

    def after_first(self, obj, method, second):
        original = getattr(obj, method)

        def hooked(*args, **kwargs):
            answer = original(*args, **kwargs)
            setattr(obj, method, original)
            self.now(second)
            return answer

        setattr(obj, method, hooked)

    def now(self, second):
        """Let the second party in from here."""
        self.thread = threading.Thread(target=self._run, args=(second,))
        self.thread.start()
        self.thread.join(WINDOW)

    def _run(self, second):
        try:
            second()
        except BaseException as exc:        # handed to the test by done()
            self.failure = exc

    def done(self):
        """Wait for the second party; the error it met, if any, is the test's."""
        self.thread.join(5)
        assert not self.thread.is_alive()
        if self.failure is not None:
            raise self.failure


# --- the reference pool --------------------------------------------------------------------------

class Pool:
    """düğün's reference pool on a real folder, with the stores its three doors use."""

    def __init__(self, tmp_path, *names):
        (tmp_path / "düğün").mkdir()
        self.dir = tmp_path / "düğün" / "referans"
        self.storage = storage = Storage(str(tmp_path))
        self.store = DrivePhotoStore(storage, storage)
        self.pool = DriveReferenceStore(storage)
        self.orders = DriveReferenceOrderStore(storage)
        self.plan = DrivePlanStore(storage)
        if names:
            self.add(*names)

    def add(self, *files):
        """Each file a name, or a (name, bytes) pair."""
        files = [(one, one.encode()) if isinstance(one, str) else one for one in files]
        add_references(self.store, self.pool, self.orders, None, self.plan, "düğün", files)

    def remove(self, name):
        remove_reference(self.store, self.pool, self.orders, self.plan, "düğün", name)

    def drag(self, names):
        save_reference_order(self.store, self.pool, self.orders, self.plan, "düğün",
                             {references.PICTURE: names})

    def standing(self):
        """The pictures as the pool places them: by the saved order."""
        return [row["name"] for row in
                list_references(self.store, self.pool, self.orders, "düğün")]

    def ordered(self):
        return self.orders.read("düğün").get(references.PICTURE)


def test_two_uploads_of_one_name_at_once_keep_both_files(tmp_path):
    """Each upload chose its free name from the pool it had read: both took kedi.png, and the later
    file was written over the earlier."""
    pool, meanwhile = Pool(tmp_path), Meanwhile()
    meanwhile.after_first(pool.pool, "items", lambda: pool.add(("kedi.png", b"IKINCI")))

    pool.add(("kedi.png", b"ILK"))
    meanwhile.done()

    assert sorted(path.read_bytes() for path in pool.dir.iterdir()) == [b"IKINCI", b"ILK"]
    assert sorted(pool.ordered()) == ["kedi-2.png", "kedi.png"]


@pytest.mark.parametrize("first, then", [
    (lambda pool: pool.add("bir.png"), ["eski.png", "bir.png", "yeni.png"]),
    (lambda pool: pool.remove("eski.png"), ["yeni.png"]),
    (lambda pool: pool.drag(["eski.png"]), ["eski.png", "yeni.png"]),
], ids=["upload", "removal", "drag"])
def test_an_upload_in_the_middle_of_another_write_keeps_its_place(tmp_path, first, then):
    """Each door read the order and wrote it back whole: an upload landing in between was dropped
    from it, and stood wherever its name sorts rather than at the end of its row."""
    pool, meanwhile = Pool(tmp_path, "eski.png"), Meanwhile()
    meanwhile.after_first(pool.orders, "read", lambda: pool.add("yeni.png"))

    first(pool)
    meanwhile.done()

    assert pool.ordered() == then
    assert pool.standing() == then


def test_an_upload_the_pool_refuses_leaves_no_hidden_file_behind(tmp_path):
    """The bytes are written under hidden names before the gate (madde 523's reviewer), and the
    limit is weighed under it: a refusal there takes them away, on the disk itself."""
    pool = Pool(tmp_path, *[f"{n}.png" for n in range(references.LIMITS[references.PICTURE])])
    before = sorted(path.name for path in pool.dir.iterdir())

    with pytest.raises(references.PoolLimit):
        pool.add("fazla.png")

    assert sorted(path.name for path in pool.dir.iterdir()) == before


def test_an_upload_sweeps_what_earlier_uploads_left_staged_an_hour_ago(tmp_path):
    """A staged file outlives its upload when the folder is renamed between the staging and the gate
    -- it moves with the folder, and the discard under the old name finds nothing -- or when the
    server dies. Hidden, but megabytes of Drive each (madde 523's reviewer). One younger may be
    another upload's still waiting for the gate, and stays."""
    pool = Pool(tmp_path, "eski.png")
    old, fresh = pool.dir / f"{TEMP_PREFIX}eski", pool.dir / f"{TEMP_PREFIX}taze"
    old.write_bytes(b"KALDI")
    fresh.write_bytes(b"BEKLIYOR")
    two_hours_ago = time.time() - 7200
    os.utime(old, (two_hours_ago, two_hours_ago))

    pool.add("yeni.png")

    assert sorted(path.name for path in pool.dir.iterdir()) == sorted(
        ["eski.png", "yeni.png", fresh.name])


# --- the archive marks ---------------------------------------------------------------------------

class Projects:
    """Three projects on a real root, düğün archived when asked."""

    def __init__(self, tmp_path, archived=False):
        self.storage = Storage(str(tmp_path))
        self.store = DriveProjectStore(self.storage)
        for name in ("düğün", "kına", "sünnet"):
            self.store.create(name)
        if archived:
            self.store.archive("düğün")

    def archived(self):
        return sorted(project.name for project in self.store.list_archived())


@pytest.mark.parametrize("archived, first, then", [
    (False, lambda store: store.archive("düğün"), ["düğün", "kına"]),
    (True, lambda store: store.restore("düğün"), ["kına"]),
    (True, lambda store: store.delete("düğün"), ["kına"]),
    (True, lambda store: store.rename("düğün", "nişan"), ["kına", "nişan"]),
], ids=["archive", "restore", "delete", "rename"])
def test_an_archive_in_the_middle_of_another_mark_change_is_kept(tmp_path, archived, first, then):
    """arsiv.json is one file for every project: each change read the marks and wrote them back
    whole, and an archive of another project landing in between was undone."""
    projects, meanwhile = Projects(tmp_path, archived), Meanwhile()
    meanwhile.after_first(projects.storage, "read_text", lambda: projects.store.archive("kına"))

    first(projects.store)
    meanwhile.done()

    assert projects.archived() == then


# --- a press as the project is deleted -----------------------------------------------------------

def test_a_press_as_the_project_is_deleted_starts_no_run(tmp_path):
    """522's reviewer: the delete stopped the production, a press then wrote its job and claimed the
    idle worker, and the folder went -- the worker was left pointed at a project that was no more.
    The press now waits for the delete and finds no project."""
    (tmp_path / "düğün").mkdir()
    storage = Storage(str(tmp_path))
    store, record, plan = DrivePhotoStore(storage, storage), DrivePhotoRecord(storage), \
        DrivePlanStore(storage)
    projects = DriveProjectStore(storage)
    runs = []
    runner = PhotoRunner(spawn=runs.append)
    meanwhile = Meanwhile()

    def press():
        start_batch(runner, store, record, plan, {layers.PHOTO: FakeGenerator()}, lambda: 7,
                    lambda: "t", "düğün", '["ilk"]', "", 1)

    meanwhile.after_first(storage, "read_text", press)      # the delete's read of the marks

    delete_project(projects, partial(follow_delete, runner, plan, lambda: None, lambda _: None),
                   "düğün")

    with pytest.raises(ProjectMissing):
        meanwhile.done()
    assert runner.status() == {"status": "idle"}
    assert runs == []
    assert not (tmp_path / "düğün").exists()


# --- an upload as the project is deleted ---------------------------------------------------------

def deleting(pool):
    """The delete as main.py wires it, over the pool's own root."""
    projects = DriveProjectStore(pool.storage)
    runner = PhotoRunner(spawn=lambda fn: None)
    return lambda: delete_project(
        projects, partial(follow_delete, runner, pool.plan, lambda: None, lambda _: None), "düğün")


def test_an_upload_during_a_slow_removal_never_brings_the_project_back(tmp_path, monkeypatch):
    """Madde 523's QA: an upload staged its bytes outside the gate into the referans folder a delete
    was removing; the removal failed on a folder that was no longer empty, the project survived
    gutted, and the upload took the gate, found it and answered 200 -- a deleted project back with
    that one reference. Drive's removal takes tens of seconds, so the window is real. Here the
    removal takes its files first and its folders after, and the upload comes in between."""
    pool, meanwhile = Pool(tmp_path, "eski.png"), Meanwhile()

    def slow_removal(path, *_args, **_kwargs):
        for folder, _dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(folder, name))
        meanwhile.now(lambda: pool.add("yeni.png"))
        for folder, _dirs, _files in os.walk(path, topdown=False):
            os.rmdir(folder)

    monkeypatch.setattr(storage_module.shutil, "rmtree", slow_removal)

    failed = None
    try:
        deleting(pool)()
    except OSError as exc:
        failed = exc

    with pytest.raises(ProjectMissing):
        meanwhile.done()
    assert not (tmp_path / "düğün").exists()
    assert failed is None


def test_an_upload_into_the_trash_by_name_is_told_there_is_no_project(tmp_path):
    """A crafted URL naming a deleted project's trash finds no project, like every other door."""
    pool = Pool(tmp_path)
    trash = pool.storage.trash_dir("düğün")

    with pytest.raises(ProjectMissing):
        add_references(pool.store, pool.pool, pool.orders, None, pool.plan, trash,
                       [("yeni.png", b"PNG")])
    assert not (tmp_path / trash / "referans").exists()


def test_an_upload_whose_project_is_deleted_before_its_bytes_go_is_told_it_is_gone(tmp_path):
    """The delete lands between the upload's look at the project and its staging: the bytes have
    nowhere to go, and the answer is the screen's sentence, not the OS's."""
    pool = Pool(tmp_path)
    stage = pool.pool.stage

    def deleted_first(project, data):
        pool.pool.stage = stage
        deleting(pool)()
        return stage(project, data)

    pool.pool.stage = deleted_first

    with pytest.raises(ProjectMissing):
        pool.add("yeni.png")
    assert not (tmp_path / "düğün").exists()
