import pytest

from backend.features.photo_generation.domain import references
from backend.features.photo_generation.domain.usecases.add_references import (
    UnknownReference,
    add_references,
)
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.remove_reference import remove_reference
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class FakeStore:
    """Only what the pool asks of the photo store: does this project exist at all."""

    def __init__(self, projects=("düğün",)):
        self.projects = list(projects)

    def project_exists(self, project):
        return project in self.projects


class FakeClips:
    """ffprobe, without ffprobe: answers from a table of bytes, and remembers what it was asked.

    Remembering is the point of one test: a picture has no length, so nothing may ever ask it.
    """

    def __init__(self, lengths=None, fails=None):
        self.lengths = dict(lengths or {})
        self.fails = fails
        self.asked = []

    def seconds(self, data):
        self.asked.append(data)
        if self.fails:
            raise RuntimeError(self.fails)
        return self.lengths.get(data, 4.0)


class FakeReferenceStore:
    """The pool as a dict per project, answering by name like the real one.

    By name because that is the one order a folder can promise: a file's timestamp is coarser than
    the writes, so the order they were written in is not on the disk to be read.

    It asks the same clip tool the real one asks, for the same reason: a stored file's length is
    read off the file, never remembered from the day it arrived.
    """

    def __init__(self, clips=None):
        self.pools = {}
        self._clips = clips

    def save(self, project, name, data):
        self.pools.setdefault(project, {})[name] = data

    def items(self, project):
        return [(name, self._length(name, data))
                for name, data in sorted(self.pools.get(project, {}).items())]

    def delete(self, project, name):
        self.pools.get(project, {}).pop(name, None)

    def _length(self, name, data):
        if self._clips is None or references.kind_of(name) == references.PICTURE:
            return None
        return self._clips.seconds(data)


def pool_of(store, references_store, project="düğün"):
    return list_references(store, references_store, project)


def added(store, pool, files, clips=None, project="düğün"):
    return add_references(store, pool, clips or FakeClips(), project, files)


def picture(name="kedi.png"):
    return {"name": name, "kind": references.PICTURE, "seconds": None}


def clip(name, kind, seconds=4.0):
    return {"name": name, "kind": kind, "seconds": seconds}


def test_a_reference_is_written_into_the_projects_pool():
    store, pool = FakeStore(), FakeReferenceStore()

    answer = added(store, pool, [("kedi.png", b"PNG")])

    assert pool.pools["düğün"] == {"kedi.png": b"PNG"}
    # The pool comes back with the answer: the screen would ask for exactly this next.
    assert answer == [picture()]


def test_a_file_nobody_can_read_is_refused():
    """And nothing at all is written: the whole press is decided before the first write, so one
    bad file does not leave half an upload behind."""
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(UnknownReference) as exc:
        added(store, pool, [("kedi.png", b"PNG"), ("notlar.txt", b"...")])

    assert "notlar.txt" in str(exc.value)
    assert pool.pools == {}


def test_a_reference_for_a_project_that_does_not_exist_is_refused():
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(ProjectMissing):
        added(store, pool, [("kedi.png", b"PNG")], project="yok")


def test_the_pool_lists_in_one_stable_order():
    """By name, whichever order they arrived in: that is the one order a folder can promise, and
    the order the user WANTS is a document of its own (madde 300)."""
    clips = FakeClips()
    store, pool = FakeStore(), FakeReferenceStore(clips)

    added(store, pool, [("kedi.png", b"PNG")], clips)
    added(store, pool, [("rüzgar.wav", b"WAV"), ("dans.mp4", b"MP4")], clips)

    assert pool_of(store, pool) == [clip("dans.mp4", references.VIDEO), picture(),
                                    clip("rüzgar.wav", references.AUDIO)]


def test_the_pool_says_how_long_each_clip_is():
    """The length is read off the file every time, never remembered from the day it arrived: a
    reference the user replaced in Drive would otherwise be counted as the old one."""
    clips = FakeClips({b"MP4": 6.5})
    store, pool = FakeStore(), FakeReferenceStore(clips)

    added(store, pool, [("kedi.png", b"PNG"), ("dans.mp4", b"MP4")], clips)

    assert pool_of(store, pool) == [clip("dans.mp4", references.VIDEO, 6.5), picture()]


def test_only_a_clip_is_asked_how_long_it_is():
    clips = FakeClips()
    store, pool = FakeStore(), FakeReferenceStore(clips)

    added(store, pool, [("kedi.png", b"PNG"), ("dans.mp4", b"MP4")], clips)

    # A picture has no length at all, so nothing may ever ask it for one.
    assert b"PNG" not in clips.asked


def test_a_clip_whose_length_cannot_be_read_is_refused():
    """A reference whose length is unknown would make every limit after it unanswerable."""
    clips = FakeClips(fails="moov atom not found")
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(references.PoolLimit) as exc:
        added(store, pool, [("dans.mp4", b"MP4")], clips)

    assert "moov atom not found" in str(exc.value)
    assert pool.pools == {}


def test_a_reference_that_passes_a_limit_is_refused_and_nothing_is_written():
    clips = FakeClips({b"LONG": 20.0})
    store, pool = FakeStore(), FakeReferenceStore(clips)

    with pytest.raises(references.PoolLimit):
        added(store, pool, [("kedi.png", b"PNG"), ("uzun.mp4", b"LONG")], clips)

    assert pool.pools == {}


def test_a_file_the_pool_cannot_read_is_not_in_it():
    """The folder is the pool, so anything can be dropped into it from Drive. What the pool cannot
    give a kind is not a reference, and it is left where it is rather than listed."""
    store, pool = FakeStore(), FakeReferenceStore()
    pool.save("düğün", "notlar.txt", b"...")
    added(store, pool, [("kedi.png", b"PNG")])

    assert pool_of(store, pool) == [picture()]


def test_a_second_file_with_the_same_name_stands_beside_the_first():
    store, pool = FakeStore(), FakeReferenceStore()

    added(store, pool, [("kedi.png", b"ONE")])
    added(store, pool, [("kedi.png", b"TWO")])

    assert pool.pools["düğün"] == {"kedi.png": b"ONE", "kedi-2.png": b"TWO"}


def test_two_files_with_one_name_in_one_press_both_land():
    # The names are worked out as the press is decided, so the second one already sees the first.
    store, pool = FakeStore(), FakeReferenceStore()

    added(store, pool, [("kedi.png", b"ONE"), ("kedi.png", b"TWO")])

    assert list(pool.pools["düğün"]) == ["kedi.png", "kedi-2.png"]


def test_removing_takes_the_file_off_the_disk():
    clips = FakeClips()
    store, pool = FakeStore(), FakeReferenceStore(clips)
    added(store, pool, [("kedi.png", b"PNG"), ("dans.mp4", b"MP4")], clips)

    remove_reference(store, pool, "düğün", "kedi.png")

    assert pool_of(store, pool) == [clip("dans.mp4", references.VIDEO)]


def test_removing_something_that_is_not_there_is_not_an_error():
    """Deleting twice has to end where deleting once ends: another tab can get there first."""
    store, pool = FakeStore(), FakeReferenceStore()

    assert remove_reference(store, pool, "düğün", "kedi.png") == []
