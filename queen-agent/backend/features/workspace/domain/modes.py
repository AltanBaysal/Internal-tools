"""What a mode lets through without asking.

What the model may do used to be a sentence inside a skill's text -- "do not create a file" -- and
a sentence is a request. The verify skill is the proof of what that is worth: it says it fixes
nothing, and then it fixes things. So the rule became the tool list, and a tool that was not in the
request could not be called.

Since Madde 99 the list is still the rule, one step later. Every tool goes into the request; this
is which of them run without stopping to ask. The authority did not weaken -- the model still
cannot write on its own -- and what changed is that a user in the wrong mode now gets a question
instead of silence.
"""
from backend.features.workspace.domain.tools import TOOL_SPECS

PLAN = "plan"
ASK = "ask"
EDIT = "edit"
DEFAULT = EDIT

# read_schema joined them in Madde 96: it opens no file and changes nothing, so no mode has a
# reason to stop for it.
READS = ("list_files", "read_file", "read_schema")

_WITHOUT_ASKING = {
    ASK: READS,
    # Reading, and one way to write -- a plan. Given create_file without a question it could write
    # the plan and the deliverable in the same turn, which is doing the work instead of planning it.
    PLAN: READS + ("write_plan",),
    # Everything, which is the mode's whole meaning: here the app does what it can do and stops for
    # nothing. write_plan is among them since Madde 97 -- in this mode a plan is an ordinary file,
    # which is why the flow can write one to keep its place and carry on in the same turn.
    EDIT: READS
    + ("create_file", "edit_file", "build_prompts", "build_character_prompts", "write_plan"),
}

_KNOWN = {spec["function"]["name"] for spec in TOOL_SPECS}


def needs_permission(mode, tool):
    """Whether this call has to be asked about before it runs.

    A tool nobody knows is never asked about. It will not run whatever the answer is, and asking
    would put a name this app does not have in front of the user for them to approve.

    A mode nobody knows is the default one, for the reason the old tool list had: an older browser,
    or a body with no mode in it at all, would otherwise start raising questions nobody expected.
    """
    if tool not in _KNOWN:
        return False
    return tool not in _WITHOUT_ASKING.get(mode, _WITHOUT_ASKING[DEFAULT])


def ends_the_turn(mode, tool):
    """Whether this call is where the turn stops.

    One pair rather than a count: the rule is not "write once", it is "the plan is written, so the
    next move is the user's". The same tool in another mode is an ordinary write.
    """
    return mode == PLAN and tool == "write_plan"
