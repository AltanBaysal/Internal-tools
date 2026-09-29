"""Create a project -- born under the name the naming screen asked for (Madde 361)."""
from backend.features.workspace.domain.errors import InvalidProjectName
from backend.features.workspace.domain.project import Project


def create_project(store, new_id, name, now):
    # Trimmed and refused when blank, as a rename is (edit_project.py). The screen sends no blank
    # name, but that is a convenience; the rule lives here.
    trimmed = (name or "").strip()
    if not trimmed:
        raise InvalidProjectName(name)
    project = Project(id=new_id, name=trimmed, created_at=now)
    store.add(project)
    return project
