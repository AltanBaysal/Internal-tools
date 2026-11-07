"""Bytes between the machine's disk and Drive (the m534 spec, Yükleme and `get`).

An upload up to `simple_most` is one request, read whole. Past it a resumable one, a chunk in
memory at a time: Drive makes the file only with its last byte, so a cut upload leaves none; after
a cut Drive is asked where the upload stands and it goes on from there. Its md5 is of the bytes
Drive confirmed holding, in order: what was written, never Drive's word for it.

A download checks the disk's room first, streams into a file beside its target and takes the
target's place only once its size and md5 are Drive's: the target is whole or untouched.
"""

import hashlib
import os
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO

from core.clock.clock import Clock
from core.storage.drive.api import DriveApi
from core.storage.drive.limits import PIECE, Limits
from core.storage.drive.retry import Backoff, Conflict, Missing, again, read, resumed
from core.storage.port import Rejected, Stored, TooLarge, Unconfirmed

# What a file's write answers: enough to compare with what was sent.
FIELDS = "id,md5Checksum,size"


@dataclass(frozen=True)
class Sent:
    md5: str  # of the bytes sent, or of the source when nothing was
    size: int
    answer: dict[str, Any] | None  # Drive's, or None: a file was at the id already (409)


def upload(
    api: DriveApi, clock: Clock, limits: Limits, metadata: dict[str, Any], source: Path, size: int
) -> Sent:
    """`source`, of `size` bytes when it was looked at, to Drive as `metadata` says. Missing when
    its parent is not there; ValueError for a source that changes while it is read, the core's
    mistake."""
    if size <= limits.simple_most:
        return _whole(api, clock, limits, metadata, source)
    return _chunked(api, clock, limits, metadata, source, size)


def hashed(source: Path) -> tuple[str, int]:
    """The md5 and size of a file on disk, read a piece at a time."""
    hasher, size = hashlib.md5(), 0
    with source.open("rb") as file:
        while piece := file.read(PIECE):
            hasher.update(piece)
            size += len(piece)
    return hasher.hexdigest(), size


def download(
    api: DriveApi,
    clock: Clock,
    target: Path,
    expected: Stored,
    keep_free: int,
    free: Callable[[Path], int],
) -> None:
    """The file at `expected.ref` to `target`, whose folder is there. TooLarge when it would leave
    under `keep_free` bytes free; Rejected when it is not the file `expected` describes; Missing
    when it left Drive meanwhile."""
    room = free(target.parent) - keep_free
    if expected.size > room:
        raise TooLarge(expected.size, max(room, 0))
    handle, temporary = tempfile.mkstemp(dir=target.parent, prefix=target.name, suffix=".part")
    try:
        with os.fdopen(handle, "wb") as out:
            sink = _Sink(out)

            def fetch() -> None:
                sink.restart()  # a cut stream is tried again from nothing
                # One byte past its size: a file grown since its look is seen, never held.
                api.stream(expected.ref, expected.size, sink)

            if expected.size:
                read(clock, fetch)
        if (sink.size, sink.md5.hexdigest()) != (expected.size, expected.md5):
            raise Rejected(
                f"File {expected.ref} changed while it was read: {sink.size:,} bytes came, "
                f"{expected.size:,} were described."
            )
        os.replace(temporary, target)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


class _Sink:
    """Where a stream's pieces go: the file, and their md5 and count."""

    def __init__(self, out: BinaryIO) -> None:
        self._out = out
        self.md5 = hashlib.md5()
        self.size = 0

    def restart(self) -> None:
        self._out.seek(0)
        self._out.truncate()
        self.md5 = hashlib.md5()
        self.size = 0

    def __call__(self, piece: bytes) -> None:
        self._out.write(piece)
        self.md5.update(piece)
        self.size += len(piece)


def _whole(
    api: DriveApi, clock: Clock, limits: Limits, metadata: dict[str, Any], source: Path
) -> Sent:
    with source.open("rb") as file:
        content = file.read(limits.simple_most + 1)
    if len(content) > limits.simple_most:
        raise ValueError(f"{source} changed while it was read: it grew.")
    md5 = hashlib.md5(content).hexdigest()
    try:
        # A lost answer is tried again: an earlier try that made it meets 409.
        answer = again(clock, lambda: api.create(metadata, content, FIELDS))
    except Conflict:
        return Sent(md5, len(content), None)
    return Sent(md5, len(content), answer)


def _chunked(
    api: DriveApi,
    clock: Clock,
    limits: Limits,
    metadata: dict[str, Any],
    source: Path,
    size: int,
) -> Sent:
    try:
        # A session makes nothing: one started twice is harmless. Its 409 comes before any byte.
        session = again(clock, lambda: api.upload_start(metadata, size, FIELDS))
    except Conflict:
        return Sent(*hashed(source), None)
    hasher = hashlib.md5()
    held = 0  # the bytes Drive confirmed
    stall = Backoff(clock)  # renewed whenever the upload moves on
    with source.open("rb") as file:
        while True:
            file.seek(held)
            wanted = min(limits.chunk, size - held)
            data = file.read(wanted)  # the one copy of the chunk in memory
            if len(data) != wanted:
                raise ValueError(f"{source} changed while it was read: it shrank.")
            try:
                answer, waited = _chunk(api, session, data, held, size, stall)
            except Conflict:  # another upload of this ref finished first: a repeat
                return Sent(*hashed(source), None)
            now = size if isinstance(answer, dict) else answer
            if not held <= now <= held + len(data):
                raise Rejected(
                    f"Drive says it holds {now:,} bytes of the upload; it held {held:,} and was "
                    f"sent up to {held + len(data):,}."
                )
            hasher.update(memoryview(data)[: now - held])  # a slice, not a copy
            if isinstance(answer, dict):
                return Sent(hasher.hexdigest(), size, answer)
            if now > held:
                stall = Backoff(clock)
            # A round that made no progress waits once: after a cut, `resumed` waited already.
            elif not waited and not stall.wait():
                raise Rejected(f"Drive took none of the upload past byte {held:,} for a minute.")
            held = now


def _chunk(
    api: DriveApi, session: str, data: bytes, start: int, size: int, stall: Backoff
) -> tuple[int | dict[str, Any], bool]:
    """Where the upload stands once `data` is sent, and whether a cut was waited out first.
    Conflict when another upload made the file at the ref first."""
    last = start + len(data) == size
    asked = False

    def status() -> int | dict[str, Any]:
        nonlocal asked
        asked = True
        return api.upload_status(session, size)

    try:
        answer = resumed(stall, lambda: api.upload_chunk(session, data, start, size), status)
    except Missing as gone:
        said = f"The upload's session ended: {gone}"
        # Before the last byte no file was made; with it, one may have been.
        raise (Unconfirmed(said) if last else Rejected(said)) from None
    except Unconfirmed as unconfirmed:
        if last:
            raise
        raise Rejected(unconfirmed.said, unconfirmed.code) from unconfirmed
    return answer, asked
