"""Edit a project -- a partial update: whatever is not sent stays as it is."""
from dataclasses import replace

from backend.features.workspace.domain.errors import InvalidProjectName, ProjectNotFound
from backend.features.workspace.domain.project import Project


def edit_project(store, project_id, name=None, desc=None) -> Project:
    current = store.get(project_id)
    if current is None:
        raise ProjectNotFound(project_id)

    changes = {}
    if name is not None:
        trimmed = name.strip()
        # The browser cancels on an empty prompt, but that is a convenience; the rule lives here.
        if not trimmed:
            raise InvalidProjectName(name)
        changes["name"] = trimmed
    if desc is not None:
        changes["desc"] = desc.strip()

    # hue and created_at are never in `changes`: one is part of the project's identity, the other is
    # its history.
    edited = replace(current, **changes)
    store.replace(edited)
    return edited
