import pytest

from backend.features.photo_generation.domain import layers, production_mode, queue
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
from backend.features.photo_generation.domain.usecases.queue_layer import (
    InvalidMode,
    frames_in_scope,
    queue_layer,
)
from backend.features.photo_generation.domain.usecases.regenerate import (
    FrameMissing,
    LayerMissing,
    regenerate,
)
from backend.features.photo_generation.domain.usecases.remove_layer import remove_layer
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
from backend.features.photo_generation.domain.usecases.export_summary import (
    export_summary,
    exportable,
)
from backend.features.photo_generation.domain.usecases.resume_batch import (
    NothingToResume,
    resume_batch,
)
from backend.features.photo_generation.domain.usecases import halt_project as halt_module
from backend.features.photo_generation.domain.usecases.halt_project import halt_project
from backend.features.photo_generation.domain.usecases.save_order import InvalidOrder, save_order
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
from backend.features.photo_generation.runner import PhotoRunner


class FakeStore:
    def __init__(self, projects=("düğün",), next_no=0):
        self.projects = list(projects)
        self.next_no = next_no
        self.saved = []
        self.deleted = []
        self.files = {}                   # what read() answers with, by name

    def project_exists(self, project):
        return project in self.projects

    def next_number(self, project):
        return self.next_no

    def save(self, project, filename, data):
        self.saved.append((filename, data))
        self.files[filename] = data
        return filename

    def read(self, project, filename):
        return self.files.get(filename)

    def delete(self, project, filename):
        self.deleted.append(filename)

    def photo_dir(self, project):
        return f"/fake/{project}"

    def export_dir(self, project):
        return f"/fake/{project}/export"


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
        self.sources = []
        # Kept apart from sources: what a layer is made from and where it arrives are two different
        # questions, and one list holding both could not answer either.
        self.ends = []
        self.models_called = 0
        self.fail_on = list(fail_on)
        self.installed = list(installed)

    def models(self):
        self.models_called += 1
        return list(self.installed)

    def generate(self, prompt, negative, seed, model="", source=None, end=None):
        self.calls.append((prompt, negative, seed, model))
        self.sources.append(source)
        self.ends.append(end)
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
            cell = {"status": row.get("status", "done"), "file": row["file"]}
            if isinstance(row.get("error"), str):
                cell["error"] = row["error"]
            folded.setdefault(self._frame_of(row), {})[self._layer_of(row)] = cell
        return folded

    def prompts(self, project):
        folded = {}
        for row in self.rows:
            prompt = row.get("prompt")
            if isinstance(prompt, str):
                folded.setdefault(self._frame_of(row), {})[self._layer_of(row)] = prompt
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

    def spy(prompt, negative, seed, model="", source=None, end=None):
        seen.append(runner.status())
        return original(prompt, negative, seed, model, source, end)

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

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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
        def generate(self, prompt, negative, seed, model="", source=None, end=None):
            raise FrameFault("node 41: OOM")

    store, runner = FakeStore(), sync_runner()
    run_batch(runner, store, AlwaysBroken(), text='["a", "b"]', variants=2)
    state = runner.status()
    assert state["status"] == "done"
    assert (state["done"], state["failed"], state["total"]) == (0, 4, 4)


def test_a_loader_failure_is_no_longer_special():
    """It used to stop the run on the first frame. ComfyUI answered, so it is now the frame's."""
    class BrokenLoader:
        def generate(self, prompt, negative, seed, model="", source=None, end=None):
            raise FrameFault("node 9 (CheckpointLoaderSimple): dosya yok")

    runner = sync_runner()
    run_batch(runner, FakeStore(), BrokenLoader(), text='["a"]', variants=2)
    state = runner.status()
    assert (state["status"], state["failed"]) == ("done", 2)


def test_the_same_frame_is_tried_three_times_when_nothing_answers():
    class Unreachable:
        def __init__(self):
            self.calls = []

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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
        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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
        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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


def halting_runner(project="düğün"):
    """A worker that has claimed `project` and never lets go on its own."""
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start(project, lambda: {"status": "done"})
    return runner


def test_halting_a_project_asks_its_run_to_stop_and_cuts_the_render():
    runner = halting_runner()
    calls = []

    assert halt_project(runner, lambda: calls.append("interrupt"), lambda _: None, "düğün") is True

    assert calls == ["interrupt"]
    assert runner.stop_requested() is True
    # This worker never comes back, so it is still the one holding the machine -- saying "idle"
    # here would be the lie. It is left as it is and its own ending publishes the truth.
    assert runner.status()["status"] == "running"


def test_halting_leaves_a_run_that_belongs_to_another_project_alone():
    """Deleting «düğün» must not cut «nişan» short -- one project's bin is not a global stop."""
    runner = halting_runner("nişan")
    calls = []

    assert halt_project(runner, lambda: calls.append("interrupt"), lambda _: None, "düğün") is False

    assert calls == []
    assert runner.status()["status"] == "running"


def test_halting_an_idle_worker_is_a_no_op_that_still_answers():
    runner = PhotoRunner()

    assert halt_project(runner, lambda: None, lambda _: None, "düğün") is False


def test_halting_survives_a_dead_comfy():
    """The renderer being unreachable cannot be what stops a project from being deleted."""
    runner = halting_runner()

    def broken_interrupt():
        raise RuntimeError("connection refused")

    assert halt_project(runner, broken_interrupt, lambda _: None, "düğün") is True
    assert runner.stop_requested() is True


def test_halting_gives_up_waiting_rather_than_holding_the_delete_forever():
    """The worker never leaves "running": the wait ends on its own and the delete goes ahead."""
    runner = halting_runner()
    slept = []

    halt_project(runner, lambda: None, lambda step: slept.append(step), "düğün")

    assert len(slept) == halt_module.LIMIT
    assert slept[0] == halt_module.STEP


def test_halting_stops_waiting_the_moment_the_worker_leaves():
    jobs = []
    runner = PhotoRunner(spawn=jobs.append)      # the job waits here until a test runs it
    runner.start("düğün", lambda: {"status": "stopped"})
    slept = []

    def step(seconds):
        slept.append(seconds)
        # The batch ends between frames: on the second tick this one reaches that point.
        if len(slept) == 2:
            jobs[0]()

    halt_project(runner, lambda: None, step, "düğün")

    assert len(slept) == 2
    assert runner.status() == {"status": "idle"}


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


def test_a_frame_whose_video_is_queued_is_still_one_frame():
    # The plan holds a job per layer; the gallery holds a row per frame.
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store = FakePlanStore(frames=[
        frame(0),
        {"id": "0_a", "type": "video", "number": 0, "prompt": "", "negative": "", "seed": None,
         "model": ""},
    ])

    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert [f["id"] for f in frames] == ["0_a"]
    # The row comes from the photo job, so it still carries what the photo was asked for.
    assert frames[0]["prompt"] == "p"


def test_a_frame_says_which_layers_the_queue_still_owes_it():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store = FakePlanStore(frames=[
        frame(0),
        {"id": "0_a", "type": "video", "number": 0, "prompt": "", "negative": "", "seed": None,
         "model": ""},
        frame(1),
    ])

    rows = {row["id"]: row for row in
            list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")}

    assert rows["0_a"]["owed"] == ["video"]     # its photo landed; the video is still coming
    assert rows["1_a"]["owed"] == ["photo"]
    assert rows["0_a"]["failed"] == []


def test_a_frame_carries_the_prompt_of_every_layer_it_holds():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done",
                            "prompt": "kırmızı elbise"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})
    plan_store = FakePlanStore(frames=[frame(0)])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert rows[0]["prompts"] == {"photo": "kırmızı elbise", "video": "kadın dönüyor"}


def test_a_frame_whose_record_kept_no_prompt_falls_back_to_the_plans():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store = FakePlanStore(frames=[frame(0)])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert rows[0]["prompts"] == {"photo": "p"}


def test_a_produced_layer_leaves_the_owed_list():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    plan_store = FakePlanStore(frames=[
        frame(0),
        {"id": "0_a", "type": "video", "number": 0, "prompt": "", "negative": "", "seed": None,
         "model": ""},
    ])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert rows[0]["owed"] == []


def test_a_layer_that_blew_up_is_named_as_such():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", "failed", "t", error="node 41")
    plan_store = FakePlanStore(frames=[frame(0)])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    # A failed layer holds its slot -- it is not owed and it is not done.
    assert rows[0]["failed"] == ["video"]
    assert rows[0]["owed"] == []


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

    # The screen drags frames; identities in, identities out.
    assert save_order(FakeRecord(), FakeStore(), plan_store, order, "düğün",
                      ["1_a", "0_a"]) == ["1_a", "0_a"]
    assert order.order == ["1_a", "0_a"]


def test_save_order_keeps_only_the_first_of_a_repeated_frame():
    plan_store = planned((0, "a", "a"), (1, "a", "b"))

    assert save_order(FakeRecord(), FakeStore(), plan_store, FakeOrderStore(), "düğün",
                      ["1_a", "0_a", "1_a"]) == ["1_a", "0_a"]


def test_save_order_keeps_pending_frames_in_the_sequence():
    # A pending frame has a place in the gallery, so a drag that moved a photo past one is storable.
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    plan_store = planned((0, "a", "a"), (1, "a", "b"))

    assert save_order(record, FakeStore(), plan_store, FakeOrderStore(), "düğün",
                      ["0_a", "1_a"]) == ["0_a", "1_a"]


def test_save_order_drops_names_the_gallery_does_not_know():
    plan_store = planned((1, "a", "b"))
    order = FakeOrderStore()

    assert save_order(FakeRecord(), FakeStore(), plan_store, order, "düğün",
                      ["hayalet", "1_a"]) == ["1_a"]
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


def test_the_summary_counts_the_frames_that_have_a_video():
    store, record, plan_store = layered_project(audio=False)
    record.append("düğün", {"file": "1_a.png", "frame": "1_a", "layer": "photo", "status": "done"})

    summary = export_summary(record, store, plan_store, FakeOrderStore(), lambda: 5,"düğün")

    assert summary == {"videos": 1, "seconds": 5, "silent": 1, "withoutVideo": 1,
                       "folder": "/fake/düğün/export"}


def test_the_total_length_comes_from_whoever_knows_how_long_a_video_is():
    # Not a number of this use case's own: the graph sets the length, and a copy of it here goes on
    # being quoted after the graph moves.
    store, record, plan_store = layered_project()

    summary = export_summary(record, store, plan_store, FakeOrderStore(), lambda: 7.5, "düğün")

    assert summary["videos"] == 1 and summary["seconds"] == 7.5


def test_a_project_with_no_video_exports_nothing():
    store, record, plan_store = video_project((0, "a"))

    assert export_summary(record, store, plan_store, FakeOrderStore(), lambda: 5,"düğün") == {
        "videos": 0, "seconds": 0, "silent": 0, "withoutVideo": 1,
        "folder": "/fake/düğün/export"}


def test_a_video_that_blew_up_is_not_counted():
    store, record, plan_store = video_project((0, "a"))
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", "failed", "t")

    assert export_summary(record, store, plan_store, FakeOrderStore(), lambda: 5,"düğün")["videos"] == 0


def test_the_summary_reads_the_gallery_from_the_bottom_up():
    # The video starts at the foot of the gallery: the badge counts up from there.
    store, record, plan_store = layered_project(audio=False)
    record.append("düğün", {"file": "1_a.png", "frame": "1_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "1_a_V1_0.mp4", "frame": "1_a", "layer": "video",
                            "status": "done"})

    frames = list_frames(record, store, plan_store, FakeOrderStore(), "düğün")

    assert [f["id"] for f in exportable(frames)] == ["1_a", "0_a"]


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


def test_a_type_with_no_producer_makes_the_queue_wait_rather_than_fail():
    runner, store, record = sync_runner(), FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[{"id": "P0_0", "type": "video", "prompt": "a",
                                        "negative": "", "seed": 1, "model": "", "number": 0}])

    resume_batch(runner, store, record, plan_store, {layers.PHOTO: FakeGenerator()},
                 lambda: "t", "düğün")

    assert runner.status()["status"] == "waiting"
    assert runner.status()["waitingFor"] == "video"
    # Nothing was written, so the job is still owed: installing the producer is all it takes.
    assert queue.open_jobs(plan_store.read("düğün")["frames"], record.slots("düğün"))


def test_the_engine_does_not_skip_past_the_type_it_is_waiting_for():
    runner, store, record = sync_runner(), FakeStore(), FakeRecord()
    generator = FakeGenerator()
    # Audio could be done -- but video comes first, and video has nobody to do it.
    plan_store = FakePlanStore(frames=[
        {"id": "P0_0", "type": "video", "prompt": "a", "negative": "", "seed": 1, "model": "",
         "number": 0},
        {"id": "P0_0", "type": "audio", "prompt": "b", "negative": "", "seed": 2, "model": "",
         "number": 0},
    ])

    resume_batch(runner, store, record, plan_store, {layers.AUDIO: generator}, lambda: "t", "düğün")

    assert runner.status()["waitingFor"] == "video"
    assert generator.calls == []


class FakeWriter:
    """The language model, without one: answers the same sentence and counts the asks."""

    def __init__(self, answer="kadın başını yavaşça çeviriyor", blows_up=None):
        self.answer = answer
        self.blows_up = blows_up
        self.calls = []

    def write(self, prompts):
        self.calls.append(prompts)
        if self.blows_up:
            raise self.blows_up
        return self.answer


class FailsTwice:
    """Drops the first two attempts at the same job, then renders whatever is offered."""

    def __init__(self):
        self.calls = []

    def generate(self, prompt, negative, seed, model="", source=None, end=None):
        self.calls.append((prompt, negative, seed, model))
        if len(self.calls) < 3:
            raise FrameFault(f"node 41: {prompt}")
        return b"MP4"


def video_job_project(prompt="p", job_prompt=""):
    """A produced photo and one video job owed on it."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[
        frame(0, prompt=prompt),
        {"id": "0_a", "type": "video", "number": 0, "variant": 0, "prompt": job_prompt,
         "negative": "", "seed": None, "model": ""},
    ])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done",
                            "prompt": prompt})
    return store, record, plan_store


def test_a_video_job_with_no_prompt_has_one_written_from_the_photos():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    generator, writer = FakeGenerator(), FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.calls == [{"photo": "kırmızı elbiseli kadın"}]
    # Produced with the written text, and the record says the layer was made with it.
    assert generator.calls == [("kadın başını yavaşça çeviriyor", "", None, "")]
    video = [row for row in record.rows if row.get("layer") == "video"][0]
    assert video["prompt"] == "kadın başını yavaşça çeviriyor"


def test_a_sound_is_made_from_the_frames_video_and_written_beside_it():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})
    store.files["0_a_V1_0.mp4"] = b"MP4DATA"
    plan_store.frames.append({"id": "0_a", "type": "audio", "number": 0, "variant": 0,
                              "prompt": "sessiz oda", "negative": "", "seed": None, "model": ""})
    generator = FakeGenerator()

    resume_batch(sync_runner(), store, record, plan_store,
                 {layers.VIDEO: FakeGenerator(), layers.AUDIO: generator},
                 lambda: "t", "düğün")

    assert generator.sources == [("0_a_V1_0.mp4", b"MP4DATA")]
    assert [name for name, _d in store.saved] == ["0_a_V1_0_S1_0.wav"]


def test_a_video_is_written_under_the_layers_own_name():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    generator = FakeGenerator()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: FakeWriter()})

    assert [name for name, _data in store.saved] == ["0_a_V1_0.mp4"]
    video = [row for row in record.rows if row.get("layer") == "video"][0]
    assert video["file"] == "0_a_V1_0.mp4"


def test_the_video_producer_is_handed_the_frames_own_photo():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    store.files["0_a.png"] = b"PNGDATA"
    generator = FakeGenerator()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: FakeWriter()})

    assert generator.sources == [("0_a.png", b"PNGDATA")]


def test_a_photo_is_made_from_its_prompt_alone():
    runner, store, record = sync_runner(), FakeStore(), FakeRecord()
    generator = FakeGenerator()

    run_batch(runner, store, generator, text='["a"]', variants=1, record=record)

    assert generator.sources == [None]


def test_a_sound_job_is_written_from_the_frames_two_prompts():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın başını çeviriyor"})
    plan_store.frames.append({"id": "0_a", "type": "audio", "number": 0, "variant": 0,
                              "prompt": "", "negative": "", "seed": None, "model": ""})
    writer = FakeWriter(answer="fabric rustling")

    resume_batch(sync_runner(), store, record, plan_store,
                 {layers.VIDEO: FakeGenerator(), layers.AUDIO: FakeGenerator()},
                 lambda: "t", "düğün", writers={layers.AUDIO: writer})

    assert writer.calls == [{"photo": "kırmızı elbiseli kadın", "video": "kadın başını çeviriyor"}]


def test_a_job_that_carries_its_own_prompt_never_reaches_the_model():
    # An edited prompt is the user's own words: asking the model again would overwrite them.
    store, record, plan_store = video_job_project(job_prompt="elini kaldırıyor")
    generator, writer = FakeGenerator(), FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.calls == []
    assert generator.calls == [("elini kaldırıyor", "", None, "")]


def test_a_frame_with_no_photo_prompt_is_not_worth_an_ask():
    store, record, plan_store = video_job_project(prompt="")
    generator, writer = FakeGenerator(), FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert writer.calls == []
    assert generator.calls == [("", "", None, "")]


def test_the_three_attempts_of_one_job_spend_a_single_ask():
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    generator, writer = FailsTwice(), FakeWriter()

    resume_batch(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    assert len(generator.calls) == 3
    assert len(writer.calls) == 1


def test_a_model_that_will_not_answer_stops_the_run():
    # No answer is not this frame's fault: the next job would fall exactly the same way.
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")
    runner = sync_runner()
    writer = FakeWriter(blows_up=RuntimeError("xAI HTTP 401\ninvalid key"))

    resume_batch(runner, store, record, plan_store, {layers.VIDEO: FakeGenerator()},
                 lambda: "t", "düğün", writers={layers.VIDEO: writer})

    state = runner.status()
    assert state["status"] == "error"
    assert "401" in state["error"]
    # Nothing written: the job is still owed once the key is fixed.
    assert [row for row in record.rows if row.get("layer") == "video"] == []


def video_project(*frames):
    """A plan and a record where every named frame has a produced photo."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(number) for number, _letter in frames])
    for number, _letter in frames:
        record.append("düğün", {"file": f"{number}_a.png", "frame": f"{number}_a",
                                "layer": "photo", "status": "done"})
    return store, record, plan_store


def queue_video(store, record, plan_store, mode, order=(), files=None):
    """Queue a video job the way the panel would, and hand back the plan lines it wrote."""
    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(order),
                        {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO,
                        files=files, mode=mode)
    return added, (plan_store.appended[-1] if plan_store.appended else [])


def test_a_video_job_carries_the_mode_it_was_queued_with():
    store, record, plan_store = video_project((0, "a"), (1, "a"))

    _added, jobs = queue_video(store, record, plan_store, production_mode.LOOP)

    # The mode is on the job, not on the batch: the queue holds work from several presses at once,
    # and a batch-level answer would be read by whichever job happened to be next.
    assert [job["mode"] for job in jobs] == ["loop", "loop"]


def test_a_linked_video_job_names_the_frame_it_ends_on():
    """Resolved as the job is queued rather than as it is rendered: the queue runs for hours and the
    gallery can be dragged while it does, so a target read later would not be the one the user was
    looking at when they pressed the button."""
    store, record, plan_store = video_project((0, "a"), (1, "a"))

    _added, jobs = queue_video(store, record, plan_store, production_mode.LINKED)

    # The gallery is newest-first, so 1_a is above 0_a and the frame after 0_a is 1_a.
    by_id = {job["id"]: job for job in jobs}
    assert by_id["0_a"]["linkedTo"] == "1_a"


def test_the_last_frame_takes_no_linked_job_but_the_rest_do():
    """The frame at the top of the gallery has no next one. Production is not blocked over it: that
    one frame stays out and the rest go in, and fixing the selection is one press away."""
    store, record, plan_store = video_project((0, "a"), (1, "a"))

    added, jobs = queue_video(store, record, plan_store, production_mode.LINKED)

    assert added == 1
    assert [job["id"] for job in jobs] == ["0_a"]


def test_a_linked_batch_with_nowhere_to_end_takes_nothing():
    store, record, plan_store = video_project((0, "a"))

    added, _jobs = queue_video(store, record, plan_store, production_mode.LINKED)

    # Nothing owed and nothing started -- exactly what an empty scope already answers.
    assert added == 0
    assert plan_store.appended == []


def test_a_sound_job_carries_no_mode_at_all():
    """A sound is laid over the whole of a video and arrives nowhere. Writing "standard" on its line
    would be a field claiming an answer to a question the layer never asks."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.AUDIO)

    assert "mode" not in plan_store.appended[-1][0]


def test_a_mode_nobody_knows_is_refused():
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(InvalidMode):
        queue_video(store, record, plan_store, "kelebek")


def test_a_sound_cannot_be_asked_to_end_anywhere():
    # Only a video ends on a picture. Ignoring the argument would hide the caller's mistake behind
    # a sound that came out fine.
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(InvalidMode):
        queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                    {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.AUDIO,
                    mode=production_mode.LOOP)


def render_one_video(mode, linked_to=None, gallery=((0, "a"), (1, "a")), photos=("0_a", "1_a")):
    """One video job, planned by hand with the mode already on it, run to completion.

    Planned by hand rather than through queue_layer: what is under test here is the engine reading
    a mode, and going through the queue would make one test answer for two rules at once.
    """
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(number) for number, _letter in gallery])
    for fid in photos:
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        store.files[f"{fid}.png"] = f"{fid} bytes".encode()
    job = {"id": "0_a", "type": "video", "number": 0, "variant": 0, "prompt": "p", "negative": "",
           "seed": None, "model": "", "mode": mode}
    if linked_to is not None:
        job["linkedTo"] = linked_to
    plan_store.append("düğün", [job])
    generator = FakeGenerator()
    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
             lambda: "t", "düğün")()
    return generator, record


def test_a_plain_video_is_produced_with_no_ending_frame():
    generator, _record = render_one_video(production_mode.STANDARD)

    assert generator.ends == [None]


def test_a_loop_video_ends_on_its_own_picture():
    """A loop is a video that arrives where it started, so the ending picture is the frame's own --
    the very file it is being made from."""
    generator, _record = render_one_video(production_mode.LOOP)

    assert generator.ends == [("0_a.png", b"0_a bytes")]
    assert generator.sources == [("0_a.png", b"0_a bytes")]


def test_a_linked_video_ends_on_the_next_frames_picture():
    generator, _record = render_one_video(production_mode.LINKED, linked_to="1_a")

    assert generator.sources == [("0_a.png", b"0_a bytes")]
    assert generator.ends == [("1_a.png", b"1_a bytes")]


def test_a_linked_video_whose_target_lost_its_photo_turns_that_frame_red():
    """The frame it was told to end on is gone -- deleted between the press and the render. One
    frame's trouble, so the tile turns red and the queue goes on; falling back to a plain video
    would hand the user something other than what they asked for and say nothing about it."""
    # The gallery holds one frame and the job still points at 1_a: that is what deletion leaves
    # behind. A gallery that still listed 1_a would leave its own photo job owed, and the run would
    # stop waiting for a photo producer this test does not have -- the video would never be reached.
    generator, record = render_one_video(production_mode.LINKED, linked_to="1_a",
                                         gallery=((0, "a"),), photos=("0_a",))

    assert generator.ends == []          # nothing was ever rendered for this job
    video = record.slots("düğün")["0_a"]["video"]
    assert video["status"] == queue.FAILED


def test_a_video_job_is_planned_for_every_frame_that_has_none():
    store, record, plan_store = video_project((0, "a"), (1, "a"))

    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                         {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO)

    assert added == 2
    planned = [(job["id"], job["type"]) for job in plan_store.appended[-1]]
    assert planned == [("0_a", "video"), ("1_a", "video")]


def test_a_layer_job_is_planned_with_no_seed_of_its_own():
    """Only a photo is made from a prompt and a seed; a layer is made from what is under it. The
    producer contract runs against this, so the two must not drift apart."""
    store, record, plan_store = video_project((0, "a"))

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO)

    assert plan_store.appended[-1][0]["seed"] is None


def settled_slot_project(layer, status):
    """A frame with a photo and a video, and a `layer` slot whose last line settled it.

    This is what emptying the queue leaves behind: nothing was produced, but the slot has been
    written about, and a written slot is closed for good unless something reopens it.
    """
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0)])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    store.files["0_a.png"] = b"PNGDATA"
    store.files["0_a_V1_0.mp4"] = b"MP4DATA"
    record.mark("düğün", "0_a", layer, "0_a.png", status, "t")
    return store, record, plan_store


def ask_again(store, record, plan_store, layer, generator, files=None):
    return queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                       {layer: generator}, lambda: "t", "düğün", layer, files=files)


def test_a_sound_pulled_out_of_the_queue_can_be_asked_for_again():
    """2026-08-14: the queue was emptied and sound could never be queued again. Emptying writes
    removed on the slot, a written slot is settled, and queue_layer appended a job nobody could
    see -- the run ended having found nothing and reported the previous batch's total."""
    store, record, plan_store = settled_slot_project(layers.AUDIO, queue.REMOVED)
    generator = FakeGenerator()

    added = ask_again(store, record, plan_store, layers.AUDIO, generator)

    assert added == 1
    # Not the plan's contents: whether the sound was actually made.
    assert len(generator.calls) == 1
    assert [name for name, _data in store.saved] == ["0_a_V1_0_S1_0.wav"]


def test_a_video_pulled_out_of_the_queue_can_be_asked_for_again():
    """The hole is not the sound layer's: every layer is closed by the same rule."""
    store, record, plan_store = settled_slot_project(layers.VIDEO, queue.REMOVED)
    generator = FakeGenerator()

    ask_again(store, record, plan_store, layers.VIDEO, generator)

    assert len(generator.calls) == 1


def test_a_deleted_layer_can_be_asked_for_again():
    """A deleted layer frees its slot without putting the frame back in line -- which is right, and
    is also why asking for it again has to do the putting back."""
    store, record, plan_store = settled_slot_project(layers.AUDIO, queue.DELETED)
    generator = FakeGenerator()

    ask_again(store, record, plan_store, layers.AUDIO, generator)

    assert len(generator.calls) == 1


def test_reopening_a_settled_slot_is_written_down():
    """queued is the one written status that reopens a job, so the reopening is a line in the log
    rather than an assumption. Without this the hole could be closed by loosening is_open instead,
    and the queue's single rule would live in two places."""
    store, record, plan_store = settled_slot_project(layers.AUDIO, queue.REMOVED)

    ask_again(store, record, plan_store, layers.AUDIO, FakeGenerator())

    said = [row["status"] for row in record.rows if row.get("layer") == "audio"]
    assert queue.QUEUED in said
    assert said.index(queue.QUEUED) > said.index(queue.REMOVED)


def test_a_failed_layer_stays_out_of_the_scope_nobody_picked():
    """A guard, not a hole: a failed slot counts as taken, so the frame leaves the panel's own
    scope and is rescued by Tekrar dene alone -- one frame never gets two ways to be produced at
    once. Reopening settled slots must not drag failed ones back in."""
    store, record, plan_store = settled_slot_project(layers.AUDIO, queue.FAILED)
    generator = FakeGenerator()

    added = ask_again(store, record, plan_store, layers.AUDIO, generator)

    assert added == 0
    assert generator.calls == []


def test_a_failed_layer_picked_by_hand_becomes_a_frame_of_its_own():
    """The other guard: picking the frame says these ones, and asking for a layer it already holds
    is asking for a second one -- which is born as a copy frame (madde 25), never written over the
    first. This path works today and must keep working."""
    store, record, plan_store = settled_slot_project(layers.AUDIO, queue.FAILED)
    generator = FakeGenerator()

    ask_again(store, record, plan_store, layers.AUDIO, generator, files=["0_a.png"])

    assert len(generator.calls) == 1
    # The new identity is the frame's, not the file's: a sound is named after the video it sits on,
    # and the copy carries its source's video -- so the name is no way to tell the two apart.
    made = [row for row in record.rows
            if row.get("layer") == "audio" and row.get("status") == "done"]
    assert len(made) == 1
    assert made[0]["frame"] != "0_a"


def test_a_frame_that_already_has_a_video_is_out_of_scope():
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                         {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO)

    assert added == 1
    assert [job["id"] for job in plan_store.appended[-1]] == ["1_a"]


def test_a_selection_narrows_the_scope_to_itself():
    store, record, plan_store = video_project((0, "a"), (1, "a"))

    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                         {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO,
                         files=["1_a.png"])

    assert added == 1
    assert [job["id"] for job in plan_store.appended[-1]] == ["1_a"]


def test_a_selected_frame_that_has_a_video_is_still_in_scope():
    # "These ones" is the user's own word: madde 25's copies have no other way in.
    gallery = [{"id": "0_a", "file": "0_a.png", "status": "done",
                "layers": {"video": "0_a_V1_0.mp4"}},
               {"id": "1_a", "file": "1_a.png", "status": "done", "layers": {}}]

    assert [f["id"] for f in frames_in_scope(gallery, layers.VIDEO, ["0_a.png"])] == ["0_a"]
    # The panel's row is called "Videosu olmayanlar": with no selection it means exactly that.
    assert [f["id"] for f in frames_in_scope(gallery, layers.VIDEO)] == ["1_a"]


def test_a_frame_whose_name_claims_no_number_takes_no_video():
    # Its job could not be stored: the plan keeps a number per job and reads back only the jobs that
    # have one, so the video would quietly vanish instead of being made.
    gallery = [{"id": "kapak", "file": "kapak.png", "status": "done", "layers": {}}]

    assert frames_in_scope(gallery, layers.VIDEO, ["kapak.png"]) == []


def test_audio_skips_a_frame_that_has_no_video():
    # Sound is mixed over a video: a frame without one is never in its scope (madde 31).
    gallery = [{"id": "0_a", "file": "0_a.png", "status": "done", "layers": {}, "failed": []},
               {"id": "1_a", "file": "1_a.png", "status": "done",
                "layers": {"video": "1_a_V1_0.mp4"}, "failed": []}]

    assert [f["id"] for f in frames_in_scope(gallery, layers.AUDIO)] == ["1_a"]
    # Even when it is picked by hand: there is nothing to lay the sound over.
    assert frames_in_scope(gallery, layers.AUDIO, ["0_a.png"]) == []


def test_audio_skips_a_video_that_blew_up():
    gallery = [{"id": "0_a", "file": "0_a.png", "status": "done",
                "layers": {"video": "0_a_V1_0.mp4"}, "failed": ["video"]}]

    assert frames_in_scope(gallery, layers.AUDIO) == []


def test_an_audio_job_is_planned_for_a_frame_with_a_video():
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                        {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.AUDIO)

    assert added == 1
    job = plan_store.appended[-1][0]
    assert (job["id"], job["type"]) == ("0_a", "audio")


def test_a_sound_copy_carries_the_photo_and_the_video():
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.AUDIO, variants=2)

    copy = record.slots("düğün")["P0_1"]
    assert copy["photo"]["file"] == "0_a.png"
    assert copy["video"]["file"] == "0_a_V1_0.mp4"
    # And the words each of them was made from come with them.
    assert record.prompts("düğün")["P0_1"] == {"photo": "p", "video": "kadın dönüyor"}


def test_a_video_copy_still_carries_only_the_photo():
    store, record, plan_store = video_project((0, "a"))

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO, variants=2)

    assert list(record.slots("düğün")["P0_1"]) == ["photo"]


def test_a_frame_whose_photo_has_not_landed_is_skipped():
    # There is nothing to hang a video on yet.
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0)])

    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                         {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO)

    assert added == 0
    assert plan_store.appended == []


def test_one_variant_hangs_the_video_on_the_frame_itself():
    store, record, plan_store = video_project((0, "a"))

    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                         {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO,
                         variants=1)

    assert added == 1
    assert [job["id"] for job in plan_store.appended[-1]] == ["0_a"]
    assert photo_statuses(record) == {"0_a": "done"}      # no copy was born


def test_the_variants_past_the_first_are_born_as_copy_frames():
    store, record, plan_store = video_project((0, "a"))

    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                         {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO,
                         variants=3)

    assert added == 3
    assert [job["id"] for job in plan_store.appended[-1]] == ["0_a", "P0_1", "P0_2"]


def test_a_copy_points_at_its_sources_own_photo():
    store, record, plan_store = video_project((0, "a"))

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO, variants=2)

    copy = record.slots("düğün")["P0_1"]
    assert copy["photo"] == {"status": "done", "file": "0_a.png"}
    # Only a photo: a video variant carries no audio (madde 102), and its own video is still owed.
    assert list(copy) == ["photo"]


def test_every_variant_of_a_frame_that_has_a_video_is_a_copy():
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    added = queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                         {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO,
                         files=["0_a.png"], variants=2)

    assert added == 2
    assert [job["id"] for job in plan_store.appended[-1]] == ["P0_1", "P0_2"]


def test_a_copy_frame_carries_its_sources_prompt():
    store, record, plan_store = video_project((0, "a"))

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO, variants=2)

    born = [row for row in record.rows if row["frame"] == "P0_1"][0]
    assert born["prompt"] == "p"                 # the source's own, from the plan's photo job
    assert born["createdAt"] == "t"


def test_a_video_job_says_which_number_and_variant_it_belongs_to():
    # The plan drops a job whose number is not a number, so a copy's job has to carry its own.
    store, record, plan_store = video_project((0, "a"))

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO, variants=2)

    jobs = {job["id"]: job for job in plan_store.appended[-1]}
    assert (jobs["0_a"]["number"], jobs["0_a"]["variant"]) == (0, 0)
    assert (jobs["P0_1"]["number"], jobs["P0_1"]["variant"]) == (0, 1)


def test_a_copy_takes_its_place_right_above_its_source():
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    order = FakeOrderStore()

    queue_layer(sync_runner(), store, record, plan_store, order,
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO,
                 files=["0_a.png"], variants=3)

    # The whole gallery is written down, newest first, with the copies hanging above their source.
    assert order.order == ["1_a", "P0_2", "P0_1", "0_a"]


def test_the_gallery_draws_the_copy_next_to_its_source():
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    order = FakeOrderStore()

    queue_layer(sync_runner(), store, record, plan_store, order,
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO,
                 files=["0_a.png"], variants=2)

    frames = list_frames(record, store, plan_store, order, "düğün")
    assert [f["id"] for f in frames] == ["1_a", "P0_1", "0_a"]
    assert [f["file"] for f in frames] == ["1_a.png", "0_a.png", "0_a.png"]


def test_nothing_is_written_to_the_order_file_when_no_copy_is_born():
    store, record, plan_store = video_project((0, "a"))
    order = FakeOrderStore()

    queue_layer(sync_runner(), store, record, plan_store, order,
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO, variants=1)

    assert order.order == []


def test_the_video_variant_count_has_the_same_ceiling_as_a_photo_batch():
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(InvalidVariants):
        queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                     {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.VIDEO, variants=27)
    assert plan_store.appended == []


def test_an_empty_scope_starts_nothing():
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    runner = sync_runner()

    assert queue_layer(runner, store, record, plan_store, FakeOrderStore(),
                        {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün",
                        layers.VIDEO) == 0
    assert runner.status()["status"] == "idle"


def test_regenerating_with_the_same_prompt_stays_in_the_family():
    store, record, plan_store = video_project((0, "a"))

    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", "0_a", layers.PHOTO, "p")

    assert born == "P0_1"
    job = plan_store.appended[-1][0]
    assert (job["type"], job["prompt"], job["seed"]) == ("photo", "p", 7)


def test_a_changed_prompt_takes_the_next_prompt_number():
    store, record, plan_store = video_project((0, "a"))

    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", "0_a", layers.PHOTO, "başka bir şey")

    assert born == "P1_0"


def test_only_the_words_count_as_a_change():
    # Space around the text is not an edit: it would name a whole new prompt for nothing.
    store, record, plan_store = video_project((0, "a"))

    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", "0_a", layers.PHOTO, "  p\n")

    assert born == "P0_1"


def test_the_new_frame_stands_next_to_its_source():
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    order = FakeOrderStore()

    regenerate(sync_runner(), store, record, plan_store, order,
               {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
               "düğün", "0_a", layers.PHOTO, "p")

    assert order.order == ["1_a", "P0_1", "0_a"]


def test_a_frame_made_again_is_produced_under_its_own_name():
    store, record, plan_store = video_project((0, "a"))

    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", "0_a", layers.PHOTO, "p")

    assert [name for name, _data in store.saved] == ["P0_1.png"]
    # The source is left exactly as it was: "üret = ekle" holds here too (madde 77).
    assert record.slots("düğün")["0_a"]["photo"] == {"status": "done", "file": "0_a.png"}
    assert record.prompts("düğün")[born] == {"photo": "p"}


def test_regenerating_a_video_gives_the_new_frame_the_sources_photo():
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", "0_a", layers.VIDEO, "kadın dönüyor")

    assert record.slots("düğün")[born]["photo"]["file"] == "0_a.png"
    # Nothing above the layer being made comes along, and the source keeps its own video.
    assert list(record.slots("düğün")[born]) == ["photo"]
    assert record.slots("düğün")["0_a"]["video"]["status"] == "done"


def test_regenerating_a_sound_carries_the_photo_and_the_video():
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})
    record.append("düğün", {"file": "0_a_V1_0_S1_0.wav", "frame": "0_a", "layer": "audio",
                            "status": "done", "prompt": "kalabalık"})

    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", "0_a", layers.AUDIO, "kalabalık")

    copy = record.slots("düğün")[born]
    assert copy["photo"]["file"] == "0_a.png"
    assert copy["video"]["file"] == "0_a_V1_0.mp4"
    assert "audio" not in copy               # the layer being made is the one it is missing


def test_a_layer_made_again_is_planned_with_no_seed_of_its_own():
    # Only a photo is made from a prompt and a seed; the others are made from what is under them.
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
               {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
               "düğün", "0_a", layers.VIDEO, "kadın yürüyor")

    job = plan_store.appended[-1][0]
    assert (job["type"], job["prompt"], job["seed"]) == ("video", "kadın yürüyor", None)
    assert (job["number"], job["variant"]) == (1, 0)


def test_a_layer_the_frame_cannot_carry_is_refused():
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(LayerMissing):
        regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                   {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                   "düğün", "0_a", layers.AUDIO, "ses")
    assert plan_store.appended == []


def test_a_copy_frame_is_made_again_from_its_own_layer():
    # It shares its source's picture, so only the identity says which of the two was asked for.
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a.png", "frame": "P0_1", "layer": "photo", "status": "done",
                            "prompt": "p"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "P0_1", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", "P0_1", layers.VIDEO, "kadın dönüyor")

    assert born == "P0_2"
    # Born from the copy: it carries the picture the copy holds, and the source keeps its video.
    assert record.slots("düğün")[born]["photo"]["file"] == "0_a.png"
    assert "video" not in record.slots("düğün")["0_a"]


def test_regenerating_a_frame_the_gallery_does_not_know_is_refused():
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(FrameMissing):
        regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                   {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                   "düğün", "yok", layers.PHOTO, "p")


def layered_project(audio=True):
    """A produced frame that carries a photo, a video and (by default) a sound."""
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})
    if audio:
        record.append("düğün", {"file": "0_a_V1_0_S1_0.wav", "frame": "0_a", "layer": "audio",
                                "status": "done", "prompt": "kumaş"})
    return store, record, plan_store


def test_deleting_a_video_takes_the_sound_over_it():
    store, record, plan_store = layered_project()

    gone = remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                        "düğün", "0_a", layers.VIDEO)

    assert gone == {"deleted": ["0_a_V1_0.mp4", "0_a_V1_0_S1_0.wav"]}
    assert sorted(store.deleted) == ["0_a_V1_0.mp4", "0_a_V1_0_S1_0.wav"]
    # The frame keeps its place and its picture.
    assert record.slots("düğün")["0_a"]["photo"]["status"] == "done"
    assert record.slots("düğün")["0_a"]["video"]["status"] == "deleted"
    assert record.slots("düğün")["0_a"]["audio"]["status"] == "deleted"


def test_deleting_a_sound_leaves_the_video_alone():
    store, record, plan_store = layered_project()

    remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                 "düğün", "0_a", layers.AUDIO)

    assert store.deleted == ["0_a_V1_0_S1_0.wav"]
    assert record.slots("düğün")["0_a"]["video"]["status"] == "done"


def test_a_layer_the_frame_does_not_carry_costs_nothing():
    store, record, plan_store = layered_project(audio=False)

    assert remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                        "düğün", "0_a", layers.AUDIO) == {"deleted": []}
    assert store.deleted == []


def with_a_copy(record):
    """A second frame holding the same picture and the same video (madde 102)."""
    record.append("düğün", {"file": "0_a.png", "frame": "P0_1", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "P0_1", "layer": "video",
                            "status": "done"})


def test_a_file_another_frame_still_holds_is_left_on_disk_when_a_layer_goes():
    store, record, plan_store = layered_project(audio=False)
    with_a_copy(record)

    remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                 "düğün", "0_a", layers.VIDEO)

    assert store.deleted == []
    assert record.slots("düğün")["P0_1"]["video"]["status"] == "done"


def test_the_copy_is_the_one_that_loses_its_layer_when_the_copy_is_named():
    # One file name, two frames: only the identity says which of them is being asked about.
    store, record, plan_store = layered_project(audio=False)
    with_a_copy(record)

    remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                 "düğün", "P0_1", layers.VIDEO)

    assert record.slots("düğün")["P0_1"]["video"]["status"] == "deleted"
    assert record.slots("düğün")["0_a"]["video"]["status"] == "done"


def test_a_job_still_owed_above_the_deleted_layer_leaves_the_queue():
    # Its video is gone, so the sound that was coming has nothing to lie over.
    store, record, plan_store = layered_project(audio=False)
    plan_store.append("düğün", [{"id": "0_a", "type": "audio", "number": 0, "variant": 0,
                                 "prompt": "", "negative": "", "seed": None, "model": ""}])

    remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                 "düğün", "0_a", layers.VIDEO)

    assert record.slots("düğün")["0_a"]["audio"]["status"] == "removed"
    assert owed_files(record, plan_store) == []


def test_deleting_a_layer_of_a_frame_the_gallery_does_not_know_is_refused():
    store, record, plan_store = layered_project()

    with pytest.raises(FrameMissing):
        remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                     "düğün", "yok", layers.VIDEO)


def test_the_gallery_stops_reporting_a_deleted_layer():
    store, record, plan_store = layered_project()

    remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                 "düğün", "0_a", layers.VIDEO)

    frame = list_frames(record, store, plan_store, FakeOrderStore(), "düğün")[0]
    assert frame["layers"] == {"photo": "0_a.png"}
    assert frame["status"] == "done"


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
                           ["0_a", "2_a"])

    assert result == {"deleted": ["0_a", "2_a"], "removed": []}
    assert store.deleted == ["0_a.png", "2_a.png"]
    assert [row["file"] for row in record.list("düğün")] == ["1_a.png"]
    assert order.order == ["1_a"]


def test_a_frame_that_was_never_produced_only_leaves_the_queue():
    store, record = FakeStore(), FakeRecord()
    plan_store = planned((0, "a", "a"), (1, "a", "b"))

    result = remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün",
                           ["1_a"])

    assert result == {"deleted": [], "removed": ["1_a"]}
    assert store.deleted == []                       # there is no file to delete yet
    assert owed_files(record, plan_store) == ["0_a.png"]


def test_a_failed_frame_leaves_the_gallery_the_same_way():
    store, record = FakeStore(), FakeRecord()
    record.mark("düğün", "1_a", "photo", "1_a.png", "failed", "t1")
    plan_store = planned((0, "a", "a"), (1, "a", "b"))

    result = remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün",
                           ["1_a"])

    assert result == {"deleted": [], "removed": ["1_a"]}
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
                           ["0_a"])

    assert result == {"deleted": ["0_a"], "removed": []}
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

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a"])

    # Its own picture goes; the video the other frame still plays stays.
    assert store.deleted == ["0_a.png"]


def test_the_last_holder_takes_the_shared_file_with_it():
    store, record = FakeStore(), FakeRecord()
    plan_store = shared_video_pair(record)

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün",
                  ["0_a", "1_a"])

    assert sorted(store.deleted) == ["0_a.png", "0_a_v0.mp4", "1_a.png"]


def test_deleting_a_frame_whose_video_failed_unlinks_what_is_there():
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_v0.mp4", "failed", "t2", error="ComfyUI 500")
    plan_store = planned((0, "a", "a"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a"])

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

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a"])

    assert record.slots("düğün")["0_a"] == {
        "photo": {"status": "deleted", "file": "0_a.png"},
        "video": {"status": "deleted", "file": "0_a_v0.mp4"}}
    assert sorted(store.deleted) == ["0_a.png", "0_a_v0.mp4"]


def test_a_deleted_photo_still_never_returns_to_the_queue():
    # v4's guard: a free slot is not a debt. If the layer rule leaks into the queue, this goes red.
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    plan_store = planned((0, "a", "a"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a"])

    assert owed_files(record, plan_store) == []


def test_a_frame_pulled_out_never_gets_its_number_back():
    store, record = FakeStore(next_no=0), FakeRecord()
    plan_store = planned((0, "a", "a"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a"])

    assert next_number(store, plan_store, record, "düğün") == 1


def test_a_name_the_gallery_does_not_know_is_skipped_not_refused():
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})

    result = remove_frames(record, store, FakePlanStore(), FakeOrderStore(), stamped, "düğün",
                           ["hayalet", "0_a"])

    assert result == {"deleted": ["0_a"], "removed": []}
    assert store.deleted == ["0_a.png"]


def test_removing_takes_the_named_frame_not_the_one_sharing_its_picture():
    store, record, plan_store = layered_project(audio=False)
    with_a_copy(record)

    gone = remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["P0_1"])

    assert gone == {"deleted": ["P0_1"], "removed": []}
    # Nothing left the disk: every file the copy held is its source's too (madde 101).
    assert store.deleted == []
    assert record.slots("düğün")["0_a"]["photo"]["status"] == "done"
    assert record.slots("düğün")["P0_1"]["photo"]["status"] == "deleted"


def test_a_body_that_is_not_a_list_of_names_is_rejected():
    with pytest.raises(InvalidFiles):
        remove_frames(FakeRecord(), FakeStore(), FakePlanStore(), FakeOrderStore(), stamped,
                      "düğün", "0_a.png")


def test_removing_in_a_missing_project_is_rejected():
    with pytest.raises(ProjectMissing):
        remove_frames(FakeRecord(), FakeStore(projects=()), FakePlanStore(), FakeOrderStore(),
                      stamped, "yok", ["0_a"])


def test_the_summary_counts_the_videos_with_no_sound():
    store, record, plan_store = layered_project(audio=False)

    assert export_summary(record, store, plan_store, FakeOrderStore(), lambda: 5,"düğün")["silent"] == 1


def test_a_video_with_a_sound_is_not_silent():
    store, record, plan_store = layered_project()

    assert export_summary(record, store, plan_store, FakeOrderStore(), lambda: 5,"düğün")["silent"] == 0


def test_a_sound_that_blew_up_leaves_the_video_silent():
    store, record, plan_store = layered_project(audio=False)
    record.mark("düğün", "0_a", "audio", "0_a_V1_0_S1_0.wav", "failed", "t")

    assert export_summary(record, store, plan_store, FakeOrderStore(), lambda: 5,"düğün")["silent"] == 1


def test_the_summary_counts_the_frames_that_have_no_video():
    # A produced photo without a video and a frame that is not even a photo yet: neither is in the
    # sequence, and both are worth saying.
    store, record, plan_store = layered_project(audio=False)
    record.append("düğün", {"file": "1_a.png", "frame": "1_a", "layer": "photo", "status": "done"})
    plan_store.append("düğün", [{"id": "2_a", "type": "photo", "number": 2, "variant": 0,
                                 "prompt": "p", "negative": "", "seed": 1, "model": ""}])

    assert export_summary(record, store, plan_store, FakeOrderStore(), lambda: 5,
                          "düğün")["withoutVideo"] == 2


def test_the_summary_rejects_a_missing_project():
    with pytest.raises(ProjectMissing):
        export_summary(FakeRecord(), FakeStore(projects=()), FakePlanStore(), FakeOrderStore(),
                       lambda: 5, "yok")


def test_get_status_passes_the_runner_state_through():
    assert get_status(PhotoRunner()) == {"status": "idle"}


def test_the_plan_is_appended_before_the_first_frame_renders():
    plan_store, runner = FakePlanStore(), sync_runner()

    class ChecksThePlan:
        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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


def test_a_failed_render_says_how_many_times_it_was_tried():
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0)])

    run_batch(sync_runner(), store, FakeGenerator(fail_on=["p"]), record=record,
              plan_store=plan_store, text='["p"]', variants=1)

    row = [r for r in record.rows if r.get("status") == "failed"][0]
    assert row["error"] == "node 41: p — 3 kez denendi"


def test_a_frame_carries_the_reason_each_layer_failed():
    record = FakeRecord()
    record.mark("düğün", "0_a", "photo", "0_a.png", "failed", "t", error="CUDA — 3 kez denendi")

    frames = list_frames(record, FakeStore(), FakePlanStore(frames=[frame(0)]),
                         FakeOrderStore(), "düğün")

    assert frames[0]["errors"] == {"photo": "CUDA — 3 kez denendi"}


def test_a_frame_that_did_not_fail_carries_no_reason():
    store, record, plan_store = video_project((0, "a"))

    frames = list_frames(record, store, plan_store, FakeOrderStore(), "düğün")

    assert frames[0]["errors"] == {}


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

    def spy(prompt, negative, seed, model="", source=None, end=None):
        seen.append(prompt)
        if prompt == "ilk":
            plan_store.append("düğün", [{"number": 9, "letter": "a", "prompt": "sonradan",
                                         "negative": "", "seed": 7, "model": ""}])
        return rendering(prompt, negative, seed, model, source, end)

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
                lambda: "t2", "düğün", "P0_0")

    assert record.statuses("düğün") == {"P0_0": "done"}


def test_retry_puts_the_frames_failed_layer_back_rather_than_its_photo():
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", "failed", "t", error="node 41")
    plan_store = FakePlanStore(frames=[
        frame(0),
        {"id": "0_a", "type": "video", "number": 0, "prompt": "", "negative": "", "seed": None,
         "model": ""},
    ])

    retry_frame(sync_runner(), store, record, plan_store, {}, lambda: "t", "düğün", "0_a")

    cells = record.slots("düğün")["0_a"]
    assert cells["video"] == {"status": "queued", "file": "0_a_V1_0.mp4"}
    # The photo is untouched: retrying a layer does not re-render the picture under it.
    assert cells["photo"]["status"] == "done"


def test_retry_of_a_frame_with_nothing_red_still_asks_for_its_photo():
    # A deleted photo the user wants back: no layer is failed, and the photo is what is missing.
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "t")
    plan_store = FakePlanStore(frames=[frame(0)])

    retry_frame(sync_runner(), store, record, plan_store, {layers.PHOTO: FakeGenerator()},
                lambda: "t", "düğün", "0_a")

    assert record.slots("düğün")["0_a"]["photo"]["status"] == "done"   # produced again


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
                lambda: "t2", "düğün", "0_a")

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


def test_a_job_whose_type_has_no_producer_makes_the_run_wait():
    # Never silently skipped: skipping would drop work the user asked for. And not an error either
    # -- nothing failed, the engine for it is simply not installed yet.
    plan_store = FakePlanStore(frames=[{"id": "P0_0", "type": "video", "number": 0, "variant": 0,
                                        "prompt": "", "seed": 1}])
    state = make_job(sync_runner(), FakeStore(), FakeRecord(), plan_store,
                     {layers.PHOTO: FakeGenerator()}, lambda: "t1", "düğün")()

    assert state["status"] == "waiting" and state["waitingFor"] == "video"


def test_the_loop_finishes_photos_before_it_starts_videos():
    record, store = FakeRecord(), FakeStore()
    plan_store = FakePlanStore(frames=[
        {"id": "P0_0", "type": "video", "number": 0, "variant": 0, "prompt": "v", "seed": 1},
        {"id": "P1_0", "type": "photo", "number": 1, "variant": 0, "prompt": "f", "seed": 2},
    ])

    class Records:
        def __init__(self, kind):
            self.kind = kind

        def generate(self, prompt, negative, seed, model="", source=None, end=None):
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
