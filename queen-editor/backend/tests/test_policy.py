from backend.features.photo_generation.domain import policy


def test_the_first_two_attempts_keep_the_queue_going():
    assert policy.stop_reason(1) is None
    assert policy.stop_reason(2) is None


def test_the_third_attempt_on_the_same_frame_stops_the_queue():
    reason = policy.stop_reason(policy.MAX_ATTEMPTS)
    assert reason is not None and "3" in reason


def test_the_reason_says_the_queue_stopped():
    # The text lands in the status line, so it must read as a sentence to the user.
    assert "durduruldu" in policy.stop_reason(policy.MAX_ATTEMPTS)


def test_a_renderer_that_answered_blames_the_frame():
    class Answered(RuntimeError):
        frame_level = True

    assert policy.is_frame_fault(Answered("node 41: OOM")) is True


def test_anything_that_did_not_answer_blames_the_run():
    # No flag at all is the normal shape of a connection error, an HTTP error or a timeout.
    assert policy.is_frame_fault(RuntimeError("Connection refused")) is False
    assert policy.is_frame_fault(TimeoutError("300s içinde bitmedi")) is False
