"""Which tools each mode puts in the request.

What the model may do used to be a sentence inside a skill's text -- "do not create a file" -- and
a sentence is a request. The verify skill is the proof of what that is worth: it says it fixes
nothing, and then it fixes things. Here the rule is the tool list, and a tool that is not in the
request cannot be called.
"""
from backend.features.workspace.domain.tools import TOOL_SPECS

PLAN = "plan"
ASK = "ask"
EDIT = "edit"
DEFAULT = EDIT

# read_schema joined them in Madde 96: it opens no file and changes nothing, so no mode has a
# reason to withhold it.
READS = ("list_files", "read_file", "read_schema")

_OFFERED = {
    ASK: READS,
    # Reading, and one way to write -- a plan. Given create_file it could write the plan and the
    # deliverable in the same turn, which is doing the work instead of planning it.
    PLAN: READS + ("write_plan",),
    # write_plan is here too since Madde 97: in this mode a plan is an ordinary file, which is
    # exactly why the tool belongs -- the flow writes one to keep its place and carries on in the
    # same turn.
    EDIT: READS
    + ("create_file", "edit_file", "build_prompts", "build_character_prompts", "write_plan"),
}


def tools_for(mode):
    """The specs this mode offers the model. A mode nobody knows is the default one.

    Not an empty list for an unknown mode: an older browser, or a body with no mode in it at all,
    would lose its tools silently -- and a model with no tools looks exactly like a model that
    decided not to use them.
    """
    allowed = _OFFERED.get(mode, _OFFERED[DEFAULT])
    return [spec for spec in TOOL_SPECS if spec["function"]["name"] in allowed]


def ends_the_turn(mode, tool):
    """Whether this call is where the turn stops.

    One pair rather than a count: the rule is not "write once", it is "the plan is written, so the
    next move is the user's". The same tool in another mode is an ordinary write.
    """
    return mode == PLAN and tool == "write_plan"
