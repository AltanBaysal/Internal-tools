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

A name the gallery does not know is skipped, not refused. The confirm box can sit open while another
tab removes the same frame, and refusing the whole batch over one that is already gone would leave
the rest standing against the user's own decision. The answer says what really happened.

The frame being rendered needs no guard: it writes its own line when it lands, and the latest line
about a slot wins, so a removal that raced it is undone by the photo itself.
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


class InvalidFiles(Exception):
    """The body was not a list of file names."""


def remove_frames(record, store, plan_store, order_store, now, project, files):
    if not isinstance(files, list) or any(not isinstance(name, str) for name in files):
        raise InvalidFiles("Silinecek dosya listesi metin dizisi olmalı.")
    # Raises ProjectMissing when there is no such project.
    gallery = {frame["file"]: frame
               for frame in list_frames(record, store, plan_store, order_store, project)}
    slots = record.slots(project)

    # The whole deletion is decided first: which slots close, and which files that leaves unheld.
    deleted, removed, closing = [], [], set()
    for name in files:
        frame = gallery.get(name)
        if frame is None:
            continue
        if frame["status"] == queue.DONE:
            cells = slots.get(frame["id"], {})
            closing |= {(frame["id"], slot) for slot, cell in cells.items()
                        if layers.is_taken(cell["status"])}
            deleted.append(name)
        else:
            removed.append(name)

    for file in sorted(layers.files_to_unlink(slots, closing)):
        store.delete(project, file)
    for fid, slot in sorted(closing):
        record.mark(project, fid, slot, slots[fid][slot]["file"], queue.DELETED, now())
    for name in removed:
        record.mark(project, gallery[name]["id"], layers.PHOTO, name, queue.REMOVED, now())

    gone = {gallery[name]["id"] for name in deleted + removed}
    if gone:
        order_store.write(project, [fid for fid in order_store.read(project) if fid not in gone])
    return {"deleted": deleted, "removed": removed}
