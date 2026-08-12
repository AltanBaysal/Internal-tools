"""One export per mode, in the background -- the export's own worker.

Separate from PhotoRunner on purpose: an export is not a render, and the design lets the two run at
once. Two modes can also run beside each other (one merged, one separate), so the state is kept per
mode rather than as a single "busy".

The worker knows nothing about videos or folders: it starts a job, holds whatever that job reports,
and carries a cancel flag the job reads between pieces. `spawn` is injected -- production starts a
daemon thread, tests run the job inline and stay deterministic.

Nothing survives the process. An export is session-bound by design (madde 96): a dead session leaves
no half-written folder behind, because the run that would have finished it is gone with it.
"""
import threading

MERGED = "merged"
SEPARATE = "separate"
MODES = (MERGED, SEPARATE)

IDLE = {"state": "idle", "written": 0, "total": 0, "target": None, "error": None}


def _thread_spawn(fn):
    threading.Thread(target=fn, daemon=True).start()


class ExportRunner:
    def __init__(self, spawn=None):
        self._spawn = spawn or _thread_spawn
        self._lock = threading.Lock()
        self._state = {mode: dict(IDLE) for mode in MODES}
        self._cancel = {mode: False for mode in MODES}

    def state(self):
        with self._lock:
            return {mode: dict(state) for mode, state in self._state.items()}

    def start(self, mode, job):
        """Claim this mode and run `job` in the background. False means it is already running."""
        with self._lock:
            if self._state[mode]["state"] in ("running", "merging"):
                return False
            self._state[mode] = {**IDLE, "state": "running"}
            self._cancel[mode] = False   # a stale cancel must not kill the run just started
        self._spawn(lambda: self._run(mode, job))
        return True

    def report(self, mode, **patch):
        with self._lock:
            self._state[mode] = {**self._state[mode], **patch}

    def cancel(self, mode):
        with self._lock:
            self._cancel[mode] = True

    def cancelled(self, mode):
        with self._lock:
            return self._cancel[mode]

    def _run(self, mode, job):
        try:
            job()
        except Exception as exc:
            # Whatever really failed, verbatim: the screen prints this line as it is.
            self.report(mode, state="error", error=str(exc))
