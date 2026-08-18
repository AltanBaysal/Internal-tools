"""Change which model a chat answers with. Works mid-conversation."""
from dataclasses import replace

from backend.features.workspace.domain.errors import ChatNotFound


def set_chat_model(chat_store, project_id, chat_id, model):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    # Only the next answer changes. What was already said was said by whoever said it, and nothing
    # in this app rewrites a message.
    changed = replace(chat, model=model)
    chat_store.replace(project_id, changed)
    return changed
