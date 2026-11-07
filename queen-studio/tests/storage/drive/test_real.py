"""The contract on the real Drive, with the test account (step 12; FOUNDATION 6).

Opt-in: it runs only when QUEEN_STUDIO_DRIVE_TOKEN gives the path of the test account's token file
(`.secrets/drive-token.json`), which only Drive's client reads. Files are a few bytes, but for two
uploads of ~0.5 MB in chunks. Drive's own waits are real here — about 0.8 s a write from Colab,
twice that from this machine (528) — so the run takes several minutes.

Every test works in its own folder inside the run's, trashed at its end. Drive has refused the
run's folder (403 appNotAuthorizedToChild, Sapma 6) though each child it lists could be trashed
alone (534); so a refusal is written down, test by test, in the repo's tmp/m534-real/trash.json,
and fails nothing: it says which test's sequence of calls leads to it.
"""

import json
import os
import secrets
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

from core.clock.clock import SystemClock
from core.storage.drive.api import FOLDER, DriveApi, DriveError, DriveLost
from core.storage.drive.google import ROOT, GoogleDrive
from core.storage.drive.limits import KIB, Limits
from core.storage.port import InProject, NotFound, Stored
from tests.storage.contract import Rig, change, create, entry, load, md5, written
from tests.storage.drive.rigs import DriveContract, DriveRig

TOKEN = os.environ.get("QUEEN_STUDIO_DRIVE_TOKEN")
OUT = Path(__file__).resolve().parents[4] / "tmp" / "m534-real"
# The smallest chunk Drive takes but the last.
CHUNK = 256 * KIB
TEN = b"0123456789"

pytestmark = pytest.mark.skipif(
    not TOKEN, reason="the real Drive: QUEEN_STUDIO_DRIVE_TOKEN names the test account's token"
)

Drive = tuple[GoogleDrive, str]


class Trash:
    """What became of each test's folder at its end, written as it goes."""

    def __init__(self) -> None:
        self.outcomes: dict[str, dict[str, str]] = {}

    def record(self, test: str, folder: str, outcome: str) -> None:
        self.outcomes[test] = {"folder": folder, "trash": outcome}
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "trash.json").write_text(json.dumps(self.outcomes, indent=2), encoding="utf-8")


TRASH = Trash()


def trash_and_record(api: GoogleDrive, test: str, folder: str) -> None:
    try:
        api.update(folder, {"trashed": True}, None, "id")
        TRASH.record(test, folder, "trashed")
    except DriveError as failed:
        TRASH.record(test, folder, f"refused: {failed}")


def folder_in(api: GoogleDrive, name: str, parent: str) -> str:
    made = api.create({"name": name, "mimeType": FOLDER, "parents": [parent]}, None, "id")
    return str(made["id"])


@pytest.fixture(scope="module")
def drive() -> Iterator[Drive]:
    assert TOKEN
    api = GoogleDrive.from_token(Path(TOKEN))
    root = folder_in(api, f"queen-studio-534-{secrets.token_hex(4)}", "root")
    try:
        yield api, root
    finally:
        trash_and_record(api, "the run's folder", root)


@pytest.fixture
def box(drive: Drive, request: pytest.FixtureRequest) -> Iterator[str]:
    """The test's own folder in the run's, trashed and recorded at its end."""
    api, root = drive
    name = request.node.name
    folder = folder_in(api, name[:120], root)
    yield folder
    trash_and_record(api, name, folder)


class TestRealDriveContract(DriveContract):
    @pytest.fixture
    def rig(self, drive: Drive, box: str, tmp_path: Path) -> Iterator[Rig]:
        made = DriveRig(drive[0], box, SystemClock(), tmp_path)
        yield made
        made.close()


def test_a_project_seals_reopens_and_trashes_on_the_real_drive(
    drive: Drive, box: str, tmp_path: Path
) -> None:
    # The fake's rules, once on Drive itself: a folder and blocks at reserved ids with Drive's
    # creation times, an open block replaced by a new one and retired, the sweep's listing after
    # each sealing head, another core reading the blocks back, and the trash.
    rig = DriveRig(drive[0], box, SystemClock(), tmp_path, Limits(tail_count=2))
    try:
        a = rig.open()
        project, version = create(a)
        for seq in range(2, 8):  # history seals at 3, reopens at 6
            version = a.commit(project, version, change(entry(seq)))

        seen = load(rig.open(), project)

        assert [found.seq for found in seen.recent] == list(range(1, 8))
        assert seen.version == version
        a.trash_project(project)
        with pytest.raises(NotFound):
            load(rig.open(), project)
    finally:
        rig.close()


class Watched:
    """The real Drive, its calls counted; the `lose`th chunk's answer dropped once Drive has it."""

    def __init__(self, api: GoogleDrive) -> None:
        self.api = api
        self.calls: list[str] = []
        self.lose: int | None = None

    def __getattr__(self, name: str) -> Any:
        call = getattr(self.api, name)

        def counted(*given: Any, **named: Any) -> Any:
            self.calls.append(name)
            answer = call(*given, **named)
            if name == "upload_chunk" and self.calls.count(name) == self.lose:
                raise DriveLost("The test dropped this answer after Drive took the chunk.")
            return answer

        return counted


def test_a_large_upload_goes_in_chunks_resumes_where_drive_stands_and_leaves_no_half_file(
    drive: Drive, box: str, tmp_path: Path
) -> None:
    api = drive[0]
    watched = Watched(api)
    limits = Limits(simple_most=CHUNK, chunk=CHUNK)
    rig = DriveRig(cast(DriveApi, watched), box, SystemClock(), tmp_path, limits)
    try:
        port = rig.open()
        project, _ = create(port)
        place = InProject(project)
        (warm, ref, half) = port.reserve(3)
        port.put(warm, written(tmp_path, "warm", b"x"), "17.png", place)  # finds media/
        content = secrets.token_bytes(2 * CHUNK + 1000)
        source = written(tmp_path, "233.mp4", content)
        watched.calls.clear()
        watched.lose = 2

        stored = port.put(ref, source, "233.mp4", place)

        assert stored == Stored(ref, len(content), md5(content))
        # A look at the ref; the second chunk's answer lost, Drive asked where it stands, then
        # the third.
        assert watched.calls == [
            "get",
            "upload_start",
            "upload_chunk",
            "upload_chunk",
            "upload_status",
            "upload_chunk",
        ]
        port.get(ref, tmp_path / "back.mp4", most=len(content))
        assert (tmp_path / "back.mp4").read_bytes() == content

        # A session left after one chunk makes no file.
        session = api.upload_start({"id": half, "name": "half", "parents": [box]}, 10**6, "id")
        assert api.upload_chunk(session, content[:CHUNK], 0, 10**6) == CHUNK
        assert port.exists(half) is None
        assert api.children(box, "id", name="half").files == []

        # The same put again: found by its look, no byte sent.
        watched.calls.clear()
        watched.lose = None
        assert port.put(ref, source, "233.mp4", place) == stored
        assert watched.calls == ["get"]
    finally:
        rig.close()


def test_what_the_adapter_assumes_of_drive_holds(drive: Drive, box: str) -> None:
    """534's probes, pinned: each is what the adapter or its fake assumes. Outcomes are written to
    tmp/m534-real/probes.json."""
    api = drive[0]
    seen: dict[str, Any] = {}
    ids = iter(api.generate_ids(10))
    plain = next(ids)
    made = api.create(
        {"id": plain, "name": "plain.png", "parents": [box], "mimeType": "image/png"},
        TEN,
        "id,md5Checksum,size",
    )
    try:
        # A used id: a session starts, and its last chunk is refused (transfer.py, files.put).
        session = api.upload_start({"id": plain, "name": "again"}, 10, "id")
        with pytest.raises(DriveError) as refused:
            api.upload_chunk(session, TEN, 0, 10)
        seen["409_with_the_last_chunk"] = str(refused.value)
        assert refused.value.status == 409

        # A folder never made lists as empty (places.py; the fake).
        seen["never_made_folder_lists"] = api.children(next(ids), "id").files
        assert seen["never_made_folder_lists"] == []

        # A copy at a reserved id answers its md5 and size (files.copy).
        copied = api.copy(
            plain, {"id": next(ids), "name": "copy.png", "parents": [box]}, "id,md5Checksum,size"
        )
        seen["copy"] = copied
        assert (copied["md5Checksum"], copied["size"]) == (made["md5Checksum"], "10")

        # storageQuota's fields (files.space).
        seen["quota_keys"] = sorted(api.about("storageQuota")["storageQuota"])
        assert {"usage", "usageInDriveTrash"} <= set(seen["quota_keys"])

        # alt=media is served, not redirected, and honours Range (google.stream).
        assert TOKEN
        http: Any = AuthorizedSession(Credentials.from_authorized_user_file(TOKEN))  # pyright: ignore[reportUnknownMemberType]
        url = f"{ROOT}drive/v3/files/{plain}?alt=media"
        with http.get(url, headers={"Range": "bytes=0-3"}, allow_redirects=False, timeout=30) as at:
            seen["media"] = [at.status_code, at.headers.get("Content-Range"), len(at.content)]
        assert seen["media"] == [206, "bytes 0-3/10", 4]

        # Properties alone keep the md5, the version (Writer.rename_folder).
        after = api.update(plain, {"properties": {"probe": "1"}}, None, "md5Checksum")
        assert after["md5Checksum"] == made["md5Checksum"]

        # A file made in a trashed folder is not trashed itself (the m534 spec, Drive'da).
        gone = folder_in(api, "gone", box)
        api.update(gone, {"trashed": True}, None, "id")
        late = api.create({"id": next(ids), "name": "late.png", "parents": [gone]}, TEN, "trashed")
        seen["made_in_a_trashed_folder"] = late
        assert late["trashed"] is False
    finally:
        OUT.mkdir(parents=True, exist_ok=True)
        text = json.dumps(seen, indent=2, default=str)
        (OUT / "probes.json").write_text(text, encoding="utf-8")


# -- which sequence keeps its folder out of the trash (Sapma 6) ---------------------------------


def made_in_a_trashed_folder(api: GoogleDrive, box: str, ids: Iterator[str]) -> None:
    gone = folder_in(api, "gone", box)
    api.update(gone, {"trashed": True}, None, "id")
    api.create({"id": next(ids), "name": "late.png", "parents": [gone]}, TEN, "id")


def a_child_trashed_before_its_parent(api: GoogleDrive, box: str, ids: Iterator[str]) -> None:
    inner = folder_in(api, "inner", box)
    file = next(ids)
    api.create({"id": file, "name": "f.png", "parents": [inner]}, TEN, "id")
    api.update(file, {"trashed": True}, None, "id")


def three_levels_at_pool_ids(api: GoogleDrive, box: str, ids: Iterator[str]) -> None:
    parent = box
    for name in ("projects", "p", "media"):
        at = next(ids)
        api.create({"id": at, "name": name, "mimeType": FOLDER, "parents": [parent]}, None, "id")
        parent = at
    api.create({"id": next(ids), "name": "f.png", "parents": [parent]}, TEN, "id")


def a_session_never_finished(api: GoogleDrive, box: str, ids: Iterator[str]) -> None:
    session = api.upload_start({"id": next(ids), "name": "half", "parents": [box]}, 10**6, "id")
    api.upload_chunk(session, bytes(CHUNK), 0, 10**6)


def a_409_at_a_reserved_id(api: GoogleDrive, box: str, ids: Iterator[str]) -> None:
    at = next(ids)
    api.create({"id": at, "name": "f.png", "parents": [box]}, TEN, "id")
    with pytest.raises(DriveError):
        api.create({"id": at, "name": "f.png", "parents": [box]}, TEN, "id")


def a_409_with_a_sessions_last_chunk(api: GoogleDrive, box: str, ids: Iterator[str]) -> None:
    at = next(ids)
    api.create({"id": at, "name": "f.png", "parents": [box]}, TEN, "id")
    session = api.upload_start({"id": at, "name": "f.png", "parents": [box]}, 10, "id")
    with pytest.raises(DriveError):
        api.upload_chunk(session, TEN, 0, 10)


def a_create_at_an_id_never_reserved(api: GoogleDrive, box: str, ids: Iterator[str]) -> None:
    with pytest.raises(DriveError):
        api.create({"id": "not" + next(ids), "name": "f.png", "parents": [box]}, TEN, "id")


def a_create_into_a_folder_never_made(api: GoogleDrive, box: str, ids: Iterator[str]) -> None:
    never = next(ids)
    with pytest.raises(DriveError):
        api.create(
            {"id": next(ids), "name": "photos", "mimeType": FOLDER, "parents": [never]}, None, "id"
        )


def a_copy_then_its_source_trashed(api: GoogleDrive, box: str, ids: Iterator[str]) -> None:
    source = next(ids)
    api.create({"id": source, "name": "f.png", "parents": [box]}, TEN, "id")
    api.copy(source, {"id": next(ids), "name": "001.png", "parents": [box]}, "id")
    api.update(source, {"trashed": True}, None, "id")


def a_file_trashed_then_taken_back(api: GoogleDrive, box: str, ids: Iterator[str]) -> None:
    file = next(ids)
    api.create({"id": file, "name": "f.png", "parents": [box]}, TEN, "id")
    api.update(file, {"trashed": True}, None, "id")
    api.update(file, {"trashed": False}, None, "id")


def a_head_written_over_and_its_properties_alone(
    api: GoogleDrive, box: str, ids: Iterator[str]
) -> None:
    head = next(ids)
    api.create({"id": head, "name": "h.json.gz", "parents": [box]}, TEN, "id")
    api.update(head, {"properties": {"n0": "x"}}, b"xx", "id")
    api.update(head, {"properties": {"folder": "y"}}, None, "id")


SEQUENCES: list[Callable[[GoogleDrive, str, Iterator[str]], None]] = [
    made_in_a_trashed_folder,
    a_child_trashed_before_its_parent,
    three_levels_at_pool_ids,
    a_session_never_finished,
    a_409_at_a_reserved_id,
    a_409_with_a_sessions_last_chunk,
    a_create_at_an_id_never_reserved,
    a_create_into_a_folder_never_made,
    a_copy_then_its_source_trashed,
    a_file_trashed_then_taken_back,
    a_head_written_over_and_its_properties_alone,
]


@pytest.mark.parametrize("sequence", SEQUENCES, ids=[each.__name__ for each in SEQUENCES])
def test_a_sequence_in_its_own_folder(
    drive: Drive, box: str, sequence: Callable[[GoogleDrive, str, Iterator[str]], None]
) -> None:
    # The box fixture trashes the folder and writes down whether Drive refused it.
    api = drive[0]
    sequence(api, box, iter(api.generate_ids(8)))
