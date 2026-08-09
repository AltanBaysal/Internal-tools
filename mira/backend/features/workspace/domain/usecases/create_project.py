"""Create a project -- the defaults a new project is born with."""
from backend.features.workspace.domain.project import Project

# The design never asks for a name up front: the project is born named and renamed afterwards.
NEW_PROJECT_NAME = "New project"
NEW_PROJECT_DESC = "Click to add a description."
# Successive projects step around the colour wheel instead of repeating a hue.
HUE_STEP = 47


def create_project(store, new_id, now):
    # The hue is decided once and stored: deleting a neighbour later must not recolour the card.
    hue = (len(store.list_all()) * HUE_STEP) % 360
    project = Project(
        id=new_id,
        name=NEW_PROJECT_NAME,
        desc=NEW_PROJECT_DESC,
        hue=hue,
        created_at=now,
    )
    store.add(project)
    return project
