"""Delete a file -- which is to say, move it out of the project's sight.

The name it takes in the trash comes back, because that is the only thing that can find it again:
nothing is written down about where a deleted file came from.
"""
from backend.features.workspace.domain.errors import FileNotFound


def delete_file(file_store, project_id, name):
    trashed = file_store.delete(project_id, name)
    if trashed is None:
        raise FileNotFound(name)
    return trashed
