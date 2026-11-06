"""The Drive adapter: the port's project operations on Drive (step 4, Depo; the m532 spec).

A project is its head file `projects/<p>.json.gz`, whose md5 is its version and whose properties
are its row, and its blocks in the folder `projects/<p>/`. A change is two calls: look at the
head's md5, then write its content and properties in one multipart update — and, every hundred
or so changes, a block first. The port looks; commit.py writes; seal.py plans; blocks.py reads.

What the port keeps between calls is kept.py's, its reserved ids pool.py's. Every Drive call goes
through one of retry.py's three waits and ends in Drive's own words; a 404 is named where it
happens. Within one core a project's commits go one at a time, as on every store: a second built
on the same version meets Stale. Across cores the look is no lock (m531). The file operations
are v1-9's.
"""

import hashlib
import logging
import re
import threading
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from core.clock.clock import Clock
from core.disk.cache import DiskCache
from core.storage.drive.api import FOLDER, DriveApi
from core.storage.drive.blocks import Blocks
from core.storage.drive.commit import Writer
from core.storage.drive.head import (
    DRIVE_ID,
    GZIP,
    MD5,
    Head,
    Stream,
    new_write,
    pack_head,
    parse_entry,
    parse_record,
    properties,
    read_folder,
    read_head,
    read_row,
)
from core.storage.drive.kept import Kept, Where
from core.storage.drive.limits import Limits
from core.storage.drive.pool import Pool
from core.storage.drive.retry import Conflict, Missing, again, read
from core.storage.drive.seal import sealable
from core.storage.drive.writes import folder_at, trash
from core.storage.port import (
    MOST_ENTRIES,
    MOST_RESERVED,
    Commit,
    Entry,
    Exists,
    Listed,
    NewerFormat,
    NotFound,
    Place,
    Project,
    Rejected,
    Space,
    Stale,
    StorageError,
    Stored,
    Taken,
    Unreadable,
    check_count,
    check_entries,
    check_project,
    check_row,
)

PROJECTS = "projects"
# What a look at a head asks: its version, its size before any download, its row, its trash.
HEAD_FIELDS = "id,md5Checksum,size,properties,trashed"
_LIST_FIELDS = "id,name,mimeType,md5Checksum,properties"
_HEAD_NAME = re.compile(r"([a-z0-9]{10})\.json\.gz")
_PROJECT = re.compile(r"[a-z0-9]{10}")
# A head that changes between its look and its download is read again, this many times in all.
_LOAD_TRIES = 3
_FILES = "Drive's file operations come with v1-9."

log = logging.getLogger("core.storage")


@dataclass(frozen=True)
class _Seen:
    """A head as one look found it."""

    where: Where
    md5: str
    size: int
    properties: object


class DrivePort:
    """One core's port onto the projects in a Drive root folder."""

    def __init__(
        self,
        api: DriveApi,
        projects: str,
        clock: Clock,
        cache: DiskCache,
        limits: Limits,
        pool: Pool,
    ) -> None:
        self._api = api
        self._projects = projects
        self._clock = clock
        self._limits = limits
        self._pool = pool
        self._kept = Kept(limits.bases, limits.bases_bytes)
        self._blocks = Blocks(api, clock, cache, limits)
        self._writer = Writer(api, clock, pool, self._blocks, limits, projects)
        self._locks_lock = threading.Lock()
        self._locks: dict[str, threading.Lock] = {}

    @classmethod
    def open(
        cls,
        api: DriveApi,
        root: str,
        clock: Clock,
        cache: DiskCache,
        limits: Limits | None = None,
    ) -> "DrivePort":
        """Finds `projects/` in the root, or makes it, and lists it once: where each head is, and
        the folders of projects whose head went to the trash without them."""
        pool = Pool(api, clock)
        projects = _projects_folder(api, clock, pool, root)
        port = cls(api, projects, clock, cache, limits or Limits(), pool)
        port._tidy()
        return port

    def close(self) -> None:
        """Ends the port's download threads; the start file closes it with the core."""
        self._blocks.close()

    # -- projects --------------------------------------------------------------------------------

    def projects(self) -> tuple[Listed, ...]:
        """Each head: one whose content cannot be read is listed; one whose properties cannot be
        is left out and logged, since the port's Listed has a row and Drive holds none."""
        listed: list[Listed] = []
        for found in self._listing(folders=False):
            project = _project_of(found)
            md5 = found.get("md5Checksum")
            if project is None or not isinstance(md5, str):
                continue
            props = found.get("properties")
            try:
                row = read_row(props)
            except Unreadable as unreadable:
                log.warning("Project %s is left out of the list: %s", project, unreadable)
                continue
            self._kept.remember(project, Where(str(found["id"]), _folder_or_none(props)))
            listed.append(Listed(project, md5, row))
        return tuple(listed)

    def version(self, project: str) -> Listed:
        check_project(project)
        seen = self._look(project)
        return Listed(project, seen.md5, read_row(seen.properties))

    def load(self, project: str, since: datetime, format: int) -> Project:
        check_project(project)
        for _ in range(_LOAD_TRIES):
            seen = self._look(project)
            row = read_row(seen.properties)
            kept = self._kept.base(project, seen.md5)
            if kept is not None:
                head, size = kept
                break
            data = self._download_head(seen)
            if hashlib.md5(data).hexdigest() == seen.md5:
                head, size = read_head(data, self._limits.head_most)
                break
        else:
            raise Rejected(
                f"Project {project}'s head file changed while it was read, {_LOAD_TRIES} times."
            )
        if head.format > format:
            raise NewerFormat(head.format, format)
        history = tuple(
            block for block in head.history.blocks if block.latest is None or block.latest >= since
        )
        blocks = head.records.blocks + history
        whole = size + sum(block.size for block in blocks)
        if whole > self._limits.project_most:
            raise Unreadable(
                f"Project {project} opens to {whole:,} bytes, past the "
                f"{self._limits.project_most:,} a project may have."
            )
        lines = self._blocks.lines(blocks)
        split = len(head.records.blocks)
        records = [parse_record(line) for each in lines[:split] for line in each]
        recent = [e for each in lines[split:] for e in map(parse_entry, each) if e.time >= since]
        self._kept.keep(project, seen.md5, head, size)
        return Project(
            id=project,
            version=seen.md5,
            row=row,
            state=head.state,
            format=head.format,
            records=tuple(records) + head.records.tail,
            recent=tuple(recent) + tuple(e for e in head.history.tail if e.time >= since),
        )

    def create(self, project: str, ref: str, change: Commit) -> str:
        check_project(project)
        check_row(change.row)
        check_entries(0, change.entries)
        sealable(change.records, change.entries, self._limits)
        # Reserved now, made at the first seal: a create tried again names the same folder.
        (folder,) = self._pool.take(1)
        # No seal here: the project's folder is never made before its head, so the opening's
        # tidy-up never takes a project being created for one half trashed.
        head = Head(
            write=new_write(),
            format=change.format,
            seq=change.entries[-1].seq if change.entries else 0,
            state=change.state,
            records=Stream((), change.records),
            history=Stream((), change.entries),
        )
        gz, size = pack_head(head, self._limits.head_most)
        version = hashlib.md5(gz).hexdigest()
        metadata: dict[str, Any] = {
            "id": ref,
            "name": f"{project}.json.gz",
            "parents": [self._projects],
            "mimeType": GZIP,
            "properties": {
                key: value
                for key, value in properties(change.row, folder).items()
                if value is not None
            },
        }
        try:
            again(self._clock, lambda: self._api.create(metadata, gz, "id"))
        except Conflict as conflict:
            self._created_before(ref, version, conflict.uncertain)
        except Missing as missing:
            raise Rejected(f"{PROJECTS}/ is not on Drive: {missing}") from None
        self._kept.remember(project, Where(ref, folder))
        self._kept.keep(project, version, head, size)
        return version

    def commit(self, project: str, expected: str, change: Commit) -> str:
        check_project(project)
        given = self._kept.given(project)
        if expected != given:
            raise ValueError(
                f"{expected} is not the version this port last gave for {project} ({given}): "
                "a change is built on what was loaded."
            )
        # A second commit built on the same version waits, then meets Stale at its look.
        with self._lock_of(project):
            return self._commit(project, expected, change)

    def history(self, project: str, before: int | None, count: int) -> tuple[Entry, ...]:
        check_project(project)
        check_count("count", count, MOST_ENTRIES)
        seen = self._look(project)
        # A newer head is read for this answer only: the base kept is always the version given.
        kept = self._kept.base(project, seen.md5)
        head = kept[0] if kept else read_head(self._download_head(seen), self._limits.head_most)[0]
        found = [
            entry for entry in reversed(head.history.tail) if before is None or entry.seq < before
        ][:count]
        # History is in step from 1: a block's first seq is the count of those before it, + 1.
        first = 1 + sum(block.count for block in head.history.blocks)
        for block in reversed(head.history.blocks):
            first -= block.count
            if len(found) == count:
                break
            if before is not None and first >= before:
                continue
            entries = [parse_entry(line) for line in reversed(self._blocks.one(block))]
            found += [e for e in entries if before is None or e.seq < before][: count - len(found)]
        return tuple(found)

    def trash_project(self, project: str) -> None:
        check_project(project)
        where = self._kept.where(project)
        if where is None:
            try:
                where = self._find(project).where
            except NotFound:
                self._kept.forget(project, given=True)
                return
        # The head first: the project is gone the moment it is in the trash (step 4).
        trash(self._api, self._clock, where.head)
        self._kept.forget(project, given=True)
        # Its folder after; one left behind, or unknown for unreadable properties, the next
        # opening's tidy-up takes.
        if where.folder is not None:
            try:
                trash(self._api, self._clock, where.folder)
            except StorageError as failed:
                log.warning("Project %s's folder stays for the next opening: %s", project, failed)

    # -- files: v1-9 -----------------------------------------------------------------------------

    def reserve(self, count: int) -> tuple[str, ...]:
        check_count("count", count, MOST_RESERVED)
        return tuple(self._pool.take(count))

    def put(self, ref: str, source: Path, name: str, place: Place) -> Stored:
        raise NotImplementedError(_FILES)

    def exists(self, ref: str) -> Stored | None:
        raise NotImplementedError(_FILES)

    def get(self, ref: str, target: Path, most: int) -> Stored:
        raise NotImplementedError(_FILES)

    def copy(self, source: str, ref: str, name: str, place: Place) -> Stored:
        raise NotImplementedError(_FILES)

    def trash(self, ref: str) -> None:
        raise NotImplementedError(_FILES)

    def export_folder(self, ref: str, name: str, inside: str | None = None) -> None:
        raise NotImplementedError(_FILES)

    def export_names(self, prefix: str) -> tuple[str, ...]:
        raise NotImplementedError(_FILES)

    def space(self) -> Space:
        raise NotImplementedError(_FILES)

    # -- a commit --------------------------------------------------------------------------------

    def _commit(self, project: str, expected: str, change: Commit) -> str:
        check_row(change.row)
        # From here the change has commit_most to its head's last write try (Limits, Mühür).
        deadline = self._clock.now() + timedelta(seconds=self._limits.commit_most)
        kept = self._kept.base(project, expected)
        # Planned before the look while its base is at hand: the core's mistakes stop here.
        sealing = None if kept is None else self._writer.sealed(kept[0], change)
        seen = self._look(project)
        if seen.md5 != expected:
            raise Stale(f"Project {project} is at {seen.md5}, not {expected}.")
        if kept is None:  # its base left: read once more, as it stands
            data = self._download_head(seen)
            if hashlib.md5(data).hexdigest() != expected:
                raise Stale(f"Project {project} moved on while its head file was read.")
            kept = read_head(data, self._limits.head_most)
        base = kept[0]
        if base.format > change.format:
            raise NewerFormat(base.format, change.format)
        folder = seen.where.folder
        if folder is None:  # every write sends the properties whole, the folder among them
            raise Unreadable(f"Project {project}'s head file names no folder for its blocks.")
        sealing = sealing or self._writer.sealed(base, change)
        planned, folder = self._writer.write(
            project, seen.where.head, folder, base, change, sealing, expected, deadline
        )
        self._kept.remember(project, Where(seen.where.head, folder))
        self._kept.keep(project, planned.version, planned.head, planned.size)
        return planned.version

    def _created_before(self, ref: str, version: str, uncertain: bool) -> None:
        """A 409 on a head's create: this one's earlier try, an earlier creation, or another
        file."""
        try:
            found = read(self._clock, lambda: self._api.get(ref, "name,parents,md5Checksum"))
        except Missing:
            raise Rejected(f"Drive said a file is at {ref}, then that none is.") from None
        name = found.get("name")
        head = found.get("parents") == [self._projects] and (
            isinstance(name, str) and _HEAD_NAME.fullmatch(name) is not None
        )
        if not head:
            raise Taken(f"A file or folder is at {ref}.")
        if not (uncertain and found.get("md5Checksum") == version):
            raise Exists(f"A project was created at {ref} before.")

    def _lock_of(self, project: str) -> threading.Lock:
        # One per project used: as many as there are projects.
        with self._locks_lock:
            return self._locks.setdefault(project, threading.Lock())

    # -- opening ---------------------------------------------------------------------------------

    def _tidy(self) -> None:
        heads: set[str] = set()
        folders: dict[str, str] = {}
        for found in self._listing(folders=None):
            if found.get("mimeType") == FOLDER:
                name = found.get("name")
                if isinstance(name, str) and _PROJECT.fullmatch(name):
                    folders[name] = str(found["id"])
                continue
            project = _project_of(found)
            if project is not None:
                heads.add(project)
                where = Where(str(found["id"]), _folder_or_none(found.get("properties")))
                self._kept.remember(project, where)
        for project, folder in folders.items():
            if project in heads:
                continue
            # Its head went to the trash and the folder did not follow (step 4, Silme).
            try:
                trash(self._api, self._clock, folder)
            except StorageError as failed:
                log.warning("The folder of trashed project %s stays for now: %s", project, failed)

    def _listing(self, folders: bool | None) -> Iterator[dict[str, Any]]:
        page: str | None = None
        for _ in range(self._limits.pages):
            try:
                found = read(
                    self._clock,
                    lambda page=page: self._api.children(
                        self._projects, _LIST_FIELDS, folders=folders, page=page
                    ),
                )
            except Missing as missing:
                raise Rejected(f"{PROJECTS}/ is not on Drive: {missing}") from None
            yield from found.files
            if found.next is None:
                return
            page = found.next
        raise Rejected(
            f"{PROJECTS}/ lists past {self._limits.pages} pages; the rest is not read, so the "
            "list is not given."
        )

    # -- looking and reading ---------------------------------------------------------------------

    def _look(self, project: str) -> _Seen:
        """One call: the head's metadata, by its id when known, else by its name."""
        where = self._kept.where(project)
        if where is None:
            return self._find(project)
        try:
            found = read(self._clock, lambda: self._api.get(where.head, HEAD_FIELDS))
        except Missing:
            self._kept.forget(project)
            raise NotFound(f"There is no project {project}.") from None
        return self._seen(project, found)

    def _find(self, project: str) -> _Seen:
        try:
            found = read(
                self._clock,
                lambda: self._api.children(
                    self._projects, HEAD_FIELDS, folders=False, name=f"{project}.json.gz"
                ),
            ).files
        except Missing:
            raise NotFound(f"There is no project {project}: {PROJECTS}/ is not on Drive.") from None
        if not found:
            raise NotFound(f"There is no project {project}.")
        if len(found) > 1:
            raise Unreadable(f"Project {project} has {len(found)} head files.")
        return self._seen(project, found[0])

    def _seen(self, project: str, found: dict[str, Any]) -> _Seen:
        if found.get("trashed") is True:
            self._kept.forget(project)
            raise NotFound(f"Project {project} is in the trash.")
        md5, size, file_id = found.get("md5Checksum"), found.get("size"), found.get("id")
        if not (
            isinstance(md5, str)
            and MD5.fullmatch(md5)
            and isinstance(size, str)
            and size.isdigit()
            and isinstance(file_id, str)
            and DRIVE_ID.fullmatch(file_id)
        ):
            raise Unreadable(f"Drive describes project {project}'s head file oddly: {found}.")
        props = found.get("properties")
        where = Where(file_id, _folder_or_none(props))
        self._kept.remember(project, where)
        return _Seen(where, md5, int(size), props)

    def _download_head(self, seen: _Seen) -> bytes:
        most = self._limits.head_most
        if seen.size > most:
            raise Unreadable(f"The head file has {seen.size:,} bytes, past the {most:,} it may.")
        try:
            data = read(self._clock, lambda: self._api.download(seen.where.head, most))
        except Missing:
            raise NotFound(f"The head file {seen.where.head} is gone.") from None
        if len(data) > most:
            raise Unreadable(f"The head file is past the {most:,} bytes it may have.")
        return data


def _projects_folder(api: DriveApi, clock: Clock, pool: Pool, root: str) -> str:
    def listed() -> list[dict[str, Any]]:
        return read(clock, lambda: api.children(root, "id", folders=True, name=PROJECTS)).files

    try:
        found = listed()
        if not found:
            pool.make(lambda made: folder_at(api, clock, made, PROJECTS, root))
            # Two cores opening a new root at once each make one: both take the oldest.
            found = listed()
    except Missing as missing:
        raise Rejected(f"The root folder {root} is not on Drive: {missing}") from None
    if not found:
        raise Rejected(f"{PROJECTS}/ was made in {root} and is not listed there.")
    return str(found[0]["id"])


def _project_of(found: dict[str, Any]) -> str | None:
    name = found.get("name")
    match = _HEAD_NAME.fullmatch(name) if isinstance(name, str) else None
    return match.group(1) if match else None


def _folder_or_none(props: object) -> str | None:
    try:
        return read_folder(props)
    except Unreadable:
        return None
