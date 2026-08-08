"""Put the worker on this project's queue, if it is free.

Changing the queue and running it are two separate acts, which is what lets a batch be submitted
while another one renders: the loop reads the plan again every turn, so "already running THIS
project" is not an error -- it is the normal case. Only another project's run is a refusal, because
there is one worker.
"""
from backend.features.photo_generation.domain.run_loop import make_job


class Busy(Exception):
    """The worker is held by another project's generation (message is user-facing)."""


def run_queue(runner, store, record, plan_store, generator, now, project, log=None):
    """`log` is only carried through: where the loop's timing line lands is main.py's choice."""
    state = runner.status()
    if state.get("status") == "running":
        if state.get("project") == project:
            return                      # the live loop will reach the new frames by itself
        raise Busy("Zaten bir üretim sürüyor.")
    job = make_job(runner, store, record, plan_store, generator, now, project, log=log)
    if not runner.start(project, job):
        # Lost the race against another request between status() and start().
        raise Busy("Zaten bir üretim sürüyor.")
