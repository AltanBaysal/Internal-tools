"""Write a message into a chat, making the chat if there is not one yet.

Madde 87 folded start_chat in here. Both jobs were the same three steps -- check the text, write the
message, hand the record back -- and splitting them meant the caller had to know which one it was
doing. An empty chat_id means there is no chat yet; a chat_id that names nothing is an error, not an
invitation to make one, or a typo would quietly become a second chat.

project_store and new_id sit at the end with defaults because only the making branch needs them:
stream_answer writes an answer into a chat that is already there and says nothing about either.
"""
from dataclasses import replace

from backend.features.workspace.domain.chat import (
    Chat,
    Message,
    Usage,
    Version,
    chat_title,
    with_open_line,
)
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
    calls=(),
    stopped=False,
    usage=Usage(),
    failed="",
    wrote=False,
    project_store=None,
    new_id="",
    branch_at=None,
    line_id="",
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
    # A message has to carry something -- a word said, a file made, a file written, or a stop. The
    # user's own message never carries a file or those flags, so an empty one they typed is still
    # refused. The second and third are the answer of a model that worked without speaking, and
    # what it did is the answer -- `wrote` is a file it changed rather than made (Madde 440, the
    # user's 9 October rule), said by the turn and not stored: its steps already show it. The last
    # is an answer somebody cut before it said anything, and the cut is what happened. Calls on
    # their own are deliberately not on this list: looking at files and saying nothing is not an
    # answer.
    #
    # Asked before anything is written, so a refused first sentence leaves no empty chat behind.
    if not trimmed and not files and not stopped and not wrote:
        raise EmptyMessage()
    message = Message(
        role=role,
        at=now,
        text=trimmed,
        files=tuple(files),
        skill=skill,
        calls=tuple(calls),
        stopped=stopped,
        usage=usage,
        failed=failed,
    )
    if making:
        # The title belongs to the message that started the chat and never moves -- an edit later
        # opens a version, and the chat is still named after the sentence that started it.
        made = Chat(id=new_id, title=chat_title(trimmed), created_at=now, messages=(message,))
        chat_store.add(project_id, made)
        return made
    if branch_at is not None:
        # Madde 195. The message is the first of a new line rather than the last of the open one,
        # and the line it splits from is whichever one the user is standing on -- not the first,
        # which they may have walked away from several edits ago.
        opened = Version(id=line_id, parent=chat.active, at=branch_at, messages=(message,))
        updated = replace(chat, versions=chat.versions + (opened,), active=line_id)
    else:
        # On the end of the open line: an answer belongs to the question that asked for it, and
        # appending to the first line would leave the open one waiting for ever.
        updated = with_open_line(chat, lambda own: own + (message,))
    chat_store.replace(project_id, updated)
    return updated
