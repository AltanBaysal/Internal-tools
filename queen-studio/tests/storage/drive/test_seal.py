import gzip
import hashlib
from datetime import timedelta
from itertools import count

import pytest

from core.storage.drive.head import Block, Head, Retired, Stream, entry_line, record_line
from core.storage.drive.limits import Limits
from core.storage.drive.seal import due, finish, reopens, seal, sealable, sealed
from core.storage.port import Commit, Entry, Record
from tests.storage.contract import T0, row

LIMITS = Limits(tail_count=3, tail_bytes=20, block_full=30, block_most=50, retire_after=60)
# For whole changes: lines of real JSON, sealed past three.
PLAN = Limits(tail_count=3, block_full=10**4, block_most=10**5, retire_after=60)


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def test_a_tail_is_due_past_its_count_or_its_bytes() -> None:
    assert not due([b"a\n"] * 3, LIMITS)
    assert due([b"a\n"] * 4, LIMITS)
    assert not due([b"x" * 20], LIMITS)
    assert due([b"x" * 21], LIMITS)


def test_the_last_block_is_open_while_under_full_and_the_tail_keeps_it_under_most() -> None:
    open_one = Block("b1", 2, 29, "0" * 32)
    full = Block("b1", 2, 30, "0" * 32)

    assert not reopens((), 5, LIMITS)
    assert reopens((open_one,), 21, LIMITS)
    assert not reopens((open_one,), 22, LIMITS)
    assert not reopens((full,), 1, LIMITS)


def test_a_new_block_is_made_at_a_fresh_id() -> None:
    blocks, write, replaced = seal(
        (), "fresh1", (b"one\n", b"two\n"), None, None, "records", LIMITS
    )

    raw = b"one\ntwo\n"
    assert (write.id, write.name) == ("fresh1", "records-1.jsonl.gz")
    assert gzip.decompress(write.gz) == raw
    assert blocks == (Block("fresh1", 2, len(raw), md5(write.gz)),)
    assert replaced is None


def test_an_open_block_is_replaced_by_a_new_one_never_written_again() -> None:
    # Two cores sealing at once each write their own file: the later head stands whole.
    old = Block("b1", 1, 4, "0" * 32, T0)

    blocks, write, replaced = seal(
        (old,), "fresh1", (b"new\n",), (b"old\n",), T0 + timedelta(1), "history", LIMITS
    )

    assert (write.id, write.name) == ("fresh1", "history-1.jsonl.gz")
    assert gzip.decompress(write.gz) == b"old\nnew\n"
    assert blocks == (Block("fresh1", 2, 8, md5(write.gz), T0 + timedelta(1)),)
    assert replaced == "b1"


def test_a_block_past_its_bound_is_never_written() -> None:
    # One change that would make a block nothing could read back is the core's mistake.
    with pytest.raises(ValueError, match="block"):
        seal((), "n1", (b"x" * 51,), None, None, "records", LIMITS)


def test_a_tail_no_block_could_hold_is_refused() -> None:
    # Made at create, such a tail could never be sealed: every later change would fail.
    big = Record("frame", 1, {"pad": "x" * 60})

    with pytest.raises(ValueError, match="records"):
        sealable((big,), (), LIMITS)
    with pytest.raises(ValueError, match="history"):
        sealable((), (Entry(1, T0, {"pad": "x" * 60}),), LIMITS)
    sealable((Record("frame", 1, {}),), (Entry(1, T0, {}),), LIMITS)


def head(blocks: tuple[Block, ...] = (), retired: tuple[Retired, ...] = (), seq: int = 3) -> Head:
    return Head("0123456789abcdef", 1, seq, {}, Stream((), ()), Stream(blocks, ()), retired)


def change(*seqs: int) -> Commit:
    return Commit(row(), {}, 1, entries=tuple(Entry(seq, T0, {}) for seq in seqs))


def test_a_change_with_no_seal_writes_and_trashes_nothing() -> None:
    sealing = sealed(head(), change(4), PLAN, lambda _: [], lambda: "never")
    planned = finish(head(), change(4), sealing, {}, PLAN)

    assert (sealing.blocks, sealing.opens_folder) == ((), False)
    assert (planned.trash, planned.now) == ((), None)
    assert planned.head.history.tail == (Entry(4, T0, {}),)


def test_a_seal_retires_the_block_it_replaces_at_drives_time_and_trashes_the_old() -> None:
    # Drive's clock on both sides: a retired block's time is its replacement's creation, and
    # what is old enough is measured from this change's own newest block's.
    open_one = Block("b1", 1, 10, "0" * 32, T0)
    lines = [entry_line(Entry(1, T0, {}))]
    made = T0 + timedelta(seconds=90)
    recent, old = Retired("r1", made - timedelta(seconds=30)), Retired("r2", T0)
    base = head((open_one,), (recent, old), seq=1)
    ids = count(1)

    sealing = sealed(base, change(2, 3, 4, 5), PLAN, lambda _: lines, lambda: f"fresh{next(ids)}")
    planned = finish(base, change(2, 3, 4, 5), sealing, {"fresh1": made}, PLAN)

    assert [write.id for write in sealing.blocks] == ["fresh1"]
    assert sealing.replaced == (("fresh1", "b1"),)
    assert planned.trash == ("r2",)
    assert planned.head.retired == (recent, Retired("b1", made))
    assert planned.now == made
    assert not sealing.opens_folder


def test_the_first_seal_opens_the_folder() -> None:
    sealing = sealed(head(seq=0), change(1, 2, 3, 4), PLAN, lambda _: [], lambda: "fresh")
    planned = finish(head(seq=0), change(1, 2, 3, 4), sealing, {"fresh": T0}, PLAN)

    assert sealing.opens_folder
    assert planned.head.history.blocks[0].id == "fresh"
    assert planned.head.history.tail == ()


def test_a_record_tail_seals_into_records() -> None:
    records = tuple(Record("frame", n, {}) for n in range(4))
    commit = Commit(row(), {}, 1, records=records, entries=(Entry(4, T0, {}),))

    sealing = sealed(head(), commit, PLAN, lambda _: [], lambda: "fresh")

    assert sealing.blocks[0].name == "records-1.jsonl.gz"
    assert gzip.decompress(sealing.blocks[0].gz) == b"".join(map(record_line, records))
