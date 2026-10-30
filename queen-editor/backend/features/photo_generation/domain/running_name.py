"""Which folder the worker is writing into, and the gate a rename passes through.

A project IS a folder and its name is the address of everything inside it, so renaming one moves the
ground under a run. The run reads the name again every turn, which is what lets the turn after a
move simply work in the new folder.

What must not happen is a read or a write that resolved the old name and lands after the move: it
would find nothing where the folder was (a write fails, the storage layer never opens a project's
folder), and a turn whose reads fell on both sides would take the moved folder for an empty one --
a finished frame made again (madde 513), a video made with no prompt (522). So a turn's reads and
its writes each resolve the name under this lock and use it only inside it, and the rename moves
the folder under it too: whatever a hold reads or writes is the folder the move has not taken away.
The writer's ask and the render are outside the lock -- the wait is a few file reads or writes, not
one frame.
"""
import threading
from contextlib import contextmanager


class RunningName:
    def __init__(self, name=None):
        # Re-entrant: nothing inside a hold takes it again today, but one that did would wait on
        # itself for ever with a plain lock.
        self._lock = threading.RLock()
        self._name = name

    def took(self, name):
        """A run has started on this project."""
        with self._lock:
            self._name = name

    def now(self):
        """The name as it stands."""
        with self._lock:
            return self._name

    @contextmanager
    def steady(self):
        """The name, held still for as long as the caller reads or writes with it."""
        with self._lock:
            yield self._name

    def moved(self, old, new, do):
        """Run `do` with no read or write able to straddle it, and follow the folder. Returns `do`'s
        answer.

        The name is followed only when it was this one: renaming a project nobody is producing must
        not point the worker somewhere else.
        """
        with self._lock:
            answer = do()
            if self._name == old:
                self._name = new
            return answer
