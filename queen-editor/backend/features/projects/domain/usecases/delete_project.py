"""Delete one project: the folder and everything inside it.

There is no separate existence check before the delete: between a check and the removal the folder
can disappear anyway, so the store's own answer ("there was nothing to remove") is the one truth
worth acting on.
"""
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def delete_project(store, name):
    if not store.delete(name):
        raise ProjectMissing(f"Proje yok: {name}")
