"""Put files in the project's reference pool. Returns the pool as it now stands.

The whole press is decided before a single file is written, the way a deletion decides it
(remove_frames): one file the pool cannot read refuses the upload, and a user who picked twelve
files does not get to find out that four of them landed.

Names are worked out in the same pass, so a second file called kedi.png already sees the first one
-- whether the first arrived a moment ago or a week ago.
"""
from backend.features.photo_generation.domain import references
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class UnknownReference(Exception):
    """A file the pool cannot read (message is user-facing)."""


def add_references(store, pool, project, files):
    """`files` is [(the name the browser sent, the bytes)]."""
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    taken = list(pool.names(project))
    writing = []
    for name, data in files:
        if references.kind_of(name) is None:
            raise UnknownReference(
                f"Bu dosya referans olamaz: {name} — fotoğraf, video ya da ses olmalı.")
        free = references.free_name(name, taken)
        taken.append(free)
        writing.append((free, data))
    # Nothing at all is written above, so a refusal leaves the pool exactly as it was.
    for name, data in writing:
        pool.save(project, name, data)
    return list_references(store, pool, project)
