"""Write a message into a chat, making the chat if there is not one yet.

Madde 87 folded start_chat in here. Both jobs were the same three steps -- check the text, write the
message, hand the record back -- and splitting them meant the caller had to know which one it was
doing. An empty chat_id means there is no chat yet; a chat_id that names nothing is an error, not an
invitation to make one, or a typo would quietly become a second chat.

project_store and new_id sit at the end with defaults because only the making branch needs them:
stream_answer writes an answer into a chat that is already there and says nothing about either.
"""
from dataclasses import replace

from backend.features.workspace.domain.chat import Chat, Message, Usage, chat_title
from backend.features.workspace.domain.errors import ChatNotFound, EmptyMessage, ProjectNotFound


def append_message(
    chat_store,
    project_id,
    chat_id,
    text,
    now,
    role="user",
    files=(),
    skill="",
    model="",
    calls=(),
    stopped=False,
    usage=Usage(),
    project_store=None,
    new_id="",
):
    making = not chat_id
    if making:
        if project_store.get(project_id) is None:
            raise ProjectNotFound(project_id)
    else:
        chat = chat_store.get(project_id, chat_id)
        if chat is None:
            raise ChatNotFound(chat_id)
    trimmed = text.strip()
    # A message has to carry something -- a word said, a file made, or a stop. The user's own
    # message never carries a file or that flag, so an empty one they typed is still refused. The
    # second case is the answer of a model that worked without speaking, and what it made is the
    # answer; the third is an answer somebody cut before it said anything, and the cut is what
    # happened. Calls are deliberately not on this list: looking at files and saying nothing is not
    # an answer.
    #
    # Asked before anything is written, so a refused first sentence leaves no empty chat behind.
    if not trimmed and not files and not stopped:
        raise EmptyMessage()
    message = Message(
        role=role,
        at=now,
        text=trimmed,
        files=tuple(files),
        skill=skill,
        model=model,
        calls=tuple(calls),
        stopped=stopped,
        usage=usage,
    )
    if making:
        # The title belongs to the message that started the chat and never moves.
        made = Chat(id=new_id, title=chat_title(trimmed), created_at=now, messages=(message,))
        chat_store.add(project_id, made)
        return made
    updated = replace(chat, messages=chat.messages + (message,))
    chat_store.replace(project_id, updated)
    return updated
