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

# One since Madde 172: the schema reader left with the shape it taught, and reading a file is the
# only thing left that opens nothing and changes nothing.
READS = ("read_file",)

_WITHOUT_ASKING = {
    ASK: READS,
    # Reading, and one way to write -- a plan. Given create_file without a question it could write
    # the plan and the deliverable in the same turn, which is doing the work instead of planning it.
    PLAN: READS + ("write_plan",),
    # Everything, which is the mode's whole meaning: here the app does what it can do and stops for
    # nothing. write_plan is among them since Madde 97 -- in this mode a plan is an ordinary file,
    # which is why the flow can write one to keep its place and carry on in the same turn.
    EDIT: READS
    + (
        "create_file",
        "start_scenario",
        # Madde 168. A rename is the widest edit any tool here makes -- the map entry and every
        # frame naming it, in one call -- so the quieter modes keep their gate in front of all three.
        "add_character",
        "update_character",
        "remove_character",
        # Madde 169. Same reason, second map.
        "add_outfit",
        "update_outfit",
        "remove_outfit",
        # Madde 170, third map.
        "add_location",
        "update_location",
        "remove_location",
        "edit_file",
        "build_prompts",
        "build_character_prompts",
        "write_plan",
        # Madde 128. It gives no position, but it changes the user's file, so ask and plan keep
        # their gate in front of it while this mode keeps none.
        "add_frames",
    ),
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
