"""What Try again does, decided by the chat's status (Madde 461; the failed answer's road, Madde 440).

The user's rule: Try again starts the loop only when it has stopped short of an answer. A question
nobody answered is answered; a failed answer is taken out of the record and its question answered
again; an answered, stopped or empty chat has nothing to try again. It never writes the question --
that is on disk already, and writing it again is what put it there twice (Madde 449).

The caller holds the chat for a turn (live_turns.py) before it reads it, so no turn is running here
and the status is the record's. A running turn's Try again is refused before it gets this far.

A failed answer goes whole, its own steps and files with it: the chat no longer shows that turn's
step cards or file cards. The files themselves stay on disk and in the rail.
"""
from dataclasses import replace

from backend.features.workspace.domain.chat import active_messages, with_open_line
from backend.features.workspace.domain.turn import FAILED, UNANSWERED, status_of


def retry_turn(chat_store, project_id, chat):
    """The chat to start a turn on, or None when there is nothing to try again."""
    status = status_of(chat, None)
    if status == UNANSWERED:
        return chat
    if status != FAILED:
        return None
    failed = active_messages(chat)[-1]

    def without(own):
        # A line's own messages begin with its question, so the failed answer is never alone here.
        kept = own[:-1]
        # Continue here marks the line's last message, which can be this one. The trim outlives it:
        # the mark moves to the question in front of it, still on the same line.
        if failed.trimmed:
            kept = kept[:-1] + (replace(kept[-1], trimmed=failed.trimmed),)
        return kept

    # The one write: the turn starts from this record, and nothing else is written before its end.
    dropped = with_open_line(chat, without)
    chat_store.replace(project_id, dropped)
    return dropped
