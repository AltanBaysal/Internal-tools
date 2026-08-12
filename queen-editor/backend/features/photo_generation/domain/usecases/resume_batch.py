"""Put the worker back on a queue that still owes work.

What is left is not kept anywhere of its own: it is the plan minus the jobs the record has settled.
Two places holding "what remains" would be two chances to disagree, and both of these live on Drive,
so a resumed run needs nothing the dead session had to remember.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class NothingToResume(Exception):
    """The queue has no job left to do."""


def resume_batch(runner, store, record, plan_store, producers, now, project, log=None,
                 order_store=None, writers=None):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    jobs = plan_store.read(project)["frames"]
    # No order here on purpose: this asks whether anything is owed at all, and that answer is a set
    # rather than a sequence.
    if not queue.open_jobs(jobs, record.slots(project)):
        raise NothingToResume("Devam edilecek kare yok.")
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers)
