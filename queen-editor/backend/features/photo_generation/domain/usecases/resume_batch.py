"""Put the worker back on a queue that still owes frames.

What is left is not kept anywhere of its own: it is the plan minus the frames the record has
settled. Two places holding "what remains" would be two chances to disagree, and both of these live
on Drive, so a resumed run needs nothing the dead session had to remember.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class NothingToResume(Exception):
    """The queue has no frame left to produce."""


def resume_batch(runner, store, record, plan_store, generator, now, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    frames = plan_store.read(project)["frames"]
    if not queue.open_frames(frames, record.statuses(project)):
        raise NothingToResume("Devam edilecek kare yok.")
    run_queue(runner, store, record, plan_store, generator, now, project)
