"""The contract between the queue and the real producers: the photo's and the video's, the two
there are since madde 514 took MMAudio out.

Every other test in the suite runs one side of this contract: a producer's own test calls it
directly, and the queue's tests run against fakes. Both sides can be green while they disagree
about the call -- which is exactly what shipped. This file runs the real producer classes under
the real loop, and it is the only place that does.

Fake here is what a test machine cannot have: the ComfyUI server. The graphs
are the shipped ones, because a producer that cannot patch its own graph does not satisfy the
contract in practice.
"""
import os

import pytest

from backend import config
from backend.features.photo_generation.data.comfy_h3_video_generator import ComfyH3VideoGenerator
from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.running_name import RunningName
from backend.features.photo_generation.domain.run_loop import make_job
from backend.tests.test_comfy_h3_video_generator import png

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# The shipped graphs, asked of config: where they live is its answer, and a second copy of the
# path here would go on being right about the old place (madde 251).
PHOTO_GRAPH = config.WORKFLOW_PATH

# Every graph config knows the way to -- the four it names, in one place.
GRAPHS = (config.WORKFLOW_PATH, config.KREA2_WORKFLOW_PATH,
          config.H3_VIDEO_WORKFLOW_PATH, config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH)


def test_no_graph_is_left_in_the_tool_root():
    """The graphs live under assets/ with the disclaimer (madde 251, user's call). A copy left in
    the root would be the one somebody edits next, and nothing would say it is not the one that
    ships."""
    left = [name for name in os.listdir(ROOT)
            if name.startswith("workflow_") and name.endswith(".json")]

    assert left == [], f"Kökte grafik kalmış: {left}"


def test_every_graph_config_names_is_a_file():
    """Moving is not deleting, and the test above cannot tell the two apart on its own."""
    for path in GRAPHS:
        assert os.path.isfile(path), f"Grafik yok: {path}"


class PhotoComfy:
    """The photo graph's server: takes a workflow, answers with a picture of the size the graph's
    own Width and Height nodes say -- the shape the video made from it then follows (madde 476)."""

    def submit(self, workflow):
        self.submitted = workflow
        return "p1"

    def wait(self, prompt_id, timeout):
        return {"outputs": {}}

    def fetch_output(self, history):
        return png(self.submitted["1"]["inputs"]["value"], self.submitted["11"]["inputs"]["value"])


# What the shipped photo graph makes when nobody asks it another size: portrait, 1024 x 1536.
PORTRAIT = png(1024, 1536)


class VideoComfy:
    """The video graph's server. Records the upload, because that upload IS the frame's photo
    reaching the video producer."""

    def __init__(self):
        self.uploaded = []

    def upload_image(self, name, data):
        self.uploaded.append((name, data))
        return name

    def submit(self, workflow):
        self.submitted = workflow
        return "p2"

    def wait(self, prompt_id, timeout):
        return {"outputs": {}}

    def fetch_output(self, history, extensions=()):
        return b"MP4"


class Store:
    def __init__(self):
        self.saved = []
        self.files = {}

    def save(self, _project, filename, data):
        self.saved.append(filename)
        self.files[filename] = data
        return filename

    def read(self, _project, filename):
        return self.files.get(filename)


class Record:
    """Folds rows the way DrivePhotoRecord does: latest line per (frame, layer).

    No `prompts()`: this run has no prompt writers, so the loop never asks. A fake that answers
    questions nobody asked would hide the day one starts being asked.
    """

    def __init__(self):
        self.rows = []

    def append(self, _project, entry):
        self.rows.append(entry)

    def mark(self, _project, frame, layer, file, status, at, *, seen, error=None):
        # `seen` is not kept: this run has one writer, so no line can land over a slot that moved
        # (madde 513's rule, which DrivePhotoRecord's own tests cover).
        self.rows.append({"frame": frame, "layer": layer, "file": file, "status": status})

    def slots(self, _project):
        folded = {}
        for row in self.rows:
            folded.setdefault(row["frame"], {})[row["layer"]] = {
                "status": row.get("status", "done"), "file": row["file"]}
        return folded


class Plan:
    def __init__(self, frames):
        self._frames = frames

    def read(self, _project):
        return {"frames": list(self._frames)}


class Runner:
    """The three things the loop asks of a runner, and nothing else."""

    def __init__(self):
        # Which folder the job writes into: a project can be renamed under a run, so the loop reads
        # the name from here rather than keeping the string it was handed. Pointed at the project
        # these tests run, as a real runner's claim points it.
        self.named = RunningName("düğün")

    def stop_requested(self):
        return False

    def report(self, _state):
        pass


# One frame, both layers -- so the run also proves the order: the video is made from the photo the
# same run produced.
# The seeds are the queue's own, not this file's invention: a photo job is planned with one and a
# layer job with none (queue_layer, locked by test_a_layer_job_is_planned_with_no_seed_of_its_own).
FRAMES = [
    {"id": "P0_0", "type": "photo", "number": 0, "variant": 0,
     "prompt": "kraliçe tahtta", "negative": "blurry", "seed": 1, "model": ""},
    {"id": "P0_0", "type": "video", "number": 0, "variant": 0,
     "prompt": "kamera yaklaşır", "negative": "", "seed": None, "model": ""},
]


def h3(video_comfy=None):
    """H3's producer over its shipped graphs: the one video model (madde 435)."""
    return ComfyH3VideoGenerator(video_comfy or VideoComfy(), config.H3_VIDEO_WORKFLOW_PATH,
                                 config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH, timeout=60)


def producers_over(video_comfy):
    return {
        layers.PHOTO: ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60),
        layers.VIDEO: h3(video_comfy),
    }


def test_a_producer_with_no_end_frame_takes_the_argument_anyway():
    """The queue has one call shape: whatever the loop hands a producer, every producer takes. A
    photo is made from its words -- it has no ending picture, and is still handed the argument."""
    photo = ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60).generate(
        "kraliçe tahtta", "blurry", 1, end=("P1_0.png", b"PNG"))

    assert photo == PORTRAIT


def test_the_queue_runs_the_real_producers_end_to_end():
    store, video_comfy = Store(), VideoComfy()

    state = make_job(Runner(), store, Record(), Plan(FRAMES), producers_over(video_comfy),
                     lambda: "2026-08-13T00:00:00+00:00")()

    assert state["status"] == "done"
    # The domain names every file; no producer gets a say in it.
    assert store.saved == ["P0_0.png", "P0_0_V1_0.mp4"]
    # And what landed under each name is what its producer answered -- bytes, not a pair.
    assert store.files["P0_0.png"] == PORTRAIT
    assert store.files["P0_0_V1_0.mp4"] == b"MP4"


def test_each_layer_is_made_from_the_one_below_it():
    store, video_comfy = Store(), VideoComfy()

    make_job(Runner(), store, Record(), Plan(FRAMES), producers_over(video_comfy),
             lambda: "2026-08-13T00:00:00+00:00")()

    assert video_comfy.uploaded == [("P0_0.png", PORTRAIT)]  # the video hangs on the frame's photo


def test_a_producer_that_makes_no_video_takes_a_length_anyway():
    """Madde 422: a video job carries how long it is, and the queue hands it to whichever producer
    it calls -- one call shape. A photo takes it and ignores it."""
    photo = ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60).generate(
        "kraliçe tahtta", "blurry", 1, seconds=8)

    assert photo == PORTRAIT


def test_the_queue_hands_the_real_producers_a_video_job_that_carries_its_length():
    """The real loop, the real producers: H3 takes the job's length, and the run goes through."""
    store, video_comfy = Store(), VideoComfy()
    timed = [{**job, "seconds": 8} if job["type"] == "video" else job for job in FRAMES]

    state = make_job(Runner(), store, Record(), Plan(timed), producers_over(video_comfy),
                     lambda: "2026-10-06T00:00:00+00:00")()

    assert state["status"] == "done"
    assert store.saved == ["P0_0.png", "P0_0_V1_0.mp4"]


class BatchComfy(PhotoComfy):
    """The photo graph's server on an A100: it holds the batch, and answers with as many pictures
    as the graph asked for."""

    def __init__(self):
        self.graphs = []

    def submit(self, workflow):
        self.graphs.append(workflow)
        return "p1"

    def vram_total(self):
        return round(39.56 * 1024 ** 3)

    def fetch_outputs(self, history, count):
        return [f"PNG{index}".encode() for index in range(count)]


# One prompt's two variants, the way plan_frames writes them.
VARIANTS = [{"id": f"P0_{variant}", "type": "photo", "number": 0, "variant": variant,
             "prompt": "kraliçe tahtta", "negative": "blurry", "seed": 1, "model": "", "lora": ""}
            for variant in range(2)]


def test_a_prompts_variants_go_through_the_real_photo_producer_as_one_batch():
    """Madde 411 on the shipped graph: the node the count is written into is the one its latent
    reads the batch size from, so ComfyUI really makes both pictures in one job."""
    store, comfy = Store(), BatchComfy()

    make_job(Runner(), store, Record(), Plan(VARIANTS),
             {layers.PHOTO: ComfyPhotoGenerator(comfy, PHOTO_GRAPH, timeout=60)},
             lambda: "2026-10-01T00:00:00+00:00")()

    assert len(comfy.graphs) == 1
    graph = comfy.graphs[0]
    assert graph["23"]["inputs"]["value"] == 2
    assert graph["25"]["class_type"] == "EmptyLatentImage"
    assert graph["25"]["inputs"]["batch_size"] == ["23", 0]
    assert store.saved == ["P0_0.png", "P0_1.png"]


# --- Madde 482: Krea 2 Turbo, a model with a graph of its own ---------------------------------------

class KreaComfy(BatchComfy):
    """Krea's graph's server: answers with a picture of the size its latent was handed."""

    def fetch_output(self, history):
        latent = self.graphs[-1]["53:5"]["inputs"]
        return png(latent["width"], latent["height"])


def test_a_krea_prompt_goes_through_the_real_photo_producers_on_its_own_graph(tmp_path):
    """The real loop, the producer main.py wires: a Krea prompt's two variants are two jobs on the
    shipped Krea graph, each with its own seed, landscape at 1280 x 720 -- and the Nova prompt
    planned after it still goes to the photo graph, as one batch."""
    from backend.features.photo_generation.data.comfy_krea_photo_generator import (
        ComfyKreaPhotoGenerator,
    )
    from backend.features.photo_generation.data.photo_by_model import PhotoByModel

    krea_jobs = [{**job, "id": f"P1_{job['variant']}", "number": 1, "model": "krea2",
                  "seed": 5 + job["variant"], "orientation": "yatay"} for job in VARIANTS]
    store, sdxl, krea = Store(), BatchComfy(), KreaComfy()
    photo = PhotoByModel(ComfyPhotoGenerator(sdxl, PHOTO_GRAPH, timeout=60),
                         {"krea2": ComfyKreaPhotoGenerator(krea, config.KREA2_WORKFLOW_PATH,
                                                           timeout=60)})

    state = make_job(Runner(), store, Record(), Plan(krea_jobs + VARIANTS), {layers.PHOTO: photo},
                     lambda: "2026-10-21T00:00:00+00:00")()

    assert state["status"] == "done"
    assert [graph["53:3"]["inputs"]["seed"] for graph in krea.graphs] == [5, 6]
    assert {graph["53:19"]["inputs"]["value"] for graph in krea.graphs} == {"kraliçe tahtta"}
    assert store.files["P1_0.png"] == png(1280, 720)
    assert len(sdxl.graphs) == 1 and sdxl.graphs[0]["23"]["inputs"]["value"] == 2


# --- Madde 423: a video's row says how long the video that was made runs ---------------------------

def video_row(video, asked):
    """One frame's layers under the real loop, its video made by `video` and its job asked at
    `asked` seconds (None: asked none) -- the row the video left."""
    record = Record()
    jobs = [{**job, "seconds": asked} if job["type"] == "video" and asked is not None else job
            for job in FRAMES]
    producers = {**producers_over(VideoComfy()), layers.VIDEO: video}
    make_job(Runner(), Store(), record, Plan(jobs), producers,
             lambda: "2026-10-06T00:00:00+00:00")()
    return next(row for row in record.rows if row["layer"] == layers.VIDEO)


@pytest.mark.parametrize("asked", [4, 8, 12])
def test_an_h3_video_says_the_length_it_was_asked(asked):
    assert video_row(h3(), asked)["seconds"] == asked


def test_an_h3_video_asked_no_length_says_its_graphs_own():
    """Every H3 job queued before madde 422: the Director keeps the graph's 4."""
    assert video_row(h3(), None)["seconds"] == 4


# --- Madde 426: Mutlu son -----------------------------------------------------------------------------

def test_a_producer_that_makes_no_video_takes_a_happy_ending_anyway():
    """A video job carries whether it ends happily, and the queue hands it to whichever producer it
    calls -- one call shape. A photo takes it and ignores it."""
    photo = ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60).generate(
        "kraliçe tahtta", "blurry", 1, happy_ending=True)

    assert photo == PORTRAIT


def test_the_queue_hands_the_real_h3_a_video_job_that_ends_happily():
    """The real loop, the real producers: H3 takes the job's switch and loads HMCumshot."""
    store, video_comfy = Store(), VideoComfy()
    happy = [{**job, "happyEnding": True} if job["type"] == "video" else job for job in FRAMES]

    state = make_job(Runner(), store, Record(), Plan(happy), producers_over(video_comfy),
                     lambda: "2026-10-09T00:00:00+00:00")()

    assert state["status"] == "done"
    assert "HMCumshot_V1.0.safetensors" in video_comfy.submitted["2678"]["inputs"]["stack_data"]


# --- Madde 476: the video follows the shape of its photo ------------------------------------------

def sizes_made(lines):
    """One frame's photo and video under the real loop and the shipped graphs: the size the photo
    graph was asked for, and the size the video graph was."""
    photo_comfy, video_comfy = PhotoComfy(), VideoComfy()
    producers = {**producers_over(video_comfy),
                 layers.PHOTO: ComfyPhotoGenerator(photo_comfy, PHOTO_GRAPH, timeout=60)}
    state = make_job(Runner(), Store(), Record(), Plan(lines), producers,
                     lambda: "2026-10-20T00:00:00+00:00")()
    assert state["status"] == "done"
    photo, director = photo_comfy.submitted, video_comfy.submitted["2730"]["inputs"]
    return ((photo["1"]["inputs"]["value"], photo["11"]["inputs"]["value"]),
            (director["width"], director["height"]))


@pytest.mark.parametrize("asked, sizes", [
    ("yatay", ((1536, 864), (1024, 576))),
    ("dikey", ((1024, 1536), (576, 864))),
], ids=["yatay", "dikey"])
def test_a_frame_s_photo_and_its_video_stand_the_way_the_photo_was_asked(asked, sizes):
    """The item's own sentence, end to end: the photo is made in its orientation, and the video --
    told nothing -- comes out the same shape, read off the picture the photo graph made."""
    lines = [{**job, "orientation": asked} if job["type"] == "photo" else job for job in FRAMES]

    assert sizes_made(lines) == sizes


def test_an_old_frame_s_photo_and_video_stay_portrait():
    """A line planned before madde 476 carries no orientation, and is made as it always was."""
    assert sizes_made(FRAMES) == ((1024, 1536), (576, 864))
