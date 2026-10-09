"""Trim a full chat from the start -- what Continue here asks for (Madde 345).

The oldest turns stop going to the model and stop counting against the ceiling. Nothing leaves the
record, so the screen keeps every message. It asks no confirmation and cannot be undone: the owner
kept the designer's recommendation (29 September).
"""
from dataclasses import replace

from backend.features.workspace.domain.chat import (
    active_messages,
    is_full,
    trim_point,
    with_open_line,
)
from backend.features.workspace.domain.errors import ChatNotFound, ChatNotFull


def trim_chat(chat_store, project_id, chat_id):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    # Continue here is offered only on a full chat (the owner's decision, 28 September).
    if not is_full(chat):
        raise ChatNotFull(chat_id)
    # Written on the open line's last message -- the answer that filled it -- rather than on the
    # chat, so each line keeps its own trim (chat.py, Message.trimmed).
    marked = replace(active_messages(chat)[-1], trimmed=trim_point(chat))
    chat_store.replace(project_id, with_open_line(chat, lambda own: own[:-1] + (marked,)))
