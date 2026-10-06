"""Madde 423: the export's total is added up from each video's own length.

Since madde 422 an H3 video's line in the photo record says how long it was made ("seconds"). A video
whose line says nothing -- every one made before 422, and every WAN video -- runs as long as its
graph says, which the summary asks of the session's video producer, as it always did.

The record is the real one over a folder: what is proved is the whole road from a line on Drive to
the number on the export screen, the fold included.
"""
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.usecases.copy_frames import copy_frames
from backend.features.photo_generation.domain.usecases.export_summary import export_summary
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.services.drive.storage import DriveStorage
from backend.tests.test_photo_usecases import (
    FakeGenerator,
    FakeOrderStore,
    FakePlanStore,
    FakeStore,
    frame,
    sync_runner,
)


def project(tmp_path, *videos):
    """Frames 0_a, 1_a, … each with its photo and a produced video. `videos` is the length each
    video's line says, None for a line that says none -- what every line before madde 422 is."""
    record = DrivePhotoRecord(DriveStorage(str(tmp_path)))
    plan_store = FakePlanStore(frames=[frame(number) for number in range(len(videos))])
    for number, seconds in enumerate(videos):
        fid = f"{number}_a"
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        record.append("düğün", {"file": f"{fid}_V1_0.mp4", "frame": fid, "layer": "video",
                                "status": "done",
                                **({} if seconds is None else {"seconds": seconds})})
    return FakeStore(), record, plan_store


def summary(store, record, plan_store, graph):
    """The export summary, `graph` standing for how long the session's video graph runs."""
    return export_summary(record, store, plan_store, FakeOrderStore(), lambda: graph, "düğün")


# --- The record's fold ---------------------------------------------------------------------------

def test_a_videos_line_that_says_its_length_carries_it_into_the_slot(tmp_path):
    _store, record, _plan = project(tmp_path, 12)

    assert record.slots("düğün")["0_a"]["video"]["seconds"] == 12


def test_a_line_written_before_lengths_carries_none_into_the_slot(tmp_path):
    # Every video on Drive before madde 422. Absent is the honest answer; the summary decides what
    # to do with it.
    _store, record, _plan = project(tmp_path, None)

    assert "seconds" not in record.slots("düğün")["0_a"]["video"]


# --- The gallery ---------------------------------------------------------------------------------

def test_a_card_says_how_long_its_video_runs(tmp_path):
    store, record, plan_store = project(tmp_path, 12)

    card = list_frames(record, store, plan_store, FakeOrderStore(), "düğün")[0]

    assert card["lengths"] == {"video": 12}


def test_a_card_whose_video_says_no_length_has_none(tmp_path):
    # Nothing filled in after the fact: an old video's card says no length rather than a guessed
    # one.
    store, record, plan_store = project(tmp_path, None)

    card = list_frames(record, store, plan_store, FakeOrderStore(), "düğün")[0]

    assert card["lengths"] == {}


# --- The export summary --------------------------------------------------------------------------

def test_the_total_adds_up_each_videos_own_length(tmp_path):
    """H3 videos of different lengths total what each of them runs (madde 423)."""
    store, record, plan_store = project(tmp_path, 4, 8, 12)

    answer = summary(store, record, plan_store, graph=4)

    assert (answer["videos"], answer["seconds"]) == (3, 24)


def test_a_video_whose_line_says_no_length_counts_at_the_graphs_own(tmp_path):
    """Every video made before madde 422, and every WAN video: its graph said how long it runs."""
    store, record, plan_store = project(tmp_path, 12, None)

    assert summary(store, record, plan_store, graph=5)["seconds"] == 17


def test_videos_all_of_one_length_total_what_they_did(tmp_path):
    """"Tek uzunlukta videoları olan projede toplam bugünküyle aynı" -- the projects already on
    Drive."""
    store, record, plan_store = project(tmp_path, None, None)

    assert summary(store, record, plan_store, graph=4)["seconds"] == 8


def test_a_twin_holding_a_video_counts_at_that_videos_length(tmp_path):
    """A copy frame shares its source's video file (madde 102), so it runs exactly as long."""
    store, record, plan_store = project(tmp_path, 12)
    copy_frames(record, store, plan_store, FakeOrderStore(), lambda: "t", "düğün", ["0_a"])

    answer = summary(store, record, plan_store, graph=4)

    assert (answer["videos"], answer["seconds"]) == (2, 24)


def test_a_video_made_at_a_chosen_length_counts_at_it(tmp_path):
    """Madde 422's line, the fold and the summary together: a video put in the queue at 12 seconds
    is counted at 12, whatever the graph says."""
    record = DrivePhotoRecord(DriveStorage(str(tmp_path)))
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store = FakePlanStore(frames=[frame(0)])
    plan_store.frames.append({"id": "0_a", "type": "video", "number": 0, "variant": 0,
                              "prompt": "kadın dönüyor", "negative": "", "seed": 5, "model": "",
                              "seconds": 12})
    store = FakeStore()

    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: FakeGenerator()},
             lambda: "t", "düğün")()

    assert summary(store, record, plan_store, graph=4)["seconds"] == 12
