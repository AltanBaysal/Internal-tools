"""Delete a file -- which is to say, move it out of the project's sight.

The name it takes in the trash comes back, because that is the only thing that can find it again:
nothing is written down about where a deleted file came from.

A prompt guide is refused (Madde 492): it is in every project's list but in no project's folder,
and nobody changes it (the user, 22 October: "ajan değiştiremez sadece okur").
"""
from backend.features.workspace.domain.errors import FileNotFound, ReadOnlyFile
from backend.features.workspace.domain.prompt import GUIDES


def delete_file(file_store, project_id, name):
    if name in GUIDES:
        raise ReadOnlyFile(name)
    trashed = file_store.delete(project_id, name)
    if trashed is None:
        raise FileNotFound(name)
    return trashed
