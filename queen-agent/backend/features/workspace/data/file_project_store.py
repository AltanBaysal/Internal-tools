"""FileProjectStore -- the only place that knows how a project is laid out on disk."""
import json
from datetime import datetime, timezone

from backend.features.workspace.domain.naming import unique_name
from backend.features.workspace.domain.project import Project

PROJECT_FILE = "project.json"
CHATS_DIR = "chats"
FILES_DIR = "files"
# One trash for whole projects, beside them rather than inside any of them. It can never collide
# with a project: an id is "p" plus twelve hex characters, and list_all already skips a directory
# with no project.json in it.
TRASH_DIR = "trash"
# Empty, and there or not there: each answers a question project.json does not (CODE-STANDARD). The
# pin's mtime is when the project was pinned, which is why pinning twice leaves the file alone.
PINNED_FILE = "pinned"
ARCHIVED_FILE = "archived"


class ProjectIdTaken(Exception):
    """A project directory already exists -- the user's work is never overwritten."""


class FileProjectStore:
    def __init__(self, store):
        self._store = store

    def add(self, project):
        if self._store.exists(f"{project.id}/{PROJECT_FILE}"):
            raise ProjectIdTaken(project.id)
        self._write(project)

    def replace(self, project):
        self._write(project)

    def get(self, project_id):
        for project in self.list_all():
            if project.id == project_id:
                return project
        return None

    def delete(self, project_id):
        if not self._store.exists(f"{project_id}/{PROJECT_FILE}"):
            return None
        # The directory moves whole: the chats and the files go with it rather than being deleted
        # one by one, and a second project of the same id is numbered rather than written over.
        trashed = unique_name(self._store.list_dir(TRASH_DIR), project_id)
        self._store.move(project_id, f"{TRASH_DIR}/{trashed}")
        return trashed

    def set_pinned(self, project_id, pinned):
        self._mark(project_id, PINNED_FILE, pinned)

    def set_archived(self, project_id, archived):
        self._mark(project_id, ARCHIVED_FILE, archived)

    def list_all(self):
        projects = []
        for entry in self._store.list_dir(""):
            path = f"{entry}/{PROJECT_FILE}"
            if not self._store.exists(path):
                continue  # anything else living under the root is not ours to read
            raw = json.loads(self._store.read_text(path))
            chats = self._store.list_dir(f"{entry}/{CHATS_DIR}")
            pin = f"{entry}/{PINNED_FILE}"
            projects.append(
                Project(
                    id=entry,
                    name=raw["name"],
                    created_at=raw["createdAt"],
                    chat_count=len(chats),
                    file_count=len(self._store.list_dir(f"{entry}/{FILES_DIR}")),
                    # A chat file is written whenever anybody talks in it, so the newest one says
                    # when the project was last used (Madde 346).
                    last_chat_at=max(
                        (self._stamp(f"{entry}/{CHATS_DIR}/{name}") for name in chats), default=""
                    ),
                    pinned_at=self._stamp(pin) if self._store.exists(pin) else "",
                    archived=self._store.exists(f"{entry}/{ARCHIVED_FILE}"),
                )
            )
        return projects

    def _stamp(self, path):
        # The shape the routes stamp createdAt with -- UTC, to the millisecond -- so the two compare
        # as text, which is how the list is ordered.
        return datetime.fromtimestamp(self._store.mtime(path), timezone.utc).isoformat(
            timespec="milliseconds"
        )

    def _write(self, project):
        # The id is the directory name and the counts come from the directories, so neither is
        # written here: no artifact repeats an answer another one already gives.
        self._store.write_text(
            f"{project.id}/{PROJECT_FILE}",
            json.dumps(
                {
                    "name": project.name,
                    "createdAt": project.created_at,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )

    def _mark(self, project_id, name, on):
        path = f"{project_id}/{name}"
        if self._store.exists(path) == on:
            return
        if on:
            self._store.write_text(path, "")
        else:
            self._store.remove(path)
