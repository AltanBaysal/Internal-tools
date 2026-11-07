"""The small Drive calls every part of the adapter makes: a folder at a reserved id or found by its
name, a listing page by page, a file to the trash and back out of it. Each write goes through
retry.py's `again`: the same write twice is harmless.
"""

import contextlib
from collections.abc import Iterator
from datetime import datetime
from typing import Any

from core.clock.clock import Clock
from core.storage.drive.api import FOLDER, DriveApi
from core.storage.drive.head import DRIVE_ID
from core.storage.drive.pool import Pool
from core.storage.drive.retry import Conflict, Missing, again, read
from core.storage.port import Rejected


class PastPages(Exception):
    """A listing with more pages than its bound: what was read is not the whole."""


def trash(api: DriveApi, clock: Clock, file_id: str) -> None:
    """To the trash, never deleted for good; one never made, or gone, is not there either way."""
    with contextlib.suppress(Missing):
        again(clock, lambda: api.update(file_id, {"trashed": True}, None, "id"))


def untrash(api: DriveApi, clock: Clock, file_id: str) -> None:
    """Out of the trash; Missing when Drive has it no more."""
    again(clock, lambda: api.update(file_id, {"trashed": False}, None, "id"))


def folder_at(api: DriveApi, clock: Clock, folder: str, name: str, parent: str) -> None:
    """A folder at a reserved id; a 409 is an earlier try that made it. Unusable when Drive no
    longer takes the id."""
    metadata = {"id": folder, "name": name, "mimeType": FOLDER, "parents": [parent]}
    with contextlib.suppress(Conflict):
        again(clock, lambda: api.create(metadata, None, "id"), fresh=True)


def folder_listed(api: DriveApi, clock: Clock, name: str, parent: str) -> str | None:
    """The oldest folder `name` in `parent`, or None. Missing when `parent` is not on Drive."""
    files = read(clock, lambda: api.children(parent, "id", folders=True, name=name)).files
    if not files:
        return None
    found = files[0].get("id")
    if not (isinstance(found, str) and DRIVE_ID.fullmatch(found)):
        raise Rejected(f"Drive lists {name}/ in {parent} with the id {found!r}.")
    return found


def folder_named(api: DriveApi, clock: Clock, pool: Pool, name: str, parent: str) -> str:
    """The oldest folder `name` in `parent`, made at a reserved id if none is there and listed
    again: two cores making it at once each make one, and both take the oldest. Missing when
    `parent` is not on Drive."""
    found = folder_listed(api, clock, name, parent)
    if found is None:
        pool.make(lambda at: folder_at(api, clock, at, name, parent))
        found = folder_listed(api, clock, name, parent)
        if found is None:
            raise Rejected(f"{name}/ was made in {parent} and is not listed there.")
    return found


def listed(
    api: DriveApi, clock: Clock, parent: str, fields: str, folders: bool | None, pages: int
) -> Iterator[dict[str, Any]]:
    """What is in `parent`, out of the trash, a page at a time. Missing when `parent` is not on
    Drive; PastPages past `pages` pages, the rest unread: each caller says what that means."""
    page: str | None = None
    for _ in range(pages):
        found = read(
            clock, lambda page=page: api.children(parent, fields, folders=folders, page=page)
        )
        yield from found.files
        if found.next is None:
            return
        page = found.next
    raise PastPages(pages)


def created(value: object) -> datetime | None:
    """Drive's `createdTime`, as it writes it (2026-11-06T09:00:00.123Z)."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
