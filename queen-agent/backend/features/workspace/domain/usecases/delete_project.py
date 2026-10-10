"""Delete a project -- which is to say, move the whole thing out of the workspace's sight.

The chats and the files inside are not deleted one by one: they live in the directory, so they go
with it. Nothing on disk is lost, which is what lets the confirmation be the only protection.

Not while one of its chats has a turn running (Madde 461): the turn would write into the moved
folder's old place and build it anew there.
"""
from backend.features.workspace.domain.errors import ProjectAnswering, ProjectNotFound


def delete_project(project_store, turns, project_id):
    if turns.any_in(project_id):
        raise ProjectAnswering(project_id)
    trashed = project_store.delete(project_id)
    if trashed is None:
        raise ProjectNotFound(project_id)
    return trashed
