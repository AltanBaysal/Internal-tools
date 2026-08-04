"""Delete one photo: from Drive, from the record, and from the gallery order.

Order matters. The file goes first: if that fails nothing has changed yet and the error is the whole
truth. The record is then appended to (never rewritten -- see data/photo_record.py), and the order
file drops the name so it carries no dead entries.
"""
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class PhotoMissing(Exception):
    """No such photo in this project's record."""


def delete_photo(record, store, order_store, now, project, file):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    if file not in {row["file"] for row in record.list(project)}:
        raise PhotoMissing(f"Fotoğraf yok: {file}")
    store.delete(project, file)
    record.mark_deleted(project, file, now())
    order_store.write(project, [name for name in order_store.read(project) if name != file])
