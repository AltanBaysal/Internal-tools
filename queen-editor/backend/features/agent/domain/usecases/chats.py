"""The agent's chats at the door: a new chat, the list, one chat opened (madde 417); a question
asked, the agent stopped, and which chats' agents are working (madde 420).

The messages are user-facing Turkish; presentation forwards them untouched. ProjectMissing is this
feature's own, since a feature never imports another, and says what the projects feature says.
"""


class ProjectMissing(Exception):
    """No such project folder (message is the user-facing text)."""


class ChatMissing(Exception):
    """No chat under that id in the project (message is the user-facing text)."""


class EmptyQuestion(Exception):
    """The question has no words in it (message is the user-facing text)."""


class AgentBusy(Exception):
    """The chat's agent is still working on its last question (message is the user-facing text)."""


def _require(record, project):
    # Asked before anything is written: every folder under the root is a project, and a write into
    # an unknown name would make one.
    if not record.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")


def new_chat(record, project):
    """The empty chat waiting in the project, or a new one -- never a second empty chat
    (BEHAVIOUR.md, Agent panel).

    A new chat takes the highest number plus one, and since nothing is deleted no number comes back.
    Two requests at once can both take it: their two lines then fold into one empty chat, which is
    exactly the answer the rule asks for.
    """
    _require(record, project)
    chats = record.chats(project)
    for chat in chats:
        if not chat["questions"]:
            return chat
    chat_id = max((chat["id"] for chat in chats), default=0) + 1
    record.add_chat(project, chat_id)
    return {"id": chat_id, "questions": []}


def list_chats(record, project):
    """The chats with a question, the newest last question first; each with its first question
    whole -- cutting it to one line is the screen's -- and when the last one was asked."""
    _require(record, project)
    rows = [{"id": chat["id"], "firstQuestion": chat["questions"][0]["text"],
             "lastAskedAt": chat["questions"][-1]["askedAt"]}
            for chat in record.chats(project) if chat["questions"]]
    # The times are ISO text in one shape, so their order as text is their order in time.
    return sorted(rows, key=lambda row: row["lastAskedAt"], reverse=True)


def open_chat(record, project, chat_id):
    _require(record, project)
    for chat in record.chats(project):
        if chat["id"] == chat_id:
            return chat
    raise ChatMissing(f"Sohbet yok: {chat_id}")


def ask_question(record, runner, agent, now, project, chat_id, text):
    """Write the question and start the agent on it; the chat comes back as it stands.

    The agent goes on in the background (runner.py), so this returns at once. It is handed the chat's
    questions so far, read before this one is written. The text is kept as it was sent; one with no
    words in it is refused -- the screen's button is off then, and the rule is the server's.
    """
    earlier = open_chat(record, project, chat_id)["questions"]
    if not isinstance(text, str) or not text.strip():
        raise EmptyQuestion("Soru boş.")
    if not runner.start(project, chat_id, text, now(),
                        lambda run: agent(run, project, earlier, text)):
        raise AgentBusy("Bu sohbette agent hâlâ çalışıyor.")
    return open_chat(record, project, chat_id)


def stop_agent(record, runner, project, chat_id):
    """Stop the chat's agent if it works; the chat comes back as it stands."""
    open_chat(record, project, chat_id)
    runner.stop(project, chat_id)
    return open_chat(record, project, chat_id)


def working_chats(record, runner, project):
    """The ids of the project's chats whose agent works now: the list's live dot and the open chat's
    ■ read this, since it lives in the process and not in the record."""
    _require(record, project)
    return runner.working(project)
