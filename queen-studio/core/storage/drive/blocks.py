"""A project's blocks: read from the disk cache or Drive, written at fresh ids, and its folder swept
(the m532 spec, Mühür).

A block never changes once written, so the disk cache keeps it by its md5 for good; one not on the
disk is downloaded, a few at once, by one pool of threads that lives as long as the port.

The sweep runs after a sealing change's head is written, about one change in a hundred: one
listing of the project's folder. It trashes each block that the head does not name, that is not
retired, and that Drive made more than twice `retire_after` ago — a core that lost a race of two
writes at once, or died between a block and its head, left it; nothing newer, which a commit still
in flight may yet name. And, the listing being whole, it takes back out of the trash any block the
head names that is not in it: a block the trash took too early is the one fault that would lose a
project for good, 30 days later.
"""

import contextlib
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from core.clock.clock import Clock
from core.disk.cache import DiskCache
from core.storage.drive.api import DriveApi
from core.storage.drive.head import GZIP, Block, read_lines
from core.storage.drive.limits import Limits
from core.storage.drive.retry import Conflict, Missing, again, read
from core.storage.drive.seal import Write
from core.storage.drive.writes import created, trash, untrash
from core.storage.port import StorageError, Unreadable

# Measured: eight reads at once go no slower (528); four blocks download together.
WORKERS = 4
_SWEEP_FIELDS = "id,name,mimeType,createdTime"
_BLOCK_NAME = re.compile(r"(records|history)-\d+\.jsonl\.gz")

log = logging.getLogger("core.storage")


class Blocks:
    def __init__(self, api: DriveApi, clock: Clock, cache: DiskCache, limits: Limits) -> None:
        self._api = api
        self._clock = clock
        self._cache = cache
        self._limits = limits
        # Its threads start at the first downloads that go together, and end at close.
        self._downloads = ThreadPoolExecutor(max_workers=WORKERS)

    def close(self) -> None:
        self._downloads.shutdown(wait=True)

    def lines(self, blocks: tuple[Block, ...]) -> list[list[bytes]]:
        """Each block's lines, in order."""
        if len(blocks) <= 1:
            return [self.one(block) for block in blocks]
        return list(self._downloads.map(self.one, blocks))

    def one(self, block: Block) -> list[bytes]:
        most = self._limits.block_most
        data = self._cache.get(block.gz)
        if data is not None:
            return read_lines(data, block, most)
        try:
            data = read(self._clock, lambda: self._api.download(block.id, most))
        except Missing as missing:
            raise Unreadable(f"Block {block.id} is not on Drive: {missing}") from None
        if len(data) > most:
            raise Unreadable(f"Block {block.id} is past the {most:,} bytes it may have.")
        lines = read_lines(data, block, most)
        self._cache.put(data)
        return lines

    def write(self, folder: str, write: Write) -> datetime:
        """At its fresh id; the time Drive made it. A 409 is a try of this one that got no answer:
        its time is asked for (+1). Unusable when Drive no longer takes the id."""
        metadata = {"id": write.id, "name": write.name, "mimeType": GZIP, "parents": [folder]}
        made: object = None
        with contextlib.suppress(Conflict):
            answer = again(
                self._clock,
                lambda: self._api.create(metadata, write.gz, "id,createdTime"),
                fresh=True,
            )
            made = answer.get("createdTime")
        if made is None:
            made = read(self._clock, lambda: self._api.get(write.id, "createdTime"))["createdTime"]
        self._cache.put(write.gz)
        time = created(made)
        if time is None:
            raise Unreadable(f"Drive gives block {write.id} no creation time: {made!r}.")
        return time

    def sweep(self, folder: str, named: set[str], retired: set[str], now: datetime) -> None:
        """Trashes the folder's blocks neither named nor retired made more than twice
        `retire_after` before `now`, Drive's time; untrashes a named one the whole listing lacks.
        A failure is logged: the next seal sweeps again."""
        made_before = now - timedelta(seconds=2 * self._limits.retire_after)
        listed: set[str] = set()
        page: str | None = None
        try:
            for _ in range(self._limits.pages):
                found = read(
                    self._clock,
                    lambda page=page: self._api.children(
                        folder, _SWEEP_FIELDS, folders=False, page=page
                    ),
                )
                for file in found.files:
                    file_id, name = str(file.get("id")), file.get("name")
                    listed.add(file_id)
                    made = created(file.get("createdTime"))
                    if (
                        isinstance(name, str)
                        and _BLOCK_NAME.fullmatch(name)
                        and file_id not in named | retired
                        and made is not None
                        and made < made_before
                    ):
                        trash(self._api, self._clock, file_id)
                if found.next is None:
                    break
                page = found.next
            else:
                log.warning(
                    "Folder %s lists past %s pages; the rest waits.", folder, self._limits.pages
                )
                return  # not whole: what is missing from it may just be on a page not read
            for missing in named - listed:
                log.warning("Block %s is named and was in the trash: taken back out.", missing)
                try:
                    untrash(self._api, self._clock, missing)
                except Missing as gone:
                    log.error("Block %s is named and gone from Drive: %s", missing, gone)
        except Missing as gone:
            log.warning("Folder %s was not swept: %s", folder, gone)
        except StorageError as failed:  # the sweep is tidying, never the change itself
            log.warning("Folder %s was not swept: %s", folder, failed)
