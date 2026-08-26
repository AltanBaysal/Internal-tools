"""MemoryStops -- the connection a running answer is reading, for as long as it runs.

Deliberately not on disk, and that is not an exception to "truth lives on disk". What has to
survive a restart is the message, and it does. What is kept here lives exactly as long as one
answer: if the process dies mid-answer the answer dies with it, so there is nothing left to stop.
Written to disk, it would outlive its answer and cut the next run instead.

Two threads reach it -- the one streaming the answer and the one carrying the stop -- because the
server handles requests concurrently. Hence the lock.
"""
import threading


class MemoryStops:
    def __init__(self):
        self._wanted = set()
        # How to cut the connection each running answer is reading. Since Madde 90 this is the
        # thing a stop acts on: the flag beside it only records that we were the ones who cut.
        self._cuts = {}
        self._lock = threading.Lock()

    def hold(self, project_id, chat_id, cut):
        # Which of the two comes first is nobody's to arrange: the press can land before the
        # connection exists, and that is the very case this exists for -- a model that thinks for
        # minutes before its first word.
        with self._lock:
            self._cuts[(project_id, chat_id)] = cut
            asked = (project_id, chat_id) in self._wanted
        if asked:
            cut()

    def want(self, project_id, chat_id):
        with self._lock:
            self._wanted.add((project_id, chat_id))
            cut = self._cuts.get((project_id, chat_id))
        # Outside the lock. Cutting is one system call and the reading thread never touches this
        # lock while it waits, so nothing would block -- but what a cut does is not this class's
        # business, and holding a lock across somebody else's code is how that stops being true.
        if cut:
            cut()

    def wanted(self, project_id, chat_id):
        with self._lock:
            return (project_id, chat_id) in self._wanted

    def clear(self, project_id, chat_id):
        # Discard rather than remove: every answer clears on its way out, and most were never
        # stopped. The connection goes too -- a stop arriving after the answer ended would reach a
        # socket number that belongs to somebody else by then.
        with self._lock:
            self._wanted.discard((project_id, chat_id))
            self._cuts.pop((project_id, chat_id), None)
