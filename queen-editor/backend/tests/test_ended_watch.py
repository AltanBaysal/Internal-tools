"""The queue ended, told to whoever listens (madde 509).

The queue's worker says so, with how it ended; the screen hears it through one held ask. The asks
that wait use the real clock and wait a fraction of a second at most.
"""
import threading
import time

import pytest

DONE = {"status": "done", "project": "düğün", "done": 2, "failed": 0, "total": 2}
STOPPED = {"status": "error", "project": "düğün", "error": "ComfyUI cevap vermedi.\nTimeout"}


@pytest.fixture
def watch():
    from backend.features.queue_ended.watch import EndedWatch
    return EndedWatch()


def held_ask(watch, after):
    said = []
    thread = threading.Thread(target=lambda: said.append(watch.changed_since(after, 5)),
                              daemon=True)
    thread.start()
    return said, thread


def test_an_ask_with_no_count_is_answered_at_once(watch):
    assert watch.changed_since(None, 30) == {"ended": 0, "last": None}


def test_each_ending_counts_and_the_last_one_is_kept(watch):
    watch.ended(DONE)
    watch.ended(STOPPED)

    assert watch.changed_since(None, 30) == {"ended": 2, "last": STOPPED}


def test_an_ask_for_the_count_it_has_waits_out_its_limit(watch):
    started = time.monotonic()

    said = watch.changed_since(0, 0.2)

    assert said == {"ended": 0, "last": None}
    assert time.monotonic() - started >= 0.2


def test_an_ask_for_an_old_count_is_answered_at_once(watch):
    watch.ended(DONE)

    assert watch.changed_since(0, 30) == {"ended": 1, "last": DONE}


def test_a_held_ask_hears_the_queue_end_at_once(watch):
    said, thread = held_ask(watch, 0)
    started = time.monotonic()

    watch.ended(DONE)
    thread.join(5)

    assert said == [{"ended": 1, "last": DONE}]
    assert time.monotonic() - started < 2
