"""A change's writes, once its look has passed (the m532 spec, `commit` and Mühür): the project's
folder on its first seal, the blocks, the head, and — once the head stands — the tidying.

Order is what keeps a project whole: no head names a block not yet written; the head is written
by its deadline or not at all, so no head lands so late that it names a block another core has
since trashed; and the trash and the sweep come after the head, so a failed tidy-up neither delays
nor fails the change. A folder made at a new id, the reserved one refused, goes back to the trash
if the change then fails: no head names it.

`rename_folder` is the one other write to a head: its `folder` property alone, when a project's
first file made `<p>/` at a new id (places.py), under the same project lock as a commit.
"""

import logging
from datetime import datetime
from typing import Any

from core.clock.clock import Clock
from core.storage.drive.api import DriveApi
from core.storage.drive.blocks import Blocks
from core.storage.drive.head import Head, properties, read_folder
from core.storage.drive.limits import Limits
from core.storage.drive.pool import Pool
from core.storage.drive.retry import Missing, Unusable, again, read, written
from core.storage.drive.seal import Planned, Sealing, finish, sealed
from core.storage.drive.writes import folder_at, trash
from core.storage.port import Commit, NotFound, Rejected, StorageError, Unconfirmed

log = logging.getLogger("core.storage")


class Writer:
    def __init__(
        self,
        api: DriveApi,
        clock: Clock,
        pool: Pool,
        blocks: Blocks,
        limits: Limits,
        projects: str,
    ) -> None:
        self._api = api
        self._clock = clock
        self._pool = pool
        self._blocks = blocks
        self._limits = limits
        self._projects = projects

    def sealed(self, head: Head, change: Commit) -> Sealing:
        """The blocks to write, and the head as it would be, packed once to meet its bound
        before anything is written."""
        sealing = sealed(
            head, change, self._limits, self._blocks.one, lambda: self._pool.take(1)[0]
        )
        now = self._clock.now()
        finish(head, change, sealing, {write.id: now for write in sealing.blocks}, self._limits)
        return sealing

    def write(
        self,
        project: str,
        head: str,
        folder: str,
        base: Head,
        change: Commit,
        sealing: Sealing,
        expected: str,
        deadline: datetime,
    ) -> tuple[Planned, str]:
        """The change written on `base`, the head at `expected`: the head written, and the folder
        it names."""
        made_folder: str | None = None  # one made at a new id, the reserved one refused
        try:
            created: dict[str, datetime] = {}
            if sealing.blocks:
                if sealing.opens_folder:
                    opened = self._open_folder(project, folder)
                    if opened != folder:
                        # The pool the blocks were planned from was refused with it.
                        made_folder = folder = opened
                        sealing = self.sealed(base, change)
                sealing, created = self._write_blocks(project, folder, base, change, sealing)
            planned = finish(base, change, sealing, created, self._limits)
            metadata = {"properties": properties(change.row, folder)}
            self._write_head(head, expected, planned, metadata, deadline)
        except Unconfirmed:
            raise  # its head may name the new folder
        except BaseException:
            if made_folder is not None:  # no head names it: it goes, with what was put in it
                self._quietly_trash(made_folder)
            raise
        if planned.now is not None:
            self._tidy(folder, planned, planned.now)
        return planned, folder

    def rename_folder(self, project: str, head: str, old: str, made: str) -> str:
        """The head's `folder` property turned from `old` to `made`, a `<p>/` made at a new id by
        a project's first file (places.py), since Drive no longer takes `old`; the folder the head
        names after. The caller holds the project's lock, so no commit of this core is between
        its look and its write: the properties are read again here, and if another core turned
        them first its folder stands and `made` goes to the trash. Properties alone are written:
        Drive keeps the keys not sent, and the content's md5, the version, stays."""

        def trashed(found: dict[str, Any]) -> dict[str, Any]:
            if found.get("trashed") is True:
                raise NotFound(f"Project {project} went to the trash meanwhile.")
            return found

        try:
            seen = trashed(read(self._clock, lambda: self._api.get(head, "properties,trashed")))
            named = read_folder(seen.get("properties"))
            if named == old:
                update = {"properties": {"folder": made}}
                trashed(again(self._clock, lambda: self._api.update(head, update, None, "trashed")))
                named = made
        except Missing:
            self._quietly_trash(made)
            raise NotFound(f"Project {project}'s head file is gone.") from None
        except BaseException:
            self._quietly_trash(made)  # no head names it
            raise
        if named == made:
            log.warning(
                "Drive refused project %s's folder id; its folder is now %s.", project, made
            )
        else:
            self._quietly_trash(made)
        return named

    def _open_folder(self, project: str, folder: str) -> str:
        """The project's folder, on its first seal, at the id reserved at its creation; if Drive
        no longer takes it, at a new one, which the head's properties then name."""
        try:
            return self._pool.make(
                lambda made: folder_at(self._api, self._clock, made, project, self._projects),
                first=folder,
            )
        except Unconfirmed as unconfirmed:
            raise Rejected(unconfirmed.said, unconfirmed.code) from unconfirmed
        except Missing as missing:
            raise Rejected(f"projects/ is not on Drive: {missing}") from None

    def _write_blocks(
        self, project: str, folder: str, base: Head, change: Commit, sealing: Sealing
    ) -> tuple[Sealing, dict[str, datetime]]:
        """Each block, before the head: the sealing written, and the time Drive made each block.
        Ids Drive no longer takes are planned again once. A failed write leaves the change
        unmade: Rejected; what was written no head names, for the sweep."""
        for attempt in range(2):
            try:
                created = {write.id: self._blocks.write(folder, write) for write in sealing.blocks}
                return sealing, created
            except Unusable as unusable:
                if attempt:
                    raise Rejected(unusable.said, unusable.code) from None
                self._pool.drop()
                sealing = self.sealed(base, change)
            except Unconfirmed as unconfirmed:
                raise Rejected(unconfirmed.said, unconfirmed.code) from unconfirmed
            except Missing as missing:
                raise Rejected(f"Project {project}'s folder is not on Drive: {missing}") from None
        raise AssertionError("unreachable")

    def _write_head(
        self,
        head: str,
        expected: str,
        planned: Planned,
        metadata: dict[str, Any],
        deadline: datetime,
    ) -> None:
        """Content and properties in one call, looked at before any second try, none past
        `deadline`."""

        def trashed(found: dict[str, Any]) -> dict[str, Any]:
            # Drive writes into a trashed file and says so only in `trashed` (m531).
            if found.get("trashed") is True:
                raise NotFound(f"The head file {head} went to the trash meanwhile.")
            return found

        def write() -> object:
            return trashed(self._api.update(head, metadata, planned.gz, "md5Checksum,trashed"))

        def look() -> str:
            return str(trashed(self._api.get(head, "md5Checksum,trashed")).get("md5Checksum"))

        try:
            written(self._clock, write, look, planned.version, expected, deadline)
        except Missing:
            raise NotFound(f"The head file {head} is gone.") from None

    def _tidy(self, folder: str, planned: Planned, now: datetime) -> None:
        """Once the head stands: the retired blocks old enough to the trash, then the sweep. A
        failure delays nothing and fails nothing: a block left is the next sweep's."""
        for retired in planned.trash:
            self._quietly_trash(retired)
        retired_now = {each.id for each in planned.head.retired}
        self._blocks.sweep(folder, planned.head.named(), retired_now, now)

    def _quietly_trash(self, file_id: str) -> None:
        try:
            trash(self._api, self._clock, file_id)
        except StorageError as failed:
            log.warning("%s stays out of the trash for now: %s", file_id, failed)
