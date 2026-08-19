"""Create a project -- the defaults a new project is born with."""
from backend.features.workspace.domain.project import Project

# The design never asks for a name up front: the project is born named and renamed afterwards.
NEW_PROJECT_NAME = "New project"


def create_project(store, new_id, now):
    project = Project(id=new_id, name=NEW_PROJECT_NAME, created_at=now)
    store.add(project)
    return project
