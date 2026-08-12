"""Take one layer off a frame -- the frame itself stays in the gallery.

"sil = kaldır" read at one height of the stack: what goes is the named layer and everything ABOVE
it, because a sound is mixed over a video and a sound whose video is gone lies over nothing (madde
31). What is under it is not touched.

Removing the photo is not this use case's business: the photo is the base layer, so deleting it is
deleting the frame, and remove_frames is where that lives.

Which files really go is decided the way a frame's deletion decides it -- a file another frame still
holds stays where it is (madde 101) -- and the disk is touched before the log, so a failed unlink
leaves the record untouched.
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.photo_name import layer_file
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.retry_frame import FrameMissing  # noqa: F401


def remove_layer(record, store, plan_store, order_store, now, project, fid, kind):
    """Returns what really left the disk: {"deleted": [file names]}.

    The frame is named by its identity rather than by a file: a copy frame shares its source's
    picture (madde 102), so one file name can belong to two frames and only one of them is losing
    its video.
    """
    # Raises ProjectMissing when there is no such project.
    gallery = {frame["id"]: frame
               for frame in list_frames(record, store, plan_store, order_store, project)}
    frame = gallery.get(fid)
    if frame is None:
        raise FrameMissing(f"Bu kare galeride yok: {fid}")

    slots = record.slots(project)
    cells = slots.get(fid, {})
    over = queue.ORDER[queue.ORDER.index(kind):]      # the layer itself and everything above it
    closing = {(fid, slot) for slot in over
               if layers.is_taken((cells.get(slot) or {}).get("status"))}
    deleted = sorted(layers.files_to_unlink(slots, closing))

    for name in deleted:
        store.delete(project, name)
    for fid, slot in sorted(closing):
        record.mark(project, fid, slot, slots[fid][slot]["file"], queue.DELETED, now())
    # A job the queue still owes above the closed layer never gets to be made: it would go looking
    # for a video that is no longer there. The name written down is the one it would have taken.
    for slot in over:
        if slot in frame.get("owed", []):
            record.mark(project, fid, slot,
                        layer_file(slot, fid, (cells.get(layers.VIDEO) or {}).get("file")),
                        queue.REMOVED, now())
    return {"deleted": deleted}
