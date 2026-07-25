"""One photo job at a time, in the background -- this feature's own worker.

Deliberately NOT a shared service: video generation will copy this file rather than depend on it,
so a change here can never break another pipeline (the maintenance rule for this project).

A photo takes 30-90s, far longer than a request should stay open, so `start` returns immediately
and the UI asks `status()`. `spawn` is injected: production starts a daemon thread, tests run the
job inline and stay deterministic.
"""
import threading


def _thread_spawn(fn):
    threading.Thread(target=fn, daemon=True).start()


class PhotoRunner:
    def __init__(self, spawn=None):
        self._spawn = spawn or _thread_spawn
        self._lock = threading.Lock()
        self._state = {"status": "idle"}

    def status(self):
        with self._lock:
            return dict(self._state)

    def start(self, project, step):
        """Claim the worker and run `step` in the background. False means one is already running."""
        with self._lock:
            if self._state["status"] == "running":
                return False
            self._state = {"status": "running", "project": project}
        self._spawn(lambda: self._run(project, step))
        return True

    def _run(self, project, step):
        try:
            filename = step()
        except Exception as exc:   # the message is user-facing: whatever really failed, verbatim
            self._set({"status": "error", "project": project, "error": str(exc)})
            return
        self._set({"status": "done", "project": project, "file": filename})

    def _set(self, state):
        with self._lock:
            self._state = state
