"""ProjectStore over Storage -- the only place that knows a project IS one folder directly
under the Drive root. The root itself comes from config; the domain never learns where it is.

It is also the only place that knows what archiving means, which since madde 227 is a MARK and not a
move: the project stays exactly where it is and goes on working -- it opens, it renders, it exports
-- and the mark says which of the two lists it is drawn in. Madde 221 moved the folder instead, and
the move closed the project to everything that reaches it by name; the user, having used it, asked
for the opposite.

Nothing here carries home what that version moved. An install from those days has projects sitting
under arsiv/, and moving them back is done in Drive by hand -- the user's own call, so that a repair
needed once does not live in this file forever.
"""
import json
import threading

from backend.features.projects.domain import name_rules
from backend.features.projects.domain.project import Project

# One file at the root rather than one flag per project: drawing the list would otherwise open N
# files over Drive, and this screen is slow enough already (madde 225).
MARK_FILE = "arsiv.json"
KEY = "arsiv"
# How old another delete's trash is before a delete sweeps it, in seconds: far past any removal
# still going.
STALE = 3600


def _parse(raw):
    """The archived names in the mark file's text; none when there is no file. A ValueError when
    the text is not one this store wrote."""
    if raw is None:
        return []
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get(KEY), list):
        raise ValueError(f'"{KEY}" listesi yok')
    return data[KEY]


class DriveProjectStore:
    def __init__(self, storage):
        self.storage = storage
        # Every change of the marks reads the one file and writes it back whole: two at once, even
        # for two projects, would each write the list they read and the first one's mark would be
        # lost (madde 523). One process serves every press. Nothing is taken inside it, and it is
        # held for a read, a write and at most a folder's rename -- a rename holds it under the
        # project's name lock, which the loop waits on, so a folder's removal never runs in it.
        self._lock = threading.Lock()

    # --- the mark ---------------------------------------------------------------------------

    def _marks(self):
        """The archived names, for drawing a list. Anything unreadable is an empty archive, which
        is settings.json's own rule: no broken file may make the list of projects impossible to
        draw."""
        try:
            return _parse(self.storage.read_text((), MARK_FILE))
        except ValueError:
            return []

    def _held_marks(self):
        """The archived names, for a change that writes them back.

        Strict where _marks is lenient: an unreadable file read as empty and written back would lose
        every mark it held, so the change stops with the reason instead and the file stays as it is.
        """
        try:
            return _parse(self.storage.read_text((), MARK_FILE))
        except ValueError as exc:
            raise OSError(f"{MARK_FILE} okunamıyor, üstüne yazılmadı: {exc}") from exc

    def _write_marks(self, names):
        self.storage.write_text(
            (), MARK_FILE, json.dumps({KEY: names}, ensure_ascii=False, indent=2))

    # --- the two lists ----------------------------------------------------------------------

    def list(self):
        marks = self._marks()
        # The root's folders ARE the projects, but for the app's own (name_rules): the folder madde
        # 221 moved archived projects into, which old installs still have. Neither list ever draws
        # it as a card.
        return [Project(name, mtime) for name, mtime in self.storage.list_dirs()
                if name not in marks and not name_rules.is_reserved(name)]

    def list_archived(self):
        marks = self._marks()
        return [Project(name, mtime) for name, mtime in self.storage.list_dirs()
                if name in marks and not name_rules.is_reserved(name)]

    # --- putting away and taking back -------------------------------------------------------

    def archive(self, name):
        """True, or False when there is no such project.

        A bool and not the project: nothing moves, so there is no new date to report, and reading
        one back would cost another listing over Drive.
        """
        if not self.storage.dir_exists(name):
            return False
        with self._lock:
            marks = self._held_marks()
            if name not in marks:
                self._write_marks(marks + [name])
        return True

    def restore(self, name):
        with self._lock:
            marks = self._held_marks()
            if name not in marks:
                return False
            self._write_marks([held for held in marks if held != name])
        return True

    def is_archived(self, name):
        """Asked when a create or a rename was refused, to tell that refusal's sentence from the
        ordinary one (madde 223)."""
        return name in self._marks()

    # --- the rest ---------------------------------------------------------------------------

    def create(self, name):
        mtime = self.storage.make_dir(name)
        if mtime is None:
            return None
        return Project(name, mtime)

    def delete(self, name):
        """Take the project away at once: its folder put in the trash, its mark dropped. What is
        left to clear -- the trash -- or False when there was no such project.

        The folder goes in one rename (Storage.trash_dir) rather than a removal, which over Drive
        takes tens of seconds: an upload writing into the folder meanwhile made the removal fail half
        way, and the project survived, gutted, holding that upload (madde 523's QA). Renamed, the
        name is gone at once, and the slow part is clear's, after the caller has let the project's
        gate go.

        The mark goes with it. A name left behind breaks no list -- there is no folder under it --
        right up until somebody makes a project with that name, which would then be born archived.
        The marks are read before the folder goes, so a file that cannot be read stops the delete
        while the project is still there, and written after, so a rename that fails leaves an
        archived project archived. All three under the marks' lock, as a rename of a project is:
        one read, one rename, one write.
        """
        with self._lock:
            marks = self._held_marks()
            trash = self.storage.trash_dir(name)
            if name in marks:
                self._write_marks([held for held in marks if held != name])
        return trash

    def clear(self, trash):
        """Remove what delete put in the trash, and sweep the trash older deletes left -- a removal
        that failed, or a server that died -- once it is STALE seconds old: a younger one may be
        another delete's, still being removed.

        Never raises: the project is already gone, and an error now would tell the user a delete
        failed that did not. What cannot be removed stays hidden from every list, for the next
        delete's sweep.
        """
        try:
            self.storage.delete_dir(trash)
            self.storage.sweep_trash(STALE)
        except OSError:
            pass

    def rename(self, old, new):
        """The renamed project, None when the new name is taken, False when the old one is gone.

        The marks are read first, for the reason delete reads them first. The folder's move is
        under the marks' lock with them: it is one rename, and a mark change of another project
        landing between the read and the write would be lost."""
        with self._lock:
            marks = self._held_marks()
            moved = self.storage.rename_dir(old, new)
            # `is` and not truthiness: an mtime can be 0.0 and that is a success.
            if moved is None or moved is False:
                return moved
            # The mark hangs on a name now rather than on where the folder sits, so it has to
            # follow.
            if old in marks:
                self._write_marks([new if held == old else held for held in marks])
        return Project(new, moved)
