"""Delete photos: from Drive, from the record, and from the gallery order.

One use case for one photo and for many -- the detail page sends a list of one. Two entry points
would be two copies of the same rule.

Per file the order matters: the file goes first, so a failure leaves nothing changed and the error
is the whole truth; then the record is appended to (never rewritten -- see data/photo_record.py).
The order file is written once at the end rather than per file: it is a single small document, and
one write is one chance to be interrupted instead of N.

A name the record does not know is skipped, not refused. The confirm box can sit open while another
tab deletes the same photo, and refusing the whole batch over a photo that is already gone would
leave the rest standing against the user's own decision. The answer says what was really deleted.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class InvalidFiles(Exception):
    """The body was not a list of file names."""


def delete_photos(record, store, order_store, now, project, files):
    if not isinstance(files, list) or any(not isinstance(name, str) for name in files):
        raise InvalidFiles("Silinecek dosya listesi metin dizisi olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    known = {row["file"] for row in record.list(project)}
    deleted = []
    for file in files:
        if file not in known:
            continue
        store.delete(project, file)
        record.mark(project, file, queue.DELETED, now())
        deleted.append(file)

    if deleted:
        gone = set(deleted)
        order_store.write(project, [name for name in order_store.read(project) if name not in gone])
    return deleted
