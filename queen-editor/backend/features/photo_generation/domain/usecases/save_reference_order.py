"""Save the order the user dragged the reference pool into. Returns the pool as it now stands.

The sequence is filtered against what the pool really holds before it is stored, the way the
gallery's own order is (save_order): the server writes only names it can see itself, so a stale tab
cannot leave ghosts in the file.

That filter is also how a gap closes. A deleted reference's name goes on holding its slot until
somebody sends a sequence without it -- and a drag sends exactly what the screen now shows.
"""
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class InvalidReferenceOrder(Exception):
    """The body was not a list of names per kind (message is user-facing)."""


def save_reference_order(store, pool, orders, project, order):
    if not isinstance(order, dict) or any(
            not isinstance(names, list) or any(not isinstance(name, str) for name in names)
            for names in order.values()):
        raise InvalidReferenceOrder("Sıra, her tip için metin dizisi olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    known = {row["name"] for row in list_references(store, pool, orders, project)}
    # dict.fromkeys keeps the first of any repeated name, and the order they came in.
    orders.write(project, {kind: [name for name in dict.fromkeys(names) if name in known]
                           for kind, names in order.items()})
    return list_references(store, pool, orders, project)
