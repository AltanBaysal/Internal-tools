"""Stream an answer, reaching for tools as the model asks.

The generator yields text pieces and finally the updated Chat. Telling them apart by type is
simpler than carrying a separate "this one is the last" flag.
"""
from backend.features.workspace.domain.chat import ToolCall, Usage
from backend.features.workspace.domain.context_box import files_opened, schema_was_read
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.modes import EDIT, ends_the_turn, needs_permission
from backend.features.workspace.domain.permission import PermissionWanted, Waiting, refusal_text
from backend.features.workspace.domain.prompt import LAST_ROUND
from backend.features.workspace.domain.schema import SCHEMA
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.domain.tools import (
    MAX_ROUNDS,
    TOOL_SPECS,
    WRITES_FILES,
    FileStarted,
    FileWritten,
    numbered,
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


def _named(names):
    """What the project holds, in one line for the model (Madde 127).

    Counting to zero does not say "there are none": the two are different sentences, and a model
    reading an empty list would go looking for the tool that used to answer this.
    """
    if not names:
        return "This project holds no files yet."
    return "The project's files right now: " + ", ".join(names)


def _boxed(file_store, project_id, chat, steps):
    """What this chat has opened, with the contents it has on disk right now (Madde 129).

    Read here rather than remembered from when the tool ran: that is the whole of it -- a copy
    would go stale the moment the file was written to, and staleness is what sent the model back
    to read the same file three times.

    A name whose file is gone is skipped without a word: the box holds names, and a heading with
    nothing under it reads as an empty file. Nothing at all means no box -- an empty heading is a
    line the model has to read before finding out it is empty.
    """
    blocks = []
    for name in files_opened(chat, steps):
        content = file_store.read(project_id, name)
        if content is None:
            continue
        # Numbered here as well as in the tool's own answer (Madde 131). Since the box arrived the
        # model looks at a file here rather than reading it twice, so a bare copy here would be the
        # one it actually reads -- and two shapes of one file would leave it choosing which of them
        # its anchor has to match.
        blocks.append(f"--- {name} ---\n{numbered(content)}")
    if schema_was_read(chat, steps):
        # Not numbered: the column is for picking an anchor, and no anchor is ever written into the
        # schema. It is one text for the whole app rather than a file on disk.
        blocks.append(f"--- prompt structure schema ---\n{SCHEMA}")
    if not blocks:
        return ""
    return (
        "Files you have opened in this chat, with their contents as they are now:\n\n"
        + "\n\n".join(blocks)
    )


def _asked(conversation, names, box, instruction, last=False):
    """The request as it goes out: the conversation, then what the project holds, then the
    instruction behind all of it, and on the final round the notice that closes the turn.

    Two measures put the instruction at the end. Attention: accuracy is highest at the two ends of
    a context and falls by more than a third in the middle. Cache: what is fixed leads so the
    prefix holds, and what changes trails so only it goes stale.

    The names and the opened files ride between the two. Behind the conversation because a file
    born or changed in this turn has to be seen by the next round; in front of the instruction
    because Madde 93 gave it the last word.

    Built fresh on every round rather than once, because `conversation` grows -- each round appends
    what the model said and what the tools answered. An instruction placed inside it once would sit
    behind those from the second round on, and the reason this exists would stop holding after the
    first one.

    The closing notice goes behind the instruction, by the same measure that put the instruction
    last. Madde 93's rule is that what is fixed leads and what changes trails: the instruction is
    settled before the first round and holds for the whole turn, while this shows up in one round
    out of sixteen. The order is extended rather than broken.
    """
    asked = conversation + [{"role": "system", "content": _named(names)}]
    if box:
        asked = asked + [{"role": "system", "content": box}]
    # Each piece its own condition and one return at the end. An early exit on a missing
    # instruction used to stand here, and the notice could never have got past it -- a chat with no
    # skill selected is the ordinary case rather than the exception.
    if instruction:
        asked = asked + [{"role": "system", "content": instruction}]
    if last:
        asked = asked + [{"role": "system", "content": LAST_ROUND}]
    return asked


HEARTBEAT_SECONDS = 15
"""How often a paused turn writes something.

Not a timeout: the wait itself has no end. Nothing is holding the other side of the model's
connection -- the tool call arrives with the round's last frame and that request is closed by the
time the gate opens -- and the service documents no limit of its own. What this number says is how
often the browser hears from us while nothing happens: a stream gone quiet inside a tunnel is a
stream a tunnel may close, and a browser that went away is only discovered by writing to it.
Comfortably under the idle window proxies usually keep, and not measured against any one of them.
"""


def _waited_on(permissions, stops, project_id, chat_id, call):
    """Hold the turn until the user decides, or until somebody stops it.

    A generator, because the beat has to leave down the same connection the answer is arriving on.
    What it hands back is the decision, or None when the wait ended without one.

    The stop is handed a way to wake this wait rather than a way to cut a socket: the model's
    request closed with the round, so there is nothing left to cut, and without this the stop
    button would do nothing for as long as the question stood. `hold` carries the other half -- a
    press that landed before we got here runs the moment it is given.
    """
    yield PermissionWanted(call["function"]["name"], call["function"]["arguments"])
    stops.hold(project_id, chat_id, lambda: permissions.wake(project_id, chat_id))
    while True:
        decision = permissions.wait(project_id, chat_id, HEARTBEAT_SECONDS)
        if decision is not None:
            return decision
        if stops.wanted(project_id, chat_id):
            return None
        yield Waiting()


def stream_answer(
    chat_store, file_store, engine, project_id, chat_id, now, stops, permissions, mode=EDIT
):
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
        for index in range(MAX_ROUNDS):
            # The round the turn ends on, whatever it has or has not finished. It is told so and it
            # is handed no tools, because a round that looks like every other one gets answered like
            # every other one -- with a call whose result no round is left to read, and a turn that
            # never spoke (Madde 137).
            last = index == MAX_ROUNDS - 1
            spoken, calls = [], []
            # This round's bill so far. None until the engine says anything about it, so an engine
            # that measures nothing leaves the total alone rather than adding zeroes to it.
            round_spent = None
            try:
                for piece in engine.stream(
                    # Both are read here rather than before the loop: a round that wrote a file
                    # changes the answer, and the next round has to hear the new one. `made`
                    # carries this turn's steps, which reach the record only when it is written.
                    _asked(
                        conversation,
                        file_store.list_names(project_id),
                        _boxed(file_store, project_id, chat, made),
                        instruction,
                        last,
                    ),
                    # Every tool, in every mode. Since Madde 99 the mode is not what the request
                    # carries -- it is which of them run out of it without a question. The closing
                    # round is the one exception, and it is not about the mode: nothing it asked for
                    # could come back, so it is offered nothing to ask with.
                    tools=None if last else TOOL_SPECS,
                    # Only the transport holds a socket, so only it can hand out a way to cut one.
                    on_open=lambda cut: stops.hold(project_id, chat_id, cut),
                    # The chat is the conversation: its id is the name the service's cache files
                    # this turn's prefix under (Madde 124).
                    conversation_id=chat_id,
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
                    # Replaced rather than added (Madde 133). The three above are a bill and add up;
                    # this one is a measurement of one request, and each round's is bigger than the
                    # last because the conversation grew. The final reading is where it ended.
                    round_spent["sent"],
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
                if needs_permission(mode, tool):
                    decision = yield from _waited_on(permissions, stops, project_id, chat_id, call)
                    if decision is None:
                        # The wait ended with nobody deciding, which leaves one reason: a stop.
                        cut_short = True
                        break
                    if not decision.allowed:
                        # The card goes up all the same -- what the turn did is what the chat
                        # shows, and being refused is something it did. No file name: nothing was
                        # touched.
                        step = ToolCall(tool, "", "Not allowed")
                        made.append(step)
                        yield step
                        conversation.append(
                            {
                                "role": "tool",
                                "tool_call_id": call["id"],
                                "content": refusal_text(tool, decision.reason),
                            }
                        )
                        continue
                    # What the rest of this turn runs in. The next call is not asked about again,
                    # and a plan written from here on is an ordinary write -- the user said yes to
                    # working, and ending the turn there would take that back.
                    mode = EDIT
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
            # cut_short as well as done: a stop landing inside the tool loop is asked about only at
            # the top of the next round, so without this the turn would send one more request
            # before noticing.
            if done or cut_short:
                break
    except Exception as failure:
        # Half an answer that nobody asked to end is never kept: the design's line is that an answer
        # either exists or does not, and a file cannot be born of an unfinished thought. A stop is
        # the other case -- somebody decided, and what they had read is theirs.
        raise EngineFailed(str(failure)) from failure
    finally:
        # However this ended. Left standing, the flag would cut the next answer as it was born, and
        # a decision nobody spent would settle the next question before it was asked.
        stops.clear(project_id, chat_id)
        permissions.clear(project_id, chat_id)

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
