"""Change what a chat answers with: its model, its skill, or one without the other.

Both work mid-conversation. Only the next answer changes -- what was already said was said by
whoever said it, and nothing in this app rewrites a message.
"""
from dataclasses import replace

from backend.features.workspace.domain.errors import ChatNotFound

# Absent rather than empty: an empty string is a real choice (no skill / back to the default model),
# so "not given" needs a value of its own.
UNCHANGED = object()


def set_chat_choices(chat_store, project_id, chat_id, model=UNCHANGED, skill=UNCHANGED):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    changes = {}
    if model is not UNCHANGED:
        changes["model"] = model
    if skill is not UNCHANGED:
        changes["skill"] = skill
    changed = replace(chat, **changes)
    chat_store.replace(project_id, changed)
    return changed
