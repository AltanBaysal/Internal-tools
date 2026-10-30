"""The queue started or ended, told to whoever listens (madde 509, 518).

The queue's worker says so -- a start when it takes the worker, an ending with how it ended -- and the
screen hears both through one held ask. The asks that wait use the real clock and wait a fraction of a
second at most.
"""
import threading
import time

import pytest

DONE = {"status": "done", "project": "düğün", "done": 2, "failed": 0, "total": 2}
STOPPED = {"status": "error", "project": "düğün", "error": "ComfyUI cevap vermedi.\nTimeout"}


@pytest.fixture
def watch():
    from backend.features.queue_watch.watch import QueueWatch
    return QueueWatch()


def held_ask(watch, seen):
    said = []
    thread = threading.Thread(target=lambda: said.append(watch.changed_since(seen, 5)),
                              daemon=True)
    thread.start()
    return said, thread


def test_an_ask_with_no_counts_is_answered_at_once(watch):
    assert watch.changed_since(None, 30) == {"started": 0, "ended": 0, "last": None}


def test_each_ending_counts_and_the_last_one_is_kept(watch):
    watch.ended(DONE)
    watch.ended(STOPPED)

    assert watch.changed_since(None, 30) == {"started": 0, "ended": 2, "last": STOPPED}


def test_starts_are_counted_apart_from_endings(watch):
    watch.started()
    watch.ended(DONE)
    watch.started()

    assert watch.changed_since(None, 30) == {"started": 2, "ended": 1, "last": DONE}


def test_an_ask_for_the_counts_it_has_waits_out_its_limit(watch):
    started = time.monotonic()

    said = watch.changed_since((0, 0), 0.2)

    assert said == {"started": 0, "ended": 0, "last": None}
    assert time.monotonic() - started >= 0.2


@pytest.mark.parametrize("seen", [(0, 0), (1, 0), (0, 1)], ids=["both", "start", "end"])
def test_an_ask_for_old_counts_is_answered_at_once(watch, seen):
    watch.started()
    watch.ended(DONE)

    assert watch.changed_since(seen, 30) == {"started": 1, "ended": 1, "last": DONE}


def test_a_held_ask_hears_the_queue_end_at_once(watch):
    said, thread = held_ask(watch, (0, 0))
    started = time.monotonic()

    watch.ended(DONE)
    thread.join(5)

    assert said == [{"started": 0, "ended": 1, "last": DONE}]
    assert time.monotonic() - started < 2


def test_a_held_ask_hears_the_queue_start_at_once(watch):
    """Madde 518: a page left open while the queue is idle learns that work was added elsewhere."""
    said, thread = held_ask(watch, (0, 0))
    started = time.monotonic()

    watch.started()
    thread.join(5)

    assert said == [{"started": 1, "ended": 0, "last": None}]
    assert time.monotonic() - started < 2
