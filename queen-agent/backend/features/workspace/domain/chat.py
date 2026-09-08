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
    # Which model answered this turn (Madde 146). Beside skill and for the very same reason, and it
    # is what makes comparing two of them possible at all: a turn keeps the choice it was sent
    # with, so a later selection cannot rewrite who said what. The chat's own root carries none --
    # Madde 82 took that one out and it stays out; these two share a name and nothing else.
    model: str = ""
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
class Version:
    """One line the conversation took, and where it left the line before it (Madde 195).

    `at` is how many of the parent's messages this one keeps, so the line it draws is
    parent[:at] + messages. The kept part is not copied here on purpose: written twice, one of the
    two copies is the one that goes stale, and the whole point of a version is that the past it
    grew out of is the same past.
    """

    id: str
    # The line it grew out of. Empty is the chat's first line -- the one Chat.messages holds.
    parent: str = ""
    at: int = 0
    messages: tuple = ()


@dataclass(frozen=True)
class Chat:
    id: str
    title: str
    created_at: str
    messages: tuple = ()
    # Every line after the first (Madde 195), in the order they were opened -- which is the order
    # the arrows step through.
    versions: tuple = ()
    # Which line is open. Empty is the first one, so a chat that never branched is what it always
    # was and no field has to be filled to say so.
    active: str = ""

    @property
    def last_activity(self):
        said = active_messages(self)
        return said[-1].at if said else self.created_at


def chat_title(text):
    """A chat is named after the message that started it."""
    trimmed = text.strip()
    if len(trimmed) <= TITLE_LIMIT:
        return trimmed
    # Only a message that actually lost something is marked as cut.
    return trimmed[:TITLE_LIMIT] + "…"


def active_messages(chat):
    """The conversation as it stands: the open line, walked back to the first one.

    Everything that reads a chat reads this rather than `messages` (Madde 195). A line nobody is
    standing on is not sent to the model any more, so it does not decide whether an answer is owed,
    it does not fill the chat, and it is not what the screen draws.
    """
    return _line(chat, chat.active)


def _line(chat, name):
    if not name:
        return chat.messages
    for version in chat.versions:
        if version.id == name:
            return _line(chat, version.parent)[: version.at] + version.messages
    # A name nobody wrote. A chat on disk can be edited by hand -- the store reads it field by field
    # for the same reason -- and the first line is the one that always exists.
    return chat.messages


def variants_of(chat):
    """For each message of the open line, the versions standing where it stands.

    The base is the line whose own message fills that place: if the line carrying it split exactly
    there, the base is its parent; otherwise it is that line itself. The options are the base first,
    because its message was there first, then the versions that split there in the order they were
    opened. Nothing else decides which way the arrows point.
    """
    said = active_messages(chat)
    standing = _chain(chat, chat.active)
    return [_variants_at(chat, standing, index) for index in range(len(said))]


def _chain(chat, name):
    """The open line and everything it grew out of, first line first."""
    if not name:
        return [None]
    for version in chat.versions:
        if version.id == name:
            return _chain(chat, version.parent) + [version]
    return [None]


def _variants_at(chat, standing, index):
    # Which line of the open chain owns this place: the last one that starts at or before it.
    owner = None
    for line in standing:
        if line is None or line.at <= index:
            owner = line
    base = owner.parent if owner is not None and owner.at == index else _name(owner)
    options = [base] + [
        version.id
        for version in chat.versions
        if version.parent == base and version.at == index
    ]
    return {"index": options.index(_name(owner)), "of": len(options), "versions": options}


def _name(line):
    return "" if line is None else line.id


def is_owed_an_answer(chat):
    """Whether the last thing said in this chat was the user's.

    This lived in the browser until Madde 88, where it could run without anybody asking -- on a
    reload, and on a connection coming back. Here it can only be reached by a request.
    """
    said = active_messages(chat)
    return bool(said) and said[-1].role == "user"


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

    The open line since Madde 195: a turn the user walked away from is not sent any more, and what
    is not sent cannot fill the chat.
    """
    for message in reversed(active_messages(chat)):
        if message.role == "ai":
            return message.usage.context
    return 0


def is_full(chat):
    """Whether this chat has reached the ceiling and may not take another turn."""
    return last_context(chat) >= CONTEXT_CEILING
