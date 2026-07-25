import pytest

from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.start_generation import (
    Busy,
    InvalidPrompt,
    ProjectMissing,
    start_generation,
)
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
        self.saved.append((project, number, letter, data))
        return f"{number}_{letter}.png"

    def photo_dir(self, project):
        return f"/fake/{project}"


class FakeGenerator:
    def __init__(self):
        self.calls = []

    def generate(self, prompt, seed):
        self.calls.append((prompt, seed))
        return b"PNG"


def sync_runner():
    return PhotoRunner(spawn=lambda fn: fn())


def start(runner, store, generator, project="düğün", prompt="kraliçe tahtta", seed=99):
    return start_generation(runner, store, generator, lambda: seed, project, prompt)


def test_generates_and_saves_with_the_next_number():
    store, generator, runner = FakeStore(next_no=3), FakeGenerator(), sync_runner()
    start(runner, store, generator)
    assert generator.calls == [("kraliçe tahtta", 99)]
    assert store.saved == [("düğün", 3, "a", b"PNG")]
    assert runner.status() == {"status": "done", "project": "düğün", "file": "3_a.png"}


@pytest.mark.parametrize("prompt", ["", "   "])
def test_empty_prompt_is_rejected(prompt):
    store, generator = FakeStore(), FakeGenerator()
    with pytest.raises(InvalidPrompt) as exc:
        start(sync_runner(), store, generator, prompt=prompt)
    assert str(exc.value) == "Prompt boş olamaz."
    assert generator.calls == []


def test_missing_project_is_rejected():
    with pytest.raises(ProjectMissing) as exc:
        start(sync_runner(), FakeStore(), FakeGenerator(), project="yok")
    assert str(exc.value) == "Proje yok: yok"


def test_busy_runner_is_rejected():
    runner = PhotoRunner(spawn=lambda fn: None)   # stays "running"
    start(runner, FakeStore(), FakeGenerator())
    with pytest.raises(Busy) as exc:
        start(runner, FakeStore(), FakeGenerator())
    assert str(exc.value) == "Zaten bir üretim sürüyor."


def test_generator_failure_lands_in_the_status():
    class Broken:
        def generate(self, prompt, seed):
            raise RuntimeError("node 41: OOM")

    runner = sync_runner()
    start(runner, FakeStore(), Broken())
    assert runner.status()["error"] == "node 41: OOM"


def test_get_status_passes_the_runner_state_through():
    assert get_status(PhotoRunner()) == {"status": "idle"}
