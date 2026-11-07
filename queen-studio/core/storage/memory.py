"""The in-memory store: the port as the tests run it (step 4, Bellek içi adaptör; step 12).

It imitates the Drive adapter: a file is made only at a ref reserved for it, the same write again is
harmless, md5 and size come back, projects are listed, the trash and a quota are there, and a
commit's look is no lock. It lists in one go, where Drive pages: paging is the Drive adapter's own
to test. A MemoryStore is the data, what Drive is to the Colabs; each `open` is one core's port onto
it, so a second core, or a restarted one, opens on the same store. Each port has its own faults and
counted calls (core/storage/faults.py), remembers the versions it handed out, and sleeps on the
clock it was opened with.

What is stored is JSON text, as on Drive: a value JSON cannot hold fails here too, and nothing the
core changes after writing, or in what it read, reaches the store. Every operation holds one lock
for its part, never across a fault's hook.
"""

import copy
import hashlib
import json
import os
import tempfile
import threading
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Any

from core.clock.clock import Clock
from core.lists.pattern import fold
from core.storage.faults import Fault, Faults
from core.storage.port import (
    MOST_ENTRIES,
    MOST_RESERVED,
    Commit,
    Entry,
    Exists,
    InExport,
    InProject,
    Listed,
    NewerFormat,
    NotFound,
    Op,
    Place,
    Project,
    Record,
    Rejected,
    Row,
    Space,
    Stale,
    Stored,
    Taken,
    TooLarge,
    Unreadable,
    check_count,
    check_entries,
    check_project,
    check_row,
    check_time,
)


@dataclass(frozen=True)
class _Snapshot:
    """A project as it stands; a commit puts a new one in its place."""

    ref: str
    version: str
    row: Row
    state: str
    format: int
    records: tuple[tuple[str, int, str], ...]  # kind, id, data
    entries: tuple[tuple[int, datetime, str], ...]  # seq, time, data
    spoiled: Unreadable | None = None


@dataclass(frozen=True)
class _Packed:
    """A change as it will be stored, made before the store is asked."""

    row: Row
    state: str
    format: int
    records: tuple[tuple[str, int, str], ...]
    entries: tuple[tuple[int, datetime, str], ...]


@dataclass
class _File:
    place: Place
    name: str
    content: bytes
    md5: str
    trashed: bool = False


@dataclass
class _Folder:
    name: str
    parent: str | None  # the export folder it is in, or None for an export's own
    trashed: bool = False


class _Data:
    def __init__(self, quota: int | None) -> None:
        self.lock = threading.Lock()
        self.quota = quota
        self.projects: dict[str, _Snapshot] = {}
        self.files: dict[str, _File] = {}
        self.folders: dict[str, _Folder] = {}
        # The refs projects were created at: used for good, the project trashed or not.
        self.heads: set[str] = set()
        self.reserved: set[str] = set()
        self._counter = 0

    def next(self) -> int:
        """Refs and versions alike; under the lock."""
        self._counter += 1
        return self._counter


class MemoryStore:
    """The store's data, shared by every core opened on it."""

    def __init__(self, quota: int | None = None) -> None:
        self._data = _Data(quota)

    @property
    def quota(self) -> int | None:
        return self._data.quota

    @quota.setter
    def quota(self, quota: int | None) -> None:
        """Changed as the user frees or fills their Drive (v1-18's `storage_low`)."""
        with self._data.lock:
            self._data.quota = quota

    def open(self, clock: Clock) -> "MemoryPort":
        return MemoryPort(self._data, clock)

    def spoil(self, project: str, said: str) -> None:
        """The project as a crash or a hand on Drive might leave it: listed, its version moved, and
        never read or written; `said` is what the reader says."""
        with self._data.lock:
            found = self._data.projects.get(project)
            if found is None:
                raise NotFound(f"There is no project {project}.")
            version = str(self._data.next())
            self._data.projects[project] = replace(found, version=version, spoiled=Unreadable(said))


class MemoryPort:
    """One core's port onto a MemoryStore."""

    def __init__(self, data: _Data, clock: Clock) -> None:
        self._data = data
        self._faults = Faults(clock)
        # Per project, the last version this port's load, create or commit gave: what a commit
        # may build on. The Drive adapter keeps the head file that goes with it.
        self._given: dict[str, str] = {}
        self._lock = threading.Lock()

    def inject(
        self,
        op: Op,
        fault: Fault,
        times: int = 1,
        *,
        skip: int = 0,
        project: str | None = None,
    ) -> None:
        """`op`'s next `times` calls meet the fault, after `skip` calls pass untouched; with
        `project`, only calls touching it. core/storage/faults.py says the order they fire in."""
        self._faults.inject(op, fault, times, skip, project)

    @property
    def calls(self) -> list[tuple[Op, str | None]]:
        """Each call in order, with the project it touches; a refused one too."""
        return self._faults.calls

    # -- projects --------------------------------------------------------------------------------

    def projects(self) -> tuple[Listed, ...]:
        self._faults.enter("projects")
        with self._data.lock:
            return tuple(
                Listed(project, found.version, found.row)
                for project, found in self._data.projects.items()
            )

    def version(self, project: str) -> Listed:
        check_project(project)
        self._faults.enter("version", project)
        with self._data.lock:
            found = self._snapshot(project)
        return Listed(project, found.version, found.row)

    def load(self, project: str, since: datetime, format: int) -> Project:
        check_project(project)
        self._faults.enter("load", project)
        with self._data.lock:
            found = self._readable(project)
        if found.format > format:
            raise NewerFormat(found.format, format)
        self._give(project, found.version)
        return Project(
            id=project,
            version=found.version,
            row=found.row,
            state=json.loads(found.state),
            format=found.format,
            records=tuple(Record(kind, id, json.loads(data)) for kind, id, data in found.records),
            recent=tuple(
                Entry(seq, time, json.loads(data))
                for seq, time, data in found.entries
                if time >= since
            ),
        )

    def create(self, project: str, ref: str, change: Commit) -> str:
        check_project(project)
        packed = _pack(change)
        due = self._faults.enter("create", project)
        with self._data.lock:
            if ref in self._data.heads:
                raise Exists(f"A project was created at {ref} before.")
            if self._used(ref):
                raise Taken(f"A file or folder is at {ref}.")
            if ref not in self._data.reserved:
                raise Rejected(f"{ref} was never reserved.")
            if project in self._data.projects:
                raise ValueError(f"Project {project} is there already, at another ref.")
            _guard(None, change)
            version = str(self._data.next())
            self._data.projects[project] = _Snapshot(
                ref,
                version,
                packed.row,
                packed.state,
                packed.format,
                packed.records,
                packed.entries,
            )
            self._data.heads.add(ref)
        due.leave()
        self._give(project, version)
        return version

    def commit(self, project: str, expected: str, change: Commit) -> str:
        check_project(project)
        with self._lock:
            given = self._given.get(project)
        if expected != given:
            raise ValueError(
                f"{expected} is not the version this port last gave for {project} ({given}): "
                "a change is built on what was loaded."
            )
        packed = _pack(change)
        due = self._faults.enter("commit", project)
        with self._data.lock:
            base = self._snapshot(project)
            # The version first, as Drive's md5 is: an unreadable project's moved when it broke.
            if base.version != expected:
                raise Stale(f"Project {project} is at {base.version}, not {expected}.")
            if base.spoiled is not None:
                raise copy.copy(base.spoiled)
            if base.format > change.format:
                raise NewerFormat(base.format, change.format)
            _guard(base, change)
            version = None if due.between else self._write(project, base, packed)
        if version is None:
            for then in due.between:
                then()
            # Whatever was written meanwhile is lost whole: the project is the base and this change.
            with self._data.lock:
                version = self._write(project, base, packed)
        # A dropped answer leaves the version given as it was: the core loads to learn which holds.
        due.leave()
        self._give(project, version)
        return version

    def history(self, project: str, before: int | None, count: int) -> tuple[Entry, ...]:
        check_project(project)
        check_count("count", count, MOST_ENTRIES)
        self._faults.enter("history", project)
        with self._data.lock:
            found = self._readable(project)
        kept = [each for each in found.entries if before is None or each[0] < before][-count:]
        return tuple(Entry(seq, time, json.loads(data)) for seq, time, data in reversed(kept))

    def trash_project(self, project: str) -> None:
        check_project(project)
        due = self._faults.enter("trash_project", project)
        with self._data.lock:
            self._data.projects.pop(project, None)
        with self._lock:
            self._given.pop(project, None)
        due.leave()

    # -- files -----------------------------------------------------------------------------------

    def reserve(self, count: int) -> tuple[str, ...]:
        check_count("count", count, MOST_RESERVED)
        self._faults.enter("reserve")
        with self._data.lock:
            refs = tuple(f"m{self._data.next()}" for _ in range(count))
            self._data.reserved.update(refs)
        return refs

    def put(self, ref: str, source: Path, name: str, place: Place) -> Stored:
        due = self._faults.enter("put", _project_of(place))
        size = source.stat().st_size
        with self._data.lock:
            existing = self._data.files.get(ref)
            if existing is None:
                self._fresh(ref, place, size)
            # Read under the lock, after the quota's look: a test's file is a few bytes, and one
            # section keeps a second put of the same ref from slipping in between.
            content = source.read_bytes()
            stored = Stored(ref, len(content), hashlib.md5(content).hexdigest())
            if existing is None:
                self._data.files[ref] = _File(place, name, content, stored.md5)
            elif not self._alive(existing) or (len(existing.content), existing.md5) != (
                stored.size,
                stored.md5,
            ):
                raise Taken(f"Another file, or one in the trash, is at {ref}.")
        due.leave()
        return stored

    def exists(self, ref: str) -> Stored | None:
        self._faults.enter("exists", self._project_at(ref))
        with self._data.lock:
            file = self._data.files.get(ref)
            if file is None or not self._alive(file):
                return None
            return Stored(ref, len(file.content), file.md5)

    def get(self, ref: str, target: Path, most: int) -> Stored:
        self._faults.enter("get", self._project_at(ref))
        with self._data.lock:
            file = self._data.files.get(ref)
            if file is None or not self._alive(file):
                raise NotFound(f"There is no file {ref}.")
        if len(file.content) > most:
            raise TooLarge(len(file.content), most)
        _write_whole(target, file.content)
        return Stored(ref, len(file.content), file.md5)

    def copy(self, source: str, ref: str, name: str, place: Place) -> Stored:
        into = _project_of(place)
        due = self._faults.enter("copy", self._project_at(source) or into)
        with self._data.lock:
            original = self._data.files.get(source)
            if original is None or not self._alive(original):
                raise NotFound(f"There is no file {source}.")
            existing = self._data.files.get(ref)
            if existing is None:
                self._fresh(ref, place, len(original.content))
                self._data.files[ref] = _File(place, name, original.content, original.md5)
            elif not self._alive(existing) or (len(existing.content), existing.md5) != (
                len(original.content),
                original.md5,
            ):
                raise Taken(f"Another file, or one in the trash, is at {ref}.")
        due.leave()
        return Stored(ref, len(original.content), original.md5)

    def trash(self, ref: str) -> None:
        due = self._faults.enter("trash", self._project_at(ref))
        with self._data.lock:
            found = self._data.files.get(ref) or self._data.folders.get(ref)
            if found is not None:
                found.trashed = True
        due.leave()

    def export_folder(self, ref: str, name: str, inside: str | None = None) -> None:
        due = self._faults.enter("export_folder")
        with self._data.lock:
            found = self._data.folders.get(ref)
            if found is None:
                self._fresh(ref)
                if inside is not None and not self._folder_there(inside):
                    raise NotFound(f"There is no export folder {inside}.")
                self._data.folders[ref] = _Folder(name, inside)
            elif (found.name, found.parent) != (name, inside):
                raise Taken(f"Folder {ref} is {found.name!r} in {found.parent}.")
        due.leave()

    def export_names(self, prefix: str) -> tuple[str, ...]:
        self._faults.enter("export_names")
        start = fold(prefix)
        with self._data.lock:
            return tuple(
                sorted(
                    folder.name
                    for folder in self._data.folders.values()
                    if folder.parent is None
                    and not folder.trashed
                    and fold(folder.name).startswith(start)
                )
            )

    def space(self) -> Space:
        self._faults.enter("space")
        with self._data.lock:
            files = self._data.files.values()
            trash = sum(len(file.content) for file in files if not self._alive(file))
            return Space(self._data.quota, self._used_bytes(), trash)

    # -- inside, the store's lock held where named -----------------------------------------------

    def _give(self, project: str, version: str) -> None:
        with self._lock:
            self._given[project] = version

    def _project_at(self, ref: str) -> str | None:
        """The project whose file is at `ref`, for the count of calls."""
        with self._data.lock:
            file = self._data.files.get(ref)
        return None if file is None else _project_of(file.place)

    def _snapshot(self, project: str) -> _Snapshot:
        # Under the store's lock.
        found = self._data.projects.get(project)
        if found is None:
            raise NotFound(f"There is no project {project}.")
        return found

    def _readable(self, project: str) -> _Snapshot:
        # Under the store's lock.
        found = self._snapshot(project)
        if found.spoiled is not None:
            raise copy.copy(found.spoiled)
        return found

    def _write(self, project: str, base: _Snapshot, packed: _Packed) -> str:
        # Under the store's lock. A project trashed meanwhile stays trashed, as Drive's head would.
        if project not in self._data.projects:
            raise NotFound(f"Project {project} went to the trash meanwhile.")
        version = str(self._data.next())
        self._data.projects[project] = _Snapshot(
            base.ref,
            version,
            packed.row,
            packed.state,
            packed.format,
            base.records + packed.records,
            base.entries + packed.entries,
        )
        return version

    def _used(self, ref: str) -> bool:
        # Under the store's lock.
        return ref in self._data.files or ref in self._data.folders or ref in self._data.heads

    def _fresh(self, ref: str, place: Place | None = None, size: int = 0) -> None:
        """Refuses a new file or folder of `size` bytes at `ref`, in `place`, unless it may be."""
        # Under the store's lock.
        if self._used(ref):
            raise Taken(f"Something else is at {ref}.")
        if ref not in self._data.reserved:
            raise Rejected(f"{ref} was never reserved.")
        if place is not None and not self._there(place):
            raise NotFound(f"There is no {place}.")
        quota = self._data.quota
        if quota is not None and self._used_bytes() + size > quota:
            raise Rejected("The storage quota is used up.", "storageQuotaExceeded")

    def _there(self, place: Place) -> bool:
        # Under the store's lock.
        match place:
            case InProject(project=project):
                return project in self._data.projects
            case InExport(folder=ref):
                return self._folder_there(ref)

    def _folder_there(self, ref: str) -> bool:
        # Under the store's lock: neither it nor the export folder it is in trashed.
        folder = self._data.folders.get(ref)
        if folder is None or folder.trashed:
            return False
        return folder.parent is None or self._folder_there(folder.parent)

    def _alive(self, file: _File) -> bool:
        # Under the store's lock: not trashed, nor the project or folder it is in.
        return not file.trashed and self._there(file.place)

    def _used_bytes(self) -> int:
        # Under the store's lock: the trash counts, as on Drive.
        return sum(len(file.content) for file in self._data.files.values())


def _project_of(place: Place) -> str | None:
    if isinstance(place, InExport):
        return None
    # An id from the address may reach a place: checked before anything is looked up.
    check_project(place.project)
    return place.project


def _pack(change: Commit) -> _Packed:
    """The change as JSON text; ValueError for what Drive could not store either."""
    check_row(change.row)
    for entry in change.entries:
        check_time(entry.time)
    return _Packed(
        change.row,
        _json(change.state),
        change.format,
        tuple((record.kind, record.id, _json(record.data)) for record in change.records),
        tuple((entry.seq, entry.time, _json(entry.data)) for entry in change.entries),
    )


def _json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    except TypeError as wrong:  # a value JSON has no form for; NaN is already a ValueError
        raise ValueError(f"Not JSON: {wrong}") from wrong


def _guard(base: _Snapshot | None, change: Commit) -> None:
    """History in step, every adapter's rule; and, this store's alone, a record written once:
    the Drive adapter does not hold every record to look."""
    check_entries(base.entries[-1][0] if base and base.entries else 0, change.entries)
    ids = {id for _, id, _ in base.records} if base else set[int]()
    for record in change.records:
        if record.id in ids:
            raise ValueError(f"Record {record.id} is written already; a record never changes.")
        ids.add(record.id)


def _write_whole(target: Path, content: bytes) -> None:
    """Beside it, then into place: a crash leaves no half file at `target`."""
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=target.parent, prefix=target.name, suffix=".part")
    try:
        with os.fdopen(handle, "wb") as out:
            out.write(content)
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
