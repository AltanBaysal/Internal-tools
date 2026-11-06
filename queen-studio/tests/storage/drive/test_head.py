import gzip
import hashlib
import json
from datetime import timedelta
from typing import Any

import pytest

from core.storage.drive.head import (
    Block,
    Head,
    Retired,
    Stream,
    entry_line,
    inflate,
    pack_head,
    properties,
    read_head,
    read_lines,
    read_row,
    record_line,
)
from core.storage.port import Entry, Record, Unreadable
from tests.storage.contract import T0, row

MD5 = "0" * 32


def head(**changes: Any) -> Head:
    fields: dict[str, Any] = {
        "write": "0123456789abcdef",
        "format": 1,
        "seq": 1,
        "state": {"frames": [[17, None]], "note": "Çığ"},
        "records": Stream((), (Record("frame", 17, {"seed": 4}),)),
        "history": Stream((), (Entry(1, T0, {"what": "create"}),)),
        **changes,
    }
    return Head(**fields)


def gz(value: object) -> bytes:
    return gzip.compress(json.dumps(value).encode(), mtime=0)


# -- the head file -------------------------------------------------------------------------------


def test_a_head_reads_back_as_it_was_packed() -> None:
    block = Block("blockid", 3, 120, MD5, T0 + timedelta(hours=1))
    written = head(
        history=Stream((block,), (Entry(4, T0, {"x": [1, None]}),)),
        retired=(Retired("oldblock", T0),),
    )
    packed, size = pack_head(written, 1000)

    assert read_head(packed) == (written, size)
    assert size == len(gzip.decompress(packed))


def test_the_same_head_is_the_same_bytes() -> None:
    # Its md5 is the project's version: a retry of the same write is the same version.
    assert pack_head(head(), 1000) == pack_head(head(), 1000)


def test_a_head_past_its_bound_is_never_written() -> None:
    with pytest.raises(ValueError, match="head"):
        pack_head(head(state={"big": "x" * 200}), 100)


@pytest.mark.parametrize("value", [float("nan"), {1, 2}], ids=["nan", "set"])
def test_a_value_json_cannot_hold_is_refused(value: object) -> None:
    with pytest.raises(ValueError):
        pack_head(head(state={"x": value}), 1000)


@pytest.mark.parametrize(
    ("data", "said"),
    [
        (b"xx", "gzip"),
        (gzip.compress(b"{")[:-6], "gzip"),
        (gzip.compress(b"{}") + b"more", "gzip"),
        (gz({"v": 2}), "layout"),
        (gz([1]), "head"),
        (gz({"v": 1, "w": 1}), "head"),
        (gzip.compress(b"[" * 100_000, mtime=0), "JSON"),
        (gzip.compress(b"\xff\xfe", mtime=0), "JSON"),
    ],
    ids=[
        "not-gzip",
        "cut",
        "trailing",
        "newer-layout",
        "not-object",
        "wrong-field",
        "deep",
        "utf8",
    ],
)
def test_anything_but_a_whole_head_is_unreadable_never_empty(data: bytes, said: str) -> None:
    # Step 4, Okunamayan baş dosyası: never taken as empty, and RecursionError is caught too.
    with pytest.raises(Unreadable, match=said):
        read_head(data)


def test_a_bad_id_or_md5_in_a_head_is_unreadable() -> None:
    good = json.loads(gzip.decompress(pack_head(head(), 1000)[0]))
    bad_id = json.loads(json.dumps(good))
    bad_id["records"]["blocks"] = [{"id": "../x", "count": 1, "size": 1, "gz": MD5}]
    bad_retired = {**good, "retired": [{"id": "x" * 200, "at": "2026-11-06T09:00:00Z"}]}
    bad_md5 = json.loads(json.dumps(good))
    bad_md5["records"]["blocks"] = [{"id": "b", "count": 1, "size": 1, "gz": "../x"}]

    for changed, said in ((bad_id, "Drive id"), (bad_retired, "Drive id"), (bad_md5, "md5")):
        with pytest.raises(Unreadable, match=said):
            read_head(gz(changed))


def test_opening_stops_at_its_bound() -> None:
    # CODE-STANDARD, Cost: a small file that opens to gigabytes is refused at the bound.
    bomb = gzip.compress(b"0" * 10_000)

    assert inflate(gzip.compress(b"0" * 100), 100) == b"0" * 100
    with pytest.raises(Unreadable, match="100"):
        inflate(bomb, 100)
    with pytest.raises(Unreadable):
        read_head(bomb, 100)


# -- blocks --------------------------------------------------------------------------------------


def block_of(lines: list[bytes]) -> tuple[bytes, Block]:
    raw = b"".join(lines)
    packed = gzip.compress(raw, mtime=0)
    return packed, Block("blockid", len(lines), len(raw), hashlib.md5(packed).hexdigest())


def test_a_block_gives_its_lines() -> None:
    lines = [record_line(Record("frame", n, {"n": n})) for n in range(3)]
    packed, block = block_of(lines)

    assert read_lines(packed, block, 1000) == lines


def test_a_block_that_is_not_the_one_its_head_names_is_unreadable() -> None:
    # A block is written once: other bytes at its id are a fault, never other records to read.
    lines = [record_line(Record("frame", n, {})) for n in range(3)]
    _, block = block_of(lines)
    others, _ = block_of([record_line(Record("frame", 9, {}))] * 3)

    with pytest.raises(Unreadable, match="md5"):
        read_lines(others, block, 1000)


def test_a_block_with_other_lines_than_its_head_counts_is_unreadable() -> None:
    lines = [record_line(Record("frame", n, {})) for n in range(3)]
    packed, block = block_of(lines)

    with pytest.raises(Unreadable, match="lines"):
        read_lines(packed, Block(block.id, 4, block.size, block.gz), 1000)


def test_a_block_past_its_bound_is_unreadable() -> None:
    lines = [record_line(Record("frame", n, {"pad": "x" * 50})) for n in range(5)]
    packed, block = block_of(lines)

    with pytest.raises(Unreadable):
        read_lines(packed, block, 100)


def test_lines_are_one_json_object_each() -> None:
    entry = Entry(3, T0, {"what": "rename", "to": "Işık\nyeni"})

    assert entry_line(entry).count(b"\n") == 1
    assert json.loads(entry_line(entry)) == {
        "seq": 3,
        "time": "2026-11-06T09:00:00Z",
        "data": {"what": "rename", "to": "Işık\nyeni"},
    }


# -- the row in the head's properties ------------------------------------------------------------


@pytest.mark.parametrize(
    "name", ["Bir", "ğ" * 64, "😀" * 64, "a" * 64, "ŞÖĞÜÇİ ışık 東京"], ids=str
)
def test_the_row_goes_to_properties_and_back(name: str) -> None:
    # Drive gives a property 124 bytes, key and value in UTF-8 (step 4): the name takes up to three,
    # cut between characters.
    written = row(name, archived=True, runner="k3v9q2mz7a", updated=T0 + timedelta(days=1))

    found = properties(written, "folderid")

    assert all(len(key.encode()) + len(value.encode()) <= 124 for key, value in _set(found))
    assert found["folder"] == "folderid"
    assert read_row(_given(found)) == written


def test_every_key_is_sent_so_a_shorter_name_or_no_runner_clears_the_old() -> None:
    # Drive keeps a property an update leaves out: null is what clears it.
    found = properties(row("Bir"), "folderid")

    assert set(found) == {"n0", "n1", "n2", "archived", "created", "updated", "runner", "folder"}
    assert (found["n1"], found["n2"], found["runner"]) == (None, None, None)


@pytest.mark.parametrize(
    "props",
    [
        None,
        {},
        {
            "n0": "Bir",
            "archived": "yes",
            "created": "2026-11-06T09:00:00Z",
            "updated": "2026-11-06T09:00:00Z",
        },
        {
            "n0": "Bir",
            "archived": "false",
            "created": "2026-11-6T9:00:00Z",
            "updated": "2026-11-06T09:00:00Z",
        },
        {
            "n0": "Bir",
            "archived": "false",
            "created": "2026-11-06T09:00:00Z",
            "updated": "2026-11-06T09:00:00Z",
            "runner": "../core",
        },
    ],
    ids=["none", "empty", "archived", "time", "runner"],
)
def test_a_row_drive_holds_wrongly_is_unreadable(props: object) -> None:
    with pytest.raises(Unreadable):
        read_row(props)


def _set(found: dict[str, str | None]) -> list[tuple[str, str]]:
    return [(key, value) for key, value in found.items() if value is not None]


def _given(found: dict[str, str | None]) -> dict[str, str]:
    return dict(_set(found))
