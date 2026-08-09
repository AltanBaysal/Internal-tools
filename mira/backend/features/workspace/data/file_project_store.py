"""FileProjectStore -- the only place that knows the project.json schema."""
import json

from backend.features.workspace.domain.project import Project

PROJECT_FILE = "project.json"


class ProjectIdTaken(Exception):
    """A project directory already exists -- the user's work is never overwritten."""


class FileProjectStore:
    def __init__(self, store):
        self._store = store

    def add(self, project):
        path = f"{project.id}/{PROJECT_FILE}"
        if self._store.exists(path):
            raise ProjectIdTaken(project.id)
        # The id is the directory name, so it is not written into the file: no artifact repeats an
        # answer another one already gives.
        self._store.write_text(
            path,
            json.dumps(
                {
                    "name": project.name,
                    "desc": project.desc,
                    "hue": project.hue,
                    "createdAt": project.created_at,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )

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
                    desc=raw["desc"],
                    hue=raw["hue"],
                    created_at=raw["createdAt"],
                )
            )
        return projects
