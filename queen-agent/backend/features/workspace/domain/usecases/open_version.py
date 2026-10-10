"""Open another version of a chat (Madde 195).

Nothing is written to the conversation here -- every version keeps everything it said, and this only
moves which one is being read. Held while it reads and writes (Madde 461): refused while a turn runs.
"""
from dataclasses import replace

from backend.features.workspace.domain.errors import ChatNotFound, VersionNotFound
from backend.features.workspace.domain.usecases.hold_chat import hold_chat


def open_version(chat_store, turns, project_id, chat_id, wanted):
    hold_chat(turns, project_id, chat_id, lambda: _opened(chat_store, project_id, chat_id, wanted))


def _opened(chat_store, project_id, chat_id, wanted):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    # The empty name is the first line and always exists; anything else has to have been opened.
    if wanted and wanted not in [version.id for version in chat.versions]:
        raise VersionNotFound(wanted)
    chat_store.replace(project_id, replace(chat, active=wanted))
