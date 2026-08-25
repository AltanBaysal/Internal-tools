"""MemoryStops -- who asked for an answer to stop, for as long as that answer runs.

Deliberately not on disk, and that is not an exception to "truth lives on disk". What has to
survive a restart is the message, and it does. A stop request lives exactly as long as one answer:
if the process dies mid-answer the answer dies with it, so there is nothing left to stop. Written
to disk, the flag would outlive its answer and cut the next run instead.

Two threads reach it -- the one streaming the answer and the one carrying the stop -- because the
server handles requests concurrently. Hence the lock.
"""
import threading


class MemoryStops:
    def __init__(self):
        self._wanted = set()
        self._lock = threading.Lock()

    def want(self, project_id, chat_id):
        with self._lock:
            self._wanted.add((project_id, chat_id))

    def wanted(self, project_id, chat_id):
        with self._lock:
            return (project_id, chat_id) in self._wanted

    def clear(self, project_id, chat_id):
        # Discard rather than remove: every answer clears on its way out, and most were never
        # stopped.
        with self._lock:
            self._wanted.discard((project_id, chat_id))
