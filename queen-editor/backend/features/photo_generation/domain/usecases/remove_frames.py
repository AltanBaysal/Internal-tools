"""Take frames out of the gallery -- whatever they are.

One use case for one frame and for many, and for photos and pending frames alike: the confirm box
is a single window over a mixed selection, so the request behind it is a single call. What each name
costs is decided here, from its own state:

  produced  -> every layer it owns leaves the disk and the log says deleted
  not yet   -> nothing to delete; the log says removed and the queue skips it

Which files really go is decided before a single line is written: a picture two frames share stays
where it is until the last of them lets go (design v3, madde 101). The disk is touched first, so a
failed unlink leaves the record untouched and the error is the whole truth; then the log is appended
to (never rewritten -- see data/photo_record.py). The order file is written once at the end rather
than per frame: it is a single small document, and one write is one chance to be interrupted
instead of N.

Frames are named by their identities, not by their files: a copy frame shares its source's picture
(madde 102), so one file name can belong to two frames and only one of them is being taken out.

An identity the gallery does not know is skipped, not refused. The confirm box can sit open while
another tab removes the same frame, and refusing the whole batch over one that is already gone would
leave the rest standing against the user's own decision. The answer says what really happened.

The frame being rendered needs no guard: it writes its own line when it lands, and the latest line
about a slot wins, so a removal that raced it is undone by the photo itself.
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.frame_list import checked
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


def remove_frames(record, store, plan_store, order_store, now, project, frames):
    checked(frames, "Silinecek")
    # Raises ProjectMissing when there is no such project.
    gallery = {frame["id"]: frame
               for frame in list_frames(record, store, plan_store, order_store, project)}
    slots = record.slots(project)

    # The whole deletion is decided first: which slots close, and which files that leaves unheld.
    deleted, removed, closing = [], [], set()
    for fid in frames:
        frame = gallery.get(fid)
        if frame is None:
            continue
        if frame["status"] == queue.DONE:
            cells = slots.get(fid, {})
            closing |= {(fid, slot) for slot, cell in cells.items()
                        if layers.is_taken(cell["status"])}
            deleted.append(fid)
        else:
            removed.append(fid)

    for file in sorted(layers.files_to_unlink(slots, closing)):
        store.delete(project, file)
    for fid, slot in sorted(closing):
        record.mark(project, fid, slot, slots[fid][slot]["file"], queue.DELETED, now())
    for fid in removed:
        # The name it was planned to take: nothing was ever produced under it, and a line still has
        # to say which file the frame was about.
        record.mark(project, fid, layers.PHOTO, gallery[fid]["file"], queue.REMOVED, now())

    gone = set(deleted + removed)
    if gone:
        order_store.write(project, [fid for fid in order_store.read(project) if fid not in gone])
    return {"deleted": deleted, "removed": removed}
