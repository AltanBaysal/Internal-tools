"""Append a message to an existing chat."""
from dataclasses import replace

from backend.features.workspace.domain.chat import Message
from backend.features.workspace.domain.errors import ChatNotFound, EmptyMessage


def append_message(chat_store, project_id, chat_id, text, now, role="user", files=()):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    trimmed = text.strip()
    if not trimmed:
        raise EmptyMessage()
    # The title belongs to the message that started the chat and never moves.
    message = Message(role=role, at=now, text=trimmed, files=tuple(files))
    updated = replace(chat, messages=chat.messages + (message,))
    chat_store.replace(project_id, updated)
    return updated
