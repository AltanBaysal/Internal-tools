"""What a chat has opened, remembered by name (Madde 129).

A read's result used to freeze where it was written: the file moved on and the message did not, so
the model read it again -- three times in one trial, each copy riding every later request. What
travels now is the name; the contents are read from disk when the request is built, so there is one
entry per file and it cannot go stale.

Derived rather than stored. A chat's record already says which tool touched which file (Madde 66
and 78), so nothing new is written to disk and no older chat needs converting. Only the tools whose
result carries meaning are remembered -- reads. A write answers in one sentence, and one sentence
needs no box.

Files, and only files, since Madde 172. The structure schema used to ride here beside them, watched
by a function of its own, and it left with the tool that fetched it: a file is the one thing in this
app whose contents can change under a message that has already gone out, which is the whole reason
this module exists. A chat that fetched the schema before then still carries the step in its record,
and the reading walks past that name rather than tripping on it.

Nothing here touches the disk: this module answers which names, and the caller answers what is in
them. That is what lets it be tested without a store.
"""
BOX_LIMIT = 5
"""How many files a chat keeps in front of the model.

A limit rather than everything, so a long chat's box does not grow with it. The oldest falls out
first: what has been out of sight longest is what the turn is least likely to be working on.
"""

# What a read answers with when the file is not there (tools.py). A call that missed is still a
# step the turn took, so the record keeps it -- but there is nothing to put in front of the model,
# and a heading with nothing under it reads as an empty file.
_MISSED = "No file by that name"


def _steps_newest_first(chat, steps):
    """Every step this chat has taken, the most recent first.

    This turn's steps lead: they are not in the record yet -- `made` reaches it only when the
    answer is written -- and the next round is inside the same turn.
    """
    yield from reversed(list(steps))
    for message in reversed(chat.messages):
        yield from reversed(list(message.calls))


def files_opened(chat, steps=()):
    """The files this chat has read, newest first, at most BOX_LIMIT of them."""
    opened = []
    for call in _steps_newest_first(chat, steps):
        if call.tool != "read_file" or not call.target or call.outcome == _MISSED:
            continue
        if call.target in opened:
            continue  # the same file read twice is one entry, kept where it was newest
        opened.append(call.target)
        if len(opened) == BOX_LIMIT:
            break
    return opened


