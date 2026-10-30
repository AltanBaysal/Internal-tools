"""Save the order the user dragged the reference pool into. Returns the pool as it now stands.

The sequence is filtered against what the pool really holds before it is stored, the way the
gallery's own order is (save_order): the server writes only names it can see itself, so a stale tab
cannot leave ghosts in the file -- names that stand in no slot (madde 321).

Only the rows that were sent change, and every other row keeps the order it was saved in
(madde 427). The screen sends the dragged row alone: a file written from the body alone would lose
every other row, and the pool would then place those by name (references.placed).

Under the project's write gate, as an upload is (add_references says why): an upload landing between
the read and the write would drop out of the order (madde 523). And a file of the row the drag does
not name keeps its place rather than leaving the order: a tab drawn before another tab's upload
sends a row without it, and replacing the row whole lost that upload's place.
"""
from backend.features.photo_generation.domain import gallery_order
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class InvalidReferenceOrder(Exception):
    """The body was not a list of names per kind (message is user-facing)."""


def save_reference_order(store, pool, orders, plan_store, project, order):
    if not isinstance(order, dict) or any(
            not isinstance(names, list) or any(not isinstance(name, str) for name in names)
            for names in order.values()):
        raise InvalidReferenceOrder("Sıra, her tip için metin dizisi olmalı.")
    with plan_store.held(project):
        if not store.project_exists(project):
            raise ProjectMissing(f"Proje yok: {project}")
        standing = list_references(store, pool, orders, project)
        order_now = orders.read(project)
        for kind, names in order.items():
            row = [one["name"] for one in standing if one["kind"] == kind]
            # dict.fromkeys keeps the first of any repeated name, and the order they came in. A file
            # of the row the drag does not name -- one another tab uploaded after this one drew its
            # pool -- keeps its place, as a frame the gallery's drag leaves out does (madde 512).
            order_now[kind] = gallery_order.keep_unnamed(
                [name for name in dict.fromkeys(names) if name in row], row)
        orders.write(project, order_now)
        return list_references(store, pool, orders, project)
