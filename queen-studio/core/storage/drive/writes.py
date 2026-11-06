"""The small Drive writes every part of the adapter makes: a folder at a reserved id, a file to the
trash and back out of it. Each goes through retry.py's `again`: the same write twice is harmless.
"""

import contextlib
from datetime import datetime

from core.clock.clock import Clock
from core.storage.drive.api import FOLDER, DriveApi
from core.storage.drive.retry import Conflict, Missing, again


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


def created(value: object) -> datetime | None:
    """Drive's `createdTime`, as it writes it (2026-11-06T09:00:00.123Z)."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
