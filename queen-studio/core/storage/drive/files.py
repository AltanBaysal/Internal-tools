"""The port's file operations on Drive (the m534 spec, İşlemler): DrivePort hands them here.

Every new file or folder is made at the ref the core reserved, so a repeat meets Drive's 409 and
is compared, never made twice: the same content is the same file, other content Taken. Where a
place's files go is places.py's; the bytes, transfer.py's; the waits, retry.py's. Nothing is
deleted for good: `trash` is Drive's trash, and DriveApi has no other way.
"""

import shutil
from collections.abc import Callable
from pathlib import Path, PurePath
from typing import Any, TypeGuard

from core.clock.clock import Clock
from core.lists.pattern import fold
from core.storage.drive.api import FOLDER, DriveApi
from core.storage.drive.head import MD5, check_ref
from core.storage.drive.limits import Limits
from core.storage.drive.places import Places
from core.storage.drive.retry import Conflict, Missing, again, read
from core.storage.drive.transfer import FIELDS, download, hashed, upload
from core.storage.drive.writes import PastPages, listed, trash
from core.storage.port import (
    InExport,
    NotFound,
    Place,
    Rejected,
    Space,
    Stored,
    Taken,
    TooLarge,
)

# What a look at a stored file asks: what `exists` gives, and whether it is in the trash.
_STAT = "md5Checksum,size,trashed"
# Drive shows a preview by the type; anything else is plain bytes.
_KINDS = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
}


def _free(directory: Path) -> int:
    return shutil.disk_usage(directory).free


class Files:
    def __init__(
        self,
        api: DriveApi,
        clock: Clock,
        limits: Limits,
        places: Places,
        free: Callable[[Path], int] = _free,
    ) -> None:
        self._api = api
        self._clock = clock
        self._limits = limits
        self._places = places
        self._free = free

    def put(self, ref: str, source: Path, name: str, place: Place) -> Stored:
        check_ref(ref)
        size = source.stat().st_size  # a source not there fails before Drive is asked
        metadata = {
            "id": ref,
            "name": name,
            "parents": [self._places.folder(place)],
            "mimeType": _KINDS.get(PurePath(name).suffix.lower(), "application/octet-stream"),
        }
        if size > self._limits.simple_most:
            # Drive refuses a used id only with a resumable upload's last chunk (534): a repeat
            # is looked for first, one call, rather than found after every chunk is sent again.
            found = self._at(ref)
            if found is not None:
                return self._compared(ref, found, *hashed(source))
        try:
            sent = upload(self._api, self._clock, self._limits, metadata, source, size)
        except Missing as missing:
            self._places.forget(place)
            raise NotFound(f"{_described(place)} is not on Drive: {missing}") from None
        if sent.answer is None:  # 409: something is at the ref
            return self._same(ref, sent.md5, sent.size)
        drive = _stored(ref, sent.answer)
        if drive is not None and (drive.size, drive.md5) != (sent.size, sent.md5):
            raise Taken(
                f"Drive's file at {ref} differs from the bytes sent: Drive has md5 {drive.md5} "
                f"and {drive.size:,} bytes, the bytes sent md5 {sent.md5} and {sent.size:,}."
            )
        # The md5 of what was sent, never Drive's word for it (m531).
        return Stored(ref, sent.size, sent.md5)

    def exists(self, ref: str) -> Stored | None:
        check_ref(ref)
        return self._look(ref)

    def get(self, ref: str, target: Path, most: int) -> Stored:
        check_ref(ref)
        found = self._look(ref)
        if found is None:
            raise NotFound(f"There is no file {ref}, or it is in the trash.")
        if found.size > most:
            raise TooLarge(found.size, most)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            download(self._api, self._clock, target, found, self._limits.keep_free, self._free)
        except Missing as missing:
            raise NotFound(f"File {ref} left Drive while it was read: {missing}") from None
        return found

    def copy(self, source: str, ref: str, name: str, place: Place) -> Stored:
        check_ref(source)
        check_ref(ref)
        metadata = {"id": ref, "name": name, "parents": [self._places.folder(place)]}
        try:
            answer = again(self._clock, lambda: self._api.copy(source, metadata, FIELDS))
        except Conflict:
            original = self._look(source)
            if original is None:
                raise NotFound(f"There is no file {source} to copy.") from None
            return self._same(ref, original.md5, original.size)
        except Missing as missing:  # the source or the place; Drive's words name which
            self._places.forget(place)
            raise NotFound(f"Nothing to copy {source} to {ref} with: {missing}") from None
        made = _stored(ref, answer)
        if made is None:
            raise Rejected(f"Drive's copy at {ref} came back as {answer}.")
        return made

    def trash(self, ref: str) -> None:
        check_ref(ref)
        trash(self._api, self._clock, ref)

    def export_folder(self, ref: str, name: str, inside: str | None = None) -> None:
        check_ref(ref)
        if inside is not None:
            check_ref(inside)
        parent = inside if inside is not None else self._places.exports(make=True)
        metadata = {"id": ref, "name": name, "mimeType": FOLDER, "parents": [parent]}
        try:
            again(self._clock, lambda: self._api.create(metadata, None, "id"))
        except Conflict:
            found = self._read(ref, "name,mimeType,parents")
            if (found.get("name"), found.get("mimeType"), found.get("parents")) != (
                name,
                FOLDER,
                [parent],
            ):
                raise Taken(f"Something else is at {ref}.") from None
        except Missing as missing:
            if inside is not None:
                raise NotFound(f"There is no export folder {inside}: {missing}") from None
            self._places.forget_exports()
            raise Rejected(f"exports/ is not on Drive: {missing}") from None

    def export_names(self, prefix: str) -> tuple[str, ...]:
        exports = self._places.exports(make=False)
        if exports is None:
            return ()
        # In code, with ilike's four i's: Drive's own search misses the Turkish I (528), and the
        # prefix never reaches a query.
        start = fold(prefix)
        pages = listed(self._api, self._clock, exports, "name", True, self._limits.pages)
        try:
            return tuple(
                name
                for each in pages
                if isinstance(name := each.get("name"), str) and fold(name).startswith(start)
            )
        except Missing:
            self._places.forget_exports()
            return ()
        except PastPages:
            raise Rejected(
                f"exports/ lists past {self._limits.pages} pages; the rest is not read, so the "
                "names are not given."
            ) from None

    def space(self) -> Space:
        found = read(self._clock, lambda: self._api.about("storageQuota")).get("storageQuota")
        quota: dict[str, Any] = found if isinstance(found, dict) else {}  # pyright: ignore[reportUnknownVariableType]
        limit, usage, trashed = (quota.get(key) for key in ("limit", "usage", "usageInDriveTrash"))
        if not ((limit is None or _count(limit)) and _count(usage) and _count(trashed)):
            raise Rejected(f"Drive's quota is not as this core reads it: {found!r}.")
        return Space(None if limit is None else int(limit), int(usage), int(trashed))

    # -- inside ----------------------------------------------------------------------------------

    def _at(self, ref: str) -> dict[str, Any] | None:
        """What Drive has at `ref`, or None."""
        try:
            return read(self._clock, lambda: self._api.get(ref, _STAT))
        except Missing:
            return None

    def _look(self, ref: str) -> Stored | None:
        found = self._at(ref)
        return None if found is None else _stored(ref, found)

    def _same(self, ref: str, md5: str, size: int) -> Stored:
        """After a 409: the file at `ref` if it holds these bytes, else Taken."""
        return self._compared(ref, self._at(ref) or {}, md5, size)

    def _compared(self, ref: str, found: dict[str, Any], md5: str, size: int) -> Stored:
        """`found`, at `ref`, if it is a stored file of these bytes; else Taken."""
        stored = _stored(ref, found)
        if stored is None or (stored.size, stored.md5) != (size, md5):
            raise Taken(f"Another file, a folder or a trashed file is at {ref}.")
        return stored

    def _read(self, ref: str, fields: str) -> dict[str, Any]:
        try:
            return read(self._clock, lambda: self._api.get(ref, fields))
        except Missing:
            raise Rejected(f"Drive said something is at {ref}, then that nothing is.") from None


def _stored(ref: str, found: dict[str, Any]) -> Stored | None:
    """The file Drive describes; None for one in the trash, a folder, or odd fields."""
    md5, size = found.get("md5Checksum"), found.get("size")
    if found.get("trashed") is True or not (
        isinstance(md5, str) and MD5.fullmatch(md5) and _count(size)
    ):
        return None
    return Stored(ref, int(size), md5)


def _count(value: object) -> TypeGuard[str]:
    return isinstance(value, str) and value.isdigit()


def _described(place: Place) -> str:
    if isinstance(place, InExport):
        return f"Export folder {place.folder}"
    return f"Project {place.project}'s media folder"
