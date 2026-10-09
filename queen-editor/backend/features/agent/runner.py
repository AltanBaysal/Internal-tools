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
"""
import threading


def _thread_spawn(fn):
    threading.Thread(target=fn, daemon=True).start()


class AgentRunner:
    def __init__(self, record, spawn=None):
        self._record = record
        self._spawn = spawn or _thread_spawn
        self._lock = threading.Lock()
        self._runs = {}

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

    def working(self, project):
        """The ids of the project's chats whose agent is working now, smallest first."""
        with self._lock:
            return sorted(chat_id for name, chat_id in self._runs if name == project)

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

    def stopped(self):
        return self.over

    def add_step(self, running, done):
        self._runner._write(self, "add_step", running, done)

    def finish_step(self):
        self._runner._write(self, "finish_step")

    def answer(self, text):
        self._runner._write(self, "answer", text, ends=True)

    def fail(self, text):
        self._runner._write(self, "fail", text, ends=True)
