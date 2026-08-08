"""The queue rule: the plan minus the frames that already settled."""
from backend.features.photo_generation.domain import queue


def frame(number, letter="a"):
    return {"number": number, "letter": letter, "prompt": "p", "negative": "", "seed": 1}


def test_a_frame_with_no_line_is_still_owed():
    assert queue.open_frames([frame(0), frame(1)], {}) == [frame(0), frame(1)]


def test_a_produced_frame_is_not_owed_again():
    assert queue.open_frames([frame(0), frame(1)], {"0_a.png": queue.DONE}) == [frame(1)]


def test_a_failed_frame_is_not_retried_on_its_own():
    assert queue.open_frames([frame(0)], {"0_a.png": queue.FAILED}) == []


def test_a_frame_pulled_out_of_the_queue_is_not_owed():
    assert queue.open_frames([frame(0)], {"0_a.png": queue.REMOVED}) == []


def test_a_deleted_photo_does_not_fall_back_into_the_queue():
    assert queue.open_frames([frame(0)], {"0_a.png": queue.DELETED}) == []


def test_queued_reopens_a_settled_frame():
    assert queue.open_frames([frame(0)], {"0_a.png": queue.QUEUED}) == [frame(0)]


def test_next_frame_is_the_first_one_still_owed():
    statuses = {"0_a.png": queue.DONE, "1_a.png": queue.FAILED}
    assert queue.next_frame([frame(0), frame(1), frame(2)], statuses) == frame(2)


def test_next_frame_is_none_when_the_queue_is_empty():
    assert queue.next_frame([frame(0)], {"0_a.png": queue.DONE}) is None


def test_counts_are_read_from_the_statuses():
    frames = [frame(0), frame(1), frame(2)]
    statuses = {"0_a.png": queue.DONE, "1_a.png": queue.FAILED}
    assert queue.counts(frames, statuses) == {"total": 3, "done": 1, "failed": 1,
                                              "failures": ["1_a.png"]}
