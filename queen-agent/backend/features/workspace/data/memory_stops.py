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
        raise NotImplementedError

    def wanted(self, project_id, chat_id):
        raise NotImplementedError

    def clear(self, project_id, chat_id):
        raise NotImplementedError
