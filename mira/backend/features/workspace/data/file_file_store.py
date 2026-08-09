"""FileFileStore -- the only place that knows a project's files/ directory.

It takes the name it is given: what a file may be called is decided in the domain.
"""
FILES_DIR = "files"


class FileFileStore:
    def __init__(self, store):
        self._store = store

    def list_names(self, project_id):
        return self._store.list_dir(f"{project_id}/{FILES_DIR}")

    def read(self, project_id, name):
        path = f"{project_id}/{FILES_DIR}/{name}"
        return self._store.read_text(path) if self._store.exists(path) else None

    def write(self, project_id, name, content):
        self._store.write_text(f"{project_id}/{FILES_DIR}/{name}", content)
        return name
