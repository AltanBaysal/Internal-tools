"""The contract between the queue and the three real producers.

Every other test in the suite runs one side of this contract: a producer's own test calls it
directly, and the queue's tests run against fakes. Both sides can be green while they disagree
about the call -- which is exactly what shipped. This file runs the real producer classes under
the real loop, and it is the only place that does.

Fake here is what a test machine cannot have: the ComfyUI server, torch, and ffmpeg. The graphs
are the shipped ones, because a producer that cannot patch its own graph does not satisfy the
contract in practice.
"""
import os

import pytest

from backend import config
from backend.features.photo_generation.data.comfy_h3_video_generator import ComfyH3VideoGenerator
from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator
from backend.features.photo_generation.data.comfy_video_generator import ComfyVideoGenerator
from backend.features.photo_generation.data.mmaudio_generator import MMAudioGenerator
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.running_name import RunningName
from backend.features.photo_generation.domain.run_loop import make_job

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# The shipped graphs, asked of config: where they live is its answer, and a second copy of the
# path here would go on being right about the old place (madde 251).
PHOTO_GRAPH = config.WORKFLOW_PATH
VIDEO_GRAPH = config.VIDEO_WORKFLOW_PATH
FIRST_LAST_GRAPH = config.VIDEO_FIRST_LAST_WORKFLOW_PATH

# Every graph config knows the way to -- the five it names, in one place.
GRAPHS = (config.WORKFLOW_PATH, config.VIDEO_WORKFLOW_PATH,
          config.VIDEO_FIRST_LAST_WORKFLOW_PATH, config.H3_VIDEO_WORKFLOW_PATH,
          config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH)


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
    """The photo graph's server: takes a workflow, answers with a picture."""

    def submit(self, workflow):
        self.submitted = workflow
        return "p1"

    def wait(self, prompt_id, timeout):
        return {"outputs": {}}

    def fetch_output(self, history):
        return b"PNG"


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


class Sampler:
    """Stands in for torch on the one point that decides this contract: manual_seed takes a long
    and raises on anything else. A fake that shrugs at the seed is exactly what let a seedless
    sound job reach Colab."""

    def render(self, video, prompt, negative, seed, duration):
        assert isinstance(seed, int), f"MMAudio needs an integer seed, got {seed!r}"
        return b"RIFFwav"


class Ffmpeg:
    """Reads the file it is asked about, so the test can prove which bytes arrived."""

    def __init__(self):
        self.saw = None

    def duration(self, video):
        with open(video, "rb") as handle:
            self.saw = handle.read()
        return 5.0

    def cut(self, video, start, duration, target):
        with open(target, "wb") as handle:
            handle.write(b"piece")

    def join(self, parts, target, fade_ms):
        raise AssertionError("a five second video is one piece")


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

    def mark(self, _project, frame, layer, file, status, at, error=None):
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
        # the name from here rather than keeping the string it was handed.
        self.named = RunningName()

    def stop_requested(self):
        return False

    def report(self, _state):
        pass


# One frame, all three layers -- so the run also proves the order: the video is made from the
# photo the same run produced, and the sound from that video.
# The seeds are the queue's own, not this file's invention: a photo job is planned with one and a
# layer job with none (queue_layer, locked by test_a_layer_job_is_planned_with_no_seed_of_its_own).
# Writing seeds in by hand here is what kept the sound producer's demand for one out of sight.
FRAMES = [
    {"id": "P0_0", "type": "photo", "number": 0, "variant": 0,
     "prompt": "kraliçe tahtta", "negative": "blurry", "seed": 1, "model": ""},
    {"id": "P0_0", "type": "video", "number": 0, "variant": 0,
     "prompt": "kamera yaklaşır", "negative": "", "seed": None, "model": ""},
    {"id": "P0_0", "type": "audio", "number": 0, "variant": 0,
     "prompt": "dalga sesi", "negative": "", "seed": None, "model": ""},
]


def producers_over(video_comfy, ffmpeg, tmp_path):
    return {
        layers.PHOTO: ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60),
        layers.VIDEO: ComfyVideoGenerator(video_comfy, VIDEO_GRAPH, FIRST_LAST_GRAPH, timeout=60),
        layers.AUDIO: MMAudioGenerator(Sampler(), ffmpeg, tmp_dir=str(tmp_path)),
    }


def test_a_producer_with_no_end_frame_takes_the_argument_anyway(tmp_path):
    """The queue has one call shape, not three: whatever the loop hands a producer, every producer
    takes. A photo is made from its words and a sound from the video under it -- neither has an
    ending picture, and both are still handed the argument."""
    ffmpeg = Ffmpeg()

    photo = ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60).generate(
        "kraliçe tahtta", "blurry", 1, end=("P1_0.png", b"PNG"))
    # A real seed, because the sound engine no longer invents one: the loop picks it before the
    # render so the number can also be written on the produced layer's row.
    sound = MMAudioGenerator(Sampler(), ffmpeg, tmp_dir=str(tmp_path)).generate(
        "dalga sesi", "", 4242, source=("P0_0_V1_0.mp4", b"MP4"), end=("P1_0.png", b"PNG"))

    assert photo == b"PNG"
    assert sound == b"RIFFwav"


def test_the_queue_runs_the_three_real_producers_end_to_end(tmp_path):
    store, video_comfy, ffmpeg = Store(), VideoComfy(), Ffmpeg()

    state = make_job(Runner(), store, Record(), Plan(FRAMES),
                     producers_over(video_comfy, ffmpeg, tmp_path),
                     lambda: "2026-08-13T00:00:00+00:00", "düğün")()

    assert state["status"] == "done"
    # The domain names every file; no producer gets a say in it.
    assert store.saved == ["P0_0.png", "P0_0_V1_0.mp4", "P0_0_V1_0_S1_0.wav"]
    # And what landed under each name is what its producer answered -- bytes, not a pair.
    assert store.files["P0_0.png"] == b"PNG"
    assert store.files["P0_0_V1_0.mp4"] == b"MP4"
    assert store.files["P0_0_V1_0_S1_0.wav"] == b"RIFFwav"


def test_each_layer_is_made_from_the_one_below_it(tmp_path):
    store, video_comfy, ffmpeg = Store(), VideoComfy(), Ffmpeg()

    make_job(Runner(), store, Record(), Plan(FRAMES),
             producers_over(video_comfy, ffmpeg, tmp_path),
             lambda: "2026-08-13T00:00:00+00:00", "düğün")()

    assert video_comfy.uploaded == [("P0_0.png", b"PNG")]   # the video hangs on the frame's photo
    assert ffmpeg.saw == b"MP4"                             # the sound is laid over that video


def test_a_producer_that_makes_no_video_takes_a_length_anyway(tmp_path):
    """Madde 422: a video job carries how long it is, and the queue hands it to whichever producer
    it calls -- one call shape. A photo and a sound take it and ignore it."""
    photo = ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60).generate(
        "kraliçe tahtta", "blurry", 1, seconds=8)
    sound = MMAudioGenerator(Sampler(), Ffmpeg(), tmp_dir=str(tmp_path)).generate(
        "dalga sesi", "", 4242, source=("P0_0_V1_0.mp4", b"MP4"), seconds=8)

    assert photo == b"PNG"
    assert sound == b"RIFFwav"


def test_the_queue_hands_the_real_producers_a_video_job_that_carries_its_length(tmp_path):
    """The real loop, the real producers: WAN takes the job's length and keeps its own, and the
    run goes through."""
    store, video_comfy, ffmpeg = Store(), VideoComfy(), Ffmpeg()
    timed = [{**job, "seconds": 8} if job["type"] == "video" else job for job in FRAMES]

    state = make_job(Runner(), store, Record(), Plan(timed),
                     producers_over(video_comfy, ffmpeg, tmp_path),
                     lambda: "2026-10-06T00:00:00+00:00", "düğün")()

    assert state["status"] == "done"
    assert store.saved == ["P0_0.png", "P0_0_V1_0.mp4", "P0_0_V1_0_S1_0.wav"]


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
             lambda: "2026-10-01T00:00:00+00:00", "düğün")()

    assert len(comfy.graphs) == 1
    graph = comfy.graphs[0]
    assert graph["23"]["inputs"]["value"] == 2
    assert graph["25"]["class_type"] == "EmptyLatentImage"
    assert graph["25"]["inputs"]["batch_size"] == ["23", 0]
    assert store.saved == ["P0_0.png", "P0_1.png"]


# --- Madde 423: a video's row says how long the video that was made runs ---------------------------

def wan():
    return ComfyVideoGenerator(VideoComfy(), VIDEO_GRAPH, FIRST_LAST_GRAPH, timeout=60)


def h3():
    return ComfyH3VideoGenerator(VideoComfy(), config.H3_VIDEO_WORKFLOW_PATH,
                                 config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH, timeout=60)


def video_row(video, asked, tmp_path):
    """One frame's three layers under the real loop, its video made by `video` and its job asked at
    `asked` seconds (None: asked none) -- the row the video left."""
    record = Record()
    jobs = [{**job, "seconds": asked} if job["type"] == "video" and asked is not None else job
            for job in FRAMES]
    producers = {**producers_over(VideoComfy(), Ffmpeg(), tmp_path), layers.VIDEO: video}
    make_job(Runner(), Store(), record, Plan(jobs), producers,
             lambda: "2026-10-06T00:00:00+00:00", "düğün")()
    return next(row for row in record.rows if row["layer"] == layers.VIDEO)


def test_a_video_queued_for_h3_and_made_by_wan_says_wans_length(tmp_path):
    """An H3 session queued it at 12 seconds; a later session installed WAN, which makes its graph's
    5 whatever it is asked. The row says what was made -- the export adds these up (madde 423)."""
    assert video_row(wan(), 12, tmp_path)["seconds"] == 5


def test_a_wan_video_says_its_graphs_length(tmp_path):
    assert video_row(wan(), None, tmp_path)["seconds"] == 5


@pytest.mark.parametrize("asked", [4, 8, 12])
def test_an_h3_video_says_the_length_it_was_asked(tmp_path, asked):
    assert video_row(h3(), asked, tmp_path)["seconds"] == asked


def test_an_h3_video_asked_no_length_says_its_graphs_own(tmp_path):
    """Every H3 job queued before madde 422: the Director keeps the graph's 4."""
    assert video_row(h3(), None, tmp_path)["seconds"] == 4
