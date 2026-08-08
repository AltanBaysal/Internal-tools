"""Save the gallery order the user dragged into place.

The client's list is filtered against what the gallery really holds before it is stored: the server
writes only names it can see itself, so a stale tab cannot leave ghosts in the file. A name the list
forgot is not an error -- that frame simply comes back on top on the next read (see
gallery_order.apply_order).

The set to check against is the gallery's own sequence, not the photos: pending frames have places
in it too, and a drag that moved a photo past one has to be storable.
"""
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


class InvalidOrder(Exception):
    """The body was not a list of file names."""


def save_order(record, store, plan_store, order_store, project, order):
    if not isinstance(order, list) or any(not isinstance(name, str) for name in order):
        raise InvalidOrder("Sıra listesi metin dizisi olmalı.")
    # Raises ProjectMissing when there is no such project.
    known = {frame["file"] for frame in list_frames(record, store, plan_store, order_store, project)}
    cleaned = []
    seen = set()
    for name in order:
        if name in known and name not in seen:
            seen.add(name)
            cleaned.append(name)
    order_store.write(project, cleaned)
    return cleaned
