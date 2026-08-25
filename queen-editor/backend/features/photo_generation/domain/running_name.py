"""Which folder the worker is writing into, and the gate a rename passes through.

A project IS a folder and its name is the address of everything inside it, so renaming one moves the
ground under a run. The run reads the name again every turn, which is what lets the turn after a
move simply work in the new folder.

What must not happen is a write that resolved the old name and lands after the move: the storage
layer creates a folder it is missing, so such a write would leave a ghost beside the real project
with one file in it. The writes take this lock and the rename takes it too, so no write can fall on
both sides of a move. The render is outside the lock -- the wait is one file write, not one frame.
"""
import threading
from contextlib import contextmanager


class RunningName:
    def __init__(self, name=None):
        # Re-entrant: a write asks for the name it is about to use while already inside the gate.
        self._lock = threading.RLock()
        self._name = name

    def took(self, name):
        """A run has started on this project."""
        with self._lock:
            self._name = name

    def now(self):
        """The name as it stands. Read at the top of every turn."""
        with self._lock:
            return self._name

    @contextmanager
    def steady(self):
        """The name, held still for as long as the caller writes with it."""
        with self._lock:
            yield self._name

    def moved(self, old, new, do):
        """Run `do` with no write able to straddle it, and follow the folder. Returns `do`'s answer.

        The name is followed only when it was this one: renaming a project nobody is producing must
        not point the worker somewhere else.
        """
        with self._lock:
            answer = do()
            if self._name == old:
                self._name = new
            return answer
