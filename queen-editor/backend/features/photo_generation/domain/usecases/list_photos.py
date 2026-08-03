"""The gallery's list: the photos the record says exist, newest first.

The folder is not scanned. A row is appended only after its photo is written, so the record is the
list -- and it carries the metadata the gallery's later features (order, export, detail) need,
which a directory listing cannot.
"""
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def list_photos(record, store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return record.list(project)
