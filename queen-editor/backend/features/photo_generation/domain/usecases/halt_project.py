"""Stop the production a project owns, and wait until the worker has really let go.

Deleting a project is what asks for this: the confirm promises that a running production is stopped
and the queue thrown away, and a worker still writing into a folder that is being removed is exactly
the error that promise rules out.

The waiting is the whole point. The stop flag alone only ends the batch *between* frames, and the
frame in flight can be a minute of rendering -- ComfyUI's interrupt cuts that short, but neither is
instant. So this blocks until the worker leaves "running", with a ceiling: a user's delete cannot be
held hostage by a worker that never comes back.
"""
LIMIT = 50      # 5 seconds in tenths -- an interrupted render lands well inside this
STEP = 0.1


def halt_project(runner, interrupt, sleep, project):
    """True when the worker was this project's and has been cleared, False when it was somebody
    else's (or nobody's) and was left exactly as it was."""
    if runner.status().get("project") != project:
        return False
    if runner.status().get("status") == "running":
        runner.request_stop()
        try:
            interrupt()
        except Exception:
            pass    # a dead renderer must not be what stops a project from being deleted
        for _ in range(LIMIT):
            if runner.status().get("status") != "running":
                break
            sleep(STEP)
    # Refused while a job runs, so a worker that outlasted the wait keeps its state and the status
    # screen keeps telling the truth about it.
    runner.reset()
    return True
