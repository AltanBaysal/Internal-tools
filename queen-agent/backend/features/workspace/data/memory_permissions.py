"""MemoryPermissions -- the answer a paused turn is waiting for, for as long as it waits.

Sibling of MemoryStops and deliberately the same shape: in memory rather than on disk, keyed by
chat, reached by two threads at once -- the one streaming the answer and the one carrying the
decision. Hence the lock.

On disk it would outlive its turn and settle the next one's question without anybody being asked.
"""
import threading

from backend.features.workspace.domain.permission import Decision


class MemoryPermissions:
    def __init__(self):
        self._decided = {}
        # One event per chat, so a decision wakes exactly the turn it belongs to.
        self._events = {}
        self._lock = threading.Lock()

    def answer(self, project_id, chat_id, allowed, reason):
        # Which of the two comes first is nobody's to arrange: an answer can be left before the
        # question is asked, and that is not a mistake -- it is the race hold() carries too.
        with self._lock:
            self._decided[(project_id, chat_id)] = Decision(bool(allowed), reason or "")
            event = self._events.get((project_id, chat_id))
        # Outside the lock, like the cut a stop hands out: waking is somebody else's code, and
        # holding a lock across it is how "this lock is never held long" stops being true.
        if event:
            event.set()

    def wait(self, project_id, chat_id, tick):
        event = self._event_for(project_id, chat_id)
        # Looked at before waiting as well as after: the answer may already be here, and a wait
        # that only looked afterwards would sit out a whole tick with the decision in its hand.
        decision = self._spend(project_id, chat_id)
        if decision is not None:
            return decision
        event.wait(tick)
        return self._spend(project_id, chat_id)

    def wake(self, project_id, chat_id):
        with self._lock:
            event = self._events.get((project_id, chat_id))
        if event:
            event.set()

    def clear(self, project_id, chat_id):
        # Every turn clears on its way out, asked or not -- the same as a stop does.
        with self._lock:
            self._decided.pop((project_id, chat_id), None)
            self._events.pop((project_id, chat_id), None)

    def _event_for(self, project_id, chat_id):
        with self._lock:
            event = self._events.get((project_id, chat_id))
            if event is None:
                event = threading.Event()
                self._events[(project_id, chat_id)] = event
            return event

    def _spend(self, project_id, chat_id):
        """Take the decision rather than read it, and leave the event ready for the next question.

        A turn may ask twice, and the second question is a question -- not something the first
        answer already settled.
        """
        with self._lock:
            decision = self._decided.pop((project_id, chat_id), None)
            event = self._events.get((project_id, chat_id))
            if event:
                event.clear()
        return decision
