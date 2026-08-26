"""Start a chat -- a chat is born with its first message; there is no empty chat."""
from backend.features.workspace.domain.chat import Chat, Message, chat_title
from backend.features.workspace.domain.errors import EmptyMessage, ProjectNotFound


def start_chat(chat_store, project_store, project_id, text, new_id, now, skill=""):
    if project_store.get(project_id) is None:
        raise ProjectNotFound(project_id)
    trimmed = text.strip()
    if not trimmed:
        raise EmptyMessage()
    chat = Chat(
        id=new_id,
        title=chat_title(trimmed),
        created_at=now,
        messages=(Message(role="user", at=now, text=trimmed, skill=skill),),
        skill=skill,
    )
    chat_store.add(project_id, chat)
    return chat
