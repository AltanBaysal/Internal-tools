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


class FakeReferenceStore:
    """The pool as a dict per project, in insertion order.

    Insertion order is what the real one answers in: it sorts by the file's own timestamp, so the
    pool reads in the order it was filled.
    """

    def __init__(self):
        self.pools = {}

    def save(self, project, name, data):
        self.pools.setdefault(project, {})[name] = data

    def names(self, project):
        return list(self.pools.get(project, {}))

    def delete(self, project, name):
        self.pools.get(project, {}).pop(name, None)


def pool_of(store, references_store, project="düğün"):
    return list_references(store, references_store, project)


def test_a_reference_is_written_into_the_projects_pool():
    store, pool = FakeStore(), FakeReferenceStore()

    answer = add_references(store, pool, "düğün", [("kedi.png", b"PNG")])

    assert pool.pools["düğün"] == {"kedi.png": b"PNG"}
    # The pool comes back with the answer: the screen would ask for exactly this next.
    assert answer == [{"name": "kedi.png", "kind": references.PICTURE}]


def test_a_file_nobody_can_read_is_refused():
    """And nothing at all is written: the whole press is decided before the first write, so one
    bad file does not leave half an upload behind."""
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(UnknownReference) as exc:
        add_references(store, pool, "düğün", [("kedi.png", b"PNG"), ("notlar.txt", b"...")])

    assert "notlar.txt" in str(exc.value)
    assert pool.pools == {}


def test_a_reference_for_a_project_that_does_not_exist_is_refused():
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(ProjectMissing):
        add_references(store, pool, "yok", [("kedi.png", b"PNG")])


def test_the_pool_lists_in_the_order_it_was_filled():
    store, pool = FakeStore(), FakeReferenceStore()

    add_references(store, pool, "düğün", [("kedi.png", b"PNG"), ("dans.mp4", b"MP4")])
    add_references(store, pool, "düğün", [("rüzgar.wav", b"WAV")])

    assert pool_of(store, pool) == [{"name": "kedi.png", "kind": references.PICTURE},
                                    {"name": "dans.mp4", "kind": references.VIDEO},
                                    {"name": "rüzgar.wav", "kind": references.AUDIO}]


def test_a_file_the_pool_cannot_read_is_not_in_it():
    """The folder is the pool, so anything can be dropped into it from Drive. What the pool cannot
    give a kind is not a reference, and it is left where it is rather than listed."""
    store, pool = FakeStore(), FakeReferenceStore()
    pool.save("düğün", "notlar.txt", b"...")
    add_references(store, pool, "düğün", [("kedi.png", b"PNG")])

    assert pool_of(store, pool) == [{"name": "kedi.png", "kind": references.PICTURE}]


def test_a_second_file_with_the_same_name_stands_beside_the_first():
    store, pool = FakeStore(), FakeReferenceStore()

    add_references(store, pool, "düğün", [("kedi.png", b"ONE")])
    add_references(store, pool, "düğün", [("kedi.png", b"TWO")])

    assert pool.pools["düğün"] == {"kedi.png": b"ONE", "kedi-2.png": b"TWO"}


def test_two_files_with_one_name_in_one_press_both_land():
    # The names are worked out as the press is decided, so the second one already sees the first.
    store, pool = FakeStore(), FakeReferenceStore()

    add_references(store, pool, "düğün", [("kedi.png", b"ONE"), ("kedi.png", b"TWO")])

    assert list(pool.pools["düğün"]) == ["kedi.png", "kedi-2.png"]


def test_removing_takes_the_file_off_the_disk():
    store, pool = FakeStore(), FakeReferenceStore()
    add_references(store, pool, "düğün", [("kedi.png", b"PNG"), ("dans.mp4", b"MP4")])

    remove_reference(store, pool, "düğün", "kedi.png")

    assert pool_of(store, pool) == [{"name": "dans.mp4", "kind": references.VIDEO}]


def test_removing_something_that_is_not_there_is_not_an_error():
    """Deleting twice has to end where deleting once ends: another tab can get there first."""
    store, pool = FakeStore(), FakeReferenceStore()

    assert remove_reference(store, pool, "düğün", "kedi.png") == []
