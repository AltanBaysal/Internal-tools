"""Stream an answer: the pieces go out as they arrive, the record is written only at the end.

The generator yields text pieces and finally the updated Chat. Telling them apart by type is
simpler than carrying a separate "this one is the last" flag.
"""
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.usecases.append_message import append_message


def stream_answer(chat_store, engine, project_id, chat_id, now):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)

    pieces = []
    try:
        for piece in engine.stream(
            [{"role": message.role, "content": message.text} for message in chat.messages]
        ):
            pieces.append(piece)
            yield piece
    except Exception as failure:
        # Half an answer is never kept: the design's line is that an answer either exists or does
        # not, and Faz 8's files cannot be born of an unfinished thought.
        raise EngineFailed(str(failure)) from failure

    yield append_message(chat_store, project_id, chat_id, "".join(pieces), now, role="ai")
