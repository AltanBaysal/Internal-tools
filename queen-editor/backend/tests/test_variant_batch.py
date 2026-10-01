"""A prompt's variants made in one ComfyUI job (madde 411).

The queue's own fakes come from test_photo_usecases. None of them can make a batch, which is why
every test there still walks the one-by-one path; the producer added here can.
"""
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.usecases.regenerate import regenerate
from backend.features.photo_generation.domain.usecases.resume_batch import resume_batch
from backend.features.photo_generation.domain.usecases.retry_failed import retry_failed
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.features.photo_generation.domain.usecases.start_batch import plan_frames, start_batch
from backend.tests.test_photo_usecases import (
    Clock,
    FakeGenerator,
    FakeOrderStore,
    FakePlanStore,
    FakeRecord,
    FakeStore,
    FrameFault,
    rows_of,
    sync_runner,
    video_project,
    watched,
)

NOW = "2026-10-01T10:00:00+00:00"


class BatchGenerator(FakeGenerator):
    """A photo producer that can make a prompt's variants in one job, on a card that holds `fits`.

    `fail_on` names the prompts whose batch blows up as the frame's fault. `clock` and `seconds` say
    how long a batch works. `stop` is a runner the first batch asks to stop before it falls, the way
    Durdur interrupts ComfyUI mid-render.
    """

    def __init__(self, fits=26, fail_on=(), clock=None, seconds=0.0, stop=None):
        super().__init__(fail_on)
        self.fits, self.clock, self.seconds, self.stop = fits, clock, seconds, stop
        self.asked = []
        self.batches = []

    def fits_batch(self, count):
        self.asked.append(count)
        return count <= self.fits

    def generate_batch(self, prompt, negative, seed, count, model="", lora=""):
        self.batches.append((prompt, negative, seed, count, model, lora))
        if self.clock is not None:
            self.clock.passes(self.seconds)
        if self.stop is not None:
            runner, self.stop = self.stop, None
            runner.request_stop()
            raise RuntimeError("Processing interrupted")
        if prompt in self.fail_on:
            raise FrameFault(f"node 41: {prompt}")
        return [f"{prompt}{index}".encode() for index in range(count)]


def submit(generator, text='["a", "b"]', variants=2, seeds=(11, 22, 33, 44), runner=None,
           store=None, record=None, plan_store=None, order_store=None):
    """Kuyruğa ekle, the way the panel sends it, with these seeds drawn in turn."""
    drawn = iter(seeds)
    return start_batch(runner or sync_runner(), store or FakeStore(), record or FakeRecord(),
                       plan_store or FakePlanStore(), {layers.PHOTO: generator},
                       lambda: next(drawn), lambda: NOW, "düğün", text, "neg", variants,
                       order_store=order_store)


def one_prompt(count, seed=11):
    """A plan holding one prompt's `count` variants, the way plan_frames writes them."""
    return FakePlanStore(frames=plan_frames(0, [{"prompt": "a"}], "neg", count, lambda: seed))


def test_a_prompts_variants_go_to_the_producer_as_one_batch():
    generator = BatchGenerator()

    submit(generator)

    # One graph per prompt, carrying the seed its first variant was planned with.
    assert generator.batches == [("a", "neg", 11, 2, "", ""), ("b", "neg", 33, 2, "", "")]
    assert generator.calls == []


def test_each_variant_lands_under_its_own_name_with_its_own_picture():
    store = FakeStore()

    submit(BatchGenerator(), store=store)

    assert store.saved == [("P0_0.png", b"a0"), ("P0_1.png", b"a1"),
                           ("P1_0.png", b"b0"), ("P1_1.png", b"b1")]


class NotingStore(FakeStore):
    """Drive, writing each file it is handed into a log shared with the record."""

    def __init__(self, said):
        super().__init__()
        self.said = said

    def save(self, project, filename, data):
        self.said.append(f"file {filename}")
        return super().save(project, filename, data)


class NotingRecord(FakeRecord):
    """The record, writing each row it is handed into a log shared with Drive."""

    def __init__(self, said):
        super().__init__()
        self.said = said

    def append(self, project, entry):
        self.said.append(f"row {entry['file']}")
        super().append(project, entry)


def test_each_row_is_written_only_after_its_own_file():
    """A frame is done exactly when its row exists (CODE-STANDARD, Separation of concerns): a batch
    that dies between two files must leave no row naming a picture that is not there."""
    said = []

    submit(BatchGenerator(), text='["a"]', store=NotingStore(said), record=NotingRecord(said))

    assert said == ["file P0_0.png", "row P0_0.png", "file P0_1.png", "row P0_1.png"]


def test_every_variants_row_names_the_seed_its_batch_was_made_with():
    """The batch's variants come from one seed (madde 411, decision 1): the row says the number the
    render was handed, even though it does not make that one picture again on its own."""
    record = FakeRecord()

    submit(BatchGenerator(), record=record)

    assert [(row["frame"], row["seed"]) for row in rows_of(record, "photo")] == [
        ("P0_0", 11), ("P0_1", 11), ("P1_0", 33), ("P1_1", 33)]


def test_each_variants_time_is_its_share_of_the_batch():
    """Decision 3: a picture's time stays comparable with one made alone."""
    clock, record = Clock(), FakeRecord()

    make_job(sync_runner(), FakeStore(), record, one_prompt(4),
             {layers.PHOTO: BatchGenerator(clock=clock, seconds=80.0)}, lambda: NOW, "düğün",
             clock=clock)()

    assert [row["renderSeconds"] for row in rows_of(record, "photo")] == [20.0] * 4


def test_a_prompt_with_one_variant_is_made_as_it_always_was():
    generator = BatchGenerator()

    submit(generator, text='["a"]', variants=1)

    assert generator.calls == [("a", "neg", 11, "")]
    assert generator.batches == [] and generator.asked == []


def test_a_card_that_cannot_hold_the_batch_makes_the_variants_one_by_one():
    generator = BatchGenerator(fits=1)

    submit(generator, text='["a"]', variants=4)

    # Each with its own seed, the way every variant was made before madde 411.
    assert generator.calls == [("a", "neg", 11, ""), ("a", "neg", 22, ""),
                               ("a", "neg", 33, ""), ("a", "neg", 44, "")]
    assert generator.batches == []


def test_a_prompt_the_card_cannot_hold_is_not_batched_once_enough_of_it_is_made():
    """Decision 4 is about the prompt's batch: a card that cannot hold it makes every variant alone,
    not two alone and the rest together once what is left happens to fit."""
    generator = BatchGenerator(fits=2)

    submit(generator, text='["a"]', variants=3, seeds=(11, 22, 33))

    assert len(generator.calls) == 3 and generator.batches == []
    assert generator.asked and set(generator.asked) == {3}


def test_a_failing_batch_is_tried_again_whole_and_then_every_variant_turns_red():
    generator, record = BatchGenerator(fail_on=["a"]), FakeRecord()

    submit(generator, record=record)

    # Decision 2: the variants are tried again together -- three times, as one job (madde 8).
    assert generator.batches == [("a", "neg", 11, 2, "", "")] * 3 + [("b", "neg", 33, 2, "", "")]
    slots = record.slots("düğün")
    assert {fid: slots[fid]["photo"]["status"] for fid in ("P0_0", "P0_1", "P1_0", "P1_1")} == {
        "P0_0": "failed", "P0_1": "failed", "P1_0": "done", "P1_1": "done"}
    assert slots["P0_1"]["photo"]["error"] == "node 41: a — 3 kez denendi"


def test_a_stopped_batch_leaves_nothing_and_is_made_whole_on_resume():
    """Decision 2: a stop mid-batch loses the whole batch -- and nothing else, because nothing of it
    was written: every variant is still owed."""
    runner, store, record, plan_store = sync_runner(), FakeStore(), FakeRecord(), FakePlanStore()
    generator = BatchGenerator(stop=runner)

    submit(generator, text='["a"]', runner=runner, store=store, record=record,
           plan_store=plan_store)

    assert runner.status()["status"] == "paused"
    assert store.saved == [] and rows_of(record, "photo") == []

    resume_batch(runner, store, record, plan_store, {layers.PHOTO: generator}, lambda: NOW,
                 "düğün")

    assert generator.batches == [("a", "neg", 11, 2, "", "")] * 2
    assert [name for name, _data in store.saved] == ["P0_0.png", "P0_1.png"]


def failed_pair():
    """A prompt's two variants, both red: their batch fell three times."""
    record, seeds = FakeRecord(), iter([11, 22])
    plan_store = FakePlanStore(frames=plan_frames(0, [{"prompt": "a"}], "neg", 2,
                                                  lambda: next(seeds)))
    for fid in ("P0_0", "P0_1"):
        record.mark("düğün", fid, layers.PHOTO, f"{fid}.png", "failed", NOW,
                    error="node 41: a — 3 kez denendi")
    return record, plan_store


def test_a_variant_sent_back_with_tekrar_dene_is_made_alone():
    record, plan_store = failed_pair()
    generator = BatchGenerator()

    retry_frame(sync_runner(), FakeStore(), record, plan_store, {layers.PHOTO: generator},
                lambda: NOW, "düğün", "P0_1")

    # Its own planned seed, as before madde 411.
    assert generator.calls == [("a", "neg", 22, "")]
    assert generator.batches == []


def test_variants_sent_back_all_at_once_are_made_one_by_one():
    record, plan_store = failed_pair()
    generator = BatchGenerator()

    retry_failed(sync_runner(), FakeStore(), record, plan_store, {layers.PHOTO: generator},
                 lambda: NOW, "düğün")

    assert generator.calls == [("a", "neg", 11, ""), ("a", "neg", 22, "")]
    assert generator.batches == []


def test_a_regenerated_frame_is_made_alone():
    store, record, plan_store = video_project((0, "a"))
    generator = BatchGenerator()

    regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
               {layers.PHOTO: generator}, lambda: 7, lambda: NOW, "düğün", "0_a", layers.PHOTO,
               "p")

    assert generator.calls == [("p", "", 7, "")]
    assert generator.batches == []


def test_a_variant_dragged_elsewhere_is_made_where_it_stands_alone():
    """The gallery's order is the order work is done in: a batch is never gathered from further
    down the queue."""
    generator = BatchGenerator()
    # Newest first, as the gallery stores it -- so made from the foot up: P0_0, P1_0, P1_1, P0_1.
    order = FakeOrderStore(["P0_1", "P1_1", "P1_0", "P0_0"])

    submit(generator, order_store=order)

    assert generator.calls == [("a", "neg", 11, ""), ("a", "neg", 22, "")]
    assert generator.batches == [("b", "neg", 33, 2, "", "")]


def test_video_jobs_are_never_batched():
    """Photo only: a frame's videos each start from a picture of their own."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[
        {"id": fid, "type": "video", "number": 0, "variant": variant,
         "prompt": "kamera yaklaşır", "negative": "", "seed": None, "model": ""}
        for variant, fid in enumerate(("P0_0", "P0_1"))])
    for fid in ("P0_0", "P0_1"):
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        store.files[f"{fid}.png"] = b"PNG"
    generator = BatchGenerator()

    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator}, lambda: NOW,
             "düğün", new_seed=lambda: 5)()

    assert len(generator.calls) == 2
    assert generator.batches == [] and generator.asked == []


class Peeks(BatchGenerator):
    """Notes the status as the runner holds it while each batch is being made."""

    def __init__(self, runner):
        super().__init__()
        self.runner, self.seen = runner, []

    def generate_batch(self, *args, **kwargs):
        self.seen.append(self.runner.status())
        return super().generate_batch(*args, **kwargs)


def test_the_status_names_every_frame_its_batch_is_making():
    """The gallery draws every one of them as being made, each with the live time (madde 408)."""
    runner, reports = watched()
    generator = Peeks(runner)

    submit(generator, variants=3, seeds=(1, 2, 3, 4, 5, 6), runner=runner)

    seen = generator.seen[0]
    assert seen["current"]["id"] == "P0_0"
    assert seen["batch"] == ["P0_1", "P0_2"]
    assert seen["startedAt"] == NOW
    assert seen["pending"] == ["P1_0.png", "P1_1.png", "P1_2.png"]
    # Cleared at the top of every turn, the way the start is: nothing is being made yet.
    assert reports[0]["batch"] is None


def test_the_timing_line_names_the_batchs_files_together():
    clock, lines = Clock(), []

    make_job(sync_runner(), FakeStore(), FakeRecord(), one_prompt(2),
             {layers.PHOTO: BatchGenerator(clock=clock, seconds=80.0)}, lambda: NOW, "düğün",
             clock=clock, log=lines.append)()

    assert lines == ["⏱ P0_0.png, P0_1.png · render 80.0 sn · drive 0.0 sn"]
