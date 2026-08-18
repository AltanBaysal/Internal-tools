"""Chat and Message -- what was said in one conversation."""
from dataclasses import dataclass

TITLE_LIMIT = 42


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


@dataclass(frozen=True)
class Chat:
    id: str
    title: str
    created_at: str
    messages: tuple = ()
    # Which model answers here. Empty means the chat never picked one, and the app's default speaks
    # for it -- so a chat that made no choice keeps following the setting when the setting moves,
    # and the records written before this field existed need no migration.
    model: str = ""
    # The skill selected right now. Empty is the ordinary state -- unlike a model, a chat may have
    # no skill at all, and pressing the selected one again puts it back here.
    skill: str = ""

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
