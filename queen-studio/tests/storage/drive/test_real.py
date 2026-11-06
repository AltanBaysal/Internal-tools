"""The contract on the real Drive, with the test account (step 12; FOUNDATION 6).

Opt-in: it runs only when QUEEN_STUDIO_DRIVE_TOKEN gives the path of the test account's token file
(`.secrets/drive-token.json`), which only Drive's client reads. Everything happens in a folder the
run makes and trashes at its end; files are a few bytes. Drive's own waits are real here — about
0.8 s a write from Colab, twice that from this machine (528) — so the run takes a few minutes.
"""

import os
import secrets
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.clock.clock import SystemClock
from core.storage.drive.api import FOLDER
from core.storage.drive.google import GoogleDrive
from core.storage.drive.limits import Limits
from core.storage.port import NotFound
from tests.storage.contract import Rig, change, create, entry, load
from tests.storage.drive.rigs import DriveContract, DriveRig

TOKEN = os.environ.get("QUEEN_STUDIO_DRIVE_TOKEN")

pytestmark = pytest.mark.skipif(
    not TOKEN, reason="the real Drive: QUEEN_STUDIO_DRIVE_TOKEN names the test account's token"
)


@pytest.fixture(scope="module")
def drive() -> Iterator[tuple[GoogleDrive, str]]:
    assert TOKEN
    api = GoogleDrive.from_token(Path(TOKEN))
    name = f"queen-studio-532-{secrets.token_hex(4)}"
    root = str(api.create({"name": name, "mimeType": FOLDER}, None, "id")["id"])
    try:
        yield api, root
    finally:
        api.update(root, {"trashed": True}, None, "id")


class TestRealDriveContract(DriveContract):
    @pytest.fixture
    def rig(self, drive: tuple[GoogleDrive, str], tmp_path: Path) -> Iterator[Rig]:
        api, root = drive
        made = DriveRig(api, root, SystemClock(), tmp_path)
        yield made
        made.close()


def test_a_project_seals_reopens_and_trashes_on_the_real_drive(
    drive: tuple[GoogleDrive, str], tmp_path: Path
) -> None:
    # The fake's rules, once on Drive itself: a folder and blocks at reserved ids with Drive's
    # creation times, an open block replaced by a new one and retired, the sweep's listing after
    # each sealing head, another core reading the blocks back, and the trash.
    api, root = drive
    rig = DriveRig(api, root, SystemClock(), tmp_path, Limits(tail_count=2))
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
