from backend.features.photo_generation.domain import policy


def test_a_single_failure_keeps_the_batch_going():
    assert policy.stop_reason(1, infra=False) is None
    assert policy.stop_reason(2, infra=False) is None


def test_three_consecutive_failures_stop_the_batch():
    reason = policy.stop_reason(policy.MAX_CONSECUTIVE, infra=False)
    assert reason is not None and "3" in reason


def test_infra_failure_stops_on_the_first_one():
    reason = policy.stop_reason(1, infra=True)
    assert reason is not None and "Altyapı" in reason


def test_reasons_say_the_batch_stopped():
    # The text lands in the status line, so it must read as a sentence to the user.
    assert "durduruldu" in policy.stop_reason(1, infra=True)
    assert "durduruldu" in policy.stop_reason(3, infra=False)
