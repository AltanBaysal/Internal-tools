"""What a paused turn is made of: the question, the beat, and the answer.

Its own module rather than a corner of tools.py: none of this is a tool's own work. The gate opens
in front of a tool, and a tool never learns it was gated.
"""
from dataclasses import dataclass

from backend.features.workspace.domain.prompt import REFUSED, REFUSED_WORDS


@dataclass(frozen=True)
class Decision:
    """The user's answer. A refusal may carry their own words; an approval has nothing to add."""

    allowed: bool
    reason: str = ""


@dataclass(frozen=True)
class PermissionWanted:
    """The turn is asking, and cannot go on until it is answered.

    Arguments travel raw. run_tool is the one place that reads them, and a second reader here would
    drift from it on the first change to either.
    """

    tool: str
    arguments: str


@dataclass(frozen=True)
class Waiting:
    """A beat while the turn waits.

    Neither of its two jobs is about permission: it keeps a tunnel from closing a stream that has
    gone quiet, and it is the only thing that notices a browser which went away -- a write to a
    connection nobody is reading is how the turn learns to end.
    """


def refusal_text(tool, reason):
    """The refusal filled in: which tool, and the user's own words when they wrote any.

    The sentence itself is prompt.REFUSED (Madde 189) -- it says the same thing on every refusal
    and is a rule the model is told, not a report of what this call did.
    """
    said = REFUSED_WORDS.format(reason=reason.strip()) if reason and reason.strip() else ""
    return REFUSED.format(tool=tool, said=said)
