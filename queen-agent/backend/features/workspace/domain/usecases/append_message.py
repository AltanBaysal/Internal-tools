"""Append a message to an existing chat."""
from dataclasses import replace

from backend.features.workspace.domain.chat import Message, Usage
from backend.features.workspace.domain.errors import ChatNotFound, EmptyMessage


def append_message(
    chat_store,
    project_id,
    chat_id,
    text,
    now,
    role="user",
    files=(),
    skill="",
    calls=(),
    stopped=False,
    usage=Usage(),
):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    trimmed = text.strip()
    # A message has to carry something -- a word said or a file made. The user's own message never
    # carries a file, so an empty one is still refused; what this allows is the answer of a model
    # that worked without speaking, and what it made is the answer. Calls are deliberately not on
    # this list: looking at files and saying nothing is not an answer.
    if not trimmed and not files:
        raise EmptyMessage()
    # The title belongs to the message that started the chat and never moves.
    message = Message(
        role=role,
        at=now,
        text=trimmed,
        files=tuple(files),
        skill=skill,
        calls=tuple(calls),
        stopped=stopped,
        usage=usage,
    )
    updated = replace(chat, messages=chat.messages + (message,))
    chat_store.replace(project_id, updated)
    return updated
