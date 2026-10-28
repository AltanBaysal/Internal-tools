"""The idle watch: "orada mısın?" once nothing has worked for ten minutes (madde 498).

Colab bills the A100 whether or not it works, and the tab may be in the background. So the server --
the one place that sees all work, whichever screen is open -- counts down, and the screen only
listens.

Work tells the watch when it starts and ends by running on the watch's threads: the queue, the
export and the agent each hand `spawn` to their runner (main.py), so a start is the thread being
spawned and an end is its work returning, raised or not -- an end can never be missed. An agent
waiting on İzin ver / Reddet waits on the user, which is not work: its wait runs inside `waiting`,
and the rule lives in that one place.

With nothing running a countdown is open: from the server's start, from the last end, and from
Buradayım. Any start closes it, and the question with it. Run out, it asks, and asks again every ten
minutes while nothing runs. No thread keeps the time: the countdown is a moment, and a held ask
(`changed_since`) sleeps until that moment, a change, or its own limit -- whichever is first. While
no screen asks, nobody is told, and the first ask hears where it stands.

`version` moves each time the question is asked or closed, so a screen asking from the version it
has hears every change, an ask again every ten minutes included. Memory only: a restart starts the
count again, and there is nothing to lose.
"""
import threading
import time
from contextlib import contextmanager

WAIT_SECONDS = 600


class IdleWatch:
    def __init__(self, wait=WAIT_SECONDS, clock=time.monotonic):
        self._wait = wait
        # The countdown's clock, injected for the tests. How long an ask is held is the wall's
        # monotonic time whatever this is: it is a promise to the tunnel, not part of the count.
        self._clock = clock
        self._lock = threading.Condition()
        self._working = set()
        # When the question is due, or None while something works. Nothing works when the server
        # comes up, so the count starts there.
        self._due = clock() + wait
        self._asking = False
        self._version = 0
        # Which work the current thread is running, for `waiting`.
        self._current = threading.local()

    def spawn(self, fn):
        """Run `fn` on a thread of its own, as work: started now, ended once `fn` returns. The
        thread is handed back for the tests to join."""
        work = object()
        self._start(work)

        def run():
            self._current.work = work
            try:
                fn()
            finally:
                self._end(work)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return thread

    @contextmanager
    def waiting(self):
        """The work on this thread waits on the user: not work while inside. Off the watch's
        threads -- a runner's work run inline -- there is nothing to pause."""
        work = getattr(self._current, "work", None)
        if work is None:
            yield
            return
        self._end(work)
        try:
            yield
        finally:
            self._start(work)

    def here(self):
        """Buradayım: the question closes and the ten minutes start again -- unless something
        works, which has no countdown to start."""
        with self._lock:
            self._close()
            if not self._working:
                self._due = self._clock() + self._wait
            self._lock.notify_all()
            return self._said()

    def changed_since(self, version, timeout):
        """{"version", "asking"} once the version has moved past `version`, or as it stands after
        `timeout` seconds. With no version, at once."""
        held_until = time.monotonic() + timeout
        with self._lock:
            while True:
                self._ask_if_due()
                left = held_until - time.monotonic()
                if version is None or self._version != version or left <= 0:
                    return self._said()
                if self._due is not None:
                    left = min(left, max(self._due - self._clock(), 0))
                self._lock.wait(left)

    def _start(self, work):
        with self._lock:
            self._working.add(work)
            self._due = None
            self._close()
            self._lock.notify_all()

    def _end(self, work):
        with self._lock:
            self._working.discard(work)
            if not self._working:
                self._due = self._clock() + self._wait
                # A held ask asleep with no countdown has to wake to the one just opened.
                self._lock.notify_all()

    def _close(self):
        if self._asking:
            self._asking = False
            self._version += 1

    def _ask_if_due(self):
        now = self._clock()
        if self._due is not None and now >= self._due:
            self._asking = True
            self._version += 1
            self._due = now + self._wait

    def _said(self):
        return {"version": self._version, "asking": self._asking}
