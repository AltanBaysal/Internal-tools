"""The queue ended, told to whoever listens (madde 509).

The screen rings the browser's notification once each time the queue ends -- every photo and video
in it done, or stopped by an error or by a producer that is not installed -- whichever screen is
open and with the tab in the background. Only the queue's worker knows it ended and how, so it says
so here (main.py hands it `ended`); a pause and an export ending say nothing.

The screen hears it through one held ask (`changed_since`), as QueenAgent's events door does it
(madde 491): an ask from the count it has sleeps until the count moves or its limit runs out. While
no screen asks nobody is told, and the next ask hears the count and the last ending as they stand,
so an ending is late rather than lost; two between asks are heard as the last. Memory only: a
restart counts from 0 again, and there is nothing to lose.
"""
import threading
import time


class EndedWatch:
    def __init__(self):
        self._lock = threading.Condition()
        self._ended = 0
        self._last = None

    def ended(self, state):
        """The queue ended, as the worker's published `state` says: its status, and the error or
        the missing producer when it stopped."""
        with self._lock:
            self._ended += 1
            self._last = state
            self._lock.notify_all()

    def changed_since(self, after, timeout):
        """{"ended": how many times the queue ended, "last": how it last ended, or None} once the
        count differs from `after`, or as it stands after `timeout` seconds. With no `after`, at
        once."""
        held_until = time.monotonic() + timeout
        with self._lock:
            while True:
                left = held_until - time.monotonic()
                if after is None or self._ended != after or left <= 0:
                    return {"ended": self._ended, "last": self._last}
                self._lock.wait(left)
