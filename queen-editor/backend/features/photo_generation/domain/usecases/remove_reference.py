"""Take one reference out of the project's pool. Returns the pool as it now stands.

The name leaves the order with its file, so the ones after it move up and their slot numbers change
(madde 321) -- which is what a prompt's <Picture N> means from then on, because H3 packs the
references tight and numbers them by order. A name left in the order would not show as a hole (the
pool counts only what is there), but a file uploaded under it later would slip back into its old
place rather than join the end of its row.

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
