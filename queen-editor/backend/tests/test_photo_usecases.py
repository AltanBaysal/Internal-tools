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
    def __init__(self, projects=("düğün",), next_no=0, photos=()):
        self.projects = list(projects)
        self.next_no = next_no
        self.photos = list(photos)
        self.saved = []

    def project_exists(self, project):
        return project in self.projects

    def next_number(self, project):
        return self.next_no

    def save(self, project, number, letter, data):
        self.saved.append((number, letter, data))
        return f"{number}_{letter}.png"

    def list_photos(self, project):
        return list(self.photos)

    def photo_dir(self, project):
        return f"/fake/{project}"


class FakeGenerator:
    """Records what each frame asked for. Failure cases use their own purpose-built fakes."""

    def __init__(self):
        self.calls = []

    def generate(self, prompt, negative, seed):
        self.calls.append((prompt, negative, seed))
        return b"PNG"


class Infra(RuntimeError):
    infra = True


def sync_runner():
    return PhotoRunner(spawn=lambda fn: fn())


def run_batch(runner, store, generator, project="düğün", text='["a", "b"]', negative="neg",
              variants=2, seed=42):
    return start_batch(runner, store, generator, lambda: seed, project, text, negative, variants)


def test_plan_frames_is_prompt_major():
    assert plan_frames(3, ["ilk", "ikinci"], 2) == [
        (3, "a", "ilk"), (3, "b", "ilk"), (4, "a", "ikinci"), (4, "b", "ikinci")]


def test_numbering_continues_from_the_store():
    store, generator, runner = FakeStore(next_no=7), FakeGenerator(), sync_runner()
    run_batch(runner, store, generator, text='["a"]', variants=3)
    assert [(n, letter) for n, letter, _d in store.saved] == [(7, "a"), (7, "b"), (7, "c")]


def test_every_frame_gets_prompt_negative_and_a_fresh_seed():
    store, generator, runner = FakeStore(), FakeGenerator(), sync_runner()
    seeds = iter([11, 22, 33, 44])
    start_batch(runner, store, generator, lambda: next(seeds), "düğün", '["a", "b"]', "neg", 2)
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
    assert seen[0]["current"] == {"number": 0, "letter": "a", "prompt": "a"}
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
    state = stop_generation(runner)
    assert state["status"] == "running" and runner.stop_requested() is True


def test_stop_generation_when_idle_is_a_no_op():
    assert stop_generation(PhotoRunner()) == {"status": "idle"}


def test_list_photos_passes_the_store_through():
    assert list_photos(FakeStore(photos=["1_a.png", "0_a.png"]), "düğün") == ["1_a.png", "0_a.png"]


def test_list_photos_rejects_a_missing_project():
    with pytest.raises(ProjectMissing):
        list_photos(FakeStore(), "yok")


def test_get_status_passes_the_runner_state_through():
    assert get_status(PhotoRunner()) == {"status": "idle"}
