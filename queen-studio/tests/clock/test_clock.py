import time
from datetime import UTC, datetime, timedelta, timezone

import pytest

from core.clock.clock import Clock, ManualClock, SystemClock

START = datetime(2026, 11, 6, 9, 0, tzinfo=UTC)


def test_a_manual_clock_stands_until_it_is_told() -> None:
    clock: Clock = ManualClock(START)

    assert clock.now() == START
    assert clock.now() == START


def test_sleep_moves_it_on_at_once() -> None:
    clock = ManualClock(START)
    before = time.monotonic()

    clock.sleep(90)
    clock.sleep(0.5)

    assert clock.now() == START + timedelta(seconds=90.5)
    # No test waits a real second (step 12).
    assert time.monotonic() - before < 1


def test_its_time_is_utc() -> None:
    with pytest.raises(ValueError, match="UTC"):
        ManualClock(datetime(2026, 11, 6, 12, 0, tzinfo=timezone(timedelta(hours=3))))
    with pytest.raises(ValueError, match="UTC"):
        ManualClock(datetime(2026, 11, 6, 9, 0))


def test_it_does_not_go_back() -> None:
    clock = ManualClock(START)

    with pytest.raises(ValueError):
        clock.sleep(-1)

    assert clock.now() == START


def test_the_system_clock_gives_utc_and_sleeps_for_real() -> None:
    # Wired in the start file and in the opt-in real-Drive tests; no other test sleeps on it.
    clock: Clock = SystemClock()

    before = clock.now()
    clock.sleep(0)

    assert before.utcoffset() == timedelta(0)
    assert clock.now() >= before
