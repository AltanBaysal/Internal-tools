"""Save the gallery order the user dragged into place.

The client's list is filtered against what the gallery really holds before it is stored: the server
writes only frames it can see itself, so a stale tab cannot leave ghosts in the file. A frame the
list does not name is not an error, and it keeps its place: a copy that landed after the screen
built its list would otherwise lose the place beside its source and jump to the top (madde 512;
gallery_order.keep_unnamed).

The set to check against is the gallery's own sequence, not the photos: pending frames have places
in it too, and a drag that moved a photo past one has to be storable.

Identities in, identities out: the screen drags frames around, and two of them can be showing one
picture (madde 102), so a list of file names could not say what the sequence is.
"""
from backend.features.photo_generation.domain.gallery_order import keep_unnamed
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


class InvalidOrder(Exception):
    """The body was not a list of frame identities."""


def save_order(record, store, plan_store, order_store, project, order):
    if not isinstance(order, list) or any(not isinstance(fid, str) for fid in order):
        raise InvalidOrder("Sıra listesi metin dizisi olmalı.")
    # Held from the gallery read to the order written, as every other writer of the order holds
    # it: a copy placed in between would otherwise lose its place to this list (madde 512).
    with plan_store.held(project):
        # Raises ProjectMissing when there is no such project.
        gallery = [frame["id"]
                   for frame in list_frames(record, store, plan_store, order_store, project)]
        known = set(gallery)
        # dict.fromkeys keeps the first of any repeated identity, and the order they came in.
        named = [fid for fid in dict.fromkeys(order) if fid in known]
        cleaned = keep_unnamed(named, gallery)
        order_store.write(project, cleaned)
    return cleaned
