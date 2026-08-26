"""Stream an answer, reaching for tools as the model asks.

The generator yields text pieces and finally the updated Chat. Telling them apart by type is
simpler than carrying a separate "this one is the last" flag.
"""
from backend.features.workspace.domain.chat import ToolCall, Usage
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.domain.tools import (
    MAX_ROUNDS,
    TOOL_SPECS,
    WRITES_FILES,
    FileStarted,
    FileWritten,
    run_tool,
)
from backend.features.workspace.domain.usecases.append_message import append_message


def _conversation(chat):
    """Every message, with a skill's instruction dropped in front of the turn it governs.

    Once, not on every request: the instruction is a piece of the conversation rather than a header
    on it. Only the user's messages are watched -- an answer carries no skill, and letting one count
    would make the instruction reappear on every single turn.
    """
    active = ""
    built = []
    for message in chat.messages:
        if message.role == "user" and message.skill != active:
            active = message.skill
            # A rule fades the further back it sits, so a skill taken up again is stated again.
            instruction = instruction_for(active)
            if instruction:
                built.append({"role": "system", "content": instruction})
        built.append({"role": message.role, "content": message.text})
    return built


def stream_answer(chat_store, file_store, engine, project_id, chat_id, now, stops):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)

    # Local to this answer and never written to the chat: what the model was told and what the tools
    # answered back is bookkeeping. What the turn *did* is not -- that is `made`, and it reaches the
    # record.
    conversation = _conversation(chat)
    said = []
    born = []
    made = []
    spent = Usage()
    cut_short = False

    try:
        for _ in range(MAX_ROUNDS):
            spoken, calls = [], []
            # This round's bill so far. None until the engine says anything about it, so an engine
            # that measures nothing leaves the total alone rather than adding zeroes to it.
            round_spent = None
            for piece in engine.stream(conversation, tools=TOOL_SPECS):
                # Asked before the piece rather than after it: what the user pressed stop on is
                # everything they had already read, and nothing past it.
                if stops.wanted(project_id, chat_id):
                    cut_short = True
                    break
                if "text" in piece:
                    spoken.append(piece["text"])
                    said.append(piece["text"])
                    yield piece["text"]
                elif "usage" in piece:
                    # Replaced rather than added. Today the engine says this once, as the stream
                    # closes, so the rule idles -- but a figure is a total for the call rather than
                    # a share since the last, and an engine that reported as it went would have its
                    # bill multiplied by the number of pieces if these were summed.
                    round_spent = piece["usage"]
                else:
                    calls.extend(piece["tool_calls"])

            # Before the stop is acted on, because a round that was cut short still sent its whole
            # conversation and was still charged for it. The window is narrow -- the engine reports
            # as the stream closes, so a cut answer usually never hears the figure at all -- but
            # what did arrive was really spent, and dropping it here would throw it away.
            # Rounds add where pieces replaced: each round is its own call and its own bill, and
            # that growth is the thing this number exists to show.
            if round_spent:
                spent = Usage(
                    spent.sent + round_spent["sent"],
                    spent.cached + round_spent["cached"],
                    spent.answered + round_spent["answered"],
                )

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
