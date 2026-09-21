"""What the project's reference pool holds, in the order it was filled.

One row per file, each saying what the pool can read it as. A file the pool cannot read is left out
rather than listed as an unknown: the folder is open -- the user reaches it from Drive -- so
anything at all can be in it, and only what H3 could be handed is a reference.
"""
from backend.features.photo_generation.domain import references
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def list_references(store, pool, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    rows = [{"name": name, "kind": references.kind_of(name)} for name in pool.names(project)]
    return [row for row in rows if row["kind"]]
