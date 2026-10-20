"""Helpers more than one test file needs."""
import time

import pytest


@pytest.fixture
def until():
    """`until(found)`: what `found()` returns once it returns something, within five seconds.

    For work on a thread of its own -- an agent waiting for the user's answer (madde 480) -- which a
    test has to watch for the moment it is there; that is a moment, never seconds.
    """
    def wait(found):
        end = time.monotonic() + 5
        while time.monotonic() < end:
            value = found()
            if value:
                return value
            time.sleep(0.001)
        raise AssertionError("Nothing came within five seconds.")

    return wait


@pytest.fixture
def ended():
    """`ended(thread)`: the thread, given five seconds to end, has ended -- a run left waiting
    fails here rather than hanging on in the background."""
    def check(thread):
        thread.join(5)
        assert not thread.is_alive(), "The thread is still running after five seconds."

    return check
