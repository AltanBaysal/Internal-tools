"""Take one reference out of the project's pool. Returns the pool as it now stands.

The name leaves the order with its file, so the ones after it move up and their slot numbers change
(madde 321) -- which is what a prompt's <Picture N> means from then on, because H3 packs the
references tight and numbers them by order. The order names only references that are there, the
way a dragged one does (save_reference_order).

A name the pool does not have is not an error: another tab can get there first, and deleting twice
has to end where deleting once ends.
"""
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def remove_reference(store, pool, orders, project, name):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    pool.delete(project, name)
    orders.write(project, {kind: [one for one in names if one != name]
                           for kind, names in orders.read(project).items()})
    return list_references(store, pool, orders, project)
