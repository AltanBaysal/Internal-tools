"""The queue rule: the plan minus the frames that already settled."""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import frame_id


def frame(number, variant=0):
    return {"id": frame_id(number, variant), "number": number, "variant": variant,
            "prompt": "p", "negative": "", "seed": 1}


def test_a_frame_with_no_line_is_still_owed():
    assert queue.open_frames([frame(0), frame(1)], {}) == [frame(0), frame(1)]


def test_a_produced_frame_is_not_owed_again():
    assert queue.open_frames([frame(0), frame(1)], {"P0_0": queue.DONE}) == [frame(1)]


def test_a_failed_frame_is_not_retried_on_its_own():
    assert queue.open_frames([frame(0)], {"P0_0": queue.FAILED}) == []


def test_a_frame_pulled_out_of_the_queue_is_not_owed():
    assert queue.open_frames([frame(0)], {"P0_0": queue.REMOVED}) == []


def test_a_deleted_photo_does_not_fall_back_into_the_queue():
    assert queue.open_frames([frame(0)], {"P0_0": queue.DELETED}) == []


def test_queued_reopens_a_settled_frame():
    assert queue.open_frames([frame(0)], {"P0_0": queue.QUEUED}) == [frame(0)]


def test_next_frame_is_the_first_one_still_owed():
    statuses = {"P0_0": queue.DONE, "P1_0": queue.FAILED}
    assert queue.next_frame([frame(0), frame(1), frame(2)], statuses) == frame(2)


def test_next_frame_is_none_when_the_queue_is_empty():
    assert queue.next_frame([frame(0)], {"P0_0": queue.DONE}) is None


def test_counts_are_read_from_the_statuses():
    frames = [frame(0), frame(1), frame(2)]
    statuses = {"P0_0": queue.DONE, "P1_0": queue.FAILED}
    assert queue.counts(frames, statuses) == {"total": 3, "done": 1, "failed": 1,
                                              "failures": ["P1_0.png"]}


def test_the_queue_reads_statuses_by_frame_identity():
    # A file name is not a key here: two frames can share one picture.
    assert [f["number"] for f in queue.open_frames([frame(0), frame(1)],
                                                   {"P0_0": queue.DONE})] == [1]


def test_failures_are_reported_as_file_names():
    # The screen marks its red tiles by file name; the fold is keyed by identity.
    assert queue.counts([frame(3, 1)], {"P3_1": queue.FAILED})["failures"] == ["P3_1.png"]
