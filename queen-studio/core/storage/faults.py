"""What one core meets on its way to the in-memory store: injected faults, and its calls counted.

A fault is injected by operation, and may be held to one project's calls and let a number of
calls pass first (step 4, Bellek içi adaptör; step 12). On a call, every fault due that lets it
go on fires first — a slowness, a hook, a drop after the write — in the order injected; then the
first one due that stops it, a refusal or a drop before the write. One that stops it is spent only
when it fires. The calls are counted here too, with the project each touches: the later items'
cost tests read them.
"""

import threading
from collections.abc import Callable
from dataclasses import dataclass

from core.clock.clock import Clock
from core.storage.port import WRITES, Op, Rejected, Unconfirmed


@dataclass(frozen=True)
class Refuse:
    """The store refuses, as Drive does once the adapter's waits are spent: nothing is done."""

    said: str
    code: str | None = None


@dataclass(frozen=True)
class Drop:
    """The line drops before the store has the write, or, `after`, once it is made: Unconfirmed."""

    after: bool = False
    said: str = "The connection was lost before the store answered."


@dataclass(frozen=True)
class Slow:
    """The clock's sleep first: a ManualClock moves on and no real second passes."""

    seconds: float


@dataclass(frozen=True)
class Run:
    """`then()` before the operation; `between`, after a commit's look and before its write."""

    then: Callable[[], object]
    between: bool = False


Fault = Refuse | Drop | Slow | Run


@dataclass(frozen=True)
class Due:
    """What fires once the store has done its part."""

    dropped: Drop | None
    between: tuple[Callable[[], object], ...]

    def leave(self) -> None:
        if self.dropped is not None:
            raise Unconfirmed(self.dropped.said)


@dataclass
class _Pending:
    op: Op
    fault: Fault
    left: int  # calls it still fires on
    skip: int  # calls it lets pass first
    project: str | None  # only this project's calls, or every one


def _stops(fault: Fault) -> bool:
    return isinstance(fault, Refuse) or (isinstance(fault, Drop) and not fault.after)


class Faults:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._lock = threading.Lock()
        self._pending: list[_Pending] = []
        # Each call in order, with the project it touches; a refused one too: it reached the store.
        self.calls: list[tuple[Op, str | None]] = []

    def inject(self, op: Op, fault: Fault, times: int, skip: int, project: str | None) -> None:
        if times < 1 or skip < 0:
            raise ValueError(
                f"times is {times}, skip {skip}: a fault fires once or more, after 0 calls or more."
            )
        if isinstance(fault, Drop) and op not in WRITES:
            raise ValueError(f"{op} writes nothing, so there is nothing to drop.")
        if isinstance(fault, Run) and fault.between and op != "commit":
            raise ValueError("Only a commit has a look and a write to run between.")
        with self._lock:
            self._pending.append(_Pending(op, fault, times, skip, project))

    def enter(self, op: Op, project: str | None = None) -> Due:
        """Counts the call and fires the faults due on it (the module says in which order); what
        fires after the store's part is returned.

        No lock is held while a fault fires: a hook may call the store, and a held hook keeps no
        other call waiting.
        """
        with self._lock:
            self.calls.append((op, project))
            due: list[_Pending] = []
            for pending in self._pending:
                if pending.op != op or pending.project not in (None, project):
                    continue
                if pending.skip:
                    pending.skip -= 1
                else:
                    due.append(pending)
            stopping = [pending for pending in due if _stops(pending.fault)][:1]
            fired = [pending for pending in due if not _stops(pending.fault)] + stopping
            for pending in fired:
                pending.left -= 1
            self._pending = [pending for pending in self._pending if pending.left]
        dropped: Drop | None = None
        between: list[Callable[[], object]] = []
        for pending in fired:
            match pending.fault:
                case Slow(seconds=seconds):
                    self._clock.sleep(seconds)
                case Run(then=then, between=True):
                    between.append(then)
                case Run(then=then):
                    then()
                case Refuse(said=said, code=code):
                    raise Rejected(said, code)
                case Drop(after=False, said=said):
                    raise Unconfirmed(said)
                case Drop() as after:
                    dropped = after
        return Due(dropped, tuple(between))
