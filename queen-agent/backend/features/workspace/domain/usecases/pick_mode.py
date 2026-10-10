"""Pick a chat's mode (Madde 463): the chat's own setting, kept where its list is.

The user: "biz sadece modun bilgisini göndermemiz lazım". The browser sends what was picked, and this
is the whole of it -- no chat file is read or written, so a pick costs Drive nothing until the
projects.json writer's next write. A turn running in the chat reads the mode at its next tool call.
"""
from backend.features.workspace.domain.errors import ChatNotFound, UnknownMode
from backend.features.workspace.domain.modes import MODES


def pick_mode(chat_store, project_id, chat_id, mode):
    """The mode as it now stands. A name that is no mode is refused before anything is written."""
    if mode not in MODES:
        raise UnknownMode(mode)
    if not chat_store.set_mode(project_id, chat_id, mode):
        raise ChatNotFound(chat_id)
    return mode
