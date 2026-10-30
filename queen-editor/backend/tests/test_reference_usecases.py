import pytest

from backend.features.photo_generation.domain import references
from backend.features.photo_generation.domain.usecases.add_references import (
    UnknownReference,
    add_references,
)
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.prompt_list import InvalidPrompts
from backend.features.photo_generation.domain.usecases.queue_references import queue_references
from backend.features.photo_generation.domain.usecases.remove_reference import remove_reference
from backend.features.photo_generation.domain.usecases.save_reference_order import (
    InvalidReferenceOrder,
    save_reference_order,
)
from backend.features.photo_generation.domain.usecases.start_batch import (
    InvalidVariants,
    ProjectMissing,
)
from backend.tests.test_photo_usecases import FakePlanStore
from backend.tests.test_rename_under_queue import Gate


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
        self.staged = {}            # hidden name -> bytes, as an upload writes them before naming
        self.written = 0
        self._clips = clips

    def save(self, project, name, data):
        """A file put in the pool by the test itself -- from Drive, as far as the pool can tell."""
        self.pools.setdefault(project, {})[name] = data

    def stage(self, project, data):
        self.written += 1
        hidden = f".staged-{self.written}"
        self.staged[hidden] = data
        return hidden

    def place(self, project, staged, name):
        self.save(project, name, self.staged.pop(staged))

    def discard(self, project, staged):
        self.staged.pop(staged, None)

    def sweep(self, project):
        """Nothing is ever left over here: the staged files that outlive an upload are the real
        folder's (test_written_at_once)."""

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
    """An upload. The plan store is there for its gate alone (madde 523)."""
    return add_references(store, pool, orders or FakeOrderStore(), clips or FakeClips(),
                          FakePlanStore(), project, files)


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
        add_references(store, pool, FakeOrderStore(), FakeClips(), FakePlanStore(), "düğün",
                       [("kisa-2.wav", b"WAV")], row=references.PICTURE)

    assert str(exc.value) == "kisa-2.wav fotoğraf yuvasına giremez — bu dosya ses."
    assert pool.pools == {}


def test_a_file_of_its_rows_kind_goes_into_that_row():
    store, pool = FakeStore(), FakeReferenceStore()

    answer = add_references(store, pool, FakeOrderStore(), FakeClips(), FakePlanStore(), "düğün",
                            [("kedi.png", b"PNG")], row=references.PICTURE)

    assert answer == [picture()]


def test_a_reference_for_a_project_that_does_not_exist_is_refused():
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(ProjectMissing):
        added(store, pool, [("kedi.png", b"PNG")], project="yok")


def test_the_pool_lists_in_one_stable_order():
    """Kind by kind: a slot is a place inside a row, so the pool is read a row at a time
    (madde 300)."""
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


class GatedClips(FakeClips):
    """Writes down, each time a length is asked, whether the project's gate was held."""

    def __init__(self, gate):
        super().__init__()
        self.gate = gate
        self.under_gate = []

    def seconds(self, data):
        self.under_gate.append(self.gate.depth > 0)
        return super().seconds(data)


class GatedPool(FakeReferenceStore):
    """Writes down each write of an upload's bytes, and each naming, with whether the gate was held."""

    def __init__(self, gate):
        super().__init__()
        self.gate = gate
        self.writes = []

    def save(self, project, name, data):
        self.writes.append(("bytes", self.gate.depth > 0))
        super().save(project, name, data)

    def stage(self, project, data):
        self.writes.append(("bytes", self.gate.depth > 0))
        return super().stage(project, data)

    def place(self, project, staged, name):
        self.writes.append(("name", self.gate.depth > 0))
        self.pools.setdefault(project, {})[name] = self.staged.pop(staged)

    def sweep(self, project):
        self.writes.append(("sweep", self.gate.depth > 0))


def test_an_upload_reads_its_lengths_and_writes_its_bytes_before_the_gate():
    """Reviewer, madde 523: held across ffprobe and tens of megabytes to Drive, the gate kept every
    press on the project waiting, and the screen's timeout could say Zaman aşımı for a job that was
    still added. Only the names and the order are decided under it -- and what earlier uploads left
    staged is swept there."""
    gate = Gate()
    clips, pool = GatedClips(gate), GatedPool(gate)

    add_references(FakeStore(), pool, FakeOrderStore(), clips, gate, "düğün",
                   [("dans.mp4", b"MP4"), ("kedi.png", b"PNG")])

    assert clips.under_gate == [False]
    assert pool.writes == [("bytes", False), ("bytes", False), ("sweep", True), ("name", True),
                           ("name", True)]
    assert pool.pools["düğün"] == {"dans.mp4": b"MP4", "kedi.png": b"PNG"}


def gated_pool_of_clips(count):
    """A pool of `count` videos whose lengths are asked through clips that know the gate."""
    gate = Gate()
    clips = GatedClips(gate)
    pool = FakeReferenceStore(clips)
    for n in range(count):
        pool.save("düğün", f"{n}.mp4", f"MP4-{n}".encode())
    return gate, clips, pool


def test_an_upload_lists_the_pool_once_under_the_gate():
    """Madde 523's QA: the pool was listed twice under the gate -- for the names, and again for the
    answer -- so each clip already there was asked its length twice, and a press on the project
    waited 5.79 s with three videos at a second each. Once, and the answer is built from it."""
    gate, clips, pool = gated_pool_of_clips(2)

    answer = add_references(FakeStore(), pool, FakeOrderStore(), clips, gate, "düğün",
                            [("yeni.mp4", b"NEW")])

    assert clips.under_gate.count(True) == 2
    assert clips.under_gate.count(False) == 1                 # the new clip, before the gate
    assert [(row["name"], row["slot"]) for row in answer] == [
        ("0.mp4", 1), ("1.mp4", 2), ("yeni.mp4", 3)]


def test_a_drag_lists_the_pool_once_under_the_gate():
    gate, clips, pool = gated_pool_of_clips(3)

    answer = save_reference_order(FakeStore(), pool, FakeOrderStore(), gate, "düğün",
                                  {references.VIDEO: ["2.mp4", "0.mp4", "1.mp4"]})

    assert clips.under_gate == [True] * 3
    assert [(row["name"], row["slot"]) for row in answer] == [
        ("2.mp4", 1), ("0.mp4", 2), ("1.mp4", 3)]


def test_an_upload_the_pool_refuses_leaves_no_bytes_behind():
    """The bytes are written before the pool's limits can be weighed against the pool; a refusal
    under the gate takes them away again."""
    store, pool = FakeStore(), FakeReferenceStore()
    for n in range(references.LIMITS[references.PICTURE]):
        pool.save("düğün", f"{n}.png", b"PNG")

    with pytest.raises(references.PoolLimit):
        added(store, pool, [("fazla.png", b"PNG")])

    assert pool.staged == {}
    assert len(pool.pools["düğün"]) == references.LIMITS[references.PICTURE]


def test_removing_takes_the_file_off_the_disk():
    clips = FakeClips()
    store, pool = FakeStore(), FakeReferenceStore(clips)
    added(store, pool, [("kedi.png", b"PNG"), ("dans.mp4", b"MP4")], clips)

    remove_reference(store, pool, FakeOrderStore(), FakePlanStore(), "düğün", "kedi.png")

    assert pool_of(store, pool) == [clip("dans.mp4", references.VIDEO)]


def test_removing_something_that_is_not_there_is_not_an_error():
    """Deleting twice has to end where deleting once ends: another tab can get there first."""
    store, pool = FakeStore(), FakeReferenceStore()

    assert remove_reference(store, pool, FakeOrderStore(), FakePlanStore(), "düğün",
                            "kedi.png") == []


def test_the_pool_carries_the_slot_each_reference_stands_in():
    orders = FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("kedi.png", b"ONE"), ("kuş.png", b"TWO")], orders=orders)
    orders.write("düğün", {references.PICTURE: ["kuş.png", "kedi.png"]})

    assert [(row["name"], row["slot"]) for row in pool_of(store, pool, orders)] == [
        ("kuş.png", 1), ("kedi.png", 2)]


def test_removing_the_middle_one_moves_the_ones_after_it_up():
    """Madde 321: the slot numbers change, and that is what a prompt's <Picture N> points at from
    now on -- H3 packs the references tight and numbers them by order."""
    orders = FakeOrderStore({"düğün": {references.PICTURE: ["bir.png", "iki.png", "üç.png"]}})
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [(f"{name}.png", b"PNG") for name in ("bir", "iki", "üç")], orders=orders)

    left = remove_reference(store, pool, orders, FakePlanStore(), "düğün", "iki.png")

    assert [(row["name"], row["slot"]) for row in left] == [("bir.png", 1), ("üç.png", 2)]


def test_a_removed_name_uploaded_again_goes_to_the_end():
    """The deleted name keeps no place in the order: a file uploaded under it later is a new
    reference, and a new one goes in at the end of its row (madde 320)."""
    orders = FakeOrderStore({"düğün": {references.PICTURE: ["bir.png", "iki.png", "üç.png"]}})
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [(f"{name}.png", b"PNG") for name in ("bir", "iki", "üç")], orders=orders)
    remove_reference(store, pool, orders, FakePlanStore(), "düğün", "iki.png")

    again = added(store, pool, [("iki.png", b"NEW")], orders=orders)

    assert [(row["name"], row["slot"]) for row in again] == [
        ("bir.png", 1), ("üç.png", 2), ("iki.png", 3)]


def test_an_upload_joins_the_end_of_its_row():
    """Madde 414: what is in the row keeps its slot, whatever the new file is called -- the Ekle card
    stands after the row's last reference, and that is where the file was picked (madde 320)."""
    orders = FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("zeynep.png", b"ONE")], orders=orders)

    answer = add_references(store, pool, orders, FakeClips(), FakePlanStore(), "düğün",
                            [("ayse.png", b"TWO")], row=references.PICTURE)

    assert [(row["name"], row["slot"]) for row in answer] == [("zeynep.png", 1), ("ayse.png", 2)]
    assert [(row["name"], row["slot"]) for row in pool_of(store, pool, orders)] == [
        ("zeynep.png", 1), ("ayse.png", 2)]


def test_the_order_the_user_dragged_is_stored():
    orders = FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("kedi.png", b"ONE"), ("kuş.png", b"TWO")], orders=orders)

    left = save_reference_order(store, pool, orders, FakePlanStore(),
                                "düğün", {references.PICTURE: ["kuş.png", "kedi.png"]})

    assert [row["name"] for row in left] == ["kuş.png", "kedi.png"]
    assert orders.read("düğün") == {references.PICTURE: ["kuş.png", "kedi.png"]}


def test_a_sent_order_keeps_only_the_names_the_pool_holds():
    """A tab left open from before a delete sends a name whose file is gone. The server writes only
    what it can see: a dead name left in the order would pull a later file of that name back into
    the middle of its row."""
    orders = FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("bir.png", b"ONE"), ("üç.png", b"THREE")], orders=orders)

    save_reference_order(store, pool, orders, FakePlanStore(),
                         "düğün", {references.PICTURE: ["bir.png", "iki.png", "üç.png"]})

    assert orders.read("düğün") == {references.PICTURE: ["bir.png", "üç.png"]}


def test_a_dragged_row_leaves_every_other_row_as_it_was_saved():
    """Madde 427: a drag sends its own row alone, and the rows it did not touch keep the order they
    were saved in. Each row is saved against its name order, so a row that fell back to reading by
    name would show."""
    orders = FakeOrderStore({"düğün": {references.PICTURE: ["zeynep.png", "ayse.png"],
                                       references.VIDEO: ["iki.mp4", "bir.mp4"],
                                       references.AUDIO: ["rüzgar.wav", "kuş.wav"]}})
    store, pool = FakeStore(), FakeReferenceStore()
    for name in ("zeynep.png", "ayse.png", "bir.mp4", "iki.mp4", "rüzgar.wav", "kuş.wav"):
        pool.save("düğün", name, b"FILE")

    left = save_reference_order(store, pool, orders, FakePlanStore(),
                                "düğün", {references.VIDEO: ["bir.mp4", "iki.mp4"]})

    assert orders.read("düğün") == {references.PICTURE: ["zeynep.png", "ayse.png"],
                                    references.VIDEO: ["bir.mp4", "iki.mp4"],
                                    references.AUDIO: ["rüzgar.wav", "kuş.wav"]}
    assert [(row["name"], row["slot"]) for row in left] == [
        ("zeynep.png", 1), ("ayse.png", 2), ("bir.mp4", 1), ("iki.mp4", 2),
        ("rüzgar.wav", 1), ("kuş.wav", 2)]


def test_a_drag_from_a_tab_that_never_saw_an_upload_keeps_it_where_it_stood():
    """Reviewer, madde 523: the dragged row replaced the stored one whole, so a tab that had not seen
    another tab's upload dropped it from the order, and it stood wherever its name sorts. A file the
    drag does not name keeps its place, as a frame does in the gallery (madde 512)."""
    orders = FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("bir.png", b"ONE"), ("iki.png", b"TWO")], orders=orders)
    added(store, pool, [("aaa.png", b"NEW")], orders=orders)           # the other tab's upload

    left = save_reference_order(store, pool, orders, FakePlanStore(),
                                "düğün", {references.PICTURE: ["iki.png", "bir.png"]})

    assert orders.read("düğün") == {references.PICTURE: ["iki.png", "bir.png", "aaa.png"]}
    assert [row["name"] for row in left] == ["iki.png", "bir.png", "aaa.png"]


@pytest.mark.parametrize("order", ["kedi.png", {"picture": "kedi.png"}, {"picture": [7]}])
def test_an_order_that_is_not_lists_of_names_is_refused(order):
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(InvalidReferenceOrder):
        save_reference_order(store, pool, FakeOrderStore(), FakePlanStore(), "düğün", order)


def ready_pool(orders=None):
    """A pool with one picture in it -- everything a reference run needs."""
    orders = orders or FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("kedi.png", b"PNG")], orders=orders)
    return store, pool, orders


def run(store, pool, orders, prompts='["gotik kız"]', variants=1, project="düğün"):
    """A reference run, as far as its refusals.

    Everything a run would need once it is allowed to start is None here on purpose: these tests
    are about the checks that come first, and nothing past them is touched. What a run that IS
    allowed does is tested beside the queue's own fakes (test_photo_usecases). The plan store is
    there for its gate alone: the pool is looked at inside it (madde 522).

    No word about the video model: H3 is the one there is (madde 435), and it reads the pool.
    """
    return queue_references(None, store, None, FakePlanStore(), None, pool, orders, None, None,
                            None, project, prompts, variants)


def test_a_reference_run_with_an_empty_pool_is_refused():
    """Word for word the line the video panel shows above its button (madde 324): one state, one
    sentence, whichever side says it first."""
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(references.PoolLimit) as exc:
        run(store, pool, FakeOrderStore())

    assert str(exc.value) == "Havuzda referans yok — önce en az bir referans ekle."


def test_a_reference_run_reads_the_prompt_list_the_way_the_photo_panel_does():
    store, pool, orders = ready_pool()

    with pytest.raises(InvalidPrompts):
        run(store, pool, orders, prompts="gotik kız")


@pytest.mark.parametrize("variants", [0, 27])
def test_a_reference_run_counts_variants_the_way_a_batch_does(variants):
    store, pool, orders = ready_pool()

    with pytest.raises(InvalidVariants):
        run(store, pool, orders, variants=variants)
