import pytest

from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.photo_name import (
    frame_id,
    frame_id_of,
    legacy_frame_id,
    number_of,
    photo_file,
)
from backend.features.photo_generation.domain.prompt_list import InvalidPrompts
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.usecases.remove_frames import (
    InvalidFiles,
    remove_frames,
)
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.list_models import list_models
from backend.features.photo_generation.domain.usecases.retry_failed import retry_failed
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.features.photo_generation.domain.usecases.run_queue import Busy
from backend.features.photo_generation.domain.usecases.start_batch import (
    InvalidVariants,
    ProjectMissing,
    next_number,
    plan_frames,
    start_batch,
)
from backend.features.photo_generation.domain.usecases.cancel_generation import cancel_generation
from backend.features.photo_generation.domain.usecases.export_project import export_project
from backend.features.photo_generation.domain.usecases.resume_batch import (
    NothingToResume,
    resume_batch,
)
from backend.features.photo_generation.domain.usecases.save_order import InvalidOrder, save_order
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
from backend.features.photo_generation.runner import PhotoRunner


class FakeStore:
    def __init__(self, projects=("düğün",), next_no=0):
        self.projects = list(projects)
        self.next_no = next_no
        self.saved = []
        self.deleted = []

    def project_exists(self, project):
        return project in self.projects

    def next_number(self, project):
        return self.next_no

    def save(self, project, filename, data):
        self.saved.append((filename, data))
        return filename

    def delete(self, project, filename):
        self.deleted.append(filename)

    def photo_dir(self, project):
        return f"/fake/{project}"


class FrameFault(RuntimeError):
    """The shape ComfyUI raises when it ran the graph and the graph itself failed.

    The renderer answered, so only this frame is in trouble. Anything without the flag -- a refused
    connection, an HTTP error, a timeout -- means no answer came at all, and that is the run's
    problem rather than the frame's.
    """

    frame_level = True


class FakeGenerator:
    """Records what each frame asked for; `fail_on` names the prompts whose render fails."""

    def __init__(self, fail_on=(), installed=("nova.safetensors",)):
        self.calls = []
        self.models_called = 0
        self.fail_on = list(fail_on)
        self.installed = list(installed)

    def models(self):
        self.models_called += 1
        return list(self.installed)

    def generate(self, prompt, negative, seed, model=""):
        self.calls.append((prompt, negative, seed, model))
        if prompt in self.fail_on:
            raise FrameFault(f"node 41: {prompt}")
        return b"PNG"


class FakePlanStore:
    def __init__(self, reserved=None, frames=None, negative=""):
        self.reserved = reserved          # highest number an earlier plan reserved, or None
        self.appended = []                # each append call's frames, in order
        self.frames = list(frames or [])
        self.negative = negative          # the pre-per-frame field older plans still carry

    def append(self, project, frames):
        self.appended.append(frames)
        self.frames = self.frames + list(frames)

    def read(self, project):
        # Mirrors DrivePlanStore: a frame without its own negative falls back to the old field, one
        # planned before models could be chosen carries none at all, and one planned before
        # identities were written down keeps the one it was born with.
        return {"negative": self.negative,
                "frames": [{**f,
                            "id": f.get("id") or legacy_frame_id(f["number"],
                                                                 f.get("letter", "a")),
                            "negative": f.get("negative", self.negative),
                            "model": f.get("model", "")}
                           for f in self.frames]}

    def max_number(self, project):
        if self.reserved is not None:
            return self.reserved
        return max((f["number"] for f in self.frames), default=None)


class FakeRecord:
    """Folds the log the way DrivePhotoRecord does: the latest line per (frame, layer) wins."""

    def __init__(self):
        self.rows = []

    def append(self, project, entry):
        self.rows.append(entry)

    def mark(self, project, frame, layer, file, status, at, error=None):
        entry = {"frame": frame, "layer": layer, "file": file, "status": status, "at": at}
        if error is not None:
            entry["error"] = error
        self.rows.append(entry)

    def _frame_of(self, row):
        return row.get("frame") or frame_id_of(row["file"])

    def _layer_of(self, row):
        return row.get("layer", "photo")

    def slots(self, project):
        folded = {}
        for row in self.rows:
            folded.setdefault(self._frame_of(row), {})[self._layer_of(row)] = {
                "status": row.get("status", "done"), "file": row["file"]}
        return folded

    def statuses(self, project):
        return {frame: cells["photo"]["status"]
                for frame, cells in self.slots(project).items() if "photo" in cells}

    def list(self, project):
        live = {}
        for row in self.rows:
            if self._layer_of(row) != "photo":
                continue
            frame = self._frame_of(row)
            if row.get("status", "done") == "done":
                live[frame] = {**row, "frame": frame}
            else:
                live.pop(frame, None)
        return list(reversed(list(live.values())))

    def max_number(self, project):
        numbers = [number_of(row["file"]) for row in self.rows]
        numbers = [n for n in numbers if n is not None]
        return max(numbers) if numbers else None


class FakeOrderStore:
    """Mirrors DriveOrderStore: whatever is stored reads back as frame identities."""

    def __init__(self, order=()):
        self.order = list(order)

    def read(self, project):
        return [frame_id_of(name) for name in self.order]

    def write(self, project, order):
        self.order = list(order)


def sync_runner():
    return PhotoRunner(spawn=lambda fn: fn())


def photo_statuses(record, project="düğün"):
    """{frame: photo slot status} -- the one slot most of these tests are about."""
    return {frame: cells["photo"]["status"]
            for frame, cells in record.slots(project).items() if "photo" in cells}


def run_batch(runner, store, generator, project="düğün", text='["a", "b"]', negative="neg",
              variants=2, seed=42, record=None, plan_store=None, model="", log=None):
    return start_batch(runner, store, record or FakeRecord(), plan_store or FakePlanStore(),
                       {layers.PHOTO: generator}, lambda: seed,
                       lambda: "2026-08-03T14:32:11+00:00",
                       project, text, negative, variants, model, log)


def test_plan_frames_is_prompt_major():
    seeds = iter([11, 22, 33, 44])
    assert plan_frames(3, ["ilk", "ikinci"], "neg", 2, lambda: next(seeds), "nova.safetensors") == [
        {"id": "P3_0", "type": "photo", "number": 3, "variant": 0, "prompt": "ilk",
         "negative": "neg", "seed": 11, "model": "nova.safetensors"},
        {"id": "P3_1", "type": "photo", "number": 3, "variant": 1, "prompt": "ilk",
         "negative": "neg", "seed": 22, "model": "nova.safetensors"},
        {"id": "P4_0", "type": "photo", "number": 4, "variant": 0, "prompt": "ikinci",
         "negative": "neg", "seed": 33, "model": "nova.safetensors"},
        {"id": "P4_1", "type": "photo", "number": 4, "variant": 1, "prompt": "ikinci",
         "negative": "neg", "seed": 44, "model": "nova.safetensors"},
    ]


def test_numbering_continues_from_the_store():
    store, generator, runner = FakeStore(next_no=7), FakeGenerator(), sync_runner()
    run_batch(runner, store, generator, text='["a"]', variants=3)
    assert [name for name, _d in store.saved] == ["P7_0.png", "P7_1.png", "P7_2.png"]


def test_every_frame_gets_prompt_negative_and_a_fresh_seed():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    seeds = iter([11, 22, 33, 44])
    start_batch(runner, store, FakeRecord(), FakePlanStore(), {layers.PHOTO: generator},
                lambda: next(seeds),
                lambda: "2026-08-03T14:32:11+00:00", "düğün", '["a", "b"]', "neg", 2)
    assert generator.calls == [("a", "neg", 11, ""), ("a", "neg", 22, ""),
                               ("b", "neg", 33, ""), ("b", "neg", 44, "")]


def test_finished_batch_reports_its_counts():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    run_batch(runner, store, generator)
    assert runner.status() == {"status": "done", "project": "düğün",
                               "done": 4, "failed": 0, "total": 4, "failures": []}


def test_progress_is_reported_before_each_frame():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    seen = []
    original = generator.generate

    def spy(prompt, negative, seed, model=""):
        seen.append(runner.status())
        return original(prompt, negative, seed, model)

    generator.generate = spy
    run_batch(runner, store, generator, text='["a"]', variants=2)
    assert seen[0]["current"] == {"id": "P0_0", "type": "photo", "number": 0, "variant": 0,
                                  "prompt": "a", "negative": "neg", "seed": 42, "model": ""}
    assert (seen[0]["done"], seen[0]["total"]) == (0, 2)
    assert (seen[1]["done"], seen[1]["total"]) == (1, 2)


def test_a_failed_frame_is_skipped_and_the_batch_continues():
    class FailsFirstFrame:
        """Drops the first variant every time it is offered -- three attempts, then red."""

        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed, model=""):
            self.calls += 1
            if self.calls <= 3:
                raise FrameFault("node 41: OOM")
            return b"PNG"

    store, runner = FakeStore(), sync_runner()
    run_batch(runner, store, FailsFirstFrame(), text='["a"]', variants=2)
    state = runner.status()
    assert (state["status"], state["done"], state["failed"]) == ("done", 1, 1)
    assert [name for name, _d in store.saved] == ["P0_1.png"]


def test_a_job_the_producer_drops_is_tried_three_times_before_it_turns_red():
    class DropsTheFirstJob:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed, model=""):
            self.calls += 1
            if prompt == "patlak":
                raise FrameFault("node 41: OOM")
            return b"PNG"

    record, producer = FakeRecord(), DropsTheFirstJob()
    run_batch(sync_runner(), FakeStore(), producer, text='["patlak"]', variants=1, record=record)

    # Two attempts leave no line at all; the third writes the red one.
    assert producer.calls == 3
    assert photo_statuses(record) == {"P0_0": "failed"}


def test_a_dropped_job_writes_nothing_until_its_attempts_run_out():
    class DropsOnce:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed, model=""):
            self.calls += 1
            if self.calls == 1:
                raise FrameFault("node 41: OOM")
            return b"PNG"

    record = FakeRecord()
    run_batch(sync_runner(), FakeStore(), DropsOnce(), text='["a"]', variants=1, record=record)

    # The second attempt landed, so nothing was ever red.
    assert photo_statuses(record) == {"P0_0": "done"}


def test_each_job_gets_its_own_three_drops():
    class AlwaysDrops:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed, model=""):
            self.calls += 1
            raise FrameFault("node 41: OOM")

    record, producer = FakeRecord(), AlwaysDrops()
    run_batch(sync_runner(), FakeStore(), producer, text='["a", "b"]', variants=1, record=record)

    assert producer.calls == 6
    assert photo_statuses(record) == {"P0_0": "failed", "P1_0": "failed"}


def test_frames_that_fail_one_after_another_still_do_not_stop_the_queue():
    """The old rule counted three failed frames in a row; the new one counts attempts on ONE frame,
    so a queue of bad prompts turns red to the end instead of stopping partway."""
    class AlwaysBroken:
        def generate(self, prompt, negative, seed, model=""):
            raise FrameFault("node 41: OOM")

    store, runner = FakeStore(), sync_runner()
    run_batch(runner, store, AlwaysBroken(), text='["a", "b"]', variants=2)
    state = runner.status()
    assert state["status"] == "done"
    assert (state["done"], state["failed"], state["total"]) == (0, 4, 4)


def test_a_loader_failure_is_no_longer_special():
    """It used to stop the run on the first frame. ComfyUI answered, so it is now the frame's."""
    class BrokenLoader:
        def generate(self, prompt, negative, seed, model=""):
            raise FrameFault("node 9 (CheckpointLoaderSimple): dosya yok")

    runner = sync_runner()
    run_batch(runner, FakeStore(), BrokenLoader(), text='["a"]', variants=2)
    state = runner.status()
    assert (state["status"], state["failed"]) == ("done", 2)


def test_the_same_frame_is_tried_three_times_when_nothing_answers():
    class Unreachable:
        def __init__(self):
            self.calls = []

        def generate(self, prompt, negative, seed, model=""):
            self.calls.append(prompt)
            raise RuntimeError("Connection refused")

    generator, record, runner = Unreachable(), FakeRecord(), sync_runner()
    run_batch(runner, FakeStore(), generator, text='["ilk", "ikinci"]', variants=1, record=record)

    # Three attempts, all on the FIRST frame: a dead server no longer costs three frames.
    assert generator.calls == ["ilk", "ilk", "ilk"]
    state = runner.status()
    assert state["status"] == "error"
    assert "3 kez" in state["error"] and "Connection refused" in state["error"]
    # And no red tile: the frame never got a line, so it is still owed.
    assert record.statuses("düğün") == {}
    assert state["failed"] == 0


def test_a_frame_the_run_gave_up_on_is_still_owed():
    class Unreachable:
        def generate(self, prompt, negative, seed, model=""):
            raise RuntimeError("Connection refused")

    record, plan_store = FakeRecord(), FakePlanStore()
    run_batch(sync_runner(), FakeStore(), Unreachable(), text='["ilk"]', variants=1,
              record=record, plan_store=plan_store)

    # Kaldığı yerden devam et starts from the very frame that could not be reached.
    assert owed_files(record, plan_store) == ["P0_0.png"]


def test_an_attempt_that_lands_costs_the_frame_nothing():
    class FlakyTwice:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed, model=""):
            self.calls += 1
            if self.calls <= 2:
                raise RuntimeError("Connection refused")
            return b"PNG"

    store, record, runner = FakeStore(), FakeRecord(), sync_runner()
    run_batch(runner, store, FlakyTwice(), text='["ilk"]', variants=1, record=record)

    assert [name for name, _d in store.saved] == ["P0_0.png"]
    assert record.statuses("düğün") == {"P0_0": "done"}
    assert runner.status()["status"] == "done"


def test_every_frame_gets_its_own_three_attempts():
    class FailsOncePerFrame:
        def __init__(self):
            self.failed = set()
            self.calls = []

        def generate(self, prompt, negative, seed, model=""):
            self.calls.append(prompt)
            if prompt not in self.failed:
                self.failed.add(prompt)
                raise RuntimeError("Connection refused")
            return b"PNG"

    generator, runner = FailsOncePerFrame(), sync_runner()
    run_batch(runner, FakeStore(), generator, text='["ilk", "ikinci"]', variants=1)

    # The second frame's stumble does not land on a counter the first frame left behind.
    assert generator.calls == ["ilk", "ilk", "ikinci", "ikinci"]
    assert runner.status()["status"] == "done"


def test_stop_request_ends_the_batch_between_frames():
    store, runner = FakeStore(), sync_runner()

    class StopsAfterFirst:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed, model=""):
            self.calls += 1
            runner.request_stop()
            return b"PNG"

    generator = StopsAfterFirst()
    run_batch(runner, store, generator, text='["a", "b"]', variants=2)
    state = runner.status()
    assert (state["status"], state["done"], state["total"]) == ("paused", 1, 4)
    assert generator.calls == 1


def test_frame_killed_by_user_stop_is_not_a_failure():
    """A render that dies because the user pressed Durdur is 'stopped', never a failure."""
    store, runner = FakeStore(), sync_runner()

    class StoppingGenerator:
        def generate(self, prompt, negative, seed, model=""):
            runner.request_stop()          # the user's stop lands mid-render
            raise RuntimeError("interrupted")

    run_batch(runner, store, StoppingGenerator(), text='["a", "b", "c"]', variants=1)
    state = runner.status()
    assert state["status"] == "paused"
    assert state["failed"] == 0


def test_bad_prompt_text_is_rejected_before_anything_runs():
    store, generator = FakeStore(), FakeGenerator()
    with pytest.raises(InvalidPrompts):
        run_batch(sync_runner(), store, generator, text="42")
    assert generator.calls == [] and store.saved == []


@pytest.mark.parametrize("variants", [0, 27, "3", None, True])
def test_invalid_variants_are_rejected(variants):
    with pytest.raises(InvalidVariants) as exc:
        run_batch(sync_runner(), FakeStore(), FakeGenerator(), variants=variants)
    assert "1-26" in str(exc.value)


def test_missing_project_is_rejected():
    with pytest.raises(ProjectMissing) as exc:
        run_batch(sync_runner(), FakeStore(), FakeGenerator(), project="yok")
    assert str(exc.value) == "Proje yok: yok"


def test_a_worker_held_by_another_project_is_rejected():
    runner = PhotoRunner(spawn=lambda fn: None)   # stays "running"
    run_batch(runner, FakeStore(projects=("başka",)), FakeGenerator(), project="başka")
    with pytest.raises(Busy) as exc:
        run_batch(runner, FakeStore(), FakeGenerator())
    assert str(exc.value) == "Zaten bir üretim sürüyor."


def test_stop_generation_sets_the_flag_and_returns_the_state():
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("düğün", lambda: {"status": "done"})
    state = stop_generation(runner, interrupt=lambda: None)
    assert state["status"] == "running" and runner.stop_requested() is True


def test_stop_generation_when_idle_is_a_no_op():
    assert stop_generation(PhotoRunner(), interrupt=lambda: None) == {"status": "idle"}


def test_stop_generation_interrupts_and_reports_stopping():
    runner = PhotoRunner(spawn=lambda fn: None)     # claimed but never runs the job
    runner.start("p", lambda: {"status": "done"})
    calls = []
    state = stop_generation(runner, interrupt=lambda: calls.append("interrupt"))
    assert calls == ["interrupt"]
    assert state["status"] == "running" and state["stopping"] is True


def test_stop_generation_survives_interrupt_failure():
    """A dead ComfyUI must not turn Durdur into a 500 -- the flag alone already stops the batch."""
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("p", lambda: {"status": "done"})

    def broken_interrupt():
        raise RuntimeError("connection refused")

    state = stop_generation(runner, interrupt=broken_interrupt)
    assert state["stopping"] is True


def planned(*frames):
    """A plan store holding these frames, in the order they were queued."""
    return FakePlanStore(frames=[frame(n, letter, prompt) for n, letter, prompt in frames])


def owed_files(record, plan_store, project="düğün"):
    """The jobs the queue still has to do -- what the worker reads on its next turn."""
    return [photo_file(j["id"])
            for j in queue.open_jobs(plan_store.read(project)["frames"],
                                     record.slots(project))]


def test_the_gallery_holds_every_frame_the_plan_asked_for():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done", "prompt": "ilk"})
    plan_store = planned((0, "a", "ilk"), (1, "a", "ikinci"))

    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    # Newest on top, and the frame nobody has produced yet keeps its place in the sequence.
    assert [(f["file"], f["status"]) for f in frames] == [
        ("1_a.png", "pending"), ("0_a.png", "done")]


def test_a_removed_or_deleted_frame_leaves_the_gallery():
    record = FakeRecord()
    record.mark("düğün", "0_a", "photo", "0_a.png", "removed", "t1")
    record.mark("düğün", "1_a", "photo", "1_a.png", "deleted", "t2")
    plan_store = planned((0, "a", "ilk"), (1, "a", "ikinci"), (2, "a", "üçüncü"))

    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert [f["file"] for f in frames] == ["2_a.png"]


def test_a_failed_frame_stays_in_its_own_place():
    record = FakeRecord()
    record.mark("düğün", "1_a", "photo", "1_a.png", "failed", "t1")
    plan_store = planned((0, "a", "ilk"), (1, "a", "ikinci"), (2, "a", "üçüncü"))

    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert [(f["file"], f["status"]) for f in frames] == [
        ("2_a.png", "pending"), ("1_a.png", "failed"), ("0_a.png", "pending")]


def test_the_gallery_follows_the_stored_order():
    plan_store = planned((0, "a", "a"), (1, "a", "b"), (2, "a", "c"))
    order = FakeOrderStore(["1_a.png", "0_a.png", "2_a.png"])

    frames = list_frames(FakeRecord(), FakeStore(), plan_store, order, "düğün")

    assert [f["file"] for f in frames] == ["1_a.png", "0_a.png", "2_a.png"]


def test_a_photo_the_plan_forgot_is_still_the_gallerys():
    # Projects made before the plan became permanent kept only their last batch.
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done", "prompt": "eski"})

    frames = list_frames(record, FakeStore(), FakePlanStore(), FakeOrderStore(), "düğün")

    assert [f["file"] for f in frames] == ["0_a.png"]


def test_every_frame_carries_its_identity():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done", "prompt": "ilk"})
    plan_store = planned((0, "a", "ilk"), (1, "a", "ikinci"))

    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert [f["id"] for f in frames] == ["1_a", "0_a"]


def test_a_frames_taken_layers_are_published():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    plan_store = planned((0, "a", "ilk"))

    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert frames[0]["layers"] == {"photo": "0_a.png", "video": "0_a_v0.mp4"}


def test_an_emptied_slot_names_no_file_and_keeps_the_frame():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_v0.mp4", "deleted", "t3")
    plan_store = planned((0, "a", "ilk"))

    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    # Video and audio change how a frame looks, never whether it is here.
    assert [f["id"] for f in frames] == ["0_a"]
    assert frames[0]["layers"] == {"photo": "0_a.png"}


def test_old_and_new_frames_live_side_by_side():
    # A project made before the scheme changed: its plan holds no identities and its photo is on
    # disk under the old name. Nothing is renamed, so both have to work at once.
    record, plan_store = FakeRecord(), FakePlanStore()
    plan_store.frames = [{"number": 11, "letter": "d", "prompt": "eski", "negative": "", "seed": 1}]
    record.append("düğün", {"file": "11_d.png", "status": "done"})
    order = FakeOrderStore(["11_d"])

    run_batch(sync_runner(), FakeStore(next_no=12), FakeGenerator(), text='["yeni"]', variants=1,
              record=record, plan_store=plan_store)
    frames = list_frames(record, FakeStore(), plan_store, order, "düğün")

    # The old frame keeps its name and its place; the new one is named the new way.
    assert [f["id"] for f in frames] == ["P12_0", "11_d"]
    assert [f["file"] for f in frames] == ["P12_0.png", "11_d.png"]


def test_a_pending_frame_has_no_layers_yet():
    frames = list_frames(FakeRecord(), FakeStore(), planned((0, "a", "ilk")),
                         FakeOrderStore(), "düğün")

    assert frames[0]["layers"] == {} and frames[0]["status"] == "pending"


def test_the_gallery_rejects_a_missing_project():
    with pytest.raises(ProjectMissing):
        list_frames(FakeRecord(), FakeStore(), FakePlanStore(), FakeOrderStore(), "yok")


def test_save_order_stores_and_returns_the_kept_list():
    plan_store = planned((0, "a", "a"), (1, "a", "b"))
    order = FakeOrderStore()

    # The screen drags file names; what is stored and returned is the frame's identity.
    assert save_order(FakeRecord(), FakeStore(), plan_store, order, "düğün",
                      ["1_a.png", "0_a.png"]) == ["1_a", "0_a"]
    assert order.order == ["1_a", "0_a"]


def test_save_order_keeps_pending_frames_in_the_sequence():
    # A pending frame has a place in the gallery, so a drag that moved a photo past one is storable.
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    plan_store = planned((0, "a", "a"), (1, "a", "b"))

    assert save_order(record, FakeStore(), plan_store, FakeOrderStore(), "düğün",
                      ["0_a.png", "1_a.png"]) == ["0_a", "1_a"]


def test_save_order_drops_names_the_gallery_does_not_know():
    plan_store = planned((1, "a", "b"))
    order = FakeOrderStore()

    assert save_order(FakeRecord(), FakeStore(), plan_store, order, "düğün",
                      ["hayalet.png", "1_a.png"]) == ["1_a"]
    assert order.order == ["1_a"]


def test_save_order_rejects_a_body_that_is_not_a_list():
    with pytest.raises(InvalidOrder):
        save_order(FakeRecord(), FakeStore(), FakePlanStore(), FakeOrderStore(), "düğün", "1_a.png")


def test_save_order_rejects_a_non_string_entry():
    with pytest.raises(InvalidOrder):
        save_order(FakeRecord(), FakeStore(), FakePlanStore(), FakeOrderStore(), "düğün",
                   ["1_a.png", 7])


def test_save_order_rejects_a_missing_project():
    with pytest.raises(ProjectMissing):
        save_order(FakeRecord(), FakeStore(projects=()), FakePlanStore(), FakeOrderStore(),
                   "yok", [])


def test_export_reverses_the_gallery_so_the_bottom_frame_comes_first():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done", "prompt": "ilk"})
    record.append("düğün", {"file": "1_a.png", "status": "done", "prompt": "ikinci"})
    plan_store = planned((0, "a", "ilk"), (1, "a", "ikinci"))

    assert export_project(record, FakeStore(), plan_store, FakeOrderStore(), "düğün") == {
        "folder": "/fake/düğün",
        # The gallery reads 1_a above 0_a; the video starts at the bottom.
        "photos": [{"file": "0_a.png", "prompt": "ilk"},
                   {"file": "1_a.png", "prompt": "ikinci"}],
    }


def test_export_leaves_out_frames_that_never_became_photos():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done", "prompt": "ilk"})
    record.mark("düğün", "1_a", "photo", "1_a.png", "failed", "t1")
    plan_store = planned((0, "a", "ilk"), (1, "a", "ikinci"), (2, "a", "üçüncü"))

    exported = export_project(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert [row["file"] for row in exported["photos"]] == ["0_a.png"]


def test_export_of_an_empty_project_still_names_the_folder():
    assert export_project(FakeRecord(), FakeStore(), FakePlanStore(), FakeOrderStore(),
                          "düğün") == {"folder": "/fake/düğün", "photos": []}


def frame(number, letter="a", prompt="p", seed=1):
    return {"number": number, "letter": letter, "prompt": prompt, "seed": seed}


def test_progress_reports_name_the_frames_still_waiting():
    runner, reports = sync_runner(), []
    original = runner.report
    runner.report = lambda patch: (reports.append(patch), original(patch))[1]

    run_batch(runner, FakeStore(), FakeGenerator(), text='["a", "b"]', variants=1)

    # The first frame's report lists the one behind it; the last report has an empty queue.
    assert reports[0]["pending"] == ["P1_0.png"]
    assert reports[-1]["pending"] == []


def test_resume_only_produces_the_frames_the_record_is_missing():
    store, record, generator = FakeStore(), FakeRecord(), FakeGenerator()
    plan_store = FakePlanStore(frames=[frame(0, "a", "ilk"), frame(1, "a", "ikinci")],
                               negative="neg")
    record.append("düğün", {"file": "0_a.png"})

    resume_batch(sync_runner(), store, record, plan_store, {layers.PHOTO: generator},
                 lambda: "2026-08-05T10:00:00+00:00", "düğün")

    assert generator.calls == [("ikinci", "neg", 1, "")]
    assert [name for name, _d in store.saved] == ["1_a.png"]


def test_the_worker_starts_from_the_bottom_of_the_gallery():
    store, record, generator = FakeStore(), FakeRecord(), FakeGenerator()
    plan_store = FakePlanStore(frames=[frame(0, "a", "ilk"), frame(1, "a", "ikinci")])
    # Gallery order, top first: 0_a stands on top and 1_a at the foot -- and the foot is what gets
    # produced first, which is the opposite of the plan's own sequence.
    order_store = FakeOrderStore(["0_a.png", "1_a.png"])

    resume_batch(sync_runner(), store, record, plan_store, {layers.PHOTO: generator},
                 lambda: "2026-08-05T10:00:00+00:00", "düğün", order_store=order_store)

    assert [name for name, _d in store.saved] == ["1_a.png", "0_a.png"]


def test_retrying_them_all_puts_every_failed_job_back_in_line():
    store, record, generator = FakeStore(), FakeRecord(), FakeGenerator()
    plan_store = FakePlanStore(frames=[frame(0, "a", "ilk"), frame(1, "a", "ikinci"),
                                       frame(2, "a", "üçüncü")])
    record.mark("düğün", "0_a", "photo", "0_a.png", queue.FAILED, "t")
    record.mark("düğün", "1_a", "photo", "1_a.png", queue.DONE, "t")
    record.mark("düğün", "2_a", "photo", "2_a.png", queue.FAILED, "t")

    put_back = retry_failed(sync_runner(), store, record, plan_store,
                            {layers.PHOTO: generator}, lambda: "t2", "düğün")

    assert put_back == 2
    # The one that landed is not made again; the two red ones are.
    assert sorted(name for name, _d in store.saved) == ["0_a.png", "2_a.png"]


def test_resume_refuses_when_nothing_is_left():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png"})
    plan_store = FakePlanStore(frames=[frame(0)])

    with pytest.raises(NothingToResume):
        resume_batch(sync_runner(), FakeStore(), record, plan_store,
                     {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün")


def test_cancel_empties_the_queue_and_returns_to_idle():
    runner, record = sync_runner(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0), frame(1)])
    runner.request_stop()
    run_batch(runner, FakeStore(), FakeGenerator(), record=record, plan_store=plan_store)

    cancel_generation(runner, FakeStore(), record, plan_store, lambda: "t1", "düğün")

    # The plan keeps what was asked for; the log is what says those frames are not coming.
    assert owed_files(record, plan_store) == []
    assert runner.status() == {"status": "idle"}


def test_cancel_is_refused_while_the_queue_flows():
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("düğün", lambda: None)
    with pytest.raises(Busy):
        cancel_generation(runner, FakeStore(), FakeRecord(), FakePlanStore(), lambda: "t1",
                          "düğün")


def test_a_deleted_number_is_never_used_again():
    store, record, plan_store = FakeStore(next_no=0), FakeRecord(), FakePlanStore()
    record.append("düğün", {"file": "0_a.png"})
    record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "2026-08-05T10:00:00+00:00")

    assert next_number(store, plan_store, record, "düğün") == 1


def stamped():
    return "2026-08-05T10:00:00+00:00"


def test_a_photo_leaves_the_disk_and_the_log_says_so():
    store, record = FakeStore(), FakeRecord()
    for file in ("0_a.png", "1_a.png", "2_a.png"):
        record.append("düğün", {"file": file, "status": "done"})
    plan_store = planned((0, "a", "a"), (1, "a", "b"), (2, "a", "c"))
    order = FakeOrderStore(["0_a.png", "1_a.png", "2_a.png"])

    result = remove_frames(record, store, plan_store, order, stamped, "düğün",
                           ["0_a.png", "2_a.png"])

    assert result == {"deleted": ["0_a.png", "2_a.png"], "removed": []}
    assert store.deleted == ["0_a.png", "2_a.png"]
    assert [row["file"] for row in record.list("düğün")] == ["1_a.png"]
    assert order.order == ["1_a"]


def test_a_frame_that_was_never_produced_only_leaves_the_queue():
    store, record = FakeStore(), FakeRecord()
    plan_store = planned((0, "a", "a"), (1, "a", "b"))

    result = remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün",
                           ["1_a.png"])

    assert result == {"deleted": [], "removed": ["1_a.png"]}
    assert store.deleted == []                       # there is no file to delete yet
    assert owed_files(record, plan_store) == ["0_a.png"]


def test_a_failed_frame_leaves_the_gallery_the_same_way():
    store, record = FakeStore(), FakeRecord()
    record.mark("düğün", "1_a", "photo", "1_a.png", "failed", "t1")
    plan_store = planned((0, "a", "a"), (1, "a", "b"))

    result = remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün",
                           ["1_a.png"])

    assert result == {"deleted": [], "removed": ["1_a.png"]}
    assert [f["file"] for f in
            list_frames(record, store, plan_store, FakeOrderStore(), "düğün")] == ["0_a.png"]


def test_deleting_a_frame_takes_all_of_its_layer_files():
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    record.append("düğün", {"file": "0_a_v0_s0.wav", "frame": "0_a", "layer": "audio",
                            "status": "done"})
    plan_store = planned((0, "a", "a"))

    result = remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün",
                           ["0_a.png"])

    assert result == {"deleted": ["0_a.png"], "removed": []}
    assert sorted(store.deleted) == ["0_a.png", "0_a_v0.mp4", "0_a_v0_s0.wav"]
    assert list_frames(record, store, plan_store, FakeOrderStore(), "düğün") == []


def shared_video_pair(record):
    """Two frames over one video -- what an audio variant leaves behind (design v3, madde 102)."""
    for fid in ("0_a", "1_a"):
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        record.append("düğün", {"file": "0_a_v0.mp4", "frame": fid, "layer": "video",
                                "status": "done"})
    return planned((0, "a", "a"), (1, "a", "b"))


def test_a_file_another_frame_still_holds_is_left_on_disk():
    store, record = FakeStore(), FakeRecord()
    plan_store = shared_video_pair(record)

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a.png"])

    # Its own picture goes; the video the other frame still plays stays.
    assert store.deleted == ["0_a.png"]


def test_the_last_holder_takes_the_shared_file_with_it():
    store, record = FakeStore(), FakeRecord()
    plan_store = shared_video_pair(record)

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün",
                  ["0_a.png", "1_a.png"])

    assert sorted(store.deleted) == ["0_a.png", "0_a_v0.mp4", "1_a.png"]


def test_deleting_a_frame_whose_video_failed_unlinks_what_is_there():
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_v0.mp4", "failed", "t2", error="ComfyUI 500")
    plan_store = planned((0, "a", "a"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a.png"])

    # A failed layer holds its planned name; unlinking a file that never landed is not an error.
    assert sorted(store.deleted) == ["0_a.png", "0_a_v0.mp4"]


def test_a_frame_that_has_a_video_cannot_take_a_second_one():
    # Acceptance 1: production writes into a free slot or not at all.
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    cells = record.slots("düğün")["0_a"]
    assert layers.can_produce({slot: cell["status"] for slot, cell in cells.items()},
                              layers.VIDEO) is False


def test_deleting_a_frame_leaves_none_of_its_layer_files_behind():
    # Acceptance 2: the record closes every slot and the disk loses every file.
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    plan_store = planned((0, "a", "a"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a.png"])

    assert record.slots("düğün")["0_a"] == {
        "photo": {"status": "deleted", "file": "0_a.png"},
        "video": {"status": "deleted", "file": "0_a_v0.mp4"}}
    assert sorted(store.deleted) == ["0_a.png", "0_a_v0.mp4"]


def test_a_deleted_photo_still_never_returns_to_the_queue():
    # v4's guard: a free slot is not a debt. If the layer rule leaks into the queue, this goes red.
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    plan_store = planned((0, "a", "a"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a.png"])

    assert owed_files(record, plan_store) == []


def test_a_frame_pulled_out_never_gets_its_number_back():
    store, record = FakeStore(next_no=0), FakeRecord()
    plan_store = planned((0, "a", "a"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a.png"])

    assert next_number(store, plan_store, record, "düğün") == 1


def test_a_name_the_gallery_does_not_know_is_skipped_not_refused():
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})

    result = remove_frames(record, store, FakePlanStore(), FakeOrderStore(), stamped, "düğün",
                           ["hayalet.png", "0_a.png"])

    assert result == {"deleted": ["0_a.png"], "removed": []}
    assert store.deleted == ["0_a.png"]


def test_a_body_that_is_not_a_list_of_names_is_rejected():
    with pytest.raises(InvalidFiles):
        remove_frames(FakeRecord(), FakeStore(), FakePlanStore(), FakeOrderStore(), stamped,
                      "düğün", "0_a.png")


def test_removing_in_a_missing_project_is_rejected():
    with pytest.raises(ProjectMissing):
        remove_frames(FakeRecord(), FakeStore(projects=()), FakePlanStore(), FakeOrderStore(),
                      stamped, "yok", ["0_a.png"])


def test_export_rejects_a_missing_project():
    with pytest.raises(ProjectMissing):
        export_project(FakeRecord(), FakeStore(projects=()), FakePlanStore(), FakeOrderStore(),
                       "yok")


def test_get_status_passes_the_runner_state_through():
    assert get_status(PhotoRunner()) == {"status": "idle"}


def test_the_plan_is_appended_before_the_first_frame_renders():
    plan_store, runner = FakePlanStore(), sync_runner()

    class ChecksThePlan:
        def generate(self, prompt, negative, seed, model=""):
            assert plan_store.appended, "the batch started before the plan was appended to"
            return b"PNG"

    run_batch(runner, FakeStore(), ChecksThePlan(), text='["a"]', variants=2,
              plan_store=plan_store)
    assert plan_store.appended == [
        [{"id": "P0_0", "type": "photo", "number": 0, "variant": 0, "prompt": "a",
          "negative": "neg", "seed": 42, "model": ""},
         {"id": "P0_1", "type": "photo", "number": 0, "variant": 1, "prompt": "a",
          "negative": "neg", "seed": 42, "model": ""}]]


def test_each_produced_photo_gets_a_record_row():
    record = FakeRecord()
    run_batch(sync_runner(), FakeStore(), FakeGenerator(), text='["a"]', variants=2, record=record)
    assert record.rows == [
        {"file": "P0_0.png", "frame": "P0_0", "layer": "photo", "status": "done", "prompt": "a",
         "negative": "neg", "seed": 42, "createdAt": "2026-08-03T14:32:11+00:00"},
        {"file": "P0_1.png", "frame": "P0_1", "layer": "photo", "status": "done", "prompt": "a",
         "negative": "neg", "seed": 42, "createdAt": "2026-08-03T14:32:11+00:00"},
    ]


def test_a_failed_frame_gets_a_failure_row_not_a_photo_row():
    record = FakeRecord()
    run_batch(sync_runner(), FakeStore(), FakeGenerator(fail_on=["patlak"]),
              text='["patlak", "tutan"]', variants=1, record=record)

    assert record.statuses("düğün") == {"P0_0": "failed", "P1_0": "done"}
    assert [row["file"] for row in record.list("düğün")] == ["P1_0.png"]
    # The server's own words travel with the line -- never a guessed cause.
    assert "node 41: patlak" in record.rows[0]["error"]


def test_numbering_skips_what_an_unfinished_plan_reserved():
    # Disk stopped at 4 because the run died, but the plan had reserved through 11.
    store = FakeStore(next_no=5)
    run_batch(sync_runner(), store, FakeGenerator(), text='["a"]', variants=1,
              plan_store=FakePlanStore(reserved=11))
    assert [name for name, _d in store.saved] == ["P12_0.png"]


def test_numbering_follows_disk_when_it_is_ahead_of_the_plan():
    store = FakeStore(next_no=20)
    run_batch(sync_runner(), store, FakeGenerator(), text='["a"]', variants=1,
              plan_store=FakePlanStore(reserved=11))
    assert [name for name, _d in store.saved] == ["P20_0.png"]


def test_a_rejected_batch_writes_no_plan():
    plan_store = FakePlanStore()
    with pytest.raises(InvalidPrompts):
        run_batch(sync_runner(), FakeStore(), FakeGenerator(), text="42", plan_store=plan_store)
    assert plan_store.appended == []


def test_frames_added_while_the_loop_runs_are_produced_in_the_same_run():
    """The whole point of a live queue: the loop asks the plan again on every turn."""
    plan_store, record, generator, seen = FakePlanStore(), FakeRecord(), FakeGenerator(), []
    rendering = generator.generate

    def spy(prompt, negative, seed, model=""):
        seen.append(prompt)
        if prompt == "ilk":
            plan_store.append("düğün", [{"number": 9, "letter": "a", "prompt": "sonradan",
                                         "negative": "", "seed": 7, "model": ""}])
        return rendering(prompt, negative, seed, model)

    generator.generate = spy
    run_batch(sync_runner(), FakeStore(), generator, text='["ilk"]', variants=1,
              record=record, plan_store=plan_store)

    assert seen == ["ilk", "sonradan"]


def test_the_loop_stops_by_itself_when_the_queue_empties():
    runner = sync_runner()
    run_batch(runner, FakeStore(), FakeGenerator(), text='["tek"]', variants=1)
    assert runner.status()["status"] == "done"


def test_adding_to_the_queue_of_the_running_project_is_not_busy():
    runner = PhotoRunner(spawn=lambda fn: None)     # claims the worker, never runs the job
    runner.start("düğün", lambda: None)
    run_batch(runner, FakeStore(), FakeGenerator(), text='["ikinci parti"]', variants=1)


def test_adding_while_another_project_runs_is_busy():
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("başka", lambda: None)
    with pytest.raises(Busy) as exc:
        run_batch(runner, FakeStore(), FakeGenerator(), text='["ilk"]', variants=1)
    assert str(exc.value) == "Zaten bir üretim sürüyor."


def test_a_failed_frame_is_written_to_the_log():
    record = FakeRecord()
    run_batch(sync_runner(), FakeStore(), FakeGenerator(fail_on=["patlak"]), text='["patlak"]',
              variants=1, record=record)
    assert record.statuses("düğün") == {"P0_0": "failed"}


def test_the_gallery_still_shows_a_red_frame_after_a_restart():
    record, plan_store = FakeRecord(), FakePlanStore()
    run_batch(sync_runner(), FakeStore(), FakeGenerator(fail_on=["patlak"]),
              text='["patlak", "tutan"]', variants=1, record=record, plan_store=plan_store)

    # A restarted server holds nothing: this answer comes from the plan and the log alone.
    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")
    assert [(f["file"], f["status"]) for f in frames] == [
        ("P1_0.png", "done"), ("P0_0.png", "failed")]


def test_a_deleted_photo_does_not_come_back_as_pending():
    record, plan_store = FakeRecord(), FakePlanStore()
    run_batch(sync_runner(), FakeStore(), FakeGenerator(), text='["tek"]', variants=1,
              record=record, plan_store=plan_store)

    record.mark("düğün", "P0_0", "photo", "P0_0.png", "deleted", "t9")

    assert owed_files(record, plan_store) == []


def test_retry_puts_the_frame_back_in_line():
    record, plan_store = FakeRecord(), FakePlanStore()
    generator = FakeGenerator(fail_on=["patlak"])
    run_batch(sync_runner(), FakeStore(), generator, text='["patlak"]', variants=1,
              record=record, plan_store=plan_store)

    generator.fail_on = []
    retry_frame(sync_runner(), FakeStore(), record, plan_store, {layers.PHOTO: generator},
                lambda: "t2", "düğün", "P0_0.png")

    assert record.statuses("düğün") == {"P0_0": "done"}


def test_a_retried_frame_waits_behind_the_frames_that_never_had_a_turn():
    record, plan_store = FakeRecord(), FakePlanStore()
    generator = FakeGenerator(fail_on=["patlak"])
    # The first batch leaves P0_0 red; the second one queues two frames that have never run.
    run_batch(sync_runner(), FakeStore(), generator, text='["patlak"]', variants=1,
              record=record, plan_store=plan_store)
    plan_store.append("düğün", [{"id": "P1_0", "number": 1, "variant": 0, "prompt": "yeni",
                                 "negative": "", "seed": 1},
                                {"id": "P2_0", "number": 2, "variant": 0, "prompt": "yeni",
                                 "negative": "", "seed": 2}])

    record.mark("düğün", "P0_0", "photo", "P0_0.png", queue.QUEUED, "t2")

    # Plan order would have put P0_0 first; Tekrar dene does not jump the queue.
    assert owed_files(record, plan_store) == ["P1_0.png", "P2_0.png", "P0_0.png"]


def test_retrying_does_not_interrupt_a_run_that_is_already_going():
    record, plan_store = FakeRecord(), FakePlanStore()
    plan_store.append("düğün", [{"number": 0, "letter": "a", "prompt": "p", "negative": "",
                                 "seed": 1}])
    record.mark("düğün", "0_a", "photo", "0_a.png", queue.FAILED, "t1", error="node 41: OOM")
    runner = PhotoRunner(spawn=lambda fn: None)     # claims the worker, never runs the job
    runner.start("düğün", lambda: None)

    # No refusal, and no second worker: the live loop reads the record again on its next turn.
    retry_frame(runner, FakeStore(), record, plan_store, {layers.PHOTO: FakeGenerator()},
                lambda: "t2", "düğün", "0_a.png")

    assert record.statuses("düğün") == {"0_a": queue.QUEUED}
    assert runner.status()["status"] == "running"


def test_clearing_the_queue_keeps_the_numbers_dead():
    store, record, plan_store = FakeStore(next_no=0), FakeRecord(), FakePlanStore()
    plan_store.append("düğün", [{"number": 0, "letter": "a", "prompt": "p", "negative": "",
                                 "seed": 1}])

    cancel_generation(sync_runner(), store, record, plan_store, lambda: "t1", "düğün")

    assert record.statuses("düğün") == {"0_a": "removed"}
    assert next_number(store, plan_store, record, "düğün") == 1


def test_a_second_batch_renders_with_its_own_negative():
    plan_store, record, generator = FakePlanStore(), FakeRecord(), FakeGenerator()
    run_batch(sync_runner(), FakeStore(), generator, text='["ilk"]', negative="n1", variants=1,
              record=record, plan_store=plan_store)
    run_batch(sync_runner(), FakeStore(), generator, text='["ikinci"]', negative="n2", variants=1,
              record=record, plan_store=plan_store)

    assert [negative for _prompt, negative, _seed, _model in generator.calls] == ["n1", "n2"]


def test_a_second_batch_renders_with_its_own_model():
    """Same reason as the negative: a live queue holds batches sent under different settings."""
    plan_store, record, generator = FakePlanStore(), FakeRecord(), FakeGenerator()
    run_batch(sync_runner(), FakeStore(), generator, text='["ilk"]', variants=1,
              record=record, plan_store=plan_store, model="nova.safetensors")
    run_batch(sync_runner(), FakeStore(), generator, text='["ikinci"]', variants=1,
              record=record, plan_store=plan_store, model="başka.safetensors")

    assert [model for _p, _n, _s, model in generator.calls] == ["nova.safetensors",
                                                                "başka.safetensors"]


def test_a_frame_planned_before_models_renders_with_the_graphs_own():
    plan_store, generator = FakePlanStore(), FakeGenerator()
    # No "model" key at all -- exactly what an older plan file holds.
    plan_store.frames = [{"number": 0, "letter": "a", "prompt": "eski", "negative": "", "seed": 1}]

    resume_batch(sync_runner(), FakeStore(), FakeRecord(), plan_store, {layers.PHOTO: generator},
                 lambda: "t1", "düğün")

    assert generator.calls == [("eski", "", 1, "")]


def timed_job(lines, ticks, frames, generator=None):
    """A loop whose clock is a list of readings, so no test ever waits on a real second."""
    plan_store = FakePlanStore()
    plan_store.append("düğün", frames)
    clock = iter(ticks)
    return make_job(sync_runner(), FakeStore(), FakeRecord(), plan_store,
                    {layers.PHOTO: generator or FakeGenerator()}, lambda: "t1", "düğün",
                    clock=lambda: next(clock), log=lines.append)


def test_the_render_and_the_writes_are_measured_apart():
    lines = []
    # Readings in the order the loop asks for them: start -> rendered -> written.
    timed_job(lines, [100.0, 142.0, 143.5],
              [{"number": 0, "letter": "a", "prompt": "a", "negative": "", "seed": 1,
                "model": ""}])()

    assert lines == ["⏱ 0_a.png · render 42.0 sn · drive 1.5 sn"]


def test_every_produced_frame_gets_its_own_line():
    lines = []
    timed_job(lines, [0.0, 10.0, 10.5, 20.0, 25.0, 25.5],
              [{"number": 0, "letter": "a", "prompt": "a", "negative": "", "seed": 1, "model": ""},
               {"number": 1, "letter": "a", "prompt": "b", "negative": "", "seed": 2,
                "model": ""}])()

    assert lines == ["⏱ 0_a.png · render 10.0 sn · drive 0.5 sn",
                     "⏱ 1_a.png · render 5.0 sn · drive 0.5 sn"]


def test_a_job_whose_type_has_no_producer_stops_the_run():
    # Never silently skipped: skipping would drop work the user asked for.
    plan_store = FakePlanStore(frames=[{"id": "P0_0", "type": "video", "number": 0, "variant": 0,
                                        "prompt": "", "seed": 1}])
    state = make_job(sync_runner(), FakeStore(), FakeRecord(), plan_store,
                     {layers.PHOTO: FakeGenerator()}, lambda: "t1", "düğün")()

    assert state["status"] == "error" and "video" in state["error"]


def test_the_loop_finishes_photos_before_it_starts_videos():
    record, store = FakeRecord(), FakeStore()
    plan_store = FakePlanStore(frames=[
        {"id": "P0_0", "type": "video", "number": 0, "variant": 0, "prompt": "v", "seed": 1},
        {"id": "P1_0", "type": "photo", "number": 1, "variant": 0, "prompt": "f", "seed": 2},
    ])

    class Records:
        def __init__(self, kind):
            self.kind = kind

        def generate(self, prompt, negative, seed, model=""):
            done.append(self.kind)
            return b"X"

    done = []
    make_job(sync_runner(), store, record, plan_store,
             {layers.PHOTO: Records("photo"), layers.VIDEO: Records("video")},
             lambda: "t1", "düğün")()

    # Plan order would have put the video first; the type order does not let it.
    assert done == ["photo", "video"]


def test_a_frame_that_blew_up_writes_no_timing_line():
    lines = []
    run_batch(sync_runner(), FakeStore(), FakeGenerator(fail_on=["patlak"]), text='["patlak"]',
              variants=1, log=lines.append)

    assert lines == []


def test_nothing_is_written_when_nobody_asked_for_timings():
    # The default: the loop runs exactly as it did before and reports to nowhere.
    runner = sync_runner()
    run_batch(runner, FakeStore(), FakeGenerator(), text='["a"]', variants=1)

    assert runner.status()["status"] == "done"


def test_the_model_list_is_whatever_the_renderer_reports():
    generator = FakeGenerator(installed=["nova.safetensors", "başka.safetensors"])

    assert list_models(generator) == ["nova.safetensors", "başka.safetensors"]
    assert generator.models_called == 1
