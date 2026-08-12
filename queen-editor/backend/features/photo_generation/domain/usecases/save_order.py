"""Save the gallery order the user dragged into place.

The client's list is filtered against what the gallery really holds before it is stored: the server
writes only frames it can see itself, so a stale tab cannot leave ghosts in the file. A frame the
list forgot is not an error -- it simply comes back on top on the next read (see
gallery_order.apply_order).

The set to check against is the gallery's own sequence, not the photos: pending frames have places
in it too, and a drag that moved a photo past one has to be storable.

Identities in, identities out: the screen drags frames around, and two of them can be showing one
picture (madde 102), so a list of file names could not say what the sequence is.
"""
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


class InvalidOrder(Exception):
    """The body was not a list of frame identities."""


def save_order(record, store, plan_store, order_store, project, order):
    if not isinstance(order, list) or any(not isinstance(fid, str) for fid in order):
        raise InvalidOrder("Sıra listesi metin dizisi olmalı.")
    # Raises ProjectMissing when there is no such project.
    known = {frame["id"] for frame in list_frames(record, store, plan_store, order_store, project)}
    # dict.fromkeys keeps the first of any repeated identity, and the order they came in.
    cleaned = [fid for fid in dict.fromkeys(order) if fid in known]
    order_store.write(project, cleaned)
    return cleaned
