"""How a project lies on Drive: its head file, its blocks, and its row in the head's properties
(step 4, Drive'da ne nerede; the m532 spec, Drive'da).

The head file is gzipped JSON: the state, written whole by each commit; for each of the two
streams — records and history — the blocks it names and the tail not yet in a block; and the
blocks retired, no longer named, with the time each stopped being named. A block is one JSON
object a line, written once at a fresh id and never again: its md5 in the head checks it whole.
The row lives in the head's properties, written in the same call as its content.

What comes from Drive is input from outside the process: every file is opened against a bound,
every field checked, and anything else is Unreadable in the reader's own words — never taken as
empty. Nothing is written that the same bound would refuse to read back.
"""

import gzip
import hashlib
import json
import re
import secrets
import zlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from core.storage.drive.limits import Limits
from core.storage.port import Entry, Record, Row, Unreadable, check_row

# The head file's own layout, the adapter's; the groups' format is the port's `format`.
LAYOUT = 1
GZIP = "application/gzip"
NAME_KEYS = ("n0", "n1", "n2")
# Drive gives a property 124 bytes, key and value together, in UTF-8.
PROPERTY_BYTES = 124
# Drive's ids are letters, digits, - and _; 128 is far past the 33 they have.
DRIVE_ID = re.compile(r"[A-Za-z0-9_-]{1,128}")
MD5 = re.compile(r"[0-9a-f]{32}")
_TIME = "%Y-%m-%dT%H:%M:%SZ"
_WRITE = re.compile(r"[0-9a-f]{16}")
_CORE = re.compile(r"[a-z0-9]{10}")


def check_ref(ref: str) -> None:
    """A file's or folder's ref, a Drive id: it comes from the core, but maybe from the address
    first, and goes into a request (the m534 spec, Hatalar)."""
    if not DRIVE_ID.fullmatch(ref):
        raise ValueError(f"{ref!r} is not a file's ref: a Drive id, letters, digits, - and _.")


class _Bad(Exception):
    """Inside: what is wrong in a file read from Drive, said once as Unreadable."""


@dataclass(frozen=True)
class Block:
    id: str
    count: int  # its lines
    size: int  # their bytes
    gz: str  # the md5 of the block as written: what a reader checks, and the disk cache's key
    latest: datetime | None = None  # a history block's latest entry time


@dataclass(frozen=True)
class Retired:
    """A block no longer named since `at`: trashed once no core can still write a head that
    names it (the m532 spec, Mühür)."""

    id: str
    at: datetime


@dataclass(frozen=True)
class Stream[T]:
    blocks: tuple[Block, ...]
    tail: tuple[T, ...]


@dataclass(frozen=True)
class Head:
    # This write's own random id: the version is the content's md5, and without it two writes of
    # the same content — state A, B, A again; two cores making one change at once — would share
    # a version while their rows, in the properties, differ.
    write: str
    format: int
    seq: int
    state: dict[str, Any]
    records: Stream[Record]
    history: Stream[Entry]
    retired: tuple[Retired, ...] = ()

    def named(self) -> set[str]:
        return {block.id for block in self.records.blocks + self.history.blocks}


# -- writing -------------------------------------------------------------------------------------


def dumps(value: Any) -> str:
    """JSON as stored; ValueError for what JSON cannot hold."""
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    except TypeError as wrong:  # NaN is already a ValueError
        raise ValueError(f"Not JSON: {wrong}") from wrong


def compress(raw: bytes) -> bytes:
    # No time in the gzip header: the same content is the same bytes, and the same md5.
    return gzip.compress(raw, mtime=0)


def pack_head(head: Head, most: int) -> tuple[bytes, int]:
    """The head file, and its bytes opened: what the port keeps of it in memory."""
    raw = dumps(
        {
            "v": LAYOUT,
            "w": head.write,
            "format": head.format,
            "seq": head.seq,
            "state": head.state,
            "records": _stream_object(head.records, _record_object),
            "history": _stream_object(head.history, _entry_object),
            "retired": [{"id": each.id, "at": stamp(each.at)} for each in head.retired],
        }
    ).encode()
    if len(raw) > most:
        raise ValueError(
            f"The project's head file would be {len(raw):,} bytes, past the {most:,} it may have."
        )
    return compress(raw), len(raw)


def new_write() -> str:
    return secrets.token_hex(8)


def record_line(record: Record) -> bytes:
    return (dumps(_record_object(record)) + "\n").encode()


def entry_line(entry: Entry) -> bytes:
    return (dumps(_entry_object(entry)) + "\n").encode()


def stamp(time: datetime) -> str:
    return time.strftime(_TIME)


def properties(row: Row, folder: str) -> dict[str, str | None]:
    """The row as the head's properties, every key named: None clears one an earlier write set."""
    parts = _cut(row.name)
    found: dict[str, str | None] = {
        key: parts[index] if index < len(parts) else None for index, key in enumerate(NAME_KEYS)
    }
    found["archived"] = "true" if row.archived else "false"
    found["created"] = stamp(row.created)
    found["updated"] = stamp(row.updated)
    found["runner"] = row.runner
    found["folder"] = folder
    return found


def _cut(name: str) -> list[str]:
    """The name in parts that fit a property beside their key, cut between characters."""
    room = PROPERTY_BYTES - len(NAME_KEYS[0])
    parts = [""]
    for character in name:
        if len((parts[-1] + character).encode()) > room:
            parts.append("")
        parts[-1] += character
    if len(parts) > len(NAME_KEYS):
        raise ValueError(f"The name {name!r} does not fit Drive's properties.")
    return parts


def _stream_object[T](stream: Stream[T], item: Callable[[T], dict[str, Any]]) -> dict[str, Any]:
    return {
        "blocks": [_block_object(block) for block in stream.blocks],
        "tail": [item(each) for each in stream.tail],
    }


def _block_object(block: Block) -> dict[str, Any]:
    found: dict[str, Any] = {
        "id": block.id,
        "count": block.count,
        "size": block.size,
        "gz": block.gz,
    }
    if block.latest is not None:
        found["latest"] = stamp(block.latest)
    return found


def _record_object(record: Record) -> dict[str, Any]:
    return {"kind": record.kind, "id": record.id, "data": record.data}


def _entry_object(entry: Entry) -> dict[str, Any]:
    return {"seq": entry.seq, "time": stamp(entry.time), "data": entry.data}


# -- reading -------------------------------------------------------------------------------------


def inflate(data: bytes, most: int, what: str = "The head file") -> bytes:
    """`data` ungzipped, never past `most` bytes: past it, cut short or with more after, it is
    Unreadable."""
    opener = zlib.decompressobj(wbits=31)  # gzip
    try:
        raw = opener.decompress(data, most + 1)
    except zlib.error as wrong:
        raise Unreadable(f"{what} is not gzip: {wrong}.") from wrong
    if len(raw) > most:
        raise Unreadable(f"{what} opens past {most:,} bytes.")
    if not opener.eof:
        raise Unreadable(f"{what}'s gzip ends early: it was cut.")
    if opener.unused_data:
        raise Unreadable(f"{what} has more bytes after its gzip.")
    return raw


def read_head(data: bytes, most: int = Limits().head_most) -> tuple[Head, int]:
    """The head, and its bytes opened."""
    raw = inflate(data, most)
    found = _json(raw, "The head file")
    try:
        if not isinstance(found, dict):
            raise _Bad("it is not a JSON object")
        head: dict[str, Any] = found  # pyright: ignore[reportUnknownVariableType]
        layout = head.get("v")
        if layout != LAYOUT:
            raise Unreadable(f"The head file is in layout {layout!r}; this core reads {LAYOUT}.")
        read = Head(
            write=_write_id(head),
            format=_count(head, "format"),
            seq=_count(head, "seq"),
            state=_object(head, "state"),
            records=_stream(head, "records", _record),
            history=_stream(head, "history", _entry),
            retired=tuple(_retired(each) for each in _list(head, "retired")),
        )
        return read, len(raw)
    except _Bad as bad:
        raise Unreadable(f"The head file is not one this core reads: {bad}.") from bad


def read_lines(data: bytes, block: Block, most: int) -> list[bytes]:
    """The block's lines, checked against its head: the md5 of the bytes, then their count."""
    what = f"Block {block.id}"
    if hashlib.md5(data).hexdigest() != block.gz:
        raise Unreadable(f"{what} is not the block its head file names: its md5 differs.")
    lines = inflate(data, most, what).splitlines(keepends=True)
    if len(lines) != block.count:
        raise Unreadable(f"{what} has {len(lines)} lines; its head file names {block.count}.")
    return lines


def parse_record(line: bytes) -> Record:
    return _parsed(line, _record)


def parse_entry(line: bytes) -> Entry:
    return _parsed(line, _entry)


def read_row(props: object) -> Row:
    """The row from the head's properties; Unreadable if Drive holds anything else."""
    try:
        if not isinstance(props, dict):
            raise _Bad("the head file has no properties")
        found: dict[str, Any] = props  # pyright: ignore[reportUnknownVariableType]
        name = "".join(_text(found, key) if key in found else "" for key in NAME_KEYS)
        archived = found.get("archived")
        if archived not in ("true", "false"):
            raise _Bad(f"archived is {archived!r}")
        runner = found.get("runner")
        if runner is not None and not (isinstance(runner, str) and _CORE.fullmatch(runner)):
            raise _Bad(f"runner is {runner!r}")
        row = Row(
            name=name,
            archived=archived == "true",
            created=_time(_text(found, "created")),
            updated=_time(_text(found, "updated")),
            runner=runner,
        )
        check_row(row)
        return row
    except (_Bad, ValueError) as bad:
        raise Unreadable(f"The head file's properties are not a row: {bad}.") from bad


def read_folder(props: object) -> str:
    try:
        if not isinstance(props, dict):
            raise _Bad("the head file has no properties")
        found: dict[str, Any] = props  # pyright: ignore[reportUnknownVariableType]
        return _drive_id(found, "folder")
    except _Bad as bad:
        raise Unreadable(f"The head file's properties name no folder: {bad}.") from bad


def _json(raw: bytes, what: str) -> object:
    try:
        return json.loads(raw.decode("utf-8"))
    except (ValueError, RecursionError) as wrong:  # UTF-8 and JSON errors are ValueErrors
        raise Unreadable(f"{what} is not JSON: {type(wrong).__name__}: {wrong}") from wrong


def _parsed[T](line: bytes, parse: Callable[[object], T]) -> T:
    found = _json(line, "A block's line")
    try:
        return parse(found)
    except _Bad as bad:
        raise Unreadable(f"A block's line is not one this core reads: {bad}.") from bad


def _stream[T](head: dict[str, Any], key: str, item: Callable[[object], T]) -> Stream[T]:
    stream = _object(head, key)
    return Stream(
        tuple(_block(each) for each in _list(stream, "blocks")),
        tuple(item(each) for each in _list(stream, "tail")),
    )


def _list(found: dict[str, Any], key: str) -> list[object]:
    value = found.get(key)
    if not isinstance(value, list):
        raise _Bad(f"{key} is not a list")
    return value  # pyright: ignore[reportUnknownVariableType]


def _block(found: object) -> Block:
    if not isinstance(found, dict):
        raise _Bad("a block is not an object")
    block: dict[str, Any] = found  # pyright: ignore[reportUnknownVariableType]
    return Block(
        id=_drive_id(block, "id"),
        count=_count(block, "count"),
        size=_count(block, "size"),
        gz=_md5(block, "gz"),
        latest=_time(_text(block, "latest")) if "latest" in block else None,
    )


def _retired(found: object) -> Retired:
    if not isinstance(found, dict):
        raise _Bad("a retired block is not an object")
    retired: dict[str, Any] = found  # pyright: ignore[reportUnknownVariableType]
    return Retired(_drive_id(retired, "id"), _time(_text(retired, "at")))


def _record(found: object) -> Record:
    if not isinstance(found, dict):
        raise _Bad("a record is not an object")
    record: dict[str, Any] = found  # pyright: ignore[reportUnknownVariableType]
    return Record(_text(record, "kind"), _count(record, "id"), _object(record, "data"))


def _entry(found: object) -> Entry:
    if not isinstance(found, dict):
        raise _Bad("a history entry is not an object")
    entry: dict[str, Any] = found  # pyright: ignore[reportUnknownVariableType]
    return Entry(_count(entry, "seq"), _time(_text(entry, "time")), _object(entry, "data"))


def _count(found: dict[str, Any], key: str) -> int:
    value = found.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise _Bad(f"{key} is {value!r}, not a count")
    return value


def _text(found: dict[str, Any], key: str) -> str:
    value = found.get(key)
    if not isinstance(value, str):
        raise _Bad(f"{key} is {value!r}, not text")
    return value


def _object(found: dict[str, Any], key: str) -> dict[str, Any]:
    value = found.get(key)
    if not isinstance(value, dict):
        raise _Bad(f"{key} is not an object")
    return value  # pyright: ignore[reportUnknownVariableType]


def _drive_id(found: dict[str, Any], key: str) -> str:
    value = _text(found, key)
    if not DRIVE_ID.fullmatch(value):
        raise _Bad(f"{key} is {value[:40]!r}, not a Drive id")
    return value


def _write_id(found: dict[str, Any]) -> str:
    value = _text(found, "w")
    if not _WRITE.fullmatch(value):
        raise _Bad(f"w is {value[:40]!r}, not a write's id")
    return value


def _md5(found: dict[str, Any], key: str) -> str:
    value = _text(found, key)
    if not MD5.fullmatch(value):
        raise _Bad(f"{key} is {value[:40]!r}, not an md5")
    return value


def _time(text: str) -> datetime:
    try:
        time = datetime.strptime(text, _TIME).replace(tzinfo=UTC)
    except ValueError as wrong:
        raise _Bad(f"{text[:40]!r} is not a time") from wrong
    if stamp(time) != text:  # strptime takes 2026-11-6 too
        raise _Bad(f"{text[:40]!r} is not a time as written")
    return time
