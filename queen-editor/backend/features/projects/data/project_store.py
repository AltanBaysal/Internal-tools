"""ProjectStore over DriveStorage -- the only place that knows a project IS one folder directly
under the Drive root. The root itself comes from config; the domain never learns where it is."""
from backend.features.projects.domain.project import Project


class DriveProjectStore:
    def __init__(self, storage):
        self.storage = storage

    def list(self):
        return [Project(name, mtime) for name, mtime in self.storage.list_dirs()]

    def create(self, name):
        mtime = self.storage.make_dir(name)
        if mtime is None:
            return None
        return Project(name, mtime)

    def delete(self, name):
        """Remove the project folder with everything in it; False when there was nothing to remove."""
        return self.storage.delete_dir(name)
