"""ChatRecord over DriveStorage -- the only place that knows the chat file's name and its lines.

Every chat of a project lives in one file inside the project's own folder (madde 417): a renamed
project carries its chats and a deleted one takes them, and the list, a chat opened and a new chat
each read one file -- a file per chat would have the list open every one of them over Drive.

The file is only ever added to, the photo record's rule: a session that dies mid-write loses at most
the line it was adding, where rewriting a chat could lose all of it. Each line is one event about
one chat, and reading folds them in the order they were written. Nothing is held in memory, so a
restart loses nothing.

One record writes every chat of every project (main.py), from the doors' threads and from every
agent's own (madde 420). Two appends at once can tear a line or lose one, so lines are added one at a
time.
"""
import json
import threading

from backend.features.agent.domain.usecases.chats import ProjectMissing

FILE = "chats.jsonl"

OPENED = "opened"
QUESTION = "question"
STEP = "step"
STEP_DONE = "stepDone"
ANSWER = "answer"
FAILURE = "failure"
STOPPED = "stopped"


def _rows(lines):
    """Every readable line, in the order written.

    One that will not parse is skipped rather than raised on: the last can be half-written after a
    session death, and it must not hide the chats before it.
    """
    rows = []
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and isinstance(row.get("chat"), int):
            rows.append(row)
    return rows


def _fold(rows):
    """The chats, in the order their first line was written. Any line makes its chat exist, so
    "opened" is only ever needed by a chat with nothing asked yet."""
    chats = {}
    for row in rows:
        chat = chats.setdefault(row["chat"], {"id": row["chat"], "questions": []})
        if row.get("event") == QUESTION:
            chat["questions"].append({"text": row.get("text"), "askedAt": row.get("at"),
                                      "steps": [], "outcome": None})
        elif chat["questions"]:
            _land(chat["questions"][-1], row)
    return list(chats.values())


def _land(question, row):
    """Steps and outcomes belong to the question being worked on, which is the chat's latest.

    The agent keeps a step going while the model reads what it brought, so the outcome settles the
    last one (BEHAVIOUR.md, Agent panel): an answer or a failure finishes it, and a stop drops it,
    since it did not finish.
    """
    event = row.get("event")
    if event == STEP:
        question["steps"].append({"running": row.get("running"), "done": row.get("done"),
                                  "finished": False})
    elif event == STEP_DONE:
        _finish_last(question)
    elif event in (ANSWER, FAILURE):
        _finish_last(question)
        question["outcome"] = {"kind": event, "text": row.get("text")}
    elif event == STOPPED:
        question["steps"] = [step for step in question["steps"] if step["finished"]]
        question["outcome"] = {"kind": STOPPED}


def _finish_last(question):
    if question["steps"]:
        question["steps"][-1]["finished"] = True


class DriveChatRecord:
    def __init__(self, storage):
        self._storage = storage
        self._lock = threading.Lock()

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def chats(self, project):
        return _fold(_rows(self._storage.read_lines(project, FILE)))

    def add_chat(self, project, chat_id):
        self._add(project, chat_id, OPENED)

    def add_question(self, project, chat_id, text, at):
        self._add(project, chat_id, QUESTION, text=text, at=at)

    def add_step(self, project, chat_id, running, done):
        self._add(project, chat_id, STEP, running=running, done=done)

    def finish_step(self, project, chat_id):
        self._add(project, chat_id, STEP_DONE)

    def answer(self, project, chat_id, text):
        self._add(project, chat_id, ANSWER, text=text)

    def fail(self, project, chat_id, text):
        self._add(project, chat_id, FAILURE, text=text)

    def stop(self, project, chat_id):
        self._add(project, chat_id, STOPPED)

    def _add(self, project, chat_id, event, **fields):
        line = json.dumps({"chat": chat_id, "event": event, **fields}, ensure_ascii=False)
        with self._lock:
            # The folder is the project, and writing would make it: an agent still at work when its
            # project was renamed or deleted must not bring the old folder back as a project.
            if not self._storage.dir_exists(project):
                raise ProjectMissing(f"Proje yok: {project}")
            self._storage.append_line(project, FILE, line)
