"""Madde 512: two presses that add to one project's queue at the same moment both stay in it.

The user, 29 Ekim -- "İkisini de bu yamaya madde olarak (512 ve 513) ekleyip düzeltelim". 511's QA
saw 15 accepted presses leave 8 jobs: each press read the plan, named its jobs from what it read and
wrote the plan back whole, so two at once took the same numbers and the later write took the
earlier one's place.

Each test lets a second press in at the moment the first is about to write (Contention): before the
fix that press reads what the first has not yet written, and the two collide.
"""
import threading

from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.usecases.copy_frames import copy_frames
from backend.features.photo_generation.domain.usecases.queue_layer import queue_layer
from backend.features.photo_generation.domain.usecases.queue_references import queue_references
from backend.features.photo_generation.domain.usecases.regenerate import regenerate
from backend.features.photo_generation.domain.usecases.remove_frames import remove_frames
from backend.features.photo_generation.domain.usecases.remove_layer import remove_layer
from backend.features.photo_generation.domain.usecases.save_order import save_order
from backend.services.storage.storage import Storage
from backend.tests.test_fix_photo import Project
from backend.tests.test_photo_usecases import (
    FakeGenerator,
    FakeOrderStore,
    FakePlanStore,
    FakePool,
    FakeRecord,
    FakeReferenceOrders,
    FakeStore,
    idle_runner,
    run_batch,
    video_project,
)

# How long the first press waits for the second to finish before it writes. Long enough for a press
# over fakes or a temporary folder; a press that is made to wait for the first one does not finish
# in it, and the first goes on.
WINDOW = 0.2


class Contention:
    """Runs `press` in another thread at the first of the given writes, just before it is made.

    `writes` are (object, method name) pairs -- every write a door makes, so the second press comes
    in before the first has written anything, whichever it writes first.
    """

    def __init__(self, press, *writes):
        self.press = press
        self.thread = None
        self.answer = None
        self.failure = None
        for target, name in writes:
            self._wrap(target, name)

    def _wrap(self, target, name):
        original = getattr(target, name)

        def write(*args, **kwargs):
            if self.thread is None:
                self.thread = threading.Thread(target=self._run)
                self.thread.start()
                self.thread.join(WINDOW)
            return original(*args, **kwargs)

        setattr(target, name, write)

    def _run(self):
        try:
            self.answer = self.press()
        except BaseException as exc:            # handed to the test, which raises it
            self.failure = exc

    def done(self):
        """The second press's answer, once it has finished."""
        self.thread.join()
        if self.failure is not None:
            raise self.failure
        return self.answer


def every_write(record, plan_store, order_store=None):
    writes = [(plan_store, "append"), (record, "append"), (record, "mark")]
    return writes + ([(order_store, "write")] if order_store is not None else [])


def planned(plan_store):
    return [job["id"] for batch in plan_store.appended for job in batch]


# --- the plan file itself ------------------------------------------------------------------------

def frames(*prompts):
    return [{"id": f"P{n}_0", "type": "photo", "number": n, "variant": 0, "prompt": prompt,
             "negative": "", "seed": 1, "model": "", "lora": ""}
            for n, prompt in enumerate(prompts)]


def drive_plan(path, *projects):
    for project in projects:
        (path / project).mkdir()
    storage = Storage(str(path))
    return storage, DrivePlanStore(storage)


def test_an_append_never_takes_the_place_of_one_made_at_the_same_moment(tmp_path):
    """The plan is written whole: an append that read it before another one landed would write it
    back without that one."""
    storage, plan = drive_plan(tmp_path, "düğün")
    other = Contention(lambda: plan.append("düğün", frames("iki")), (storage, "write_text"))

    plan.append("düğün", frames("bir"))
    other.done()

    assert sorted(job["prompt"] for job in plan.read("düğün")["frames"]) == ["bir", "iki"]


def test_eight_appends_at_once_all_land(tmp_path):
    """QA's double press, many times over: no write lost, and no two of them moving their temporary
    file over the plan at once (on Windows that was "Access is denied")."""
    _storage, plan = drive_plan(tmp_path, "düğün")
    start, failures = threading.Barrier(8), []

    def press(n):
        start.wait()
        try:
            plan.append("düğün", frames(f"iş {n}"))
        except OSError as exc:
            failures.append(exc)

    threads = [threading.Thread(target=press, args=(n,)) for n in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert failures == []
    assert len(plan.read("düğün")["frames"]) == 8


def test_holding_one_project_s_plan_does_not_hold_another_s(tmp_path):
    _storage, plan = drive_plan(tmp_path, "düğün", "nişan")
    elsewhere = threading.Thread(target=lambda: plan.append("nişan", frames("başka")))

    with plan.held("düğün"):
        elsewhere.start()
        elsewhere.join(WINDOW)
        landed = not elsewhere.is_alive()
    elsewhere.join()

    assert landed
    assert [job["prompt"] for job in plan.read("nişan")["frames"]] == ["başka"]


# --- every door that names new jobs ---------------------------------------------------------------

def test_two_batches_at_once_both_stay_in_the_queue_under_their_own_numbers():
    store, record, plan_store, runner = FakeStore(), FakeRecord(), FakePlanStore(), idle_runner()

    def press(prompt):
        return run_batch(runner, store, FakeGenerator(), text=f'["{prompt}"]', variants=1,
                         record=record, plan_store=plan_store)

    other = Contention(lambda: press("iki"), *every_write(record, plan_store))
    assert press("bir") == 1
    assert other.done() == 1

    assert sorted(planned(plan_store)) == ["P0_0", "P1_0"]
    assert sorted(job["prompt"] for job in plan_store.frames) == ["bir", "iki"]


def test_two_reference_runs_at_once_take_their_own_numbers():
    store, record, plan_store, runner = FakeStore(), FakeRecord(), FakePlanStore(), idle_runner()

    def press():
        return queue_references(runner, store, record, plan_store, FakeOrderStore(), FakePool(),
                                FakeReferenceOrders(), {}, lambda: 7, lambda: "t", "düğün",
                                '["gotik kız"]', 1)

    other = Contention(press, *every_write(record, plan_store))
    press()
    other.done()

    assert sorted(planned(plan_store)) == ["P0_0", "P1_0"]


def test_two_video_presses_at_once_give_their_variants_their_own_frames():
    store, record, plan_store = video_project((0, "a"))
    order, runner = FakeOrderStore(), idle_runner()

    def press():
        return queue_layer(runner, store, record, plan_store, order, {}, lambda: "t", "düğün",
                           layers.VIDEO, variants=2)

    other = Contention(press, *every_write(record, plan_store, order))
    assert press() == 2
    assert other.done() == 2

    # Each press puts the frame's own video in line and a copy frame for its second variant.
    copies = [fid for fid in planned(plan_store) if fid != "0_a"]
    assert sorted(copies) == ["P0_1", "P0_2"]


def test_two_new_frames_of_one_family_at_once_take_their_own_names():
    store, record, plan_store = video_project((0, "a"))
    order, runner = FakeOrderStore(), idle_runner()

    def press():
        return regenerate(runner, store, record, plan_store, order, {}, lambda: 7, lambda: "t",
                          "düğün", "0_a", layers.PHOTO, "p")

    other = Contention(press, *every_write(record, plan_store, order))
    first = press()

    assert sorted([first, other.done()]) == ["P0_1", "P0_2"]


def test_two_fixes_of_one_photo_at_once_make_it_once():
    """The second fix finds the frame it was told about changed, and writes nothing."""
    project = Project()
    seen = project.card("P1_0")

    other = Contention(lambda: project.fix(seen, runner=idle_runner()),
                       *every_write(project.record, project.plan_store, project.order_store))
    first = project.fix(seen, runner=idle_runner())

    assert sorted([first, other.done()]) == ["changed", "fixed"]
    assert planned(project.plan_store) == ["P3_0"]


def test_two_copies_of_one_frame_at_once_are_two_twins():
    store, record, plan_store = video_project((0, "a"))
    order = FakeOrderStore(["0_a"])

    def press():
        return copy_frames(record, store, plan_store, order, lambda: "t", "düğün", ["0_a"])

    other = Contention(press, *every_write(record, plan_store, order))
    first = press()["copies"]

    assert sorted(first + other.done()["copies"]) == ["C1_0_a", "C2_0_a"]
    assert sorted(order.order) == ["0_a", "C1_0_a", "C2_0_a"]


# --- the doors that close frames, against the doors that name them -----------------------------

def test_a_deletion_never_takes_the_picture_a_copy_made_at_the_same_moment_stands_on():
    """remove_frames decides which files no other frame holds before it unlinks them: a twin born
    in between would be left holding a deleted picture."""
    store, record, plan_store = video_project((0, "a"))
    order = FakeOrderStore(["0_a"])

    other = Contention(
        lambda: copy_frames(record, store, plan_store, order, lambda: "t", "düğün", ["0_a"]),
        (store, "delete"), *every_write(record, plan_store, order))
    said = remove_frames(record, store, plan_store, order, lambda: "t", "düğün", ["0_a"])

    # The frame went first and whole, so there was nothing left to twin.
    assert said["deleted"] == ["0_a"]
    assert other.done()["copies"] == []
    assert store.deleted == ["0_a.png"]


def test_a_layer_taken_off_never_takes_the_photo_a_video_queued_at_the_same_moment_stands_on():
    """The user's words for the item: "Eklendi denen hiçbir iş kaybolmuyor". A copy frame's video
    queued while the photo under it was being deleted would fail on a picture that is gone."""
    store, record, plan_store = video_project((0, "a"))
    order, runner = FakeOrderStore(["0_a"]), idle_runner()

    other = Contention(
        lambda: queue_layer(runner, store, record, plan_store, order, {}, lambda: "t", "düğün",
                            layers.VIDEO, variants=2),
        (store, "delete"), *every_write(record, plan_store, order))
    remove_layer(record, store, plan_store, order, lambda: "t", "düğün", ["0_a"], layers.PHOTO)

    # The photo went first, so the frame had nothing a video could hang on.
    assert other.done() == 0
    assert planned(plan_store) == []


def test_a_drag_never_drops_the_place_of_a_copy_made_at_the_same_moment():
    store, record, plan_store = video_project((0, "a"))
    order = FakeOrderStore(["0_a"])

    other = Contention(
        lambda: copy_frames(record, store, plan_store, order, lambda: "t", "düğün", ["0_a"]),
        *every_write(record, plan_store, order))
    save_order(record, store, plan_store, order, "düğün", ["0_a"])

    assert other.done()["copies"] == ["C1_0_a"]
    assert sorted(order.order) == ["0_a", "C1_0_a"]


def test_a_drag_sent_before_a_copy_arrived_keeps_the_copy_above_its_source():
    """The other way round from the test above: the copy lands first, and the drag's list was made
    on a screen that had not seen it yet. A frame the list does not name keeps its place against the
    gallery as it stands -- directly above the frame that was under it -- rather than jumping to the
    top."""
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    order = FakeOrderStore(["1_a", "0_a"])
    copy_frames(record, store, plan_store, order, lambda: "t", "düğün", ["0_a"])

    stored = save_order(record, store, plan_store, order, "düğün", ["0_a", "1_a"])

    assert stored == order.order == ["C1_0_a", "0_a", "1_a"]


def test_frames_a_drag_does_not_name_keep_their_own_sequence():
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    order = FakeOrderStore(["1_a", "0_a"])
    copy_frames(record, store, plan_store, order, lambda: "t", "düğün", ["0_a", "1_a"])
    copy_frames(record, store, plan_store, order, lambda: "t", "düğün", ["0_a"])

    assert order.order == ["C1_1_a", "1_a", "C1_0_a", "C2_0_a", "0_a"]

    save_order(record, store, plan_store, order, "düğün", ["0_a", "1_a"])

    assert order.order == ["C1_0_a", "C2_0_a", "0_a", "C1_1_a", "1_a"]
