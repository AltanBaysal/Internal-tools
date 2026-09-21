"""Take one reference out of the project's pool. Returns the pool as it now stands.

A name the pool does not have is not an error: another tab can get there first, and deleting twice
has to end where deleting once ends.
"""
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def remove_reference(store, pool, project, name):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    pool.delete(project, name)
    return list_references(store, pool, project)
