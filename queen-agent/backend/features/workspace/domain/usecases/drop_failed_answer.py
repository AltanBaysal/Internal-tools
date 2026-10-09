"""Take a failed answer out of the record, so that its question is owed again (Madde 440).

What Try again on a failed answer's card asks for: the answer goes, and the question is answered
again by the turn that follows. Anything else at the end of the open line is left as it is.

The whole message goes, its own steps and files with it: the chat no longer shows that turn's step
cards or file cards. The files themselves stay on disk and in the rail -- only the record of the
failed turn is taken out.
"""
from dataclasses import replace

from backend.features.workspace.domain.chat import active_messages, with_open_line


def drop_failed_answer(chat_store, project_id, chat):
    said = active_messages(chat)
    if not said or not said[-1].failed:
        return chat
    failed = said[-1]

    def without(own):
        # A line's own messages begin with its question, so the failed answer is never alone here.
        kept = own[:-1]
        # Continue here marks the line's last message, which can be this one. The trim outlives it:
        # the mark moves to the question in front of it, still on the same line.
        if failed.trimmed:
            kept = kept[:-1] + (replace(kept[-1], trimmed=failed.trimmed),)
        return kept

    dropped = with_open_line(chat, without)
    chat_store.replace(project_id, dropped)
    return dropped
