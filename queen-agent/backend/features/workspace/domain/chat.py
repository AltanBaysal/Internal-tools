"""Chat and Message -- what was said in one conversation."""
from dataclasses import dataclass

TITLE_LIMIT = 42


@dataclass(frozen=True)
class ToolCall:
    """One step a turn took: which tool, and the file it was about.

    One type for two jobs -- it is yielded while the answer streams and it is what the message
    keeps. Two types would be the same fact under two names, and they would drift.

    The result is deliberately absent. What a read returned is the file itself, and that is already
    on disk; copying it here would leave the same text in two places for one of them to go stale.
    The outcome below is not that: it is a sentence about what happened, which is nowhere else.
    """

    tool: str
    # Empty when the call was about nothing in particular -- listing a directory has no file.
    target: str = ""
    # A few words on how the call went -- "45 lines", "Saved", "No file by that name". Written by
    # the tool, because the tool is what knows. Empty on calls recorded before this existed.
    outcome: str = ""


@dataclass(frozen=True)
class Usage:
    """What one answer spent, in tokens.

    Three numbers rather than four: what was paid for a second time is `sent - cached`, and a field
    that restates something already on disk is a field that goes stale on its own.

    Zero everywhere means nobody measured -- an answer from before this existed, or an engine that
    said nothing about it. That is deliberately the same as spending nothing, because both draw
    nothing and neither is worth a second way of saying "unknown".
    """

    # Everything the request carried: the whole conversation, every instruction, every tool result.
    sent: int = 0
    # The part of `sent` the service already had. A subset of it, never an addition -- so this can
    # never be larger than `sent`, and the difference is what was paid for again.
    cached: int = 0
    answered: int = 0
    # What the turn's *last* round sent, which is where the conversation stood when it ended. The
    # three above answer what this answer cost; this one answers how big the request had grown, and
    # only it can tell a chat when to stop -- a turn of six rounds spends six requests' worth, and
    # that sum is not the size of any of them (Madde 133).
    context: int = 0


@dataclass(frozen=True)
class Message:
    role: str  # "user" or "ai"
    at: str  # ISO 8601; the browser is what turns it into 11:04
    text: str
    # The files this reply produced. The design draws a card under the answer, so the message has
    # to remember them; a reload must find the card still there.
    files: tuple = ()
    # Which skill governed this turn. Kept on the message rather than only on the chat so the record
    # stays honest: changing the selection later must not make an older turn look as though the new
    # skill produced it.
    skill: str = ""
    # The steps this turn took before it spoke. Kept for the same reason the files are: the chat is
    # read again later, and a step that only existed while the answer streamed leaves that reader
    # exactly as blind as before.
    calls: tuple = ()
    # Whether the user cut this answer short. Half a sentence with no mark cannot be told from a
    # model that finished on one, and the chat is read again later by someone who was not there.
    stopped: bool = False
    # What this answer cost. On the message rather than summed on the chat, because the question it
    # answers is which turn was expensive -- and a chat's total can be added up from these, while a
    # total cannot be taken apart.
    usage: Usage = Usage()


@dataclass(frozen=True)
class Chat:
    id: str
    title: str
    created_at: str
    messages: tuple = ()

    @property
    def last_activity(self):
        return self.messages[-1].at if self.messages else self.created_at


def chat_title(text):
    """A chat is named after the message that started it."""
    trimmed = text.strip()
    if len(trimmed) <= TITLE_LIMIT:
        return trimmed
    # Only a message that actually lost something is marked as cut.
    return trimmed[:TITLE_LIMIT] + "…"


def is_owed_an_answer(chat):
    """Whether the last thing said in this chat was the user's.

    This lived in the browser until Madde 88, where it could run without anybody asking -- on a
    reload, and on a connection coming back. Here it can only be reached by a request.
    """
    return bool(chat.messages) and chat.messages[-1].role == "user"


CONTEXT_CEILING = 50_000
"""How much one chat may send before it stops taking new turns.

Not a capacity limit -- the window is 256k, so this is a fifth of it. It is a quality one: models
get worse as the input grows and what sits in the middle of a long request goes unread, so fitting
is not the same as being read. Above 200k the input also costs twice as much.
"""


def last_context(chat):
    """How big the conversation had grown when the last answer finished, or 0 if none has.

    The last round's size rather than the turn's total. Those were the same reader until Madde 133,
    and the trial that separated them closed a chat at 51.4k whose request had never passed 12k --
    six rounds of ten thousand is not a request of sixty. What the turn cost is still on the
    message, and the card still draws it; this is the other question.

    A turn's size is only known once its answer comes back, so this is one turn stale on purpose --
    a request is stopped by the size of the one before it. Walked from the end rather than read off
    the last message: a question whose answer never came can be sitting there, and a question has
    no number of its own.
    """
    for message in reversed(chat.messages):
        if message.role == "ai":
            return message.usage.context
    return 0


def is_full(chat):
    """Whether this chat has reached the ceiling and may not take another turn."""
    return last_context(chat) >= CONTEXT_CEILING
