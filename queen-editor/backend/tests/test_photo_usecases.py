import pytest

from backend.features.photo_generation.domain.prompt_list import InvalidPrompts
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.list_photos import list_photos
from backend.features.photo_generation.domain.usecases.start_batch import (
    Busy,
    InvalidVariants,
    ProjectMissing,
    plan_frames,
    start_batch,
)
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
from backend.features.photo_generation.runner import PhotoRunner


class FakeStore:
    def __init__(self, projects=("düğün",), next_no=0):
        self.projects = list(projects)
        self.next_no = next_no
        self.saved = []

    def project_exists(self, project):
        return project in self.projects

    def next_number(self, project):
        return self.next_no

    def save(self, project, number, letter, data):
        self.saved.append((number, letter, data))
        return f"{number}_{letter}.png"

    def photo_dir(self, project):
        return f"/fake/{project}"


class FakeGenerator:
    """Records what each frame asked for. Failure cases use their own purpose-built fakes."""

    def __init__(self):
        self.calls = []

    def generate(self, prompt, negative, seed):
        self.calls.append((prompt, negative, seed))
        return b"PNG"


class FakePlanStore:
    def __init__(self, reserved=None):
        self.reserved = reserved          # highest number an earlier plan reserved, or None
        self.written = None               # (negative, frames) of the last write

    def write(self, project, negative, frames):
        self.written = (negative, frames)

    def max_number(self, project):
        return self.reserved


class FakeRecord:
    def __init__(self):
        self.rows = []

    def append(self, project, entry):
        self.rows.append(entry)

    def list(self, project):
        return list(reversed(self.rows))


class Infra(RuntimeError):
    infra = True


def sync_runner():
    return PhotoRunner(spawn=lambda fn: fn())


def run_batch(runner, store, generator, project="düğün", text='["a", "b"]', negative="neg",
              variants=2, seed=42, record=None, plan_store=None):
    return start_batch(runner, store, record or FakeRecord(), plan_store or FakePlanStore(),
                       generator, lambda: seed, lambda: "2026-08-03T14:32:11+00:00",
                       project, text, negative, variants)


def test_plan_frames_is_prompt_major():
    seeds = iter([11, 22, 33, 44])
    assert plan_frames(3, ["ilk", "ikinci"], 2, lambda: next(seeds)) == [
        {"number": 3, "letter": "a", "prompt": "ilk", "seed": 11},
        {"number": 3, "letter": "b", "prompt": "ilk", "seed": 22},
        {"number": 4, "letter": "a", "prompt": "ikinci", "seed": 33},
        {"number": 4, "letter": "b", "prompt": "ikinci", "seed": 44},
    ]


def test_numbering_continues_from_the_store():
    store, generator, runner = FakeStore(next_no=7), FakeGenerator(), sync_runner()
    run_batch(runner, store, generator, text='["a"]', variants=3)
    assert [(n, letter) for n, letter, _d in store.saved] == [(7, "a"), (7, "b"), (7, "c")]


def test_every_frame_gets_prompt_negative_and_a_fresh_seed():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    seeds = iter([11, 22, 33, 44])
    start_batch(runner, store, FakeRecord(), FakePlanStore(), generator, lambda: next(seeds),
                lambda: "2026-08-03T14:32:11+00:00", "düğün", '["a", "b"]', "neg", 2)
    assert generator.calls == [("a", "neg", 11), ("a", "neg", 22),
                               ("b", "neg", 33), ("b", "neg", 44)]


def test_finished_batch_reports_its_counts():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    run_batch(runner, store, generator)
    assert runner.status() == {"status": "done", "project": "düğün",
                               "done": 4, "failed": 0, "total": 4}


def test_progress_is_reported_before_each_frame():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    seen = []
    original = generator.generate

    def spy(prompt, negative, seed):
        seen.append(runner.status())
        return original(prompt, negative, seed)

    generator.generate = spy
    run_batch(runner, store, generator, text='["a"]', variants=2)
    assert seen[0]["current"] == {"number": 0, "letter": "a", "prompt": "a", "seed": 42}
    assert (seen[0]["done"], seen[0]["total"]) == (0, 2)
    assert (seen[1]["done"], seen[1]["total"]) == (1, 2)


def test_a_failed_frame_is_skipped_and_the_batch_continues():
    class FailsFirstFrame:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("node 41: OOM")
            return b"PNG"

    store, runner = FakeStore(), sync_runner()
    run_batch(runner, store, FailsFirstFrame(), text='["a"]', variants=2)
    state = runner.status()
    assert (state["status"], state["done"], state["failed"]) == ("done", 1, 1)
    assert [(n, letter) for n, letter, _d in store.saved] == [(0, "b")]


def test_three_consecutive_failures_stop_the_batch():
    class AlwaysBroken:
        def generate(self, prompt, negative, seed):
            raise RuntimeError("node 41: OOM")

    store, runner = FakeStore(), sync_runner()
    run_batch(runner, store, AlwaysBroken(), text='["a", "b"]', variants=2)
    state = runner.status()
    assert state["status"] == "error"
    assert "Üst üste 3" in state["error"] and "OOM" in state["error"]
    assert (state["done"], state["failed"], state["total"]) == (0, 3, 4)


def test_infra_failure_stops_on_the_first_frame():
    class Broken:
        def generate(self, prompt, negative, seed):
            raise Infra("node 9 (CheckpointLoaderSimple): dosya yok")

    store, runner = FakeStore(), sync_runner()
    run_batch(runner, store, Broken(), text='["a", "b"]', variants=2)
    state = runner.status()
    assert state["status"] == "error" and "Altyapı" in state["error"]
    assert (state["failed"], state["total"]) == (1, 4)


def test_stop_request_ends_the_batch_between_frames():
    store, runner = FakeStore(), sync_runner()

    class StopsAfterFirst:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed):
            self.calls += 1
            runner.request_stop()
            return b"PNG"

    generator = StopsAfterFirst()
    run_batch(runner, store, generator, text='["a", "b"]', variants=2)
    state = runner.status()
    assert (state["status"], state["done"], state["total"]) == ("stopped", 1, 4)
    assert generator.calls == 1


def test_frame_killed_by_user_stop_is_not_a_failure():
    """A render that dies because the user pressed Durdur is 'stopped', never a failure."""
    store, runner = FakeStore(), sync_runner()

    class StoppingGenerator:
        def generate(self, prompt, negative, seed):
            runner.request_stop()          # the user's stop lands mid-render
            raise RuntimeError("interrupted")

    run_batch(runner, store, StoppingGenerator(), text='["a", "b", "c"]', variants=1)
    state = runner.status()
    assert state["status"] == "stopped"
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


def test_busy_runner_is_rejected():
    runner = PhotoRunner(spawn=lambda fn: None)   # stays "running"
    run_batch(runner, FakeStore(), FakeGenerator())
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


def test_list_photos_comes_from_the_record():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "prompt": "a"})
    record.append("düğün", {"file": "0_b.png", "prompt": "a"})
    assert list_photos(record, FakeStore(), "düğün") == [
        {"file": "0_b.png", "prompt": "a"}, {"file": "0_a.png", "prompt": "a"}]


def test_list_photos_rejects_a_missing_project():
    with pytest.raises(ProjectMissing):
        list_photos(FakeRecord(), FakeStore(), "yok")


def test_get_status_passes_the_runner_state_through():
    assert get_status(PhotoRunner()) == {"status": "idle"}


def test_the_plan_is_written_before_the_first_frame_renders():
    plan_store, runner = FakePlanStore(), sync_runner()

    class ChecksThePlan:
        def generate(self, prompt, negative, seed):
            assert plan_store.written is not None, "the batch started before the plan was written"
            return b"PNG"

    run_batch(runner, FakeStore(), ChecksThePlan(), text='["a"]', variants=2,
              plan_store=plan_store)
    negative, frames = plan_store.written
    assert negative == "neg"
    assert frames == [{"number": 0, "letter": "a", "prompt": "a", "seed": 42},
                      {"number": 0, "letter": "b", "prompt": "a", "seed": 42}]


def test_each_produced_photo_gets_a_record_row():
    record = FakeRecord()
    run_batch(sync_runner(), FakeStore(), FakeGenerator(), text='["a"]', variants=2, record=record)
    assert record.rows == [
        {"file": "0_a.png", "prompt": "a", "negative": "neg", "seed": 42,
         "createdAt": "2026-08-03T14:32:11+00:00"},
        {"file": "0_b.png", "prompt": "a", "negative": "neg", "seed": 42,
         "createdAt": "2026-08-03T14:32:11+00:00"},
    ]


def test_a_failed_frame_leaves_no_record_row():
    class FailsFirstFrame:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt, negative, seed):
            self.calls += 1
            if self.calls == 1:
                raise RuntimeError("node 41: OOM")
            return b"PNG"

    record = FakeRecord()
    run_batch(sync_runner(), FakeStore(), FailsFirstFrame(), text='["a"]', variants=2,
              record=record)
    assert [row["file"] for row in record.rows] == ["0_b.png"]


def test_numbering_skips_what_an_unfinished_plan_reserved():
    # Disk stopped at 4 because the run died, but the plan had reserved through 11.
    store = FakeStore(next_no=5)
    run_batch(sync_runner(), store, FakeGenerator(), text='["a"]', variants=1,
              plan_store=FakePlanStore(reserved=11))
    assert [(n, letter) for n, letter, _d in store.saved] == [(12, "a")]


def test_numbering_follows_disk_when_it_is_ahead_of_the_plan():
    store = FakeStore(next_no=20)
    run_batch(sync_runner(), store, FakeGenerator(), text='["a"]', variants=1,
              plan_store=FakePlanStore(reserved=11))
    assert [(n, letter) for n, letter, _d in store.saved] == [(20, "a")]


def test_a_rejected_batch_writes_no_plan():
    plan_store = FakePlanStore()
    with pytest.raises(InvalidPrompts):
        run_batch(sync_runner(), FakeStore(), FakeGenerator(), text="42", plan_store=plan_store)
    assert plan_store.written is None
