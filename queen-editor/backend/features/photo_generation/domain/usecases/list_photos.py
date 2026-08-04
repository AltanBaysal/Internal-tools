"""The gallery's list: the photos the record says exist, in the user's own order.

The folder is not scanned. A row is appended only after its photo is written, so the record is the
list -- and it carries the metadata the gallery's later features (export, detail) need, which a
directory listing cannot. The order file only sequences that list; it can neither add nor hide one.
"""
from backend.features.photo_generation.domain.gallery_order import apply_order
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def list_photos(record, store, order_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return apply_order(record.list(project), order_store.read(project))
