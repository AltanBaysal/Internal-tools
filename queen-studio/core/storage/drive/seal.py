"""A change's plan: the seal — when a stream's tail goes to a block, and to which — and the head
after it (step 4, Bloklar; the m532 spec, Mühür).

New records and history first go to the head's tail, so a change stays one write. Past 100
records or 256 KB the tail goes to a block in the same change. Every block is new, at a fresh id
from the pool, and never written again: while the last block is open (under 4 MB, and the tail
keeps it under 8) the new one holds its lines and the tail, and takes its place; the one replaced
is retired. A block retired `retire_after` ago, by Drive's clock, goes to the trash after the next
sealing change's head is written. So two cores sealing at once never write the same file: the
later head stands whole, as the port promises.

A plan comes in two halves. `sealed` plans the blocks before any is written. `finish` builds the
head once they are, with the times Drive gave them: a retired block's time is the creation time of
the block that replaced it, and a change's "now" for what is old enough is its own newest block's
— Drive's clock on both sides of every comparison. The writing is the adapter's.
"""

import hashlib
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from core.storage.drive.head import (
    Block,
    Head,
    Retired,
    Stream,
    compress,
    entry_line,
    new_write,
    pack_head,
    record_line,
)
from core.storage.drive.limits import Limits
from core.storage.port import Commit, Entry, Record, check_entries


@dataclass(frozen=True)
class Write:
    id: str
    name: str
    gz: bytes


@dataclass(frozen=True)
class Sealing:
    """The blocks a change writes first, and the streams once they are."""

    records: Stream[Record]
    history: Stream[Entry]
    blocks: tuple[Write, ...]
    replaced: tuple[tuple[str, str], ...]  # (the new block, the one it replaces)
    opens_folder: bool  # the project's first block: its folder is made before it


@dataclass(frozen=True)
class Planned:
    head: Head
    gz: bytes
    size: int  # the head's bytes opened
    version: str
    trash: tuple[str, ...]  # retired long enough: trashed once the head is written
    now: datetime | None  # the change's newest block's creation, by Drive: the sweep's now


def due(tail: Sequence[bytes], limits: Limits) -> bool:
    return len(tail) > limits.tail_count or sum(map(len, tail)) > limits.tail_bytes


def reopens(blocks: Sequence[Block], size: int, limits: Limits) -> bool:
    """Whether a tail of `size` bytes joins the last block's lines rather than starting anew."""
    if not blocks:
        return False
    last = blocks[-1]
    return last.size < limits.block_full and last.size + size <= limits.block_most


def sealable(records: Sequence[Record], entries: Sequence[Entry], limits: Limits) -> None:
    """A tail no block could hold would stop the project's every later change: refused."""
    streams = (("records", map(record_line, records)), ("history", map(entry_line, entries)))
    for stem, lines in streams:
        size = sum(map(len, lines))
        if size > limits.block_most:
            raise ValueError(
                f"The {stem} given are {size:,} bytes, past the {limits.block_most:,} one block "
                "may hold."
            )


def seal(
    blocks: tuple[Block, ...],
    fresh: str,
    tail: tuple[bytes, ...],
    open_lines: tuple[bytes, ...] | None,
    latest: datetime | None,
    stem: str,
    limits: Limits,
) -> tuple[tuple[Block, ...], Write, str | None]:
    """The stream's blocks once `tail` is sealed into a new block at `fresh`, the write that makes
    it, and the block it replaces, if any.

    `open_lines` are the last block's lines when `reopens` says the tail joins them, else None;
    `latest` a history tail's latest time.
    """
    raw = b"".join((open_lines or ()) + tail)
    if len(raw) > limits.block_most:
        raise ValueError(
            f"The change would make a {stem} block of {len(raw):,} bytes, past the "
            f"{limits.block_most:,} a block may have."
        )
    gz = compress(raw)
    count = len(tail)
    kept = blocks
    replaced: str | None = None
    if open_lines is not None:
        last = blocks[-1]
        count += last.count
        latest = max((time for time in (last.latest, latest) if time is not None), default=None)
        kept, replaced = blocks[:-1], last.id
    block = Block(fresh, count, len(raw), hashlib.md5(gz).hexdigest(), latest)
    name = f"{stem}-{len(kept) + 1}.jsonl.gz"
    return kept + (block,), Write(fresh, name, gz), replaced


def sealed(
    head: Head,
    change: Commit,
    limits: Limits,
    lines_of: Callable[[Block], list[bytes]],
    fresh: Callable[[], str],
) -> Sealing:
    """The blocks `change` on `head` writes first; ValueError for the core's mistakes, before
    anything is written."""
    check_entries(head.seq, change.entries)
    writes: list[Write] = []
    replaced: list[tuple[str, str]] = []

    def one[T](
        stream: Stream[T], lines: tuple[bytes, ...], latest: datetime | None, stem: str
    ) -> Stream[T]:
        if not due(lines, limits):
            return stream
        reopening = reopens(stream.blocks, sum(map(len, lines)), limits)
        open_lines = tuple(lines_of(stream.blocks[-1])) if reopening else None
        blocks, write, old = seal(stream.blocks, fresh(), lines, open_lines, latest, stem, limits)
        writes.append(write)
        if old is not None:
            replaced.append((write.id, old))
        return Stream(blocks, ())

    records = Stream(head.records.blocks, head.records.tail + change.records)
    records = one(records, tuple(map(record_line, records.tail)), None, "records")
    history = Stream(head.history.blocks, head.history.tail + change.entries)
    latest = max((entry.time for entry in history.tail), default=None)
    history = one(history, tuple(map(entry_line, history.tail)), latest, "history")
    return Sealing(
        records,
        history,
        tuple(writes),
        tuple(replaced),
        bool(writes) and not (head.records.blocks or head.history.blocks),
    )


def finish(
    head: Head,
    change: Commit,
    sealing: Sealing,
    created: Mapping[str, datetime],
    limits: Limits,
) -> Planned:
    """The head after the change, its blocks made at the times in `created`. Only a sealing change
    trashes: any other stays a look and a write. ValueError past the head's bound."""
    retired = list(head.retired) + [Retired(old, created[new]) for new, old in sealing.replaced]
    now = max(created.values(), default=None)
    trash: tuple[str, ...] = ()
    if now is not None:
        old_enough = now - timedelta(seconds=limits.retire_after)
        trash = tuple(each.id for each in retired if each.at <= old_enough)
    after = Head(
        write=new_write(),
        format=change.format,
        seq=change.entries[-1].seq if change.entries else head.seq,
        state=change.state,
        records=sealing.records,
        history=sealing.history,
        retired=tuple(each for each in retired if each.id not in trash),
    )
    gz, size = pack_head(after, limits.head_most)
    return Planned(after, gz, size, hashlib.md5(gz).hexdigest(), trash, now)
