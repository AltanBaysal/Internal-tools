"""Where a place's files go on Drive (the m534 spec, Drive'da): a project's `<p>/media/`, an
export's folder, and `exports/` in the root.

`media/` and `exports/` are found by their names, once per port, and kept in its memory: no head
file names them, so a put never writes one. One not there is made at a reserved id and listed
again, the oldest taken (writes.folder_named): two cores making it at once meet in one.

A project's own folder `<p>/` is made by its first file or its first seal, whichever comes first,
at the id its head's properties name. If Drive no longer takes that id (528, 6), it is made at a
new one and the head's `folder` property turned to it, by `rename`: Writer.rename_folder, under
the project's lock. Locks are taken in that order, a place's then its project's, never the other.
"""

import threading
from collections.abc import Callable

from core.clock.clock import Clock
from core.storage.drive.api import DriveApi
from core.storage.drive.head import check_ref
from core.storage.drive.kept import Kept, Where
from core.storage.drive.pool import Pool
from core.storage.drive.retry import Missing
from core.storage.drive.writes import folder_at, folder_listed, folder_named
from core.storage.port import (
    InExport,
    InProject,
    Place,
    Rejected,
    Unreadable,
    check_project,
)

MEDIA = "media"
EXPORTS = "exports"

# (project, its head, the folder id refused, the folder made) -> the folder the head names.
Rename = Callable[[str, str, str, str], str]


class Places:
    def __init__(
        self,
        api: DriveApi,
        clock: Clock,
        pool: Pool,
        kept: Kept,
        root: str,
        projects: str,
        find: Callable[[str], Where],
        rename: Rename,
    ) -> None:
        """`find`: a project's head and folder by its name, when the port does not know it."""
        self._api = api
        self._clock = clock
        self._pool = pool
        self._kept = kept
        self._root = root
        self._projects = projects
        self._find = find
        self._rename = rename
        # One lock a project, held while its media/ is found: its first files, made together
        # (a job's variants), wait for one finding rather than making a folder each. Other
        # projects do not wait.
        self._locks_lock = threading.Lock()
        self._locks: dict[str, threading.Lock] = {}
        self._media: dict[str, str] = {}  # project -> its media/: as many as there are projects
        self._exports_lock = threading.Lock()
        self._exports: str | None = None

    def folder(self, place: Place) -> str:
        """The folder a new file in `place` goes into. NotFound for a project never there."""
        match place:
            case InExport(folder=folder):
                check_ref(folder)
                return folder
            case InProject(project=project):
                check_project(project)
                return self._media_of(project)

    def forget(self, place: Place) -> None:
        """Drive said the place's folder is not there: the next file finds it again."""
        if isinstance(place, InProject):
            with self._lock_of(place.project):
                self._media.pop(place.project, None)

    def exports(self, make: bool) -> str | None:
        """`exports/`; None while it is not there, unless `make`."""
        with self._exports_lock:
            if self._exports is None:
                try:
                    if make:
                        self._exports = folder_named(
                            self._api, self._clock, self._pool, EXPORTS, self._root
                        )
                    else:
                        self._exports = folder_listed(self._api, self._clock, EXPORTS, self._root)
                except Missing as missing:
                    raise Rejected(f"The root folder is not on Drive: {missing}") from None
            return self._exports

    def forget_exports(self) -> None:
        with self._exports_lock:
            self._exports = None

    # -- a project's media/ ----------------------------------------------------------------------

    def _media_of(self, project: str) -> str:
        # Looked up each time, at no call while known: a project this port trashed is not there.
        where = self._kept.where(project) or self._find(project)
        with self._lock_of(project):
            known = self._media.get(project)
            if known is not None:
                return known
            if where.folder is None:
                raise Unreadable(f"Project {project}'s head file names no folder for its files.")
            try:
                media = folder_listed(self._api, self._clock, MEDIA, where.folder)
            except Missing:
                media = None
            if media is None:
                # No media/, or no <p>/ yet: Drive lists a folder never made as empty (534). The
                # reserved <p>/ is opened (a 409 if it is there), then media/ found or made in it.
                opened = self._open(project, where.folder, where.head)
                try:
                    media = folder_named(self._api, self._clock, self._pool, MEDIA, opened)
                except Missing as missing:
                    raise Rejected(
                        f"Project {project}'s folder is not on Drive: {missing}"
                    ) from None
            self._media[project] = media
            return media

    def _open(self, project: str, folder: str, head: str) -> str:
        """`<p>/` at the id its head names; at a new one, named in the head, if Drive no longer
        takes it."""
        try:
            made = self._pool.make(
                lambda at: folder_at(self._api, self._clock, at, project, self._projects),
                first=folder,
            )
        except Missing as missing:
            raise Rejected(f"projects/ is not on Drive: {missing}") from None
        if made == folder:
            return made
        named = self._rename(project, head, folder, made)
        self._kept.remember(project, Where(head, named))
        return named

    def _lock_of(self, project: str) -> threading.Lock:
        # One per project a file went to: as many as there are projects.
        with self._locks_lock:
            return self._locks.setdefault(project, threading.Lock())
