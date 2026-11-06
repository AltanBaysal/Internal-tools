"""A fake Drive API: the files in memory, each call counted, Drive's errors injected (step 12).

It behaves as 528 measured Drive: a file is made at an id only once (`409` again) and only at an id
`generate_ids` gave (`400` otherwise); content and metadata change in one call; `md5Checksum` and
`size` come with every file; a folder's trash covers what is in it (`trashed` says so, as Drive's
field does); writing to a trashed file succeeds; listings page, oldest first. It answers only the
fields asked for, so the adapter cannot lean on one it did not ask.

A fault is injected by call, optionally held to one file id, and fires on that many calls:
`Fail` is Drive's error, nothing done; `Lose` drops the answer, before the write or, `after`, once
it is made; `Hang` holds the call for a timeout on the clock, then drops it; `Before` runs a hook
first, outside the lock, so a hook may call the fake — the way a test sets up a race.
"""

import hashlib
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from core.clock.clock import Clock
from core.storage.drive.api import FOLDER, PAGE, DriveError, DriveLost, Page

Call = Literal["get", "download", "children", "create", "update", "generate_ids"]
WRITES: frozenset[Call] = frozenset({"create", "update"})


@dataclass(frozen=True)
class Fail:
    status: int
    reason: str
    said: str


@dataclass(frozen=True)
class Lose:
    after: bool = False
    said: str = "Connection reset by peer"


@dataclass(frozen=True)
class Hang:
    seconds: float


@dataclass(frozen=True)
class Before:
    then: Callable[[], object]


Fault = Fail | Lose | Hang | Before


@dataclass
class FakeFile:
    id: str
    name: str
    parents: list[str]
    mime: str
    content: bytes | None
    created: datetime
    properties: dict[str, str] = field(default_factory=dict[str, str])
    trashed: bool = False
    order: int = 0


@dataclass
class _Pending:
    call: Call
    fault: Fault
    left: int
    file: str | None


class FakeDrive:
    def __init__(self, clock: Clock, page_size: int = PAGE) -> None:
        self.clock = clock
        self.page_size = page_size
        self.files: dict[str, FakeFile] = {}
        self.calls: list[tuple[Call, str]] = []
        self._generated: set[str] = set()
        self._counter = 0
        self._pending: list[_Pending] = []
        self._lock = threading.RLock()

    # -- for tests -------------------------------------------------------------------------------

    def inject(self, call: Call, fault: Fault, times: int = 1, file: str | None = None) -> None:
        if isinstance(fault, Lose) and fault.after and call not in WRITES:
            raise ValueError(f"{call} writes nothing to drop after.")
        with self._lock:
            self._pending.append(_Pending(call, fault, times, file))

    def folder(self, name: str, parent: str | None = None) -> str:
        """A folder made by hand, outside any port; the root of a test's store."""
        with self._lock:
            made = self._new(self._id(), name, [parent] if parent else [], FOLDER, None)
        return made.id

    def named(self, name: str) -> FakeFile:
        (found,) = [file for file in self.files.values() if file.name == name]
        return found

    def live(self, parent: str) -> list[FakeFile]:
        """What is in `parent`, out of the trash, oldest first."""
        with self._lock:
            found = [f for f in self.files.values() if parent in f.parents and not self._trashed(f)]
        return sorted(found, key=lambda each: each.order)

    def expire(self) -> None:
        """Every id `generate_ids` gave so far, unused, is one Drive no longer takes."""
        with self._lock:
            self._generated.clear()

    def count(self, call: Call | None = None) -> int:
        return sum(1 for made, _ in self.calls if call is None or made == call)

    def made(self) -> list[Call]:
        return [call for call, _ in self.calls]

    # -- the API ---------------------------------------------------------------------------------

    def get(self, file_id: str, fields: str) -> dict[str, Any]:
        self._enter("get", file_id)
        with self._lock:
            return self._fields(self._file(file_id), fields)

    def download(self, file_id: str, most: int) -> bytes:
        self._enter("download", file_id)
        with self._lock:
            found = self._file(file_id)
            if found.content is None:
                raise DriveError(403, "fileNotDownloadable", "Only files with binary content.")
            return found.content[: most + 1]

    def children(
        self,
        parent: str,
        fields: str,
        *,
        folders: bool | None = None,
        name: str | None = None,
        page: str | None = None,
    ) -> Page:
        self._enter("children", parent)
        with self._lock:
            self._file(parent)  # Drive's 404 for a parent it does not have
            found = sorted(
                (
                    each
                    for each in self.files.values()
                    if parent in each.parents
                    and not self._trashed(each)
                    and (folders is None or (each.mime == FOLDER) == folders)
                    and (name is None or each.name == name)
                ),
                key=lambda each: each.order,
            )
            start = int(page or 0)
            end = start + self.page_size
            return Page(
                [self._fields(each, fields) for each in found[start:end]],
                str(end) if end < len(found) else None,
            )

    def create(
        self, metadata: dict[str, Any], content: bytes | None, fields: str
    ) -> dict[str, Any]:
        wanted = metadata.get("id")
        due = self._enter("create", wanted or "")
        with self._lock:
            if wanted is not None:
                if wanted in self.files:
                    raise DriveError(
                        409, "duplicate", "A file already exists with the provided ID."
                    )
                if wanted not in self._generated:
                    raise DriveError(400, "badRequest", "The provided file ID is not usable.")
            parents: list[str] = list(metadata.get("parents", []))
            for parent in parents:
                self._file(parent)
            made = self._new(
                wanted or self._id(),
                str(metadata["name"]),
                parents,
                str(metadata.get("mimeType", "application/octet-stream")),
                content,
            )
            for key, value in dict(metadata.get("properties", {})).items():
                if value is not None:
                    made.properties[str(key)] = str(value)
            answer = self._fields(made, fields)
        due()
        return answer

    def update(
        self, file_id: str, metadata: dict[str, Any], content: bytes | None, fields: str
    ) -> dict[str, Any]:
        due = self._enter("update", file_id)
        with self._lock:
            found = self._file(file_id)
            if "trashed" in metadata:
                found.trashed = bool(metadata["trashed"])
            if "name" in metadata:
                found.name = str(metadata["name"])
            for key, value in dict(metadata.get("properties", {})).items():
                if value is None:
                    found.properties.pop(str(key), None)
                else:
                    found.properties[str(key)] = str(value)
            if content is not None:
                found.content = content
            answer = self._fields(found, fields)
        due()
        return answer

    def generate_ids(self, count: int) -> list[str]:
        self._enter("generate_ids", str(count))
        with self._lock:
            ids = [self._id() for _ in range(count)]
            self._generated.update(ids)
        return ids

    # -- inside ----------------------------------------------------------------------------------

    def _enter(self, call: Call, file: str) -> Callable[[], None]:
        """Counts the call and fires its faults; what fires once the write is made is returned."""
        with self._lock:
            self.calls.append((call, file))
            due = [
                pending
                for pending in self._pending
                if pending.call == call and pending.file in (None, file)
            ]
            hooks = [pending for pending in due if isinstance(pending.fault, Before)]
            stopping = [pending for pending in due if not isinstance(pending.fault, Before)][:1]
            for pending in hooks + stopping:
                pending.left -= 1
            self._pending = [pending for pending in self._pending if pending.left]
        for pending in hooks:
            assert isinstance(pending.fault, Before)
            pending.fault.then()
        for pending in stopping:
            match pending.fault:
                case Fail(status=status, reason=reason, said=said):
                    raise DriveError(status, reason, said)
                case Hang(seconds=seconds):
                    self.clock.sleep(seconds)
                    raise DriveLost("The read operation timed out")
                case Lose(after=False, said=said):
                    raise DriveLost(said)
                case Lose(said=said):

                    def dropped() -> None:
                        raise DriveLost(said)

                    return dropped
                case Before():
                    pass
        return lambda: None

    def _id(self) -> str:
        self._counter += 1
        return f"f{self._counter:09d}"

    def _new(
        self, file_id: str, name: str, parents: list[str], mime: str, content: bytes | None
    ) -> FakeFile:
        self._counter += 1
        made = FakeFile(
            file_id, name, parents, mime, content, self.clock.now(), order=self._counter
        )
        self.files[file_id] = made
        return made

    def _file(self, file_id: str) -> FakeFile:
        found = self.files.get(file_id)
        if found is None:
            raise DriveError(404, "notFound", f"File not found: {file_id}.")
        return found

    def _trashed(self, file: FakeFile) -> bool:
        # Explicitly, or from a trashed folder it is in: Drive's `trashed` says either.
        return file.trashed or any(
            parent in self.files and self._trashed(self.files[parent]) for parent in file.parents
        )

    def _fields(self, file: FakeFile, fields: str) -> dict[str, Any]:
        everything: dict[str, Any] = {
            "id": file.id,
            "name": file.name,
            "mimeType": file.mime,
            "parents": list(file.parents),
            "trashed": self._trashed(file),
            # As Drive writes it, to the millisecond.
            "createdTime": file.created.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        }
        if file.properties:
            everything["properties"] = dict(file.properties)
        if file.content is not None:
            everything["md5Checksum"] = hashlib.md5(file.content).hexdigest()
            everything["size"] = str(len(file.content))
        wanted = {name.strip() for name in fields.split(",")}
        return {key: value for key, value in everything.items() if key in wanted}
