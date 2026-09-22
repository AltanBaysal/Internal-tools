"""Take one reference out of the project's pool. Returns the pool as it now stands.

The order is not touched: the name goes on holding its slot, and the slot is now an empty one
(madde 300). That is the user's own call -- what is left must not slide up, or H3 would read the
prompt's <Picture 3> off a different picture. The gap is closed by dragging, which sends a sequence
that simply does not carry the dead name.

A name the pool does not have is not an error: another tab can get there first, and deleting twice
has to end where deleting once ends.
"""
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def remove_reference(store, pool, orders, project, name):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    pool.delete(project, name)
    return list_references(store, pool, orders, project)
