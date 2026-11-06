"""What one Drive port keeps between calls, per project (the m531 spec, Sonraki maddeler için):

- where its head file and folder are, from listings and lookups: as many as there are projects;
- the last version the port gave, what a commit must be built on: one per project loaded;
- that version's head, opened (~1 MB at 20,000 frames), for the last `bases` projects used and
  never past `bases_bytes` opened: a commit builds on it with no download. One that left keeps
  its version given, and its commit reads the head once more.

The base kept is always the version given: nothing else is put in its place.
"""

import threading
from collections import OrderedDict
from dataclasses import dataclass

from core.storage.drive.head import Head


@dataclass(frozen=True)
class Where:
    head: str
    folder: str | None  # None while the head's properties cannot be read


@dataclass(frozen=True)
class _Base:
    version: str
    head: Head
    size: int  # its bytes opened


class Kept:
    def __init__(self, bases: int, bases_bytes: int) -> None:
        self._most = bases
        self._most_bytes = bases_bytes
        self._lock = threading.Lock()
        self._where: dict[str, Where] = {}
        self._given: dict[str, str] = {}
        self._bases: OrderedDict[str, _Base] = OrderedDict()
        self._bytes = 0

    def where(self, project: str) -> Where | None:
        with self._lock:
            return self._where.get(project)

    def remember(self, project: str, where: Where) -> None:
        with self._lock:
            self._where[project] = where

    def given(self, project: str) -> str | None:
        with self._lock:
            return self._given.get(project)

    def base(self, project: str, version: str) -> tuple[Head, int] | None:
        """The head of `version` and its bytes opened, if that is the one kept."""
        with self._lock:
            base = self._bases.get(project)
            if base is None or base.version != version:
                return None
            self._bases.move_to_end(project)
            return base.head, base.size

    def keep(self, project: str, version: str, head: Head, size: int) -> None:
        """`version` given, with its head of `size` bytes opened."""
        with self._lock:
            self._given[project] = version
            self._drop(project)
            self._bases[project] = _Base(version, head, size)
            self._bytes += size
            # The newest stays, whatever its size: the commit it serves would read it again.
            while len(self._bases) > 1 and (
                len(self._bases) > self._most or self._bytes > self._most_bytes
            ):
                self._drop(next(iter(self._bases)))

    def forget(self, project: str, given: bool = False) -> None:
        """The project is not where it was. Its version given stays unless it was trashed here:
        a commit built on it still meets NotFound, not a ValueError."""
        with self._lock:
            self._where.pop(project, None)
            self._drop(project)
            if given:
                self._given.pop(project, None)

    def _drop(self, project: str) -> None:
        # Under the lock.
        base = self._bases.pop(project, None)
        if base is not None:
            self._bytes -= base.size
