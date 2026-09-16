"""ProjectStore over DriveStorage -- the only place that knows a project IS one folder directly
under the Drive root. The root itself comes from config; the domain never learns where it is.

It is also the only place that knows where an archived project goes, which since madde 221 is one
folder down rather than a flag: the folder moves, and everything else follows from that by itself.
"""
from backend.features.projects.domain import name_rules
from backend.features.projects.domain.project import Project


class DriveProjectStore:
    def __init__(self, storage):
        self.storage = storage

    def list(self):
        # The archive lives under the same root, and every folder under the root is a project --
        # so it has to be stepped over here or it becomes one.
        return [Project(name, mtime) for name, mtime in self.storage.list_dirs()
                if name != name_rules.ARCHIVE_DIR]

    def list_archived(self):
        return [Project(name, mtime)
                for name, mtime in self.storage.list_dirs(name_rules.ARCHIVE_DIR)]

    def archive(self, name):
        """The archived project, None when the archive already holds that name, False when there was
        nothing to move -- rename's three answers, because it is the same move."""
        return self._moved(self.storage.rename_dir(name, self._in_archive(name)), name)

    def restore(self, name):
        return self._moved(self.storage.rename_dir(self._in_archive(name), name), name)

    @staticmethod
    def _in_archive(name):
        # Always a forward slash: this is a path handed to the storage layer, which joins it, and
        # os.path.join reads "/" on every platform this runs on.
        return f"{name_rules.ARCHIVE_DIR}/{name}"

    @staticmethod
    def _moved(answer, name):
        # `is` and not truthiness: an mtime can be 0.0 and that is a success.
        if answer is None or answer is False:
            return answer
        return Project(name, answer)

    def create(self, name):
        mtime = self.storage.make_dir(name)
        if mtime is None:
            return None
        return Project(name, mtime)

    def delete(self, name):
        """Remove the project folder with everything in it; False when there was nothing to remove."""
        return self.storage.delete_dir(name)

    def rename(self, old, new):
        """The renamed project, None when the new name is taken, False when the old one is gone."""
        moved = self.storage.rename_dir(old, new)
        # `is` and not truthiness: an mtime can be 0.0 and that is a success.
        if moved is None or moved is False:
            return moved
        return Project(new, moved)
