"""What the Drive adapter's two contract runs share: the fake API's and the real Drive's."""

from pathlib import Path

import pytest

from core.clock.clock import Clock
from core.disk.cache import DiskCache
from core.storage.drive.adapter import PROJECTS, DrivePort
from core.storage.drive.api import DriveApi
from core.storage.drive.limits import Limits
from tests.storage.contract import PortContract

# The contract's tests of the file operations, which are v1-9's (the m532 spec, Testler); v1-9
# deletes this list.
FILES_V1_9 = frozenset(
    {
        "test_a_create_where_a_file_or_folder_is_is_taken",
        "test_a_malformed_project_id_is_refused_before_the_store_is_asked",
        "test_a_file_put_is_read_back_by_another_core",
        "test_putting_the_same_file_again_leaves_one_file",
        "test_other_content_at_a_used_ref_is_taken",
        "test_a_ref_never_reserved_is_refused",
        "test_get_refuses_a_file_over_its_bound_and_writes_nothing",
        "test_a_missing_file_is_not_found",
        "test_a_trashed_file_is_gone_and_trashing_again_succeeds",
        "test_a_copy_is_a_new_file_and_its_repeat_is_the_same",
        "test_an_export_has_its_video_and_a_photos_folder",
        "test_a_folder_is_opened_only_inside_a_folder_that_is_there",
        "test_export_folders_are_found_by_how_their_name_begins",
        "test_no_file_is_put_into_a_project_never_there",
        "test_space_says_quota_use_and_trash",
    }
)
CACHE_BYTES = 10 * 1024 * 1024


class DriveContract(PortContract):
    @pytest.fixture(autouse=True)
    def files_are_v1_9(self, request: pytest.FixtureRequest) -> None:
        if request.function.__name__ in FILES_V1_9:
            pytest.skip("files: v1-9")


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
