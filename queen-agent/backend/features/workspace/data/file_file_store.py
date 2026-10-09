"""FileFileStore -- the only place that knows a project's files/ directory.

It takes the name it is given: what a file may be called is decided in the domain. Which files a
project holds, and when each was written, is projects.json's answer (FileProjectStore, Madde 447):
the panel and the agent's list of names are read from there, and a file is opened only once its row
names it.
"""
from datetime import datetime, timezone

from backend.features.workspace.domain.file import FileBody
from backend.features.workspace.domain.naming import unique_name

FILES_DIR = "files"
TRASH_DIR = "trash"


class FileFileStore:
    def __init__(self, store, projects):
        self._store = store
        self._projects = projects

    def list_names(self, project_id):
        return [file.name for file in self._projects.files(project_id)]

    def list_files(self, project_id):
        return self._projects.files(project_id)

    def read(self, project_id, name):
        if self._projects.file(project_id, name) is None:
            return None
        return self._text(project_id, name)

    def read_body(self, project_id, name):
        # The row and the text together: the panel wants the file's particulars and its contents in
        # the same breath, and the row is in memory.
        file = self._projects.file(project_id, name)
        text = None if file is None else self._text(project_id, name)
        return None if text is None else FileBody(file, text)

    def _text(self, project_id, name):
        try:
            return self._store.read_text(f"{project_id}/{FILES_DIR}/{name}")
        except FileNotFoundError:
            # A row that outlived its file -- a delete whose removal of the row a sudden death lost.
            # Not found, which is the truth, rather than a crash on every look.
            return None

    def write(self, project_id, name, content):
        self._store.write_text(f"{project_id}/{FILES_DIR}/{name}", content)
        # After the file itself: a row never names a file that is not on disk. The moment is the
        # server's, in the shape the routes stamp everything with -- UTC, to the millisecond.
        self._projects.put_file(
            project_id, name, datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        )
        return name

    def delete(self, project_id, name):
        if self._projects.file(project_id, name) is None:
            return None
        # The trash keeps everything it is handed: a name already in there is not written over, so
        # deleting plan.md twice leaves two files rather than one.
        trashed = unique_name(self._store.list_dir(f"{project_id}/{TRASH_DIR}"), name)
        try:
            self._store.move(
                f"{project_id}/{FILES_DIR}/{name}", f"{project_id}/{TRASH_DIR}/{trashed}"
            )
        except FileNotFoundError:
            # Already gone: a delete moved it and a sudden death lost the row's removal. The row
            # goes all the same -- left, it would name something nothing could ever remove.
            pass
        self._projects.drop_file(project_id, name)
        return trashed
