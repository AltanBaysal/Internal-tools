"""Madde 513: a finished layer is never made again, and its file is never written over.

The user, 29 Ekim -- "İkisini de bu yamaya madde olarak (512 ve 513) ekleyip düzeltelim". Two QA runs
saw a finished layer made a second time over its own file: 511's when a rename moved the folder
between two of the loop's reads, 512's when a second video press read the gallery before the loop's
line landed and the record after it. Each test lets the other party in at exactly that moment.
"""
import threading

import pytest

from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.domain import layers, production_mode, queue
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.running_name import RunningName
from backend.features.photo_generation.domain.usecases.cancel_generation import cancel_generation
from backend.features.photo_generation.domain.usecases.follow_rename import follow_rename
from backend.features.photo_generation.domain.usecases.queue_layer import queue_layer
from backend.features.photo_generation.domain.usecases.remove_frames import remove_frames
from backend.features.photo_generation.domain.usecases.retry_failed import retry_failed
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.features.photo_generation.runner import PhotoRunner
from backend.services.storage.storage import Storage
from backend.tests.test_photo_usecases import (
    FakeGenerator,
    FakeOrderStore,
    FakePlanStore,
    FakeRecord,
    FakeStore,
    frame,
    idle_runner,
    sync_runner,
)

# How long one party waits for the other to get in. Long enough for a step over fakes or a temporary
# folder; a party made to wait for a lock does not finish in it, and the first goes on.
WINDOW = 0.2


def now():
    return "t"


# --- the record's fold ---------------------------------------------------------------------------

def drive_record(tmp_path):
    (tmp_path / "düğün").mkdir()
    return DrivePhotoRecord(Storage(str(tmp_path)))


def landed(record, layer="video", file="0_a_V1_0.mp4"):
    record.append("düğün", {"file": file, "frame": "0_a", "layer": layer, "status": queue.DONE,
                            "prompt": "yürüyor"})


def status_of(record, layer="video"):
    return record.slots("düğün")["0_a"][layer]["status"]


def test_a_decision_over_a_status_the_slot_has_left_is_passed_over(tmp_path):
    """Press B read the slot removed and decided to put it back; the video landed first."""
    record = drive_record(tmp_path)
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.REMOVED, "t0", seen=None)
    landed(record)
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.QUEUED, "t1",
                seen=queue.REMOVED)

    assert status_of(record) == queue.DONE


def test_a_decision_over_the_status_the_slot_still_has_applies(tmp_path):
    record = drive_record(tmp_path)
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.REMOVED, "t0", seen=None)
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.QUEUED, "t1",
                seen=queue.REMOVED)

    assert status_of(record) == queue.QUEUED


def test_a_line_written_before_madde_513_applies_as_it_always_did(tmp_path):
    """Lines already on Drive carry no `from`: nothing is migrated, and they fold as before."""
    record = drive_record(tmp_path)
    landed(record)
    # The shape mark wrote before madde 513: no `from`.
    record.append("düğün", {"frame": "0_a", "layer": "video", "file": "0_a_V1_0.mp4",
                            "status": queue.QUEUED, "at": "t1"})

    assert status_of(record) == queue.QUEUED


def test_a_layer_that_lands_always_counts(tmp_path):
    """A done names no `from`: its file is on disk, and a free slot over it would be built on."""
    record = drive_record(tmp_path)
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.REMOVED, "t0", seen=None)
    landed(record)

    assert status_of(record) == queue.DONE


def test_a_failure_landing_after_the_job_was_pulled_out_leaves_it_pulled_out(tmp_path):
    record = drive_record(tmp_path)
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.REMOVED, "t0", seen=None)
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.FAILED, "t1", error="node 41",
                seen=None)

    assert status_of(record) == queue.REMOVED


def test_the_photos_and_the_written_prompts_read_the_same_lines_the_slots_do(tmp_path):
    """One rule for every fold of what became of a slot: a passed-over line pops no photo and ends
    no written prompt."""
    record = drive_record(tmp_path)
    landed(record, layer="photo", file="0_a.png")
    record.prompt_written("düğün", "0_a", "video", "0_a_V1_0.mp4", "yazılan", "t0")
    record.mark("düğün", "0_a", "photo", "0_a.png", queue.QUEUED, "t1", seen=queue.FAILED)
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.REMOVED, "t1",
                seen=queue.QUEUED)

    assert [row["frame"] for row in record.list("düğün")] == ["0_a"]
    assert record.written_prompts("düğün") == {"0_a": {"video": "yazılan"}}
    assert status_of(record, "photo") == queue.DONE


# --- a rename under the loop ---------------------------------------------------------------------

def test_a_rename_between_the_loops_reads_never_makes_a_finished_frame_again(tmp_path):
    """511's QA: the loop read the plan under the old name, the folder moved, the record read under
    the old name came back empty, and the finished P0_0 was made again over its own file."""
    (tmp_path / "düğün").mkdir()
    storage = Storage(str(tmp_path))
    store, record, plan = DrivePhotoStore(storage, storage), DrivePhotoRecord(storage), \
        DrivePlanStore(storage)
    plan.append("düğün", [
        {"id": f"P{n}_0", "type": "photo", "number": n, "variant": 0, "prompt": prompt,
         "negative": "", "seed": 1, "model": "", "lora": ""}
        for n, prompt in enumerate(["ilk", "ikinci"])])
    store.save("düğün", "P0_0.png", b"BITMIS")
    record.append("düğün", {"file": "P0_0.png", "frame": "P0_0", "layer": "photo",
                            "status": "done", "prompt": "ilk"})
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("düğün", lambda: None)             # the holder now names the folder
    generator = FakeGenerator()
    rename = threading.Thread(target=lambda: follow_rename(
        runner, "düğün", "nişan", lambda: storage.rename_dir("düğün", "nişan")))
    read = plan.read

    def read_then_rename(project):
        answer = read(project)
        if rename.ident is None:
            rename.start()
            rename.join(WINDOW)
        return answer

    plan.read = read_then_rename

    make_job(runner, store, record, plan, {layers.PHOTO: generator}, now)()
    rename.join()

    assert [prompt for prompt, *_rest in generator.calls] == ["ikinci"]
    assert (tmp_path / "nişan" / "P0_0.png").read_bytes() == b"BITMIS"
    assert (tmp_path / "nişan" / "P1_0.png").exists()
    assert not (tmp_path / "düğün").exists()


# --- a press as the loop lands -------------------------------------------------------------------

class LandsAfterFirstLook(FakeRecord):
    """Lets the loop's line land right after the press thread's first look at the record."""

    def __init__(self):
        super().__init__()
        self.presser = None
        self.looked = threading.Event()
        self.landed = threading.Event()

    def slots(self, project):
        answer = super().slots(project)
        if threading.current_thread() is self.presser and not self.looked.is_set():
            self.looked.set()
            self.landed.wait(WINDOW)
        return answer

    def append(self, project, entry):
        super().append(project, entry)
        if entry.get("status") == queue.DONE and entry.get("layer") == layers.VIDEO:
            self.landed.set()


class WaitsForTheLook(FakeGenerator):
    """A render that finishes only once the press has looked: the loop lands right after it."""

    def __init__(self, looked):
        super().__init__()
        self.looked = looked

    def generate(self, *args, **kwargs):
        self.looked.wait(5)
        return super().generate(*args, **kwargs)


def made_videos(record, fid):
    """How many times the frame's own video landed: each is a save over 0_a_V1_0.mp4."""
    return sum(1 for row in record.rows if row.get("frame") == fid
               and row.get("layer") == layers.VIDEO and row.get("status") == queue.DONE)


def video_press(runner, store, record, plan_store, order):
    return queue_layer(runner, store, record, plan_store, order, {}, now, "düğün", layers.VIDEO,
                       files=["0_a.png"])


def test_a_second_video_press_as_the_first_video_lands_never_makes_it_again():
    """512's QA: press B read the gallery before the loop's line and the record after it, took the
    done video for a free slot, wrote queued over it, and the video was made again over
    0_a_V1_0.mp4. Whatever B finds, the video is made once."""
    store, record, order = FakeStore(), LandsAfterFirstLook(), FakeOrderStore()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    runner = idle_runner()
    assert video_press(runner, store, record, plan_store, order) == 1      # press A
    video = WaitsForTheLook(record.looked)
    loop = threading.Thread(target=make_job(runner, store, record, plan_store,
                                            {layers.VIDEO: video}, now,
                                            named=RunningName("düğün"), order_store=order))
    loop.start()

    record.presser = threading.current_thread()
    video_press(runner, store, record, plan_store, order)                  # press B
    loop.join(5)

    # B read the record after the landing, so it asked for a new variant -- a frame of its own --
    # and 0_a's own video stays the one made.
    assert made_videos(record, "0_a") == 1
    assert record.slots("düğün")["0_a"]["video"]["status"] == queue.DONE
    assert "0_a" not in [job["id"] for job in queue.open_jobs(
        plan_store.read("düğün")["frames"], record.slots("düğün"))]


def test_a_press_on_a_video_already_back_in_line_never_makes_it_again_as_it_lands():
    """The same moment with the slot reopened: the video was pulled out of the queue, press A put it
    back with a queued line, and B -- reading it still owed -- must not write that line again over
    the video the loop has just landed."""
    store, record, order = FakeStore(), LandsAfterFirstLook(), FakeOrderStore()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store.append("düğün", [{"id": "0_a", "type": "video", "number": 0, "variant": 0,
                                 "prompt": "", "negative": "", "seed": None, "model": ""}])
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.REMOVED, "t0", seen=None)
    runner = idle_runner()
    assert video_press(runner, store, record, plan_store, order) == 1      # press A reopens it
    video = WaitsForTheLook(record.looked)
    loop = threading.Thread(target=make_job(runner, store, record, plan_store,
                                            {layers.VIDEO: video}, now,
                                            named=RunningName("düğün"), order_store=order))
    loop.start()

    record.presser = threading.current_thread()
    video_press(runner, store, record, plan_store, order)                  # press B
    loop.join(5)

    assert made_videos(record, "0_a") == 1
    assert record.slots("düğün")["0_a"]["video"]["status"] == queue.DONE


def test_a_video_press_on_a_frame_whose_video_is_in_line_adds_nothing():
    """The user, 29 Ekim -- "galeri sırada / kayıt bitti demesi lazım değil mi": a job the record
    says is in line is not added again."""
    store, record, order = FakeStore(), FakeRecord(), FakeOrderStore()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store.append("düğün", [{"id": "0_a", "type": "video", "number": 0, "variant": 0,
                                 "prompt": "", "negative": "", "seed": None, "model": ""}])
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.REMOVED, "t0", seen=None)
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", queue.QUEUED, "t1",
                seen=queue.REMOVED)
    runner = idle_runner()

    assert video_press(runner, store, record, plan_store, order) == 0
    assert len(plan_store.appended) == 1                    # only the line set up above
    assert len(record.rows) == 3                            # nothing written by the press
    assert runner.status()["status"] == "idle"


def test_a_second_video_press_before_the_first_is_made_does_not_add_the_frames_own_job_again():
    """The usual double press: the first press's job is planned and has no line in the record yet.
    The frame's own video is in line -- the user's "sırada … yeniden eklenmez" -- so the second
    press adds only its copies, says so, and the first press's mode stands on the frame's job."""
    store, record, order = FakeStore(), FakeRecord(), FakeOrderStore()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    runner = idle_runner()

    def press(mode):
        return queue_layer(runner, store, record, plan_store, order, {}, now, "düğün",
                           layers.VIDEO, files=["0_a.png"], variants=2, mode=mode)

    assert press(production_mode.LOOP) == 2
    assert press(production_mode.STANDARD) == 1

    own = [job for job in plan_store.read("düğün")["frames"]
           if job["id"] == "0_a" and job.get("type") == layers.VIDEO]
    assert [job["mode"] for job in own] == [production_mode.LOOP]
    copies = [job["id"] for job in plan_store.read("düğün")["frames"]
              if job.get("type") == layers.VIDEO and job["id"] != "0_a"]
    assert len(copies) == 2 and len(set(copies)) == 2


def sound_copy_holding_the_video():
    """P1_0 with its photo and video, a sound copy C1_P1_0 holding both files, and P1_0's video
    deleted -- P1_0_V1_0.mp4 stays on disk, because the copy still holds it (madde 101)."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[{"id": "P1_0", "number": 1, "variant": 0, "prompt": "p",
                                        "seed": 1}])
    for fid in ("P1_0", "C1_P1_0"):
        record.append("düğün", {"file": "P1_0.png", "frame": fid, "layer": "photo",
                                "status": queue.DONE})
        record.append("düğün", {"file": "P1_0_V1_0.mp4", "frame": fid, "layer": "video",
                                "status": queue.DONE})
    record.mark("düğün", "P1_0", "video", "P1_0_V1_0.mp4", queue.DELETED, "t1", seen=queue.DONE)
    return store, record, plan_store


@pytest.mark.parametrize("files", [None, ["P1_0.png"]])
def test_a_video_press_never_saves_over_the_video_a_copy_still_holds(files):
    """The deleted slot's own name is P1_0_V1_0.mp4, which the copy still stands on: reopening it
    would save the new video over the copy's. The slot counts as taken -- chosen by hand it gets a
    new variant under a name of its own, and "frames without a video" passes it by."""
    store, record, plan_store = sound_copy_holding_the_video()
    video = FakeGenerator()

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(), {layers.VIDEO: video},
                now, "düğün", layers.VIDEO, files=files)

    saved = [name for name, _data in store.saved]
    assert "P1_0_V1_0.mp4" not in saved
    assert record.slots("düğün")["P1_0"]["video"]["status"] == queue.DELETED
    if files:
        assert saved and all(name.endswith(".mp4") for name in saved)  # new variants, own names


# --- a removal as the loop lands -----------------------------------------------------------------

class LandsAtFirstLook(FakeRecord):
    """The loop's line for `row` lands right after the first look at the record."""

    def __init__(self, row):
        super().__init__()
        self.row = row

    def slots(self, project):
        answer = super().slots(project)
        if self.row is not None:
            row, self.row = self.row, None
            self.append(project, row)
        return answer


PHOTO_LANDS = {"file": "P0_0.png", "frame": "P0_0", "layer": "photo", "status": queue.DONE}


def test_clearing_the_queue_as_its_job_lands_keeps_the_photo():
    """Its line would leave P0_0.png on disk under a free slot, for the next press to make again."""
    store, record = FakeStore(), LandsAtFirstLook(PHOTO_LANDS)
    plan_store = FakePlanStore(frames=[{"id": "P0_0", "number": 0, "variant": 0, "prompt": "p",
                                        "seed": 1}])

    cancel_generation(idle_runner(), store, record, plan_store, now, "düğün")

    assert record.slots("düğün")["P0_0"]["photo"]["status"] == queue.DONE


def test_taking_out_a_pending_frame_whose_photo_lands_meanwhile_keeps_the_photo():
    """The gallery said pending, the record a moment later said done: the render wins, as
    remove_frames has always said, and no removed line is left over the file."""
    store, record = FakeStore(), LandsAtFirstLook(PHOTO_LANDS)
    plan_store = FakePlanStore(frames=[{"id": "P0_0", "number": 0, "variant": 0, "prompt": "p",
                                        "seed": 1}])

    remove_frames(record, store, plan_store, FakeOrderStore(), now, "düğün", ["P0_0"])

    assert record.slots("düğün")["P0_0"]["photo"]["status"] == queue.DONE
    assert store.deleted == []


# --- Tekrar dene ---------------------------------------------------------------------------------

def test_tekrar_dene_on_a_frame_whose_photo_is_finished_makes_nothing_again():
    """A screen a moment behind still shows the red tile; the photo has landed since. The press finds
    nothing red, and a finished photo is not what "a photo it no longer has" means."""
    store, record, generator = FakeStore(), FakeRecord(), FakeGenerator()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})

    retry_frame(sync_runner(), store, record, plan_store, {layers.PHOTO: generator}, now,
                "düğün", "0_a")

    assert generator.calls == []
    assert record.slots("düğün")["0_a"]["photo"]["status"] == queue.DONE


def test_tekrar_dene_never_makes_a_photo_over_the_picture_a_copy_still_holds():
    """P1_0's photo was deleted while its copy kept P1_0.png on disk. A screen a moment behind still
    offers Tekrar dene on P1_0's red video, which another press has already put back: nothing is red,
    and asking for P1_0's photo again would save P1_0.png over the copy's picture."""
    store, record, generator = FakeStore(), FakeRecord(), FakeGenerator()
    plan_store = FakePlanStore(frames=[{"id": "P1_0", "number": 1, "variant": 0, "prompt": "p",
                                        "seed": 1}])
    for fid in ("P1_0", "C1_P1_0"):
        record.append("düğün", {"file": "P1_0.png", "frame": fid, "layer": "photo",
                                "status": queue.DONE})
    record.mark("düğün", "P1_0", "photo", "P1_0.png", queue.DELETED, "t1", seen=queue.DONE)

    retry_frame(sync_runner(), store, record, plan_store, {layers.PHOTO: generator}, now,
                "düğün", "P1_0")

    assert generator.calls == []
    assert store.saved == []
    assert record.slots("düğün")["P1_0"]["photo"]["status"] == queue.DELETED


class PausesAfterItsLook(FakeRecord):
    """Holds one thread right after its look at the record, until the photo lands or the window
    closes."""

    def __init__(self):
        super().__init__()
        self.paused = None
        self.looked = threading.Event()
        self.landed = threading.Event()

    def slots(self, project):
        answer = super().slots(project)
        if threading.current_thread() is self.paused and not self.looked.is_set():
            self.looked.set()
            self.landed.wait(WINDOW)
        return answer

    def append(self, project, entry):
        super().append(project, entry)
        if entry.get("status") == queue.DONE:
            self.landed.set()


def _two_retries_at_once(press):
    """Press B looks at the red photo and is held; press A puts it back and the loop makes it; then
    B goes on. Returns the generator, once both presses and every run they started are over."""
    store, record, generator = FakeStore(), PausesAfterItsLook(), FakeGenerator()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.mark("düğün", "0_a", "photo", "0_a.png", queue.FAILED, "t0", seen=None,
                error="node 41")
    # One worker for both, run inline by whichever press claims it: the other joins its run.
    runner = sync_runner()

    def retry():
        press(runner, store, record, plan_store, {layers.PHOTO: generator})

    second = threading.Thread(target=retry)
    record.paused = second
    second.start()
    record.looked.wait(5)
    retry()
    second.join(5)
    return generator, record


def test_two_tekrar_dene_on_one_red_frame_at_once_make_it_once():
    generator, record = _two_retries_at_once(
        lambda runner, store, record, plan, producers: retry_frame(
            runner, store, record, plan, producers, now, "düğün", "0_a"))

    assert len(generator.calls) == 1
    assert record.slots("düğün")["0_a"]["photo"]["status"] == queue.DONE


def test_two_presses_of_tekrar_dene_for_all_at_once_make_each_once():
    generator, record = _two_retries_at_once(
        lambda runner, store, record, plan, producers: retry_failed(
            runner, store, record, plan, producers, now, "düğün"))

    assert len(generator.calls) == 1
    assert record.slots("düğün")["0_a"]["photo"]["status"] == queue.DONE
