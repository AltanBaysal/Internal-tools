"""Put the worker on this project's queue, if it is free.

Changing the queue and running it are two separate acts, which is what lets a batch be submitted
while another one renders: the loop reads the plan again every turn, so "already running THIS
project" is not an error -- it is the normal case. Only another project's run is a refusal, because
there is one worker.

Called after the queue is written, by every door into it. A run of this project is joined rather
than trusted to come round: its loop may already have looked for the last time, and joining is what
makes it look once more before it ends (madde 511). Joining and claiming are one step of the
runner's, so there is nothing to look at first.
"""
from backend.features.photo_generation.domain.run_loop import make_job


class Busy(Exception):
    """The worker is held by another project's generation (message is user-facing)."""


def run_queue(runner, store, record, plan_store, producers, now, project, log=None,
              order_store=None, writers=None, stills=None, references=None):
    """`producers` is the {job type: producer} map the loop dispatches on and `writers` the one it
    finds a job's prompt writer in; `stills` is what pulls a picture out of a landed video;
    `references` answers with the project's reference pool for a job made of it; `order_store` is
    where the loop reads the sequence from; `log` is only carried through, because where the loop's
    timing line lands is main.py's choice."""
    # Built even when the press only joins: the closure costs nothing and reads nothing until run.
    job = make_job(runner, store, record, plan_store, producers, now, log=log,
                   order_store=order_store, writers=writers, stills=stills,
                   references=references)
    if not runner.start(project, job):
        raise Busy("Zaten bir üretim sürüyor.")
