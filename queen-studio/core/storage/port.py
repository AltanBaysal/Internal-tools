"""The storage port: what the core asks of its store, in a project's terms, not Drive's files
(FOUNDATION 3; step 4, Depo portu).

A project is four things:

- its row, the main list's line: name, archived, its times, the core running its queue;
- its state, what changes: the frames' order, the edits, the waiting jobs and the queue, running
  exports, files due for the trash. One JSON object the groups shape, written whole by each commit;
- its records, what never changes once written: a frame's photo, a video, a finished job or export;
- its history, one entry per change, numbered by `seq`.

The port knows only what is written whole each time and what once and kept, which is all the
Drive adapter needs: the row and state go to the head file and its properties, records and history
to its tails and blocks. The core knows none of those. Nothing is deleted for good: a project or a
file goes to the store's trash. The same contract tests (tests/storage/contract.py) run on every
adapter.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal, Protocol

# Drive's generateIds gives at most 1000 ids a call.
MOST_RESERVED = 1000
# A list's page at most (530, MOST_LIMIT): history is read a page at a time.
MOST_ENTRIES = 1000
# Step 2's name rule. On Drive the name is cut into at most 3 properties of 124 bytes, key and
# value (step 4): 64 characters are at most 256 bytes of UTF-8, which 3 parts hold with room for
# their keys and for a cut that falls between a character's bytes.
MOST_NAME = 64

# A project's id (step 6) and a core's (core.json) alike.
_ID = re.compile(r"[a-z0-9]{10}")


@dataclass(frozen=True)
class Row:
    name: str
    archived: bool
    created: datetime
    updated: datetime
    # The core whose queue this is, or None when no Colab runs it.
    runner: str | None


@dataclass(frozen=True)
class Listed:
    id: str
    version: str
    row: Row


@dataclass(frozen=True)
class Record:
    kind: str
    # Unique in its project: every kind takes its ids from the project's one counter (step 6).
    id: int
    data: dict[str, Any]


@dataclass(frozen=True)
class Entry:
    # 1 for a project's first change, each change's the one after; a commit out of step is a
    # ValueError on every adapter.
    seq: int
    time: datetime
    data: dict[str, Any]


@dataclass(frozen=True)
class Commit:
    """A change: the row and state after it, and the records and history entries it adds."""

    row: Row
    state: dict[str, Any]
    # The groups' format of the state, records and entries, as this core writes it (step 4,
    # Değerlendirme 11): a core never writes over a project in a newer one.
    format: int
    records: tuple[Record, ...] = ()
    # Usually one; variants made together finish in one write, each with its own (step 4).
    entries: tuple[Entry, ...] = ()


@dataclass(frozen=True)
class Project:
    id: str
    version: str
    row: Row
    state: dict[str, Any]
    # As written, at most the format `load` was given: an older one the core lifts in memory.
    format: int
    records: tuple[Record, ...]  # every one, in the order written
    recent: tuple[Entry, ...]  # since the time `load` was given, by seq


@dataclass(frozen=True)
class Stored:
    ref: str
    size: int
    md5: str


@dataclass(frozen=True)
class Space:
    quota: int | None  # None: no limit
    used: int  # the trash included, as Drive counts it
    trash: int


@dataclass(frozen=True)
class InProject:
    """A project's own files, its photos and videos: they go to the trash with it."""

    project: str


@dataclass(frozen=True)
class InExport:
    """An export's folder, or a folder inside it (`photos/`), opened with `export_folder`."""

    folder: str


Place = InProject | InExport


class StorageError(Exception):
    """What the port raises; ValueError is the core's own mistake, never the store's.

    Each takes its fields as its `args`, so a copy of one is the same error.
    """


class _Said(StorageError):
    # The store's own words and, where it gave one, its code: the core shows both (step 6).
    def __init__(self, said: str, code: str | None = None) -> None:
        super().__init__(said, code)
        self.said = said
        self.code = code

    def __str__(self) -> str:
        return self.said if self.code is None else f"{self.said} ({self.code})"


class Rejected(_Said):
    """The store refused, after the adapter's own waits; nothing was written."""


class Unconfirmed(_Said):
    """A write's outcome is unknown: it may have been made or not. `load` tells which."""


class Unreadable(_Said):
    """The project's data cannot be read; it is never written over (step 4)."""


class NewerFormat(StorageError):
    def __init__(self, found: int, known: int) -> None:
        super().__init__(found, known)
        self.found = found
        self.known = known

    def __str__(self) -> str:
        return f"The project is in format {self.found}; this core knows up to {self.known}."


class NotFound(StorageError):
    """No such project or file, or it is in the trash."""


class Stale(StorageError):
    """The project is no longer at the version the commit expected; nothing was written."""


class Exists(StorageError):
    """`create`'s ref was used before: that creation was made. Nothing was written."""


class Taken(StorageError):
    """Something else is at the ref: one ref was given to two things."""


class TooLarge(StorageError):
    def __init__(self, size: int, most: int) -> None:
        super().__init__(size, most)
        self.size = size
        self.most = most

    def __str__(self) -> str:
        return f"The file has {self.size:,} bytes, past the {self.most:,} asked for."


class Port(Protocol):
    # -- projects --------------------------------------------------------------------------------

    def projects(self) -> tuple[Listed, ...]:
        """Every project but those in the trash, in no set order; an unreadable one too."""
        ...

    def version(self, project: str) -> Listed:
        """The project's version and row, cheaply; an unreadable project's too. NotFound."""
        ...

    def load(self, project: str, since: datetime, format: int) -> Project:
        """The whole project, with the history entries timed at or after `since`.

        NotFound, Unreadable; NewerFormat when it is written in a format past `format`, the
        newest the caller reads.
        """
        ...

    def create(self, project: str, ref: str, change: Commit) -> str:
        """Opens the project at `ref`, from `reserve`; its version.

        Exists when a project was created at `ref` before: that creation was made, and nothing is
        written. Taken when a file or folder is there.
        """
        ...

    def commit(self, project: str, expected: str, change: Commit) -> str:
        """Writes the change; the new version.

        `expected` is the last version this port's load, create or commit gave for the project:
        the one the change was built on. Any other is the core's mistake, a ValueError, since a
        change built on one version and written on another loses what came between. Stale when
        the project has moved on since, and nothing is written; NewerFormat when it is written in
        a format past the change's. The look is no lock: two commits at one moment may both pass
        it, and the later one's whole project stands.
        """
        ...

    def history(self, project: str, before: int | None, count: int) -> tuple[Entry, ...]:
        """The latest `count` entries whose seq is under `before` (None: all), newest first."""
        ...

    def trash_project(self, project: str) -> None:
        """The project and everything in it, its files too, to the trash; done when not there."""
        ...

    # -- files -----------------------------------------------------------------------------------

    def reserve(self, count: int) -> tuple[str, ...]:
        """Refs for `count` files or folders yet to be written: every new one is made at one."""
        ...

    def put(self, ref: str, source: Path, name: str, place: Place) -> Stored:
        """Writes the file on disk at the reserved `ref`.

        The same content again is the same file; other content, or a file at `ref` gone to the
        trash, is Taken: the ref is used. Rejected for a ref never reserved; NotFound when the
        place was never there.
        """
        ...

    def exists(self, ref: str) -> Stored | None:
        """The file at `ref`, its size and md5, or None: one in the trash is not there, nor is a
        folder. A job whose output is already stored finishes from this, with no download."""
        ...

    def get(self, ref: str, target: Path, most: int) -> Stored:
        """Writes the file to `target` on disk, whole or not at all.

        TooLarge past `most` bytes, before anything is written: the caller's bound, its budget
        for the kind of file and the room on its disk. NotFound.
        """
        ...

    def copy(self, source: str, ref: str, name: str, place: Place) -> Stored:
        """A copy inside the store at the reserved `ref`; no byte is downloaded. Again as `put`.
        A source in the trash may still be copied: no adapter is held to refuse it."""
        ...

    def trash(self, ref: str) -> None:
        """The file, or the folder with what is in it, to the trash; done when not there."""
        ...

    def export_folder(self, ref: str, name: str, inside: str | None = None) -> None:
        """Opens an export's folder at the reserved `ref`, or, `inside` one, a folder in it (its
        `photos/`); the same again is done. NotFound when `inside` is not there."""
        ...

    def export_names(self, prefix: str) -> tuple[str, ...]:
        """The export folders whose name begins with `prefix`, case aside, as `ilike` folds it;
        the folders inside them are not exports."""
        ...

    def space(self) -> Space: ...


# The port's operations, by which the in-memory store's faults are injected.
Op = Literal[
    "projects",
    "version",
    "load",
    "create",
    "commit",
    "history",
    "trash_project",
    "reserve",
    "put",
    "exists",
    "get",
    "copy",
    "trash",
    "export_folder",
    "export_names",
    "space",
]
WRITES: frozenset[Op] = frozenset(
    {"create", "commit", "trash_project", "put", "copy", "trash", "export_folder"}
)


# Every adapter's checks, made before the store is asked.


def check_project(project: str) -> None:
    """A project id comes from the address: unchecked, it could name any file."""
    if not _ID.fullmatch(project):
        raise ValueError(f"{project!r} is not a project id: 10 lowercase letters or digits.")


def check_time(time: datetime) -> None:
    """A stored time is UTC to the second (step 6): Drive's properties are text."""
    if time.utcoffset() != timedelta(0) or time.microsecond:
        raise ValueError(f"{time.isoformat()} is not a UTC time to the second.")


def check_row(row: Row) -> None:
    """A row fits the properties Drive keeps it in."""
    if not 1 <= len(row.name) <= MOST_NAME:
        raise ValueError(f"A project's name has 1 to {MOST_NAME} characters, not {len(row.name)}.")
    if row.runner is not None and not _ID.fullmatch(row.runner):
        raise ValueError(f"{row.runner!r} is not a core id: 10 lowercase letters or digits.")
    check_time(row.created)
    check_time(row.updated)


def check_entries(last: int, entries: tuple[Entry, ...]) -> None:
    """History in step: each entry's seq the one after `last`, the project's latest (0 for none).

    Lost changes are found by their seq (step 4, Değerlendirme 4).
    """
    for entry in entries:
        if entry.seq != last + 1:
            raise ValueError(f"History entry seq {entry.seq} does not follow {last}.")
        check_time(entry.time)
        last = entry.seq


def check_count(what: str, count: int, most: int) -> None:
    if not 1 <= count <= most:
        raise ValueError(f"{what} is {count}; it takes 1 to {most}.")
