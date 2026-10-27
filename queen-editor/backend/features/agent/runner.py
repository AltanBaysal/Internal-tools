"""Which chats' agents are working, in this process -- the agent's own worker (madde 420).

The agent runs on the server, not in the page: a question starts it, and it goes on while the panel
is closed, another project is open or the page reloads (v9-4). Two chats may run at once, in one
project or two; a chat whose agent works takes no second question until it is done or stopped.

What works lives here, in memory, and nowhere on disk: a restart ends every run, and the question it
was answering is left with no outcome. Nobody knows what became of it, so nothing is written about it.

A stop lands at once. The request the agent has out cannot be cut -- the box waits on it -- so the run
is marked over, "stopped" is written, and whatever the run writes afterwards is dropped. One lock
holds the mark and the write together, so a run never writes past its own stop and a new question can
start the moment the stop is in. The same lock holds a question and its run together, so two presses
cannot write two questions.

`spawn` is injected the way PhotoRunner's is: production starts a daemon thread, tests run the work
when they choose.

A run that would change something waits here for the user (madde 480). The change it waits on is
kept on the run, in memory with the rest of what works: a reload finds it again through `asking`, and
a restart ends it with the run, before anything was changed. It waits as long as it takes -- the
panel can be closed and opened again -- until the user answers or stops it, and a stop is a
rejection. Each change asked about gets a number of its own, and an answer must name it: a second
press, or a page that has not yet seen the next change, must not allow one nobody saw. The numbers
start from the clock, so a page left open across a restart cannot name a new change by an old number.
"""
import itertools
import threading
import time
from contextlib import nullcontext


def _thread_spawn(fn):
    threading.Thread(target=fn, daemon=True).start()


class AgentRunner:
    def __init__(self, record, spawn=None, waiting=None):
        self._record = record
        self._spawn = spawn or _thread_spawn
        # What a run waits on the user inside: the idle watch's, in production (madde 498), for
        # whom an agent waiting on İzin ver / Reddet is not work.
        self._waiting = waiting or nullcontext
        self._lock = threading.Lock()
        # What a run waiting for the user sleeps on; an answer and a stop wake it.
        self._answered = threading.Condition(self._lock)
        self._runs = {}
        # Microseconds, not nanoseconds: the page reads the number as a JavaScript number, exact only
        # up to 2**53 -- about 9.0e15, where the clock in nanoseconds is already 1.8e18 and would come
        # back rounded, never matching. In microseconds it is 1.8e15.
        self._numbers = itertools.count(time.time_ns() // 1000)

    def start(self, project, chat_id, text, at, work):
        """Write the question and run `work(run)` in the background. False -- and nothing written --
        when this chat's agent is still working."""
        with self._lock:
            if (project, chat_id) in self._runs:
                return False
            self._record.add_question(project, chat_id, text, at)
            run = _Run(self, project, chat_id)
            self._runs[run.key] = run
        # Outside the lock: work run inline -- the tests' -- takes it again to write.
        self._spawn(lambda: self._go(run, work))
        return True

    def stop(self, project, chat_id):
        """Stop the chat's agent and write so. A chat whose agent is not working is left as it is: a
        press that lands as the answer arrives must not turn it into "stopped"."""
        with self._lock:
            run = self._runs.pop((project, chat_id), None)
            if run is None:
                return
            run.over = True
            self._record.stop(project, chat_id)
            # A run waiting for the user wakes, finds itself over and takes it as a rejection.
            run.asking = None
            self._answered.notify_all()

    def now(self, project):
        """{"working": the ids of the project's chats whose agent works now, smallest first,
        "asking": the changes they wait on, {"chat", "id", "change"}, by chat}. One hold, so the two
        never disagree."""
        with self._lock:
            runs = sorted((key, run) for key, run in self._runs.items() if key[0] == project)
            return {"working": [run.chat_id for _key, run in runs],
                    "asking": [{"chat": run.chat_id, **run.asking}
                               for _key, run in runs if run.asking is not None]}

    def reply(self, project, chat_id, number, allow):
        """The user's answer to change `number`. False -- and nothing woken -- unless the chat's
        agent is waiting on that very change."""
        with self._lock:
            run = self._runs.get((project, chat_id))
            if run is None or run.asking is None or run.asking["id"] != number:
                return False
            run.allowed = allow
            run.asking = None
            self._answered.notify_all()
            return True

    def _permit(self, run, change):
        with self._lock:
            if run.over:
                return False
            run.allowed = False
            run.asking = {"id": next(self._numbers), "change": change}
            # The wait lets go of the lock while it sleeps: the answer and the stop take it.
            with self._waiting():
                while run.asking is not None and not run.over:
                    self._answered.wait()
            # A stop that lands after İzin ver, before this wakes, wins: the run is over.
            return run.allowed and not run.over

    def _go(self, run, work):
        try:
            work(run)
        except Exception as exc:
            # Whatever really failed, in its own words: never a guessed cause.
            run.fail(str(exc))
        finally:
            with self._lock:
                self._end(run)

    def _write(self, run, what, *args, ends=False):
        """One line of the run's, unless the run is over. An answer or a failure ends it in the same
        hold, so a stop that comes after finds nothing to stop."""
        with self._lock:
            if run.over:
                return
            getattr(self._record, what)(run.project, run.chat_id, *args)
            if ends:
                self._end(run)

    def _end(self, run):
        """Over, and off the working list -- unless a new question already took the chat's place
        there. Called under the lock."""
        run.over = True
        if self._runs.get(run.key) is run:
            del self._runs[run.key]


class _Run:
    """One question being answered: the agent writes through here (domain/ports.py, Run)."""

    def __init__(self, runner, project, chat_id):
        self._runner = runner
        self.project = project
        self.chat_id = chat_id
        self.key = (project, chat_id)
        self.over = False
        # The change waiting for the user, {"id", "change"}, or None, and the user's answer. Read and
        # written under the runner's lock.
        self.asking = None
        self.allowed = False

    def stopped(self):
        return self.over

    def permit(self, change):
        return self._runner._permit(self, change)

    def add_step(self, running, done):
        self._runner._write(self, "add_step", running, done)

    def finish_step(self):
        self._runner._write(self, "finish_step")

    def answer(self, text):
        self._runner._write(self, "answer", text, ends=True)

    def fail(self, text):
        self._runner._write(self, "fail", text, ends=True)
