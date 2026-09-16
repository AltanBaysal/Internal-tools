"""ProjectStore over DriveStorage -- the only place that knows a project IS one folder directly
under the Drive root. The root itself comes from config; the domain never learns where it is.

It is also the only place that knows what archiving means, which since madde 227 is a MARK and not a
move: the project stays exactly where it is and goes on working -- it opens, it renders, it exports
-- and the mark says which of the two lists it is drawn in. Madde 221 moved the folder instead, and
the move closed the project to everything that reaches it by name; the user, having used it, asked
for the opposite.
"""
import json

from backend.features.projects.domain import name_rules
from backend.features.projects.domain.project import Project

# One file at the root rather than one flag per project: drawing the list would otherwise open N
# files over Drive, and this screen is slow enough already (madde 225).
MARK_FILE = "arsiv.json"
KEY = "arsiv"


class DriveProjectStore:
    def __init__(self, storage):
        self.storage = storage
        self._carry_back_the_old_archive()

    # --- the mark ---------------------------------------------------------------------------

    def _marks(self):
        """The archived names. Anything unreadable is an empty archive, which is settings.json's own
        rule: no broken file may make the list of projects impossible to draw."""
        raw = self.storage.read_text("", MARK_FILE)
        if raw is None:
            return []
        try:
            data = json.loads(raw)
        except ValueError:
            return []
        names = data.get(KEY) if isinstance(data, dict) else None
        if not isinstance(names, list):
            return []
        return [name for name in names if isinstance(name, str)]

    def _write_marks(self, names):
        self.storage.write_text(
            "", MARK_FILE, json.dumps({KEY: names}, ensure_ascii=False, indent=2))

    # --- the two lists ----------------------------------------------------------------------

    def list(self):
        marks = self._marks()
        # ARCHIVE_DIR is skipped for the one case the migration cannot finish: a folder it could not
        # empty stays, and the root's folders ARE the projects, so it would show up as one.
        return [Project(name, mtime) for name, mtime in self.storage.list_dirs()
                if name not in marks and name != name_rules.ARCHIVE_DIR]

    def list_archived(self):
        marks = self._marks()
        return [Project(name, mtime) for name, mtime in self.storage.list_dirs()
                if name in marks]

    # --- putting away and taking back -------------------------------------------------------

    def archive(self, name):
        """True, or False when there is no such project.

        A bool and not the project: nothing moves, so there is no new date to report, and reading
        one back would cost another listing over Drive.
        """
        if not self.storage.dir_exists(name):
            return False
        marks = self._marks()
        if name not in marks:
            self._write_marks(marks + [name])
        return True

    def restore(self, name):
        marks = self._marks()
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
        """Remove the project folder with everything in it; False when there was nothing to remove.

        The mark goes with it. A name left behind breaks no list -- there is no folder under it --
        right up until somebody makes a project with that name, which would then be born archived.
        """
        gone = self.storage.delete_dir(name)
        marks = self._marks()
        if name in marks:
            self._write_marks([held for held in marks if held != name])
        return gone

    def rename(self, old, new):
        """The renamed project, None when the new name is taken, False when the old one is gone."""
        moved = self.storage.rename_dir(old, new)
        # `is` and not truthiness: an mtime can be 0.0 and that is a success.
        if moved is None or moved is False:
            return moved
        # The mark hangs on a name now rather than on where the folder sits, so it has to follow.
        marks = self._marks()
        if old in marks:
            self._write_marks([new if held == old else held for held in marks])
        return Project(new, moved)

    # --- madde 221's leftovers --------------------------------------------------------------

    def _carry_back_the_old_archive(self):
        """Bring home whatever madde 221 moved into arsiv/.

        The mark knows nothing about those folders and they are not in the root, so left alone they
        appear in neither list -- a project the user cannot see rather than one they put away.

        Costs one isdir per start, and after the first start there is nothing to find.
        """
        old = name_rules.ARCHIVE_DIR
        inside = self.storage.list_dirs(old)
        if not inside:
            return
        marks = self._marks()
        for name, _mtime in inside:
            landed = self._free_name(name)
            self.storage.rename_dir(f"{old}/{name}", landed)
            if landed not in marks:
                marks.append(landed)
        self._write_marks(marks)
        # Only when it really is empty. Anything unexpected left in there is somebody's, and
        # list() steps over the folder for exactly this case.
        if not self.storage.list_dirs(old) and not self.storage.list_files(old):
            self.storage.delete_dir(old)

    def _free_name(self, name):
        """The name itself when the root is free, otherwise one beside it.

        Before madde 223 an archived name could be handed to a new project -- that is the bug the
        user reported, so this pair really can be sitting on their Drive. Neither one may be lost,
        so the returning project takes a name that says where it came from. Length is not checked:
        these are folders that already exist, not names anybody is typing.
        """
        if not self.storage.dir_exists(name):
            return name
        candidate = f"{name} (arşiv)"
        nth = 2
        while self.storage.dir_exists(candidate):
            candidate = f"{name} (arşiv {nth})"
            nth += 1
        return candidate
