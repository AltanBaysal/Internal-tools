"""Madde 522: a rename at the same moment as the queue loses no press and empties no prompt.

The user, 30 Ekim -- "bu hatalarıda çöz istersen". Two faults the run found on its way (511's
reviewer, 513's coder): a press whose job was written under the old name and whose claim came after
the move, and a turn whose reads fell on both sides of the move. Each test lets the rename in at
exactly that moment, over a real folder: the name is the whole address, and fakes that ignore it
could not show either.
"""
import threading
from contextlib import contextmanager

import pytest

from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.usecases.follow_rename import follow_rename
from backend.features.photo_generation.domain.usecases.queue_layer import queue_layer
from backend.features.photo_generation.domain.usecases.queue_references import queue_references
from backend.features.photo_generation.domain.usecases.regenerate import regenerate
from backend.features.photo_generation.domain.usecases.resume_batch import resume_batch
from backend.features.photo_generation.domain.usecases.retry_failed import retry_failed
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.features.photo_generation.domain.usecases.start_batch import (
    ProjectMissing,
    start_batch,
)
from backend.features.photo_generation.runner import PhotoRunner
from backend.services.storage.storage import Storage
from backend.tests.test_fix_photo import Project as FixProject
from backend.tests.test_photo_usecases import (
    FakeGenerator,
    FakeOrderStore,
    FakePlanStore,
    FakePool,
    FakeRecord,
    FakeReferenceOrders,
    FakeStore,
    FakeWriter,
    frame,
    run_batch,
)

# How long one party waits for the other to get in: long enough for a step over a temporary folder.
# A rename made to wait for a lock does not finish in it, and the first party goes on.
WINDOW = 0.2


def now():
    return "t"


class Project:
    """düğün on a real folder, with the stores the doors and the loop use, and a rename to nişan
    that can be let in at a chosen moment."""

    def __init__(self, tmp_path):
        (tmp_path / "düğün").mkdir()
        self.root = tmp_path
        self.storage = Storage(str(tmp_path))
        self.store = DrivePhotoStore(self.storage, self.storage)
        self.record = DrivePhotoRecord(self.storage)
        self.plan = DrivePlanStore(self.storage)
        self.thread = None

    def rename(self, runner):
        """Start the rename and give it the window; it may finish, or wait on a lock."""
        if self.thread is None:
            self.thread = threading.Thread(target=lambda: follow_rename(
                runner, self.plan, "düğün", "nişan",
                lambda: self.storage.rename_dir("düğün", "nişan")))
            self.thread.start()
            self.thread.join(WINDOW)

    def renamed(self):
        self.thread.join(5)
        assert not (self.root / "düğün").exists()
        assert (self.root / "nişan").is_dir()

    def owed(self, project):
        return queue.open_jobs(self.plan.read(project)["frames"], self.record.slots(project))


# --- a press as the project is renamed -----------------------------------------------------------

class RenamedBeforeItsClaim(PhotoRunner):
    """A worker whose press is renamed from under it after the job is written, before the claim.
    The run it starts is kept rather than spawned, and run once the rename is over."""

    def __init__(self, project):
        self.runs = []
        super().__init__(spawn=self.runs.append)
        self.project = project

    def start(self, project, job):
        self.project.rename(self)
        return super().start(project, job)


def press(runner, project, generator):
    return start_batch(runner, project.store, project.record, project.plan,
                       {layers.PHOTO: generator}, lambda: 7, now, "düğün", '["ilk"]', "", 1)


def test_a_press_on_an_idle_worker_as_the_project_is_renamed_still_makes_its_job(tmp_path):
    """511's reviewer: the job was written under düğün, the folder moved to nişan, and the claim
    then pointed the worker at düğün -- the run read a folder that was not there and said done,
    and the job stayed owed in nişan with nobody to run it."""
    project = Project(tmp_path)
    runner, generator = RenamedBeforeItsClaim(project), FakeGenerator()

    assert press(runner, project, generator) == 1
    project.renamed()
    for run in runner.runs:
        run()

    assert [prompt for prompt, *_rest in generator.calls] == ["ilk"]
    assert (tmp_path / "nişan" / "P0_0.png").exists()
    assert project.owed("nişan") == []
    assert runner.status()["project"] == "nişan"


def test_a_press_joining_a_run_as_the_project_is_renamed_joins_it(tmp_path):
    """The same moment with the project's run going on: the move carried the run to nişan, and the
    press, still asking for düğün, was told another production holds the worker -- though its job
    was in the run's own queue, and the run may already have looked for the last time."""
    project = Project(tmp_path)
    runner = RenamedBeforeItsClaim(project)
    PhotoRunner.start(runner, "düğün", lambda: {"status": "done"})        # the run going on

    assert press(runner, project, FakeGenerator()) == 1
    project.renamed()

    assert runner.status() == {"status": "running", "project": "nişan"}
    assert len(runner.runs) == 1                                          # no second worker
    assert [job["id"] for job in project.owed("nişan")] == ["P0_0"]


def test_a_press_the_rename_lands_just_before_is_told_the_project_is_gone(tmp_path):
    """The move falls before the press takes the gate: the press looks at the project inside it,
    finds none and says so -- the same answer every door gives a stale tab -- rather than failing on
    a plan file it can no longer write, in the OS's words."""
    project = Project(tmp_path)
    runner = PhotoRunner(spawn=lambda fn: None)
    held = project.plan.held

    def renamed_first(name):
        project.rename(runner)
        return held(name)

    project.plan.held = renamed_first

    with pytest.raises(ProjectMissing):
        press(runner, project, FakeGenerator())
    project.renamed()
    assert runner.status() == {"status": "idle"}
    assert project.owed("nişan") == []


class Gate(FakePlanStore):
    """A plan store that knows whether its gate is held -- the tests below run in one thread."""

    def __init__(self, frames=None):
        super().__init__(frames=frames)
        self.depth = 0

    @contextmanager
    def held(self, project):
        with super().held(project):
            self.depth += 1
            try:
                yield
            finally:
                self.depth -= 1


class Claims(PhotoRunner):
    """Writes down, for each claim or join, whether the plan's gate was held at that moment."""

    def __init__(self, gate):
        super().__init__(spawn=lambda fn: None)
        self.gate = gate
        self.under_gate = []

    def start(self, project, job):
        self.under_gate.append(self.gate.depth > 0)
        return super().start(project, job)


def made_photo(status="done"):
    """0_a's photo in the record with `status`, and its file on disk."""
    store, record = FakeStore(), FakeRecord()
    record.mark("düğün", "0_a", "photo", "0_a.png", status, "t", seen=None)
    store.files["0_a.png"] = b"PNGDATA"
    return store, record


def press_start_batch(runner, gate):
    run_batch(runner, FakeStore(), FakeGenerator(), text='["a"]', variants=1, plan_store=gate)


def press_queue_layer(runner, gate):
    store, record = made_photo()
    queue_layer(runner, store, record, gate, FakeOrderStore(), {}, now, "düğün", layers.VIDEO)


def press_regenerate(runner, gate):
    store, record = made_photo()
    regenerate(runner, store, record, gate, FakeOrderStore(), {}, lambda: 7, now, "düğün", "0_a",
               layers.PHOTO, "p")


def press_queue_references(runner, gate):
    queue_references(runner, FakeStore(), FakeRecord(), gate, FakeOrderStore(), FakePool(),
                     FakeReferenceOrders(), {}, lambda: 7, now, "düğün", '["gotik kız"]', 1)


def press_retry_frame(runner, gate):
    store, record = made_photo(queue.FAILED)
    retry_frame(runner, store, record, gate, {}, now, "düğün", "0_a")


def press_retry_failed(runner, gate):
    store, record = made_photo(queue.FAILED)
    retry_failed(runner, store, record, gate, {}, now, "düğün")


def press_resume_batch(runner, gate):
    resume_batch(runner, FakeStore(), FakeRecord(), gate, {}, now, "düğün")


def press_fix_photo(runner, gate):
    project = FixProject()
    gate.frames, project.plan_store = project.plan_store.frames, gate
    project.fix(project.card("P1_0"), runner=runner)


@pytest.mark.parametrize("door", [press_start_batch, press_queue_layer, press_regenerate,
                                  press_queue_references, press_retry_frame, press_retry_failed,
                                  press_resume_batch, press_fix_photo])
def test_every_door_that_queues_work_claims_the_worker_under_its_gate(door):
    """The gate the rename takes: a door that wrote its job under it and claimed outside it left a
    moment for the move to fall between the two."""
    gate = Gate(frames=[frame(0)])
    runner = Claims(gate)

    door(runner, gate)

    assert runner.under_gate == [True]


# --- a rename between a turn's reads -------------------------------------------------------------

def video_owed(project, written=None):
    """P0_0 with its photo made from "kız yürüyor" and its video owed with no prompt of its own;
    `written` is the prompt a model already wrote for it, if any."""
    project.plan.append("düğün", [
        {"id": "P0_0", "type": "photo", "number": 0, "variant": 0, "prompt": "kız yürüyor",
         "negative": "", "seed": 1, "model": "", "lora": ""},
        {"id": "P0_0", "type": "video", "number": 0, "variant": 0, "prompt": "", "negative": "",
         "seed": None, "model": "", "lora": ""}])
    project.store.save("düğün", "P0_0.png", b"PNGDATA")
    project.record.append("düğün", {"file": "P0_0.png", "frame": "P0_0", "layer": "photo",
                                    "status": "done", "prompt": "kız yürüyor"})
    if written is not None:
        project.record.prompt_written("düğün", "P0_0", "video", "P0_0_V1_0.mp4", written, "t")


def running(project):
    """A worker whose holder names düğün, as a claim leaves it; its run is driven by the test."""
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("düğün", lambda: None)
    return runner


def after_first(obj, method, then):
    """Make `obj.method` call `then` once, right after its first answer."""
    original = getattr(obj, method)

    def hooked(*args, **kwargs):
        answer = original(*args, **kwargs)
        setattr(obj, method, original)
        then()
        return answer

    setattr(obj, method, hooked)


def drive(runner, project, video, writer=None):
    make_job(runner, project.store, project.record, project.plan, {layers.VIDEO: video}, now,
             writers={layers.VIDEO: writer} if writer else None)()
    project.renamed()


def test_a_rename_between_the_source_read_and_the_written_prompt_never_makes_an_empty_prompt(
        tmp_path):
    """513's coder: the picture was read under düğün, the folder moved, the written prompt read
    under düğün came back empty, and the video was made with no prompt into nişan."""
    project = Project(tmp_path)
    video_owed(project, written="kız yavaşça dönüyor")
    runner, video = running(project), FakeGenerator()
    after_first(project.store, "read", lambda: project.rename(runner))

    drive(runner, project, video)

    assert [prompt for prompt, *_rest in video.calls] == ["kız yavaşça dönüyor"]
    assert video.sources == [("P0_0.png", b"PNGDATA")]
    assert (tmp_path / "nişan" / "P0_0_V1_0.mp4").exists()


def test_a_rename_between_the_source_read_and_the_frames_words_never_asks_with_none(tmp_path):
    """The writer's side of the same moment: the frame's words read under düğün after the move came
    back empty, and the model was asked to write a video's prompt from nothing."""
    project = Project(tmp_path)
    video_owed(project)
    runner, video, writer = running(project), FakeGenerator(), FakeWriter()
    after_first(project.store, "read", lambda: project.rename(runner))

    drive(runner, project, video, writer)

    assert writer.calls == [{"photo": "kız yürüyor"}]
    assert [prompt for prompt, *_rest in video.calls] == [writer.answer]


def test_a_rename_between_the_frames_words_and_its_written_prompt_never_asks_again(tmp_path):
    """The turn's choice of what needs a prompt reads the frame's words and the written prompts:
    split by the move, the written one read as missing and the model was asked again."""
    project = Project(tmp_path)
    video_owed(project, written="kız yavaşça dönüyor")
    runner, video, writer = running(project), FakeGenerator(), FakeWriter()
    after_first(project.record, "prompts", lambda: project.rename(runner))

    drive(runner, project, video, writer)

    assert writer.calls == []
    assert [prompt for prompt, *_rest in video.calls] == ["kız yavaşça dönüyor"]
