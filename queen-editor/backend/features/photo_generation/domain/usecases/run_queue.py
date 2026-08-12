"""Put the worker on this project's queue, if it is free.

Changing the queue and running it are two separate acts, which is what lets a batch be submitted
while another one renders: the loop reads the plan again every turn, so "already running THIS
project" is not an error -- it is the normal case. Only another project's run is a refusal, because
there is one worker.
"""
from backend.features.photo_generation.domain.run_loop import make_job


class Busy(Exception):
    """The worker is held by another project's generation (message is user-facing)."""


def run_queue(runner, store, record, plan_store, producers, now, project, log=None,
              order_store=None):
    """`producers` is the {job type: producer} map the loop dispatches on; `order_store` is where
    the loop reads the sequence from; `log` is only carried through, because where the loop's
    timing line lands is main.py's choice."""
    state = runner.status()
    if state.get("status") == "running":
        if state.get("project") == project:
            return                      # the live loop will reach the new jobs by itself
        raise Busy("Zaten bir üretim sürüyor.")
    job = make_job(runner, store, record, plan_store, producers, now, project, log=log,
                   order_store=order_store)
    if not runner.start(project, job):
        # Lost the race against another request between status() and start().
        raise Busy("Zaten bir üretim sürüyor.")
