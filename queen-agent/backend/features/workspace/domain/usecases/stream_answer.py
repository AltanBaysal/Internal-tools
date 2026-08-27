"""Stream an answer, reaching for tools as the model asks.

The generator yields text pieces and finally the updated Chat. Telling them apart by type is
simpler than carrying a separate "this one is the last" flag.
"""
from backend.features.workspace.domain.chat import ToolCall, Usage
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.modes import EDIT, ends_the_turn, tools_for
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.domain.tools import (
    MAX_ROUNDS,
    WRITES_FILES,
    FileStarted,
    FileWritten,
    run_tool,
)
from backend.features.workspace.domain.usecases.append_message import append_message


def _conversation(chat):
    """Every message, and nothing else.

    The skill's instruction used to be dropped in here, in front of the turn it governed. Since
    Madde 93 it does not travel inside the conversation at all -- it rides at the end of the
    request, and `_asked` is what puts it there.
    """
    return [{"role": message.role, "content": message.text} for message in chat.messages]


def _current_skill(chat):
    """Which skill governs the turn being answered: the newest user message's.

    Walked from the end rather than read off the last message, for the same reason last_sent is: a
    record does not always end with the question that is waiting for an answer.
    """
    for message in reversed(chat.messages):
        if message.role == "user":
            return message.skill
    return ""


def _asked(conversation, instruction):
    """The request as it goes out: the conversation, and the instruction behind all of it.

    Two measures put it there. Attention: accuracy is highest at the two ends of a context and
    falls by more than a third in the middle. Cache: what is fixed leads so the prefix holds, and
    what changes trails so only it goes stale.

    Built fresh on every round rather than once, because `conversation` grows -- each round appends
    what the model said and what the tools answered. An instruction placed inside it once would sit
    behind those from the second round on, and the reason this exists would stop holding after the
    first one.
    """
    if not instruction:
        return conversation
    return conversation + [{"role": "system", "content": instruction}]


def stream_answer(chat_store, file_store, engine, project_id, chat_id, now, stops, mode=EDIT):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)

    # Local to this answer and never written to the chat: what the model was told and what the tools
    # answered back is bookkeeping. What the turn *did* is not -- that is `made`, and it reaches the
    # record.
    conversation = _conversation(chat)
    # Read once: which skill governs the turn being answered is settled before the first round, and
    # no round changes it.
    instruction = instruction_for(_current_skill(chat))
    said = []
    born = []
    made = []
    spent = Usage()
    cut_short = False
    # The turn reached its own end -- today that is plan mode, where the plan is on disk and the
    # next move is the user's. Kept apart from cut_short: a stopped turn is written down as
    # stopped, and this one simply finished.
    done = False

    try:
        for _ in range(MAX_ROUNDS):
            spoken, calls = [], []
            # This round's bill so far. None until the engine says anything about it, so an engine
            # that measures nothing leaves the total alone rather than adding zeroes to it.
            round_spent = None
            try:
                for piece in engine.stream(
                    _asked(conversation, instruction),
                    tools=tools_for(mode),
                    # Only the transport holds a socket, so only it can hand out a way to cut one.
                    on_open=lambda cut: stops.hold(project_id, chat_id, cut),
                ):
                    if "text" in piece:
                        spoken.append(piece["text"])
                        said.append(piece["text"])
                        yield piece["text"]
                    elif "usage" in piece:
                        # Replaced rather than added. Today the engine says this once, as the
                        # stream closes, so the rule idles -- but a figure is a total for the call
                        # rather than a share since the last, and an engine that reported as it
                        # went would have its bill multiplied by the number of pieces if these
                        # were summed.
                        round_spent = piece["usage"]
                    else:
                        calls.extend(piece["tool_calls"])
            except Exception:
                # A connection that died because we cut it is a stop; the same words from a network
                # that dropped are a fault. Nothing in the failure says which, so the record is
                # asked before it is believed.
                if not stops.wanted(project_id, chat_id):
                    raise
                cut_short = True

            # After the round however it ended, because a round that was cut short still sent its
            # whole conversation and was still charged for it. The window is narrow -- the engine
            # reports as the stream closes, so a cut answer usually never hears the figure at all
            # -- but what did arrive was really spent, and dropping it here would throw it away.
            # Rounds add where pieces replaced: each round is its own call and its own bill, and
            # that growth is the thing this number exists to show.
            if round_spent:
                spent = Usage(
                    spent.sent + round_spent["sent"],
                    spent.cached + round_spent["cached"],
                    spent.answered + round_spent["answered"],
                )

            # Asked once, at the end, rather than before every frame: since Madde 90 a stop cuts
            # the connection, so a round that was stopped is over by the time this runs. What this
            # catches is the round that ended quietly with the press landing just as it did.
            if not cut_short and stops.wanted(project_id, chat_id):
                cut_short = True

            # Reaching a stop is an end, not a failure -- the same way the round limit is.
            if cut_short or not calls:
                break

            conversation.append(
                {"role": "assistant", "content": "".join(spoken), "tool_calls": calls}
            )
            for call in calls:
                tool = call["function"]["name"]
                # The dashed card goes up before the tool runs: the name is not settled until it
                # has, and the design's card carries no name anyway.
                if tool in WRITES_FILES:
                    yield FileStarted()
                result = run_tool(file_store, project_id, tool, call["function"]["arguments"])
                # A name born twice in one turn is still one file: the card says a file exists, not
                # how many times it was written.
                if result.created and result.created not in born:
                    born.append(result.created)
                    yield FileWritten(result.created)
                # After the tool has run, because the target is not settled until then -- the same
                # reason the filled card waits. Behind the card rather than in front of it, so the
                # filled card stays next to the dashed one it replaces. A repeat is kept: reading
                # one file twice is two steps, and folding one away would misreport the turn.
                step = ToolCall(tool, result.target, result.outcome)
                made.append(step)
                yield step
                conversation.append(
                    {"role": "tool", "tool_call_id": call["id"], "content": result.text}
                )
                if ends_the_turn(mode, tool):
                    done = True
                    break
            if done:
                break
    except Exception as failure:
        # Half an answer that nobody asked to end is never kept: the design's line is that an answer
        # either exists or does not, and a file cannot be born of an unfinished thought. A stop is
        # the other case -- somebody decided, and what they had read is theirs.
        raise EngineFailed(str(failure)) from failure
    finally:
        # However this ended. Left standing, the flag would cut the next answer as it was born.
        stops.clear(project_id, chat_id)

    # Everything said across the rounds becomes one message: the user read one answer. A stop that
    # landed before the first word writes one too, empty -- a press that leaves no trace reads as a
    # press that did nothing, and the chat's last word would otherwise still be the user's, which
    # means owed an answer, which means asked for again on the next reload.
    yield append_message(
        chat_store,
        project_id,
        chat_id,
        "".join(said),
        now,
        role="ai",
        files=born,
        calls=made,
        stopped=cut_short,
        usage=spent,
    )
