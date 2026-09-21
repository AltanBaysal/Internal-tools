"""What the project's reference pool holds, in the order it was filled.

One row per file: what the pool can read it as, and how long it runs. A file the pool cannot read is
left out rather than listed as an unknown: the folder is open -- the user reaches it from Drive --
so anything at all can be in it, and only what H3 could be handed is a reference.

The length is here rather than in a place of its own because both readers want the same number: the
limits are counted from it (madde 298), and the screen draws it (299).
"""
from backend.features.photo_generation.domain import references
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def list_references(store, pool, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    rows = [{"name": name, "kind": references.kind_of(name), "seconds": seconds}
            for name, seconds in pool.items(project)]
    return [row for row in rows if row["kind"]]
