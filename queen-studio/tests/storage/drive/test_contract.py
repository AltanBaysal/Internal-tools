from collections.abc import Iterator
from pathlib import Path

import pytest

from core.clock.clock import ManualClock
from tests.storage.contract import T0, Rig
from tests.storage.drive.fake import FakeDrive
from tests.storage.drive.rigs import DriveContract, DriveRig


class TestFakeDriveContract(DriveContract):
    @pytest.fixture
    def rig(self, tmp_path: Path) -> Iterator[Rig]:
        clock = ManualClock(T0)
        drive = FakeDrive(clock)
        made = DriveRig(drive, drive.folder("root"), clock, tmp_path)
        yield made
        made.close()
