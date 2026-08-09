"""Delete a chat. The files it produced stay: a file belongs to the project, not to a chat."""
from backend.features.workspace.domain.errors import ChatNotFound


def delete_chat(chat_store, project_id, chat_id):
    if chat_store.get(project_id, chat_id) is None:
        raise ChatNotFound(chat_id)
    chat_store.delete(project_id, chat_id)
