"""One install at a time, in the background -- this feature's own worker.

A copy of the photo runner rather than a dependency on it: the maintenance rule for this project is
that a change to one pipeline's worker can never break another's. What differs is the vocabulary --
an install belongs to a producer kind, not a project, and it is cancelled rather than paused.

The worker knows nothing about models or downloads: it starts one job, holds whatever progress the
job reports, and carries the cancel flag the job reads between chunks. `spawn` is injected:
production starts a daemon thread, tests run the job inline and stay deterministic.
"""
import threading


def _thread_spawn(fn):
    threading.Thread(target=fn, daemon=True).start()


class InstallRunner:
    def __init__(self, spawn=None):
        self._spawn = spawn or _thread_spawn
        self._lock = threading.Lock()
        self._state = {"status": "idle"}
        self._cancel = False

    def status(self):
        with self._lock:
            return dict(self._state)

    def start(self, kind, job):
        """Claim the worker and run `job` in the background. False means one is already running."""
        with self._lock:
            if self._state["status"] == "running":
                return False
            self._state = {"status": "running", "kind": kind}
            self._cancel = False    # a stale request must not kill the install that just started
        self._spawn(lambda: self._run(kind, job))
        return True

    def report(self, patch):
        """Progress from the running job. Ignored unless one is running, so a late report from a
        thread that already finished cannot resurrect "running"."""
        with self._lock:
            if self._state.get("status") == "running":
                self._state = {**self._state, **patch}

    def reset(self):
        with self._lock:
            if self._state.get("status") != "running":
                self._state = {"status": "idle"}
                self._cancel = False

    def request_cancel(self):
        with self._lock:
            self._cancel = True

    def cancelled(self):
        with self._lock:
            return self._cancel

    def _run(self, kind, job):
        try:
            summary = job()
        except Exception as exc:   # the message is user-facing: whatever really failed, verbatim
            self._set({"status": "error", "kind": kind, "error": str(exc)})
            return
        self._set({**summary, "kind": kind})

    def _set(self, state):
        with self._lock:
            self._state = state
