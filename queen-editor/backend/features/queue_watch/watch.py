"""The queue started or ended, told to whoever listens (madde 509, 518).

The screen rings the browser's notification once each time the queue ends -- every photo and video
in it done, or stopped by an error or by a producer that is not installed -- whichever screen is
open and with the tab in the background. And a page left open while the queue is idle asks again
when it starts, so work added elsewhere -- by the agent, by another tab -- comes into sight without a
reload. Only the queue's worker knows it took the worker or ended and how, so it says so here
(main.py hands it `started` and `ended`); a pause and an export say nothing.

The screen hears both through one held ask (`changed_since`), as QueenAgent's events door does it
(madde 491): an ask from the counts it has sleeps until one of them moves or its limit runs out.
While no screen asks nobody is told, and the next ask hears the counts and the last ending as they
stand, so an event is late rather than lost; two between asks are heard as one. Memory only: a
restart counts from 0 again, and there is nothing to lose.
"""
import threading
import time


class QueueWatch:
    def __init__(self):
        self._lock = threading.Condition()
        self._started = 0
        self._ended = 0
        self._last = None

    def started(self):
        """The queue started: a press took the worker."""
        with self._lock:
            self._started += 1
            self._lock.notify_all()

    def ended(self, state):
        """The queue ended, as the worker's published `state` says: its status, and the error or
        the missing producer when it stopped."""
        with self._lock:
            self._ended += 1
            self._last = state
            self._lock.notify_all()

    def changed_since(self, seen, timeout):
        """{"started": how many times the queue started, "ended": how many times it ended, "last":
        how it last ended, or None} once the counts differ from `seen` -- the (started, ended) the
        asker last heard -- or as they stand after `timeout` seconds. With no `seen`, at once."""
        held_until = time.monotonic() + timeout
        with self._lock:
            while True:
                left = held_until - time.monotonic()
                if seen is None or (self._started, self._ended) != seen or left <= 0:
                    return {"started": self._started, "ended": self._ended, "last": self._last}
                self._lock.wait(left)
