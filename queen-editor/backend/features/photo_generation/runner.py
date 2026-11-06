"""One photo job at a time, in the background -- this feature's own worker.

Deliberately NOT a shared service: video generation will copy this file rather than depend on it,
so a change here can never break another pipeline (the maintenance rule for this project).

The worker knows nothing about photos, frames or policy: it starts one job, holds whatever progress
the job reports, and carries the stop flag the job reads between frames. `spawn` is injected:
production starts a daemon thread, tests run the job inline and stay deterministic.

`started` is told when a press takes the worker (madde 518): a page left open while the queue is
idle asks no more, and this is what makes it ask again. A join tells nothing: it lands while a run
goes on, and every page open is asking then already.

`ended` is told when a job ends the queue, with the state it published (madde 509): done -- which
the loop answers only once nothing is owed -- or stopped by an error, a job that raised included, or
waiting for a producer that is not installed. A pause tells nothing: whoever pressed Durdur is at the
screen.

A job queued while the run goes on joins it rather than starting a second one (`start`), and the
run answers for it: the loop can find nothing owed a moment before a job is queued, then say done.
So a run's end is published only under the lock `start` takes, and only when no job has joined
since this pass of the loop began; otherwise the loop runs again (madde 511). A job queued after
that publish finds the worker free and starts it, so no interleaving leaves one owed with nobody to
run it. Every ending, not only done: a press means the same whenever it lands, so one that joined
is answered as one made right after the end would be -- a pause comes back paused, an error gets
three fresh tries, a missing producer is still missing.
"""
import threading

from backend.features.photo_generation.domain.running_name import RunningName

# The endings `ended` hears of. Named rather than "all but paused", so a status added later tells
# nobody until someone decides it should.
TOLD = ("done", "error", "waiting")


def _thread_spawn(fn):
    threading.Thread(target=fn, daemon=True).start()


class PhotoRunner:
    def __init__(self, spawn=None, started=None, ended=None):
        self._spawn = spawn or _thread_spawn
        self._started = started or (lambda: None)
        self._ended = ended or (lambda state: None)
        self._lock = threading.Lock()
        self._state = {"status": "idle"}
        self._stop = False
        # A job has joined the run since this pass of its loop began (madde 511). Never up while
        # nothing runs: a run publishes its end only with the flag down, and only a run is joined.
        self._joined = False
        # Which folder the job is writing into. Held here because the runner is the one object every
        # way into the queue already carries, so nothing else has to be threaded a holder.
        self.named = RunningName()

    def status(self):
        with self._lock:
            state = dict(self._state)
            if state.get("status") == "running" and self._stop:
                state["stopping"] = True
            return state

    def start(self, project, job):
        """Run `job` in the background for `project`, or join the run of it that holds the worker.
        False means another project's run holds it.

        One step under the lock, so no press can fall between looking at the worker and claiming
        it. Joining leaves `job` unused and the stop flag standing: the run already has its own
        job, and a Durdur pressed before the join still stands. The holder of the folder's name is
        pointed here and nowhere else, and only by the press that won the claim -- pointed by one
        that then lost it, it would move another project's run into this folder. Outside the lock:
        the claim is already exclusive, and the holder's own lock can wait on a rename's folder
        move, which must not hold up every other door that asks this worker anything.

        `job()` returns the summary dict it wants published ({"status": "done"|"paused"|"waiting"|
        "error", ...}); the runner stamps the project's name onto it, as it stands at the end.
        """
        with self._lock:
            if self._state["status"] == "running":
                if self._state["project"] != project:
                    return False
                self._joined = True
                return True
            self._state = {"status": "running", "project": project}
            self._stop = False      # a stale request must not kill the run that just started
        self.named.took(project)
        # After the status, outside the lock, as `ended` is told: whoever hears it and asks the
        # status reads running. Before the job, so the start is never heard after its own end.
        self._started()
        self._spawn(lambda: self._run(job))
        return True

    def report(self, patch):
        """Progress from the running job. Ignored unless a job is running, so a late report from a
        thread that already finished cannot resurrect "running"."""
        with self._lock:
            if self._state.get("status") == "running":
                self._state = {**self._state, **patch}

    def reset(self):
        """Back to idle. Refused while a job runs -- only a finished or paused run can be cleared."""
        with self._lock:
            if self._state.get("status") != "running":
                self._state = {"status": "idle"}
                self._stop = False

    def rename(self, old, new):
        """Follow a project that was renamed under the worker.

        Only the stamp: the folder and the job's own name are the holder's business. The screen
        decides whether a run is its own by comparing the status's project with the page's, so a
        stale stamp would hide a run from the very page watching it.
        """
        with self._lock:
            if self._state.get("project") == old:
                self._state = {**self._state, "project": new}

    def request_stop(self):
        with self._lock:
            self._stop = True

    def stop_requested(self):
        with self._lock:
            return self._stop

    def _run(self, job):
        state = None
        while state is None:
            try:
                summary = job()
            except Exception as exc:   # the message is user-facing: whatever really failed, verbatim
                summary = {"status": "error", "error": str(exc)}
            state = self._finish(summary)
        # After the status, and outside the lock: whoever hears it and asks the status reads it.
        if state["status"] in TOLD:
            self._ended(state)

    def _finish(self, summary):
        """Publish the run's end and return it -- unless a job joined during this pass, which the
        pass may not have seen: then None, and the next pass begins with no join counted.

        Stamped with the project's name as it stands, not as it was at the start: a project renamed
        under the run ends under its new name, the one the screen compares with its own.
        """
        with self._lock:
            if self._joined:
                self._joined = False
                return None
            self._state = {**summary, "project": self._state["project"]}
            return self._state
