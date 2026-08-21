"""Take one layer off the frames named -- the frames themselves stay in the gallery.

"sil = kaldır" read at one height of the stack: what goes is the named layer and everything ABOVE
it, because a sound is mixed over a video and a sound whose video is gone lies over nothing (madde
31). What is under it is not touched.

One use case for one frame and for many: the selection bar takes a layer off a whole selection and
the detail page takes it off one. The layer is still singular -- only the frames are not.

The whole press is decided before a single line is written, the way a deletion decides it
(remove_frames). That is what makes a shared file right: a video two frames hold may only be
unlinked once BOTH of them have let go, and a frame-at-a-time reading would still see the first one
holding it while the second was being worked out.

Removing the photo is not this use case's business: the photo is the base layer, so deleting it is
deleting the frame, and remove_frames is where that lives.

An identity the gallery does not know is skipped, not refused: another tab can take a frame away
while the confirm sits open, and one gone name must not undo the rest.
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.frame_list import checked
from backend.features.photo_generation.domain.photo_name import layer_file
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


def remove_layer(record, store, plan_store, order_store, now, project, frames, kind):
    """Returns what really left the disk: {"deleted": [file names]}.

    Frames are named by their identities rather than by files: a copy frame shares its source's
    picture (madde 102), so one file name can belong to two frames and only one of them is losing
    its video.
    """
    checked(frames, "Katmanı silinecek")
    # Raises ProjectMissing when there is no such project.
    gallery = {frame["id"]: frame
               for frame in list_frames(record, store, plan_store, order_store, project)}
    slots = record.slots(project)
    over = queue.ORDER[queue.ORDER.index(kind):]      # the layer itself and everything above it

    # Which slots close, and which jobs above them never get to be made -- both for the whole press,
    # before anything is written.
    closing, dropping = set(), []
    for fid in frames:
        frame = gallery.get(fid)
        if frame is None:
            continue
        cells = slots.get(fid, {})
        closing |= {(fid, slot) for slot in over
                    if layers.is_taken((cells.get(slot) or {}).get("status"))}
        # A job the queue still owes above the closed layer would go looking for a video that is no
        # longer there. The name written down is the one it would have taken -- worked out here,
        # while the video's own row is still readable.
        dropping += [(fid, slot, layer_file(slot, fid, (cells.get(layers.VIDEO) or {}).get("file")))
                     for slot in over if slot in frame.get("owed", [])]

    deleted = sorted(layers.files_to_unlink(slots, closing))
    for name in deleted:
        store.delete(project, name)
    for fid, slot in sorted(closing):
        record.mark(project, fid, slot, slots[fid][slot]["file"], queue.DELETED, now())
    for fid, slot, name in dropping:
        record.mark(project, fid, slot, name, queue.REMOVED, now())
    return {"deleted": deleted}
