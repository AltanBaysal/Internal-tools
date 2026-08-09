"""A message sent from home opens both a project and a chat."""
from backend.features.workspace.domain.chat import chat_title
from backend.features.workspace.domain.errors import EmptyMessage
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.edit_project import edit_project
from backend.features.workspace.domain.usecases.start_chat import start_chat


def start_chat_in_new_project(project_store, chat_store, text, new_project_id, new_chat_id, now):
    trimmed = text.strip()
    # Checked before anything is written: an empty message must not leave a stray project behind.
    if not trimmed:
        raise EmptyMessage()
    # Composed rather than copied: the defaults a new project is born with have one home, and the
    # name is then set from the message with the same rule that names the chat.
    create_project(project_store, new_id=new_project_id, now=now)
    project = edit_project(project_store, new_project_id, name=chat_title(trimmed))
    chat = start_chat(
        chat_store, project_store, new_project_id, trimmed, new_id=new_chat_id, now=now
    )
    return project, chat
