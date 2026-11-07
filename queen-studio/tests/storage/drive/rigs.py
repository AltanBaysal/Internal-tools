"""What the Drive adapter's two contract runs share: the fake API's and the real Drive's."""

from pathlib import Path

from core.clock.clock import Clock
from core.disk.cache import DiskCache
from core.storage.drive.adapter import PROJECTS, DrivePort
from core.storage.drive.api import DriveApi
from core.storage.drive.limits import Limits
from tests.storage.contract import PortContract

CACHE_BYTES = 10 * 1024 * 1024


class DriveContract(PortContract):
    """The whole contract, on a Drive."""


class DriveRig:
    """Each `open` is another core: its own port, its own disk, on the one Drive."""

    def __init__(
        self, api: DriveApi, root: str, clock: Clock, disk: Path, limits: Limits | None = None
    ) -> None:
        self.api = api
        self.root = root
        self.clock = clock
        self.disk = disk
        self.limits = limits
        self.ports: list[DrivePort] = []

    def open(self) -> DrivePort:
        cache = DiskCache(self.disk / f"core-{len(self.ports)}", most=CACHE_BYTES, keep_free=0)
        port = DrivePort.open(self.api, self.root, self.clock, cache, self.limits)
        self.ports.append(port)
        return port

    def close(self) -> None:
        for port in self.ports:
            port.close()

    def spoil(self, project: str) -> None:
        """Bytes no reader opens, in the head's place; its properties stay, as a hand's upload or
        a broken writer would leave them."""
        self.api.update(self.head(project), {}, b"xx", "id")

    def head(self, project: str) -> str:
        (projects,) = self.api.children(self.root, "id", folders=True, name=PROJECTS).files
        (head,) = self.api.children(
            str(projects["id"]), "id", folders=False, name=f"{project}.json.gz"
        ).files
        return str(head["id"])
