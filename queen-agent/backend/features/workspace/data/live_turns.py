"""LiveTurns -- the turns running now, one per chat at most, each on a thread of its own (Madde 461).

In memory and nowhere else, which is not an exception to "truth lives on disk": what has to survive a
restart is the question, and it is written before its turn starts. A turn lives as long as the
process running it. If the process dies the turn dies with it, the chat reads as unanswered, and Try
again asks again; a waiting permission dies too, unanswered (the user: "(a) yalnız bellek").

The thread is a daemon on purpose: a turn waiting on a question nobody answers would otherwise keep
SIGTERM from ending the process for ever. The projects.json writer is not one, and says so itself.
"""
import logging
import threading
import uuid

from backend.features.workspace.domain.chat import Chat
from backend.features.workspace.domain.permission import Decision
from backend.features.workspace.domain.turn import Snapshot, applied, changed

log = logging.getLogger(__name__)


class LiveTurn:
    """One turn while it runs: its stop, its question, the record it was handed, and its snapshot.

    Every field changes under the one condition, and every change wakes whoever waits on it -- the
    turn's own wait for a decision and every listener alike. A stop and a decision name the turn
    and the question they were meant for, so a late one reaches nothing.
    """

    def __init__(self, turn_id):
        self.id = turn_id
        self._lock = threading.Condition()
        self._snapshot = Snapshot(id=turn_id)
        self._record = None
        self._stopped = False
        # How to cut the request this turn is reading now. The flag beside it records that we cut it.
        self._cut = None
        self._decided = None

    # ---- What the turn's own loop asks (the TurnControl port) ----

    def stopped(self):
        with self._lock:
            return self._stopped

    def hold(self, cut):
        # Which comes first is nobody's to arrange: a press can land before the request opens.
        with self._lock:
            self._cut = cut
            stopped = self._stopped
        if stopped:
            cut()

    def decision(self):
        """Wait, with no limit, for the answer to the question standing. None if the turn is stopped."""
        with self._lock:
            self._lock.wait_for(lambda: self._decided is not None or self._stopped)
            decided, self._decided = self._decided, None
            return None if self._stopped else decided

    # ---- What the runner does ----

    def hand(self, chat):
        with self._lock:
            self._record = chat

    def apply(self, piece):
        with self._lock:
            self._snapshot = applied(self._snapshot, piece)
            self._lock.notify_all()

    def end(self, error):
        # Once: the first end is the one listeners heard, and its words are the turn's.
        with self._lock:
            if self._snapshot.ended:
                return
            self._snapshot = changed(self._snapshot, ended=True, permission=None, error=error)
            self._lock.notify_all()

    # ---- What requests do ----

    def record(self):
        """The chat as this turn holds it, or None before one is handed -- then the disk has it."""
        with self._lock:
            return self._record

    def snapshot(self):
        with self._lock:
            return self._snapshot

    def changed_since(self, version, timeout):
        """The snapshot once it has moved past `version`, or as it is after `timeout` seconds."""
        with self._lock:
            self._lock.wait_for(lambda: self._snapshot.version != version, timeout)
            return self._snapshot

    def stop(self, turn_id):
        with self._lock:
            if turn_id != self.id or self._snapshot.ended:
                return
            self._stopped = True
            cut = self._cut
            # The card goes with the stop: nobody is waiting on that answer any more.
            self._snapshot = changed(self._snapshot, permission=None)
            self._lock.notify_all()
        # Outside the lock: what a cut does is the transport's business, and holding a lock across
        # somebody else's code is how "this lock is never held long" stops being true.
        if cut:
            cut()

    def decide(self, turn_id, wait, allowed, reason):
        with self._lock:
            asked = self._snapshot.permission
            if turn_id != self.id or asked is None or asked.wait != wait:
                return
            self._decided = Decision(bool(allowed), reason or "")
            self._snapshot = changed(self._snapshot, permission=None)
            self._lock.notify_all()


class LiveTurns:
    def __init__(self):
        self._turns = {}
        self._lock = threading.Lock()

    def reserve(self, project_id, chat_id):
        """A new turn holding this chat, or None if one already holds it -- looked and taken in one
        step, so of any number of requests arriving together exactly one gets it."""
        with self._lock:
            if (project_id, chat_id) in self._turns:
                return None
            turn = LiveTurn("t" + uuid.uuid4().hex[:12])
            self._turns[(project_id, chat_id)] = turn
            return turn

    def release(self, project_id, chat_id, turn, error=""):
        """Let go of the chat, then end the turn that held it (Madde 462).

        Every hold ends here, whatever it was: a turn that ran, a send refused after it was held,
        a version or a trim. Someone may be listening to any of them -- a reload in that moment --
        and a turn nobody ends keeps its listener waiting for ever. Let go before saying so:
        whoever hears the end may send the next message at once.
        """
        # Only that turn: a release arriving late must not let go of the turn after it.
        with self._lock:
            if self._turns.get((project_id, chat_id)) is turn:
                del self._turns[(project_id, chat_id)]
        turn.end(error)

    def get(self, project_id, chat_id):
        with self._lock:
            return self._turns.get((project_id, chat_id))

    def any_in(self, project_id):
        with self._lock:
            return any(held == project_id for held, _ in self._turns)

    def start(self, project_id, turn, chat, pieces):
        """Run the turn's loop on a thread of its own, from the record it is handed."""
        turn.hand(chat)
        threading.Thread(
            target=self._run,
            args=(project_id, chat.id, turn, pieces),
            name=f"turn {chat.id}",
            daemon=True,
        ).start()

    def _run(self, project_id, chat_id, turn, pieces):
        error = ""
        try:
            for piece in pieces:
                # The last piece is the chat as the turn wrote it.
                if isinstance(piece, Chat):
                    turn.hand(piece)
                else:
                    turn.apply(piece)
        except Exception as broken:  # noqa: BLE001 -- the turn must still end and let go
            # The turn's own code -- a tool, the disk: the model's faults end as an answer in the
            # black box. Nothing was written, and no browser may be there to hear it.
            error = str(broken)
            log.error("the turn in chat %s ended on a fault: %s", chat_id, error)
        finally:
            self.release(project_id, chat_id, turn, error)
