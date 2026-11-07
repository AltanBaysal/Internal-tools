"""Bytes between the disk and Drive, on the fake API (the m534 spec, Yükleme and `get`): one
request or chunk by chunk, a cut chunk resumed where Drive stands, no half file either way."""

import hashlib
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from core.clock.clock import Clock, ManualClock
from core.storage.drive.api import DriveLost
from core.storage.drive.limits import Limits
from core.storage.drive.retry import BUDGET
from core.storage.drive.transfer import Sent, download, upload
from core.storage.port import Rejected, Stored, TooLarge, Unconfirmed
from tests.storage.contract import T0
from tests.storage.drive.fake import Before, Fail, FakeDrive, Fault, Lose

# Past four bytes a file goes in chunks of four: ten bytes are three.
SMALL = Limits(simple_most=4, chunk=4)
TEN = b"0123456789"
ROOM = 10**12


def md5(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


class Rig:
    def __init__(self, tmp_path: Path, drive: Callable[[Clock], FakeDrive] = FakeDrive) -> None:
        self.clock = ManualClock(T0)
        self.drive = drive(self.clock)
        self.folder = self.drive.folder("media")
        self.tmp_path = tmp_path

    def metadata(self) -> dict[str, Any]:
        (ref,) = self.drive.generate_ids(1)
        self.drive.calls.clear()
        return {"id": ref, "name": "233.mp4", "parents": [self.folder], "mimeType": "video/mp4"}

    def source(self, content: bytes) -> Path:
        path = self.tmp_path / "source.mp4"
        path.write_bytes(content)
        return path

    def up(self, content: bytes, limits: Limits = SMALL) -> tuple[str, Sent]:
        metadata = self.metadata()
        return metadata["id"], upload(
            self.drive, self.clock, limits, metadata, self.source(content), len(content)
        )

    def on_chunk(self, number: int, then: Callable[[], object]) -> None:
        """`then` before the `number`th chunk, counted from 1."""
        if number == 1:
            self.drive.inject("upload_chunk", Before(then))
        else:
            self.drive.inject("upload_chunk", Before(lambda: self.on_chunk(number - 1, then)))

    def fault_on_chunk(self, number: int, fault: Fault, times: int = 1) -> None:
        """`fault` on the `number`th chunk: injected as the one before it enters."""

        def inject() -> None:
            self.drive.inject("upload_chunk", fault, times)

        if number == 1:
            inject()
        else:
            self.on_chunk(number - 1, inject)

    def session(self) -> Any:
        (found,) = self.drive.sessions.values()
        return found


@pytest.fixture
def rig(tmp_path: Path) -> Rig:
    return Rig(tmp_path)


START, CHUNK, STATUS = "upload_start", "upload_chunk", "upload_status"


# -- upload --------------------------------------------------------------------------------------


def test_a_file_up_to_the_simple_bound_is_one_request(rig: Rig) -> None:
    ref, sent = rig.up(b"0123")

    assert rig.drive.made() == ["create"]
    assert (sent.md5, sent.size) == (md5(b"0123"), 4)
    assert sent.answer is not None and sent.answer["id"] == ref
    assert rig.drive.files[ref].content == b"0123"


def test_a_larger_file_goes_in_chunks_and_is_made_with_its_last(rig: Rig) -> None:
    seen: list[bool] = []
    rig.on_chunk(3, lambda: seen.append(any(f.name == "233.mp4" for f in rig.drive.files.values())))

    ref, sent = rig.up(TEN)

    assert rig.drive.made() == [START, CHUNK, CHUNK, CHUNK]
    assert seen == [False]  # two chunks in, no file yet
    assert rig.drive.files[ref].content == TEN
    assert (sent.md5, sent.size) == (md5(TEN), 10)


def test_a_chunk_whose_answer_was_lost_is_not_sent_again(rig: Rig) -> None:
    rig.fault_on_chunk(2, Lose(after=True))

    ref, sent = rig.up(TEN)

    # Drive took the second chunk; its answer was lost; Drive is asked, and the third follows.
    assert rig.drive.made() == [START, CHUNK, CHUNK, STATUS, CHUNK]
    assert rig.drive.files[ref].content == TEN
    assert sent.md5 == md5(TEN)


def test_a_chunk_cut_before_drive_took_it_is_sent_again_from_where_drive_stands(rig: Rig) -> None:
    rig.fault_on_chunk(2, Lose())

    ref, _ = rig.up(TEN)

    assert rig.drive.made() == [START, CHUNK, CHUNK, STATUS, CHUNK, CHUNK]
    assert rig.drive.files[ref].content == TEN
    # One wait for the round, under two seconds: the cut's, not a second for "no progress".
    assert rig.clock.now() - T0 < timedelta(seconds=2)


def test_drive_holding_part_of_a_chunk_has_the_rest_sent_and_hashed_once(rig: Rig) -> None:
    # Drive may keep less of a cut chunk than was sent: the upload goes on from its byte.
    def kept_six() -> None:
        del rig.session().received[6:]

    rig.fault_on_chunk(2, Lose(after=True))
    rig.drive.inject("upload_status", Before(kept_six))

    ref, sent = rig.up(TEN)

    assert rig.drive.made() == [START, CHUNK, CHUNK, STATUS, CHUNK]
    assert rig.drive.files[ref].content == TEN
    assert sent.md5 == md5(TEN)


def test_an_upload_refused_midway_is_rejected_and_leaves_no_file(rig: Rig) -> None:
    forbidden = Fail(403, "forbidden", "The user does not have sufficient permissions.")
    rig.fault_on_chunk(2, forbidden)

    with pytest.raises(Rejected, match="sufficient permissions"):
        rig.up(TEN)

    assert [f.name for f in rig.drive.files.values()] == ["media"]


def test_an_upload_cut_for_a_minute_before_its_last_chunk_is_rejected(rig: Rig) -> None:
    # Nothing is made before the last byte: the outcome is known.
    rig.fault_on_chunk(2, Lose())
    rig.drive.inject("upload_status", Lose(), times=100)

    with pytest.raises(Rejected):
        rig.up(TEN)

    assert [f.name for f in rig.drive.files.values()] == ["media"]


def test_a_last_chunk_lost_for_a_minute_is_unconfirmed(rig: Rig) -> None:
    rig.fault_on_chunk(3, Lose(after=True))
    rig.drive.inject("upload_status", Lose(), times=100)

    with pytest.raises(Unconfirmed):
        rig.up(TEN)


def test_a_session_gone_midway_is_rejected(rig: Rig) -> None:
    rig.on_chunk(2, rig.drive.sessions.clear)

    with pytest.raises(Rejected, match="session"):
        rig.up(TEN)


def test_an_upload_making_no_progress_ends_within_its_budget(rig: Rig) -> None:
    # Each cut is answered "still at byte 4": waits without progress spend one budget.
    rig.fault_on_chunk(2, Lose(), times=100)

    with pytest.raises(Rejected):
        rig.up(TEN)

    # About a minute of the clock, never one per round.
    assert rig.clock.now() - T0 < timedelta(seconds=2 * BUDGET)


def test_a_used_id_gives_the_md5_of_the_source_and_no_answer(rig: Rig) -> None:
    # One request at once; a session, as on Drive (534), only with its last chunk.
    for content, made in ((b"0123", ["create"]), (TEN, [START, CHUNK, CHUNK, CHUNK])):
        metadata = rig.metadata()
        rig.drive.create({**metadata, "name": "x"}, b"other", "id")
        rig.drive.calls.clear()

        sent = upload(rig.drive, rig.clock, SMALL, metadata, rig.source(content), len(content))

        assert sent == Sent(md5(content), len(content), None)
        assert rig.drive.made() == made


def test_a_small_source_that_grew_since_it_was_looked_at_is_the_cores_mistake(rig: Rig) -> None:
    # Looked at with four bytes, read with six: past simple_most, nothing is sent.
    with pytest.raises(ValueError, match="grew"):
        upload(rig.drive, rig.clock, SMALL, rig.metadata(), rig.source(b"012345"), 4)

    assert rig.drive.made() == []


# -- download ------------------------------------------------------------------------------------


def stored(rig: Rig, content: bytes) -> Stored:
    ref, _ = rig.up(content, Limits())
    rig.drive.calls.clear()
    return Stored(ref, len(content), md5(content))


def test_a_download_is_one_stream_beside_its_target_then_moved_in(rig: Rig) -> None:
    found = stored(rig, TEN)
    target = rig.tmp_path / "cache" / "233.mp4"
    target.parent.mkdir()

    download(rig.drive, rig.clock, target, found, keep_free=0, free=lambda _: ROOM)

    assert rig.drive.made() == ["stream"]
    assert target.read_bytes() == TEN
    assert [path.name for path in target.parent.iterdir()] == ["233.mp4"]


def test_a_cut_stream_starts_again_from_nothing(tmp_path: Path) -> None:
    rig = Rig(tmp_path, CutOnce)
    found = stored(rig, TEN)
    target = rig.tmp_path / "233.mp4"

    download(rig.drive, rig.clock, target, found, keep_free=0, free=lambda _: ROOM)

    assert rig.drive.made() == ["stream", "stream"]
    assert target.read_bytes() == TEN


def test_a_file_that_changed_while_read_leaves_the_target_untouched(rig: Rig) -> None:
    found = stored(rig, TEN)
    rig.drive.files[found.ref].content = b"9876543210"
    target = rig.tmp_path / "cache" / "233.mp4"
    target.parent.mkdir()

    with pytest.raises(Rejected, match="changed"):
        download(rig.drive, rig.clock, target, found, keep_free=0, free=lambda _: ROOM)

    assert list(target.parent.iterdir()) == []


def test_an_empty_file_needs_no_download(rig: Rig) -> None:
    found = stored(rig, b"")
    target = rig.tmp_path / "empty.png"

    download(rig.drive, rig.clock, target, found, keep_free=0, free=lambda _: ROOM)

    assert rig.drive.made() == []
    assert target.read_bytes() == b""


def test_a_download_that_would_fill_the_disk_writes_nothing(rig: Rig) -> None:
    # Bound set small: 10 bytes free, 4 to keep, a 10-byte file.
    found = stored(rig, TEN)
    target = rig.tmp_path / "cache" / "233.mp4"
    target.parent.mkdir()

    with pytest.raises(TooLarge) as large:
        download(rig.drive, rig.clock, target, found, keep_free=4, free=lambda _: 10)

    assert (large.value.size, large.value.most) == (10, 6)
    assert rig.drive.made() == []
    assert list(target.parent.iterdir()) == []


class CutOnce(FakeDrive):
    """Its first stream hands over one piece, then the connection drops."""

    def __init__(self, clock: Clock) -> None:
        super().__init__(clock)
        self._cut = True

    def stream(self, file_id: str, most: int, into: Callable[[bytes], object]) -> None:
        if not self._cut:
            return super().stream(file_id, most, into)
        self._cut = False

        def then_drop(piece: bytes) -> None:
            into(piece)
            raise DriveLost("Connection reset by peer")

        super().stream(file_id, most, then_drop)
