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

# What opens nothing and changes nothing. Madde 172 left this at one -- the schema reader went with
# the shape it taught -- 187 made it two, and Madde 205 takes that one back out: the ready-piece
# tool was named in no skill text and the library it answered from never reached the model that
# writes a frame, so it was read on every request and used on almost none.
READS = ("read_file",)

_WITHOUT_ASKING = {
    ASK: READS,
    # Reading, and one write -- the plan. Madde 207 took away the tool that used to be named here:
    # what made that call a plan was never the tool, it was this mode. The old fear -- that
    # create_file would let the plan and the deliverable be written in one turn -- is answered by
    # ends_the_turn below, where the first write is where the turn stops.
    PLAN: READS + ("create_file",),
    # Everything, which is the mode's whole meaning: here the app does what it can do and stops for
    # nothing. A plan is an ordinary file here and always was -- which is why the flow can write one
    # to keep its place and carry on in the same turn.
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
        # Madde 128. It gives no position, but it changes the user's file, so ask and plan keep
        # their gate in front of it while this mode keeps none.
        "add_scene",
        # Madde 174. A removal renumbers every frame left standing, which is the widest change any
        # of these makes to a file the user is reading.
        "update_frame",
        "remove_frame",
        # Madde 176. It writes to the file and it spends the user's money at a second provider --
        # the only tool here that does either by asking somebody else.
        "write_frame_prompt",
        # Madde 185. The same, once for every frame still waiting -- so this is the widest single
        # spend any tool here makes, and the quieter modes keep their gate in front of it.
        "write_missing_actions",
        # Madde 198. The narrowest write there is, one character in one line, and still a write to
        # a file the user is reading. Not in PLAN above, and that is not a formality: that mode's
        # job is writing the plan, never closing a step off it.
        "mark_step_done",
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
    next move is the user's". The same call in another mode is an ordinary write.

    Asked of the call rather than of what it returned. A create_file refused for a name already
    taken ends the turn too -- the user reads the refusal and decides what happens next, which is
    where the rule was taking them anyway.
    """
    return mode == PLAN and tool == "create_file"
