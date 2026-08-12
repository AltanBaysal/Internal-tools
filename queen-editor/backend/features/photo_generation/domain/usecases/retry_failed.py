"""Put every red job back in line at once.

The queue's own rules do the rest: a job sent back waits behind the ones that never had a turn, and
the engine still finishes a type before it starts the next. Nothing about being retried in bulk
changes where the work lands -- only how many lines are written at once.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def retry_failed(runner, store, record, plan_store, producers, now, project, log=None,
                 order_store=None, writers=None):
    """Returns how many jobs went back into the queue."""
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    put_back = 0
    for fid, cells in record.slots(project).items():
        for layer, cell in cells.items():
            if cell["status"] != queue.FAILED:
                continue
            record.mark(project, fid, layer, cell["file"], queue.QUEUED, now())
            put_back += 1
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers)
    return put_back
