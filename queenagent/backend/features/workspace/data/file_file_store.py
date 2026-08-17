"""FileFileStore -- the only place that knows a project's files/ directory.

It takes the name it is given: what a file may be called is decided in the domain.
"""
from datetime import datetime, timezone

from backend.features.workspace.domain.file import File, FileBody, extension_of
from backend.features.workspace.domain.naming import unique_name

FILES_DIR = "files"
TRASH_DIR = "trash"


class FileFileStore:
    def __init__(self, store):
        self._store = store

    def list_names(self, project_id):
        return self._store.list_dir(f"{project_id}/{FILES_DIR}")

    def list_files(self, project_id):
        # The directory is the record: the name is the name and the time is its mtime.
        return [
            File(
                name=name,
                ext=extension_of(name),
                modified_at=_iso(self._store.mtime(f"{project_id}/{FILES_DIR}/{name}")),
            )
            for name in self.list_names(project_id)
        ]

    def read(self, project_id, name):
        path = f"{project_id}/{FILES_DIR}/{name}"
        return self._store.read_text(path) if self._store.exists(path) else None

    def read_body(self, project_id, name):
        # The stat and the text in one call: asked separately, a file deleted in between would
        # answer one question and not the other.
        path = f"{project_id}/{FILES_DIR}/{name}"
        if not self._store.exists(path):
            return None
        return FileBody(
            File(
                name=name,
                ext=extension_of(name),
                modified_at=_iso(self._store.mtime(path)),
            ),
            self._store.read_text(path),
        )

    def write(self, project_id, name, content):
        self._store.write_text(f"{project_id}/{FILES_DIR}/{name}", content)
        return name

    def rename(self, project_id, name, wanted):
        path = f"{project_id}/{FILES_DIR}/{name}"
        if not self._store.exists(path):
            return None
        # Numbering a file against itself would turn plan.md into plan-2.md for no reason.
        taken = name if wanted == name else unique_name(self.list_names(project_id), wanted)
        self._store.move(path, f"{project_id}/{FILES_DIR}/{taken}")
        return File(
            name=taken,
            ext=extension_of(taken),
            modified_at=_iso(self._store.mtime(f"{project_id}/{FILES_DIR}/{taken}")),
        )

    def delete(self, project_id, name):
        if not self._store.exists(f"{project_id}/{FILES_DIR}/{name}"):
            return None
        # The trash keeps everything it is handed: a name already in there is not written over, so
        # deleting plan.md twice leaves two files rather than one.
        trashed = unique_name(self._store.list_dir(f"{project_id}/{TRASH_DIR}"), name)
        self._store.move(
            f"{project_id}/{FILES_DIR}/{name}", f"{project_id}/{TRASH_DIR}/{trashed}"
        )
        return trashed

    def restore(self, project_id, trashed, name):
        if not self._store.exists(f"{project_id}/{TRASH_DIR}/{trashed}"):
            return None
        # Three answers, not two: gone, in the way, or done. The use case turns them into words.
        if self._store.exists(f"{project_id}/{FILES_DIR}/{name}"):
            return False
        self._store.move(
            f"{project_id}/{TRASH_DIR}/{trashed}", f"{project_id}/{FILES_DIR}/{name}"
        )
        return True


def _iso(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat(timespec="milliseconds")
