"""The clock, a gate: what the core and its adapters take the time and their waits from.

Whatever waits — the in-memory store's slowness, the Drive adapter's backoff, the core's 5 s and
30 s looks — is handed a clock, so no test waits a real second (step 12): a test hands in a
ManualClock, whose sleep moves its time on and returns at once. The real clock is wired in the start
file with the first thing that waits on Drive (v1-8).
"""

import threading
from datetime import datetime, timedelta
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        """The time, in UTC."""
        ...

    def sleep(self, seconds: float) -> None: ...


class ManualClock:
    """A clock that moves only when told: `sleep` moves it on and returns at once."""

    def __init__(self, start: datetime) -> None:
        if start.utcoffset() != timedelta(0):
            raise ValueError(f"{start.isoformat()} is not in UTC; the clock's time is.")
        self._now = start
        # Cores in one test may run in threads, each sleeping on the same clock.
        self._lock = threading.Lock()

    def now(self) -> datetime:
        with self._lock:
            return self._now

    def sleep(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError(f"A clock does not go back: sleep({seconds}).")
        with self._lock:
            self._now += timedelta(seconds=seconds)
