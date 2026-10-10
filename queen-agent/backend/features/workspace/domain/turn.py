"""A turn while it runs, and the status a chat is in (Madde 461).

The chat's status is the server's to say, in one place: running and waiting live only in memory,
while a turn runs; the rest is read off the open line's last message, so a chat file needs no field
of its own and an old one reads as it is.

The snapshot is what a running turn shows of itself: an immutable value, replaced whole on every
change and numbered by that change, so whoever is watching can tell whether anything moved since it
last looked. The steps and files in it never touch the disk -- the record keeps its own copy once the
turn has written its answer.
"""
from dataclasses import dataclass, replace

from backend.features.workspace.domain.chat import ToolCall, active_messages
from backend.features.workspace.domain.permission import PermissionWanted
from backend.features.workspace.domain.tools import FileStarted, FileWritten

RUNNING = "running"
WAITING = "waiting"
ANSWERED = "answered"
STOPPED = "stopped"
FAILED = "failed"
UNANSWERED = "unanswered"
IDLE = "idle"


@dataclass(frozen=True)
class Progress:
    """Where the turn has got to, said while it is still going (Madde 194).

    Here rather than beside FileStarted or PermissionWanted because a piece belongs next to whatever
    gives birth to it, and what gives birth to this is the turn itself.

    `round` shadows the builtin in the generated __init__ and nowhere else, and that body never
    calls it. What is bought is one word: the field, the frame's key and what the screen reads all
    say the same thing.
    """

    round: int
    of: int
    tokens: int


@dataclass(frozen=True)
class Question:
    """The permission a turn is waiting on. `wait` names this question among the turn's others."""

    wait: int
    tool: str
    arguments: str


@dataclass(frozen=True)
class Snapshot:
    """A running turn as it stands. `version` counts its changes; nothing else orders them."""

    id: str
    version: int = 0
    progress: Progress | None = None
    # A file the turn is writing this moment: between the dashed card and its filled one.
    creating: bool = False
    files: tuple = ()
    calls: tuple = ()
    permission: Question | None = None
    ended: bool = False
    # The turn's own fault, when its code broke rather than the model failing: nothing was written.
    error: str = ""


def changed(snapshot, **fields):
    """The snapshot with these fields replaced, one version on."""
    return replace(snapshot, version=snapshot.version + 1, **fields)


def applied(snapshot, piece):
    """The snapshot once this piece of the turn has happened.

    A question is named by the version that asks it: unique inside its turn and only ever growing,
    so an answer meant for an earlier question cannot settle a later one.
    """
    if isinstance(piece, Progress):
        return changed(snapshot, progress=piece)
    if isinstance(piece, FileStarted):
        return changed(snapshot, creating=True)
    if isinstance(piece, FileWritten):
        return changed(snapshot, files=snapshot.files + (piece.name,), creating=False)
    if isinstance(piece, ToolCall):
        # The step closes a write that made no new file -- an edit -- as the file closes one that did.
        return changed(snapshot, calls=snapshot.calls + (piece,), creating=False)
    if isinstance(piece, PermissionWanted):
        asked = Question(snapshot.version + 1, piece.tool, piece.arguments)
        return changed(snapshot, permission=asked)
    raise TypeError(f"not a piece of a turn: {piece!r}")


def status_of(chat, live):
    """Which of the seven states this chat is in. `live` is its turn's snapshot, or None.

    A turn that has ended leaves the answer to the record: by then it has written what it wrote.
    """
    if live is not None and not live.ended:
        return WAITING if live.permission else RUNNING
    said = active_messages(chat)
    if not said:
        return IDLE
    last = said[-1]
    if last.role == "user":
        return UNANSWERED
    if last.failed:
        return FAILED
    if last.stopped:
        return STOPPED
    return ANSWERED
