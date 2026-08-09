"""Give a chat a new title. What was said in it is not touched."""
from dataclasses import replace

from backend.features.workspace.domain.errors import ChatNotFound, InvalidChatTitle


def rename_chat(chat_store, project_id, chat_id, title):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    cleaned = (title or "").strip()
    if not cleaned:
        raise InvalidChatTitle(chat_id)
    renamed = replace(chat, title=cleaned)
    chat_store.replace(project_id, renamed)
    return renamed
