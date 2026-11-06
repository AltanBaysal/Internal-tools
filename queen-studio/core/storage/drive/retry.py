"""Waiting on Drive: which errors are tried again, for how long, and what each ends as (step 4,
Değerlendirme 9; the m532 spec, Hatalar ve bekleme).

Drive's guide asks for exponential backoff on its rate limit; 528 measured it slowing rather than
refusing, with an occasional 503. So a call is tried again with waits of 1, 2, 4… up to 32 s, each
with up to a second's jitter, for about a minute of the clock's time — the time the calls took
included, so a call that hangs until its timeout spends the same budget. The clock is handed in:
a test's ManualClock waits no real second.

Three waits, one for each kind of call:

- `read`: tried again, then Rejected in Drive's words;
- `again`, a write the same twice is harmless (a block, the trash, a folder at a reserved id):
  tried again, then Unconfirmed if a try may have been made, Rejected if none was;
- `written`, a head file's write: looked at before each new try, so a lost write never goes over
  another core's.

Drive's 404 and 409 are no failure to wait out: they reach the caller as Missing and Conflict,
for it to name; so does a 400 on a create at a reserved id, as Unusable, when the caller can take
another id.
"""

import random
from collections.abc import Callable
from datetime import datetime, timedelta

from core.clock.clock import Clock
from core.storage.drive.api import DriveError, DriveLost
from core.storage.port import Rejected, StorageError, Unconfirmed

BUDGET = 60
CAP = 32
_RATE_REASONS = frozenset({"userRateLimitExceeded", "rateLimitExceeded"})
_SERVER = frozenset({500, 502, 503, 504})


class Missing(Exception):
    """Drive's 404, in its words."""


class Conflict(Exception):
    """Drive's 409 on a create: something is at the id. `uncertain`: an earlier try of this same
    create got no answer, so what is there may be its own."""

    def __init__(self, uncertain: bool) -> None:
        super().__init__(uncertain)
        self.uncertain = uncertain


class Unusable(Exception):
    """Drive's 400 on a create at a reserved id: reserved ids may expire (528, 6)."""

    def __init__(self, failed: DriveError) -> None:
        super().__init__(failed.said, failed.reason)
        self.said = failed.said
        self.code = failed.reason


def refusal(error: DriveError | DriveLost) -> bool:
    """Drive refused for the rate: it did nothing."""
    return isinstance(error, DriveError) and (
        error.status == 429 or (error.status == 403 and error.reason in _RATE_REASONS)
    )


def retryable(error: DriveError | DriveLost) -> bool:
    """Worth another try: the rate, Drive's own failures, or no answer at all."""
    return isinstance(error, DriveLost) or refusal(error) or error.status in _SERVER


class Backoff:
    """One operation's waits."""

    def __init__(
        self,
        clock: Clock,
        budget: float = BUDGET,
        jitter: Callable[[], float] = random.random,
        until: datetime | None = None,
    ) -> None:
        """`until`: a deadline the budget never passes."""
        self._clock = clock
        end = clock.now() + timedelta(seconds=budget)
        self._end = end if until is None else min(end, until)
        self._jitter = jitter
        self._tries = 0

    def wait(self) -> bool:
        """Sleeps before the next try; False, without sleeping, once it would pass the budget."""
        pause = min(2**self._tries, CAP) + self._jitter()
        if self._clock.now() + timedelta(seconds=pause) > self._end:
            return False
        self._tries += 1
        self._clock.sleep(pause)
        return True


def read[T](clock: Clock, call: Callable[[], T]) -> T:
    backoff = Backoff(clock)
    while True:
        try:
            return call()
        except DriveError as failed:
            if failed.status == 404:
                raise Missing(failed.said) from None
            if not retryable(failed) or not backoff.wait():
                raise Rejected(failed.said, failed.reason) from failed
        except DriveLost as failed:
            if not backoff.wait():
                raise Rejected(failed.said) from failed


def again[T](clock: Clock, call: Callable[[], T], fresh: bool = False) -> T:
    """`fresh`: a create at a reserved id the caller can replace, so a 400 is Unusable."""
    backoff = Backoff(clock)
    uncertain = False
    while True:
        try:
            return call()
        except DriveError as failed:
            if failed.status == 404:
                raise Missing(failed.said) from None
            if failed.status == 409:
                raise Conflict(uncertain) from None
            if failed.status == 400 and fresh:
                raise Unusable(failed) from None
            uncertain |= _may_be_made(failed)
            if not retryable(failed) or not backoff.wait():
                raise _ended(uncertain, failed) from failed
        except DriveLost as failed:
            uncertain = True
            if not backoff.wait():
                raise _ended(uncertain, failed) from failed


def written(
    clock: Clock,
    write: Callable[[], object],
    look: Callable[[], str],
    new: str,
    expected: str,
    deadline: datetime,
) -> None:
    """`write` until the md5 `look` gives is `new`. After a failed try it looks first: `new` means
    it was made, `expected` that it may be made again, any other that another core wrote — and
    whether this one came first is unknown: Unconfirmed.

    No try starts past `deadline`, and the waits end there: a head written later could name a
    block another core has since put in the trash (the m532 spec, Mühür). Past it: Rejected, or
    Unconfirmed if an earlier try may have been made.
    """
    backoff = Backoff(clock, until=deadline)
    uncertain = False
    last: DriveError | DriveLost | None = None
    while True:
        if clock.now() > deadline:
            said = f"The change passed its deadline, {deadline:%H:%M:%S} UTC, before its write."
            if last is not None:
                said = f"{said} {last.said}"
            raise Unconfirmed(said) if uncertain else Rejected(said)
        try:
            write()
            return
        except DriveError as failed:
            if failed.status == 404:
                raise Missing(failed.said) from None
            uncertain |= _may_be_made(failed)
            if not retryable(failed):
                raise _ended(uncertain, failed) from failed
            last = failed
        except DriveLost as failed:
            uncertain, last = True, failed
        md5 = _look_again(backoff, look, uncertain, last)
        if md5 == new:
            return
        if md5 != expected:
            raise Unconfirmed(f"Another core wrote the project meanwhile. {last.said}")


def _look_again(
    backoff: Backoff, look: Callable[[], str], uncertain: bool, last: DriveError | DriveLost
) -> str:
    while backoff.wait():
        try:
            return look()
        except DriveError as failed:
            if failed.status == 404:
                raise Missing(failed.said) from None
            if not retryable(failed):
                raise _ended(uncertain, failed) from failed
        except DriveLost:
            pass
    raise _ended(uncertain, last)


def _may_be_made(failed: DriveError) -> bool:
    """Drive's own failure may come after the write was made; its 4xx refused before it."""
    return failed.status >= 500


def _ended(uncertain: bool, failed: DriveError | DriveLost) -> StorageError:
    code = failed.reason if isinstance(failed, DriveError) else None
    return Unconfirmed(failed.said, code) if uncertain else Rejected(failed.said, code)
