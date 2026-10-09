"""QueuedWrite -- keeps one file on disk up to date with a state held in memory (Madde 447).

What the user asked for: "bu yazmaları Flask yönetir, Drive değil; Flask'a öyle bir özellik ekle,
queue gibi". A change is made in memory and its request answers at once; one thread writes the file
behind it. What it writes is the state as it is when the write starts, so any number of changes
that arrive while one write is under way go out together in the next.

The thread lives only while there is something to write, and it is not a daemon: Python waits for
it on an ordinary exit -- Ctrl+C, and the notebook's pkill since main.py makes SIGTERM one. Only a
real crash loses what was not written yet, which the user accepted ("flask tak diye kapanırsa
kaybolsun sıkıntı yok").
"""
import logging
import threading
import time

log = logging.getLogger(__name__)

# A write that fails is tried again on its own: the user already saw the change succeed, and no
# other change may come to carry it to the disk before a restart. Bounded, so a disk that keeps
# refusing is not hammered for ever; the next change starts the count again.
TRIES = 3
RETRY_SECONDS = 5


class QueuedWrite:
    def __init__(self, store, path, render, pause=time.sleep):
        self._store = store
        self._path = path
        # Called on the writer's thread, so it must take whatever lock guards the state itself.
        self._render = render
        self._pause = pause
        self._lock = threading.Condition()
        self._wanted = False
        self._running = False
        # What is on disk, as far as this process knows: the state it was built on, which is what the
        # file held when it was read -- or no file, and no projects, which need no write either.
        # After that only the writer's thread reads or sets it, and one of those runs at a time.
        self._written = render()

    def changed(self):
        """The state changed: write it soon. Never waits for the disk."""
        with self._lock:
            self._wanted = True
            if self._running:
                return
            self._running = True
        try:
            # daemon=False said out loud: a thread takes the flag from the one that makes it, and this
            # is made from werkzeug's request threads, which are daemons. Inherited, an ordinary exit
            # would drop the write instead of waiting for it.
            threading.Thread(target=self._run, name=f"write {self._path}", daemon=False).start()
        except BaseException:
            # No writer is running after all; left marked as running, flush would wait for ever and
            # no later change would start one.
            with self._lock:
                self._running = False
                self._lock.notify_all()
            raise

    def flush(self):
        """Wait until nothing is left to write. Tests and measurements ask it; a request never does."""
        with self._lock:
            while self._running:
                self._lock.wait()

    def _run(self):
        while self._taken():
            self._write_newest()

    def _taken(self):
        # Takes the pending change, or -- when there is none -- ends the writer, under one lock, so a
        # change arriving now either is taken or starts a writer of its own.
        with self._lock:
            if not self._wanted:
                self._running = False
                self._lock.notify_all()
                return False
            self._wanted = False
            return True

    def _write_newest(self):
        for attempt in range(1, TRIES + 1):
            try:
                # Rendered again on every try, so a retry carries what changed while it waited.
                text = self._render()
                # A change that changed nothing -- archived=False on a project that is not archived
                # -- costs no write.
                if text != self._written:
                    self._store.write_text(self._path, text)
                    self._written = text
                return
            except Exception as error:  # noqa: BLE001 -- the thread must live to clear _running
                # The state in memory is still right; what failed is only its copy on disk.
                log.error("%s was not written (try %d of %d): %s", self._path, attempt, TRIES, error)
                if attempt < TRIES:
                    self._pause(RETRY_SECONDS)
