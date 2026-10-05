"""ChatRecord over DriveStorage -- the only place that knows the chat file's name and its lines.

Every chat of a project lives in one file inside the project's own folder (madde 417): a renamed
project carries its chats and a deleted one takes them, and the list, a chat opened and a new chat
each read one file -- a file per chat would have the list open every one of them over Drive.

The file is only ever added to, the photo record's rule: a session that dies mid-write loses at most
the line it was adding, where rewriting a chat could lose all of it. Each line is one event about
one chat, and reading folds them in the order they were written. Nothing is held in memory, so a
restart loses nothing.
"""
import json

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
    """Steps and outcomes belong to the question being worked on, which is the chat's latest."""
    event = row.get("event")
    if event == STEP:
        question["steps"].append({"running": row.get("running"), "done": row.get("done"),
                                  "finished": False})
    elif event == STEP_DONE and question["steps"]:
        question["steps"][-1]["finished"] = True
    elif event in (ANSWER, FAILURE):
        question["outcome"] = {"kind": event, "text": row.get("text")}
    elif event == STOPPED:
        question["outcome"] = {"kind": STOPPED}


class DriveChatRecord:
    def __init__(self, storage):
        self._storage = storage

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
        self._storage.append_line(project, FILE, line)
