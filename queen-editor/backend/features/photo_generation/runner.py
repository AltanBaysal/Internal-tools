"""One photo job at a time, in the background -- this feature's own worker.

Deliberately NOT a shared service: video generation will copy this file rather than depend on it,
so a change here can never break another pipeline (the maintenance rule for this project).

The worker knows nothing about photos, frames or policy: it starts one job, holds whatever progress
the job reports, and carries the stop flag the job reads between frames. `spawn` is injected:
production starts a daemon thread, tests run the job inline and stay deterministic.
"""
import threading


def _thread_spawn(fn):
    threading.Thread(target=fn, daemon=True).start()


class PhotoRunner:
    def __init__(self, spawn=None):
        self._spawn = spawn or _thread_spawn
        self._lock = threading.Lock()
        self._state = {"status": "idle"}
        self._stop = False

    def status(self):
        with self._lock:
            return dict(self._state)

    def start(self, project, job):
        """Claim the worker and run `job` in the background. False means one is already running.

        `job()` returns the summary dict it wants published ({"status": "done"|"stopped"|"error",
        ...}); the runner stamps the project onto it.
        """
        with self._lock:
            if self._state["status"] == "running":
                return False
            self._state = {"status": "running", "project": project}
            self._stop = False      # a stale request must not kill the run that just started
        self._spawn(lambda: self._run(project, job))
        return True

    def report(self, patch):
        """Progress from the running job. Ignored unless a job is running, so a late report from a
        thread that already finished cannot resurrect "running"."""
        with self._lock:
            if self._state.get("status") == "running":
                self._state = {**self._state, **patch}

    def request_stop(self):
        with self._lock:
            self._stop = True

    def stop_requested(self):
        with self._lock:
            return self._stop

    def _run(self, project, job):
        try:
            summary = job()
        except Exception as exc:   # the message is user-facing: whatever really failed, verbatim
            self._set({"status": "error", "project": project, "error": str(exc)})
            return
        self._set({**summary, "project": project})

    def _set(self, state):
        with self._lock:
            self._state = state
