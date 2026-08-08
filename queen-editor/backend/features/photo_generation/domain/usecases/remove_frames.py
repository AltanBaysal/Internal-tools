"""Take frames out of the gallery -- whatever they are.

One use case for one frame and for many, and for photos and pending frames alike: the confirm box
is a single window over a mixed selection, so the request behind it is a single call. What each name
costs is decided here, from its own state:

  produced  -> the file leaves the disk and the log says deleted
  not yet   -> nothing to delete; the log says removed and the queue skips it

Per file the order matters: the file goes first, so a failure leaves nothing changed and the error
is the whole truth; then the log is appended to (never rewritten -- see data/photo_record.py). The
order file is written once at the end rather than per file: it is a single small document, and one
write is one chance to be interrupted instead of N.

A name the gallery does not know is skipped, not refused. The confirm box can sit open while another
tab removes the same frame, and refusing the whole batch over one that is already gone would leave
the rest standing against the user's own decision. The answer says what really happened.

The frame being rendered needs no guard: it writes its own line when it lands, and the latest line
about a file wins, so a removal that raced it is undone by the photo itself.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


class InvalidFiles(Exception):
    """The body was not a list of file names."""


def remove_frames(record, store, plan_store, order_store, now, project, files):
    if not isinstance(files, list) or any(not isinstance(name, str) for name in files):
        raise InvalidFiles("Silinecek dosya listesi metin dizisi olmalı.")
    # Raises ProjectMissing when there is no such project.
    known = {frame["file"]: frame["status"]
             for frame in list_frames(record, store, plan_store, order_store, project)}

    deleted, removed = [], []
    for file in files:
        status = known.get(file)
        if status is None:
            continue
        if status == queue.DONE:
            store.delete(project, file)
            record.mark(project, file, queue.DELETED, now())
            deleted.append(file)
        else:
            record.mark(project, file, queue.REMOVED, now())
            removed.append(file)

    gone = set(deleted) | set(removed)
    if gone:
        order_store.write(project, [name for name in order_store.read(project)
                                    if name not in gone])
    return {"deleted": deleted, "removed": removed}
