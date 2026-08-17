"""FileProjectStore -- the only place that knows the project.json schema."""
import json

from backend.features.workspace.domain.naming import unique_name
from backend.features.workspace.domain.project import Project

PROJECT_FILE = "project.json"
CHATS_DIR = "chats"
FILES_DIR = "files"
# One trash for whole projects, beside them rather than inside any of them. It can never collide
# with a project: an id is "p" plus twelve hex characters, and list_all already skips a directory
# with no project.json in it.
TRASH_DIR = "trash"


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

    def list_all(self):
        projects = []
        for entry in self._store.list_dir(""):
            path = f"{entry}/{PROJECT_FILE}"
            if not self._store.exists(path):
                continue  # anything else living under the root is not ours to read
            raw = json.loads(self._store.read_text(path))
            projects.append(
                Project(
                    id=entry,
                    name=raw["name"],
                    created_at=raw["createdAt"],
                    chat_count=len(self._store.list_dir(f"{entry}/{CHATS_DIR}")),
                    file_count=len(self._store.list_dir(f"{entry}/{FILES_DIR}")),
                )
            )
        return projects

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
