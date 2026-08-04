"""Save the gallery order the user dragged into place.

The client's list is filtered against the record before it is stored: the server writes only names
it can see itself, so a stale tab cannot leave ghosts in the file. A name the list forgot is not an
error -- that photo simply comes back on top on the next read (see gallery_order.apply_order).
"""
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class InvalidOrder(Exception):
    """The body was not a list of file names."""


def save_order(record, store, order_store, project, order):
    if not isinstance(order, list) or any(not isinstance(name, str) for name in order):
        raise InvalidOrder("Sıra listesi metin dizisi olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    known = {row["file"] for row in record.list(project)}
    cleaned = []
    seen = set()
    for name in order:
        if name in known and name not in seen:
            seen.add(name)
            cleaned.append(name)
    order_store.write(project, cleaned)
    return cleaned
