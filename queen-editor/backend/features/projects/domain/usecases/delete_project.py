"""Delete one project: the folder and everything inside it.

The production comes first. The confirm window promises that a running production is stopped and the
queue thrown away, so `halt` is called before a single file goes -- the other order leaves a worker
writing into a folder that is being removed, which is the error the promise rules out. What is
behind `halt` is not this feature's business: the photo worker lives in another feature and they
meet only in main.py.

The queue needs no separate emptying: the plan lives inside the folder, so it goes with it.

There is no separate existence check before the delete: between a check and the removal the folder
can disappear anyway, so the store's own answer ("there was nothing to remove") is the one truth
worth acting on.
"""
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def delete_project(store, halt, name):
    halt(name)
    if not store.delete(name):
        raise ProjectMissing(f"Proje yok: {name}")
