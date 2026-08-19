"""Delete a project -- which is to say, move the whole thing out of the workspace's sight.

The chats and the files inside are not deleted one by one: they live in the directory, so they go
with it. Nothing on disk is lost, which is what lets the confirmation be the only protection.
"""
from backend.features.workspace.domain.errors import ProjectNotFound


def delete_project(project_store, project_id):
    trashed = project_store.delete(project_id)
    if trashed is None:
        raise ProjectNotFound(project_id)
    return trashed
