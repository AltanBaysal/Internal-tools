"""Put every red job back in line at once.

The queue's own rules do the rest: a job sent back waits behind the ones that never had a turn, and
the engine still finishes a type before it starts the next. Nothing about being retried in bulk
changes where the work lands -- only how many lines are written at once.
"""
from backend.features.photo_generation.domain import layers, queue, video_settings
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def retry_failed(runner, store, record, plan_store, producers, now, project, log=None,
                 order_store=None, writers=None, stills=None, references=None, length=None,
                 ending=None):
    """Returns how many jobs went back into the queue.

    `length` answers how long the project's videos run now, and `ending` whether they end happily:
    every red video goes back that way, as one frame's Tekrar dene sends it (madde 422, 426).
    """
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    red = [(fid, layer, cell) for fid, cells in record.slots(project).items()
           for layer, cell in cells.items() if cell["status"] == queue.FAILED]
    # Before the red lines are put back, so a loop already running never takes a video the way it is
    # leaving.
    video_settings.as_set_now(plan_store, project,
                              [fid for fid, layer, _cell in red if layer == layers.VIDEO], length,
                              ending)
    for fid, layer, cell in red:
        record.mark(project, fid, layer, cell["file"], queue.QUEUED, now())
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers, stills=stills,
              references=references)
    return len(red)
