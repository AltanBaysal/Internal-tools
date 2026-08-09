"""Answer a chat as it stands. The user's words are already on disk before this runs."""
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.usecases.append_message import append_message


def answer_in_chat(chat_store, engine, project_id, chat_id, now):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)
    try:
        answer = engine.complete(
            [{"role": message.role, "content": message.text} for message in chat.messages]
        )
    except Exception as failure:
        # Deliberately broad: every way the engine can break must be reported without the chat
        # losing anything. Narrowing it would let an unfamiliar fault pass as success.
        raise EngineFailed(str(failure)) from failure
    return append_message(chat_store, project_id, chat_id, answer["content"], now, role="ai")
