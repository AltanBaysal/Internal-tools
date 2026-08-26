"""Change which skill governs a chat's turns.

Works mid-conversation. Only the next answer changes -- what was already said was said under
whatever governed it then, and nothing in this app rewrites a message.

One field, so no sentinel: telling "not given" from "given empty" mattered while a model was
changed through here too, and an empty skill is a real choice. A call that names one field always
carries it.
"""
from dataclasses import replace

from backend.features.workspace.domain.errors import ChatNotFound


def set_chat_skill(chat_store, project_id, chat_id, skill):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    changed = replace(chat, skill=skill)
    chat_store.replace(project_id, changed)
    return changed
