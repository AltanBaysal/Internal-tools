"""One export per mode, in the background -- the export's own worker.

Separate from PhotoRunner on purpose: an export is not a render, and the design lets the two run at
once. Two modes can also run beside each other (one merged, one separate), so the state is kept per
mode rather than as a single "busy".

The worker knows nothing about videos or folders: it starts a job, holds whatever that job reports,
and carries a cancel flag the job reads between pieces. `spawn` is injected -- production starts a
daemon thread, tests run the job inline and stay deterministic.

It also times the steps, because a state change is the only thing that knows a step began and ended,
and the state lives here (madde 287). The run reports which step it is on; how long the one before
it took is worked out here. What the seconds are called on screen is the screen's business.

Nothing survives the process. An export is session-bound by design (madde 96): a dead session leaves
no half-written folder behind, because the run that would have finished it is gone with it.
"""
import threading
import time

MERGED = "merged"
SEPARATE = "separate"
MODES = (MERGED, SEPARATE)

# Not doing anything. Being busy is the other side of this, rather than a list of working states:
# such a list goes stale the moment a step is added, and a stale one let a second export start
# while the first was writing its pictures. These three are also the states with no duration to
# record -- the same question, asked twice.
RESTING = ("idle", "done", "error")

# `steps` is a tuple: state() hands out a shallow copy, and a shared list could be changed by
# whoever read it.
IDLE = {"state": "idle", "written": 0, "total": 0, "target": None, "error": None, "steps": ()}


def _thread_spawn(fn):
    threading.Thread(target=fn, daemon=True).start()


class ExportRunner:
    def __init__(self, spawn=None, clock=None):
        self._spawn = spawn or _thread_spawn
        # Monotonic, not the wall clock: a wall clock can be put back, and time spent cannot.
        self._clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._state = {mode: dict(IDLE) for mode in MODES}
        self._cancel = {mode: False for mode in MODES}
        self._started = {mode: None for mode in MODES}

    def state(self):
        with self._lock:
            return {mode: dict(state) for mode, state in self._state.items()}

    def start(self, mode, job):
        """Claim this mode and run `job` in the background. False means it is already running."""
        with self._lock:
            if self._state[mode]["state"] not in RESTING:
                return False
            self._state[mode] = {**IDLE, "state": "running"}
            self._started[mode] = self._clock()
            self._cancel[mode] = False   # a stale cancel must not kill the run just started
        self._spawn(lambda: self._run(mode, job))
        return True

    def report(self, mode, **patch):
        with self._lock:
            was = self._state[mode]
            if "state" in patch and patch["state"] != was["state"]:
                patch = {**patch, "steps": self._closed(mode, was, patch["state"])}
            self._state[mode] = {**was, **patch}

    def _closed(self, mode, was, now):
        """The steps to carry forward once the run moves off the step it was on.

        A run that went back to idle was cancelled, and its steps say nothing about anything: the
        folder is gone and so is the reason to read them.

        Called under the lock, and it marks the new step's start as it goes -- the same clock
        reading ends one step and begins the next, so no second of the run falls between two.
        """
        start, self._started[mode] = self._started[mode], self._clock()
        if now == "idle":
            return ()
        if was["state"] in RESTING or start is None:
            return was["steps"]
        return (*was["steps"],
                {"step": was["state"], "seconds": round(self._started[mode] - start, 1)})

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
