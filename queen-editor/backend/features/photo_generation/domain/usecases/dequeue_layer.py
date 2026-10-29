"""Take a layer's waiting job out of the queue -- and nothing that has landed (madde 516).

The detail page's Kuyruktan çıkar on a waiting layer's tab. What goes is the job the queue still owes
for the layer and for whatever hangs on it, because a sound waiting to be mixed over a video that
will never come would go looking for it (layers.NEEDS). The frame stays in the gallery with
everything it holds: nothing is unlinked and no slot that holds a layer is closed.

A door of its own rather than a mode of remove_layer: that door deletes what is there, and a flag
left out by some later caller would quietly turn this press back into a deletion nobody confirmed.
The screen can be behind the server -- a late poll, a tab in the background -- so a press made while
it still drew a video as waiting can reach a video that has landed. That video is left as it is: the
press meant the job.

An identity the gallery does not know is skipped, not refused, as in remove_layer.
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.frame_list import checked
from backend.features.photo_generation.domain.photo_name import layer_file
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


def owed_on(frame, cells, kind):
    """The jobs the queue still owes one frame on `kind` and on what hangs on it.

    [(slot, the file it would have been saved as, the status it was read in)]. A slot read as
    holding a layer has landed since the gallery was read: its job is no longer owed, whatever the
    gallery said (madde 513). The name is worked out while the video's own row is still readable --
    a sound's name is built on it.
    """
    video = (cells.get(layers.VIDEO) or {}).get("file")
    statuses = {slot: (cells.get(slot) or {}).get("status") for slot in layers.falls_with(kind)}
    return [(slot, layer_file(slot, frame["id"], video), status)
            for slot, status in statuses.items()
            if slot in frame.get("owed", []) and not layers.is_taken(status)]


def dequeue_layer(record, store, plan_store, order_store, now, project, frames, kind):
    """Returns the jobs taken out, by the file each would have been saved as: {"removed": [...]}."""
    checked(frames, "Kuyruktan çıkarılacak")
    # Held from the gallery read to the last line written, the other doors' way: a Kuyruğa ekle at
    # the same moment would otherwise see the job still in line, add nothing, and then find it gone
    # (madde 512).
    with plan_store.held(project):
        # Raises ProjectMissing when there is no such project.
        gallery = {frame["id"]: frame
                   for frame in list_frames(record, store, plan_store, order_store, project)}
        slots = record.slots(project)
        # Each identity once: a name sent twice is one frame.
        dropping = [(fid, job) for fid in dict.fromkeys(frames) if fid in gallery
                    for job in owed_on(gallery[fid], slots.get(fid, {}), kind)]
        # Over the status each slot was read in, so a layer the loop lands after this look keeps it
        # (madde 513).
        for fid, (slot, name, status) in dropping:
            record.mark(project, fid, slot, name, queue.REMOVED, now(), seen=status)
    return {"removed": [name for _fid, (_slot, name, _status) in dropping]}
