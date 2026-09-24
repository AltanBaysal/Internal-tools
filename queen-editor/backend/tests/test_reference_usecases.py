import pytest

from backend.features.photo_generation.domain import references
from backend.features.photo_generation.domain.usecases.add_references import (
    UnknownReference,
    add_references,
)
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.prompt_list import InvalidPrompts
from backend.features.photo_generation.domain.usecases.queue_references import (
    NoReferenceProducer,
    queue_references,
)
from backend.features.photo_generation.domain.usecases.remove_reference import remove_reference
from backend.features.photo_generation.domain.usecases.save_reference_order import (
    InvalidReferenceOrder,
    save_reference_order,
)
from backend.features.photo_generation.domain.usecases.start_batch import (
    InvalidVariants,
    ProjectMissing,
)


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


class FakeOrderStore:
    """The order the user dragged, per project. A document of its own, because it answers a
    question the folder cannot: which slot each reference stands in."""

    def __init__(self, orders=None):
        self.orders = dict(orders or {})

    def read(self, project):
        return self.orders.get(project, {})

    def write(self, project, order):
        self.orders[project] = order


def pool_of(store, references_store, orders=None, project="düğün"):
    return list_references(store, references_store, orders or FakeOrderStore(), project)


def added(store, pool, files, clips=None, orders=None, project="düğün"):
    return add_references(store, pool, orders or FakeOrderStore(), clips or FakeClips(),
                          project, files)


def picture(name="kedi.png", slot=1):
    return {"name": name, "kind": references.PICTURE, "seconds": None, "slot": slot}


def clip(name, kind, seconds=4.0, slot=1):
    return {"name": name, "kind": kind, "seconds": seconds, "slot": slot}


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


def test_a_file_of_another_kind_is_refused_by_the_row_it_was_picked_into():
    """Madde 320: a row's own Ekle card picks into that row, and that a sound is not a picture is
    the server's rule to say (FOUNDATION 4). Nothing is written."""
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(UnknownReference) as exc:
        add_references(store, pool, FakeOrderStore(), FakeClips(), "düğün",
                       [("kisa-2.wav", b"WAV")], row=references.PICTURE)

    assert str(exc.value) == "kisa-2.wav fotoğraf yuvasına giremez — bu dosya ses."
    assert pool.pools == {}


def test_a_file_of_its_rows_kind_goes_into_that_row():
    store, pool = FakeStore(), FakeReferenceStore()

    answer = add_references(store, pool, FakeOrderStore(), FakeClips(), "düğün",
                            [("kedi.png", b"PNG")], row=references.PICTURE)

    assert answer == [picture()]


def test_a_reference_for_a_project_that_does_not_exist_is_refused():
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(ProjectMissing):
        added(store, pool, [("kedi.png", b"PNG")], project="yok")


def test_the_pool_lists_in_one_stable_order():
    """Kind by kind, and by name inside a kind while nobody has dragged anything: a slot is a place
    inside a row, so the pool is read a row at a time (madde 300)."""
    clips = FakeClips()
    store, pool = FakeStore(), FakeReferenceStore(clips)

    added(store, pool, [("kedi.png", b"PNG")], clips)
    added(store, pool, [("rüzgar.wav", b"WAV"), ("dans.mp4", b"MP4")], clips)

    # Each kind counts its own slots, so all three stand first in their own row.
    assert pool_of(store, pool) == [picture(), clip("dans.mp4", references.VIDEO),
                                    clip("rüzgar.wav", references.AUDIO)]


def test_the_pool_says_how_long_each_clip_is():
    """The length is read off the file every time, never remembered from the day it arrived: a
    reference the user replaced in Drive would otherwise be counted as the old one."""
    clips = FakeClips({b"MP4": 6.5})
    store, pool = FakeStore(), FakeReferenceStore(clips)

    added(store, pool, [("kedi.png", b"PNG"), ("dans.mp4", b"MP4")], clips)

    assert pool_of(store, pool) == [picture(), clip("dans.mp4", references.VIDEO, 6.5)]


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

    remove_reference(store, pool, FakeOrderStore(), "düğün", "kedi.png")

    assert pool_of(store, pool) == [clip("dans.mp4", references.VIDEO)]


def test_removing_something_that_is_not_there_is_not_an_error():
    """Deleting twice has to end where deleting once ends: another tab can get there first."""
    store, pool = FakeStore(), FakeReferenceStore()

    assert remove_reference(store, pool, FakeOrderStore(), "düğün", "kedi.png") == []


def test_the_pool_carries_the_slot_each_reference_stands_in():
    orders = FakeOrderStore({"düğün": {references.PICTURE: ["kuş.png", "kedi.png"]}})
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("kedi.png", b"ONE"), ("kuş.png", b"TWO")], orders=orders)

    assert [(row["name"], row["slot"]) for row in pool_of(store, pool, orders)] == [
        ("kuş.png", 1), ("kedi.png", 2)]


def test_removing_the_middle_one_leaves_its_slot_empty():
    """Madde 300's whole point: what is left does not slide up, because H3 would then read the
    prompt's <Picture 3> off a different picture."""
    orders = FakeOrderStore({"düğün": {references.PICTURE: ["bir.png", "iki.png", "üç.png"]}})
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [(f"{name}.png", b"PNG") for name in ("bir", "iki", "üç")], orders=orders)

    left = remove_reference(store, pool, orders, "düğün", "iki.png")

    assert [(row["name"], row["slot"]) for row in left] == [("bir.png", 1), ("üç.png", 3)]
    # The order is not touched at all: the name holds its slot, and the slot is now empty.
    assert orders.read("düğün")[references.PICTURE] == ["bir.png", "iki.png", "üç.png"]


def test_the_order_the_user_dragged_is_stored():
    orders = FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("kedi.png", b"ONE"), ("kuş.png", b"TWO")], orders=orders)

    left = save_reference_order(store, pool, orders,
                                "düğün", {references.PICTURE: ["kuş.png", "kedi.png"]})

    assert [row["name"] for row in left] == ["kuş.png", "kedi.png"]
    assert orders.read("düğün") == {references.PICTURE: ["kuş.png", "kedi.png"]}


def test_a_dragged_order_drops_the_names_it_left_out():
    """How a gap is closed: the screen sends the sequence it now shows, and the dead name that was
    holding a slot is simply not in it."""
    orders = FakeOrderStore({"düğün": {references.PICTURE: ["bir.png", "iki.png", "üç.png"]}})
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("bir.png", b"ONE"), ("üç.png", b"THREE")], orders=orders)

    left = save_reference_order(store, pool, orders,
                                "düğün", {references.PICTURE: ["bir.png", "üç.png"]})

    assert [(row["name"], row["slot"]) for row in left] == [("bir.png", 1), ("üç.png", 2)]


@pytest.mark.parametrize("order", ["kedi.png", {"picture": "kedi.png"}, {"picture": [7]}])
def test_an_order_that_is_not_lists_of_names_is_refused(order):
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(InvalidReferenceOrder):
        save_reference_order(store, pool, FakeOrderStore(), "düğün", order)


def ready_pool(orders=None):
    """A pool with one picture in it and no holes -- everything a reference run needs."""
    orders = orders or FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("kedi.png", b"PNG")], orders=orders)
    return store, pool, orders


def run(store, pool, orders, prompts='["gotik kız"]', variants=1, has_h3=True, project="düğün"):
    """A reference run, as far as its refusals.

    Everything a run would need once it is allowed to start is None here on purpose: these tests
    are about the checks that come first, and nothing past them is touched. What a run that IS
    allowed does is tested beside the queue's own fakes (test_photo_usecases).

    The H3 flag rides with the stores rather than with the press: which video model the notebook
    installed is the installation's answer, and main.py binds it once.
    """
    return queue_references(None, store, None, None, None, pool, orders, None, None, None,
                            has_h3, project, prompts, variants)


def test_a_reference_run_without_h3_is_refused():
    """Only H3 has a mode that reads references; WAN has nothing to be handed them."""
    store, pool, orders = ready_pool()

    with pytest.raises(NoReferenceProducer) as exc:
        run(store, pool, orders, has_h3=False)

    assert "H3" in str(exc.value)


def test_a_reference_run_with_an_empty_pool_is_refused():
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(references.PoolLimit) as exc:
        run(store, pool, FakeOrderStore())

    assert "referans" in str(exc.value).lower()


def test_a_reference_run_with_a_gap_in_the_pool_is_refused():
    """H3 packs references tight and numbers them by order, so a hole would quietly move every
    reference after it (madde 300)."""
    orders = FakeOrderStore({"düğün": {references.PICTURE: ["bir.png", "iki.png", "üç.png"]}})
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("bir.png", b"1"), ("üç.png", b"3")], orders=orders)

    with pytest.raises(references.PoolLimit) as exc:
        run(store, pool, orders)

    assert "fotoğraf" in str(exc.value)


def test_a_reference_run_reads_the_prompt_list_the_way_the_photo_panel_does():
    store, pool, orders = ready_pool()

    with pytest.raises(InvalidPrompts):
        run(store, pool, orders, prompts="gotik kız")


@pytest.mark.parametrize("variants", [0, 27])
def test_a_reference_run_counts_variants_the_way_a_batch_does(variants):
    store, pool, orders = ready_pool()

    with pytest.raises(InvalidVariants):
        run(store, pool, orders, variants=variants)
