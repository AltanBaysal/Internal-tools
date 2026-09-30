"""Edit a project -- a partial update: whatever is not sent stays as it is."""
from dataclasses import replace

from backend.features.workspace.domain.errors import InvalidProjectName, ProjectNotFound
from backend.features.workspace.domain.project import Project


def edit_project(store, project_id, name=None, pinned=None, archived=None) -> Project:
    current = store.get(project_id)
    if current is None:
        raise ProjectNotFound(project_id)

    if name is not None:
        trimmed = name.strip()
        # The browser cancels on an empty prompt, but that is a convenience; the rule lives here.
        if not trimmed:
            raise InvalidProjectName(name)
        # created_at stays: it is the project's history, not something a rename rewrites.
        store.replace(replace(current, name=trimmed))
    # project.json is written on create and on rename, and a pin is neither: each of these is a
    # file of its own, written only when it is what was asked for (CODE-STANDARD).
    if pinned is not None:
        store.set_pinned(project_id, pinned)
    if archived is not None:
        store.set_archived(project_id, archived)
        # A project goes into the archive without its pin, and comes out without one (Madde 384):
        # the archive deletes it, and Unarchive clears one an archive made before that rule left.
        if archived != current.archived:
            store.set_pinned(project_id, False)
    # Read back rather than assembled here: the counts and the two marks are the disk's answer.
    return store.get(project_id)
