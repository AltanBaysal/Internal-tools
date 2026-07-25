"""ProjectStore over DriveStorage -- the only place that knows a project IS a folder under the
Drive root (photoGenV2/<name>/). The domain never learns where a project lives."""
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
