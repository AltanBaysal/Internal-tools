"""The gallery's list: what is on disk, newest first."""
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def list_photos(store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return store.list_photos(project)
