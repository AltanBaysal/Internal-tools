"""Edit a project -- a partial update: whatever is not sent stays as it is."""
from dataclasses import replace

from backend.features.workspace.domain.errors import InvalidProjectName, ProjectNotFound
from backend.features.workspace.domain.project import Project


def edit_project(store, project_id, now, name=None, pinned=None, archived=None) -> Project:
    # The browser cancels on an empty prompt, but that is a convenience; the rule lives here.
    if name is not None and not name.strip():
        raise InvalidProjectName(name)

    def change(project):
        if name is not None:
            # created_at stays: it is the project's history, not something a rename rewrites.
            project = replace(project, name=name.strip())
        if pinned is not None:
            # Pinning what is already pinned keeps the moment: the pinned are listed in the order
            # they were pinned in.
            project = replace(project, pinned_at=(project.pinned_at or now) if pinned else "")
        # A project goes into the archive without its pin, and comes out without one (Madde 384).
        # Asking for what already stands changes nothing, the pin included.
        if archived is not None and archived != project.archived:
            project = replace(project, archived=archived, pinned_at="")
        return project

    # One change for the whole request, so the store writes once. What comes back is the project as
    # it now stands -- nothing is read back.
    edited = store.update(project_id, change)
    if edited is None:
        raise ProjectNotFound(project_id)
    return edited
