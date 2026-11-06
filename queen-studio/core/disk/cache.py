"""A cache on the machine's own disk, addressed by each file's md5 (step 4, Bellek ve disk).

What it holds never changes once written — closed blocks today, media from v1-13 — so it never goes
stale: a key is its content's md5, and a file whose bytes no longer match it is a miss, removed,
never trusted. It is bounded in bytes, the least recently used going first, and it writes only
while the disk keeps `keep_free` bytes free. A cache is a convenience: with no room, or a failed
write, it keeps nothing, logs it, and the caller goes on with what it already has in hand.

The directory is scanned once on opening (the local disk, not Drive); after that its index lives
in memory, in the order of use.
"""

import hashlib
import logging
import os
import re
import shutil
import tempfile
import threading
from collections import OrderedDict
from collections.abc import Callable
from pathlib import Path

_KEY = re.compile(r"[0-9a-f]{32}")
_PART = ".part"

log = logging.getLogger("core.disk")


def _free(directory: Path) -> int:
    return shutil.disk_usage(directory).free


class DiskCache:
    def __init__(
        self,
        directory: Path,
        most: int,
        keep_free: int,
        free: Callable[[Path], int] = _free,
    ) -> None:
        self._directory = directory
        self._most = most
        self._keep_free = keep_free
        self._free = free
        self._lock = threading.Lock()
        self._used = 0
        # Key -> size, least recently used first.
        self._index: OrderedDict[str, int] = OrderedDict()
        directory.mkdir(parents=True, exist_ok=True)
        found: list[tuple[float, str, int]] = []
        for entry in os.scandir(directory):
            if entry.name.endswith(_PART):
                Path(entry.path).unlink(missing_ok=True)  # a crash's half file
            elif _KEY.fullmatch(entry.name) and entry.is_file():
                stat = entry.stat()
                found.append((stat.st_mtime, entry.name, stat.st_size))
        for _, key, size in sorted(found):
            self._index[key] = size
            self._used += size

    def get(self, md5: str) -> bytes | None:
        path = self._path(md5)
        with self._lock:
            if md5 not in self._index:
                return None
            try:
                data = path.read_bytes()
            except OSError:
                self._drop(md5)
                return None
            if hashlib.md5(data).hexdigest() != md5:
                self._drop(md5)
                return None
            self._index.move_to_end(md5)
            return data

    def put(self, data: bytes) -> str:
        """Keeps `data` if it fits; its md5, the key, either way."""
        key = hashlib.md5(data).hexdigest()
        size = len(data)
        with self._lock:
            if key in self._index or size > self._most:
                return key
            # Nothing is evicted for a file that would not fit once all of it were.
            if self._free(self._directory) + self._used - size < self._keep_free:
                log.warning("The disk cache keeps no more: under %s bytes would stay free.", size)
                return key
            while self._index and (
                self._used + size > self._most
                or self._free(self._directory) - size < self._keep_free
            ):
                self._drop(next(iter(self._index)))
            try:
                self._write(key, data)
            except OSError as failed:
                log.warning("The disk cache could not write %s: %s", key, failed)
                return key
            self._index[key] = size
            self._used += size
        return key

    def _path(self, md5: str) -> Path:
        if not _KEY.fullmatch(md5):
            raise ValueError(f"{md5!r} is not an md5: 32 lowercase hex digits.")
        return self._directory / md5

    def _drop(self, key: str) -> None:
        # Under the lock.
        self._used -= self._index.pop(key, 0)
        (self._directory / key).unlink(missing_ok=True)

    def _write(self, key: str, data: bytes) -> None:
        # Beside it, then into place: a crash leaves a .part, removed on the next opening.
        handle, temporary = tempfile.mkstemp(dir=self._directory, suffix=_PART)
        try:
            with os.fdopen(handle, "wb") as out:
                out.write(data)
            os.replace(temporary, self._directory / key)
        except BaseException:
            Path(temporary).unlink(missing_ok=True)
            raise
