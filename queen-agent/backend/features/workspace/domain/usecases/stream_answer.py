"""Answer a chat, reaching for tools as the model asks.

The generator yields what the turn does as it does it -- its rounds, steps, files and questions --
and finally the updated Chat. Telling them apart by type is simpler than carrying a separate "this
one is the last" flag. The words are not among them since Madde 440: every request goes through the
black box (black_box.py), the answer comes back whole, and the screen reads it off the record.
"""
from dataclasses import dataclass

from backend.features.workspace.domain.black_box import ask
from backend.features.workspace.domain.chat import ToolCall, Usage, active_messages, sent_messages
from backend.features.workspace.domain.context_box import BOX_LIMIT, files_opened
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.modes import EDIT, ends_the_turn, needs_permission
from backend.features.workspace.domain.permission import PermissionWanted, Waiting, refusal_text
from backend.features.workspace.domain.prompt import (
    FILES_HELD,
    LAST_ROUND,
    NO_FILES_YET,
    OPENED_FILES,
)
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


@dataclass(frozen=True)
class Progress:
    """Where the turn has got to, said while it is still going (Madde 194).

    It lives here rather than beside FileStarted or PermissionWanted because a piece belongs next to
    whatever gives birth to it, and what gives birth to this is the turn itself.

    `round` shadows the builtin in the generated __init__ and nowhere else, and that body never
    calls it. What is bought is one word: the field, the frame's key and what the screen reads all
    say the same thing.
    """

    round: int
    of: int
    tokens: int


def _volume(spent):
    """How big the turn got -- everything that crossed the wire, cache included.

    Not the bill: cached tokens are charged less, and the stamp at the end is where price is
    answered. This number answers the question the fourth trial raised -- 277.6k for a twenty-one
    frame fix -- and only sent would have hidden half of it.
    """
    return spent.sent + spent.cached + spent.answered


def _conversation(chat):
    """Every message, and nothing else.

    The skill's instruction used to be dropped in here, in front of the turn it governed. Since
    Madde 93 it does not travel inside the conversation at all -- it rides at the end of the
    request, and `_asked` is what puts it there.

    The open line since Madde 195: a version is answered with the conversation the user is standing
    in, not the one they took back. From its trim on since Madde 345: a trimmed chat's oldest turns
    stay on screen and are not sent.
    """
    return [{"role": message.role, "content": message.text} for message in sent_messages(chat)]


def _current_skill(chat):
    """Which skill governs the turn being answered: the newest user message's.

    Walked from the end rather than read off the last message, for the same reason last_sent is: a
    record does not always end with the question that is waiting for an answer -- and since Madde
    195 that end is the open line's.
    """
    for message in reversed(active_messages(chat)):
        if message.role == "user":
            return message.skill
    return ""


def _named(names):
    """What the project holds, in one line for the model (Madde 127).

    Two sentences rather than one with an empty tail, and both of them are prompt.py's (Madde 189).
    """
    if not names:
        return NO_FILES_YET
    return FILES_HELD + ", ".join(names)


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
    if not blocks:
        return ""
    return OPENED_FILES.format(limit=BOX_LIMIT) + "\n\n".join(blocks)


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
    out of thirty-two. The order is extended rather than broken.
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


class _Noting:
    """The project's files as the turn's tools reach them, noting whether any of them wrote.

    Asked at the one door every write goes through rather than of each tool's answer: a dozen tools
    write -- a new file, an edit, an entry added to a scenario -- and an outcome like "Already there"
    wrote nothing. What the turn needs is only whether it did (Madde 440, Madde 38): a turn that
    wrote a file and then says nothing is finished.
    """

    def __init__(self, files):
        self._files = files
        self.wrote = False

    def list_names(self, project_id):
        return self._files.list_names(project_id)

    def read(self, project_id, name):
        return self._files.read(project_id, name)

    def write(self, project_id, name, content):
        self.wrote = True
        return self._files.write(project_id, name, content)


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
    # What the black box gave back after five failed tries, or None (Madde 440). The turn ends on it
    # and nothing goes back to the model.
    failure = None
    # Whether a tool of this turn has written to the project yet.
    writes = _Noting(file_store)

    try:
        for index in range(MAX_ROUNDS):
            # The round the turn ends on, whatever it has or has not finished. It is told so and it
            # is handed no tools, because a round that looks like every other one gets answered like
            # every other one -- with a call whose result no round is left to read, and a turn that
            # never spoke (Madde 137).
            last = index == MAX_ROUNDS - 1
            # Before the round rather than after it (Madde 194): the number the screen shows first
            # is the one that moves first, and a round announced only once it has ended would leave
            # the strip a whole request behind the turn.
            yield Progress(index + 1, MAX_ROUNDS, _volume(spent))
            answer = ask(
                engine,
                # Both are read here rather than before the loop: a round that wrote a file changes
                # the answer, and the next round has to hear the new one. `made` carries this
                # turn's steps, which reach the record only when it is written.
                _asked(
                    conversation,
                    file_store.list_names(project_id),
                    _boxed(file_store, project_id, chat, made),
                    instruction,
                    last,
                ),
                # Every tool, in every mode. Since Madde 99 the mode is not what the request carries
                # -- it is which of them run out of it without a question. The closing round is the
                # one exception, and it is not about the mode: nothing it asked for could come back,
                # so it is offered nothing to ask with.
                tools=None if last else TOOL_SPECS,
                # Only the transport holds a socket, so only it can hand out a way to cut one.
                on_open=lambda cut: stops.hold(project_id, chat_id, cut),
                # A connection that died because we cut it is a stop; the same words from a
                # network that dropped are a fault. Nothing in the failure says which, so the
                # registry is asked before the black box tries again.
                stopped=lambda: stops.wanted(project_id, chat_id),
                # A turn that has written a file -- a new one or one it changed -- and then says
                # nothing is finished, not empty: what it did is the answer (Madde 38; the user, 9
                # October). Before any write, silence is tried again.
                silence_is_an_answer=writes.wrote,
            )

            # Rounds add: each round is its own call and its own bill, and that growth is the thing
            # this number exists to show. A round the stop threw away never brought its figure.
            if answer.usage:
                spent = Usage(
                    spent.sent + answer.usage.sent,
                    spent.cached + answer.usage.cached,
                    spent.answered + answer.usage.answered,
                )
                yield Progress(index + 1, MAX_ROUNDS, _volume(spent))

            # The registry is the one thing that knows a stop. It catches both: the request the stop
            # cut, which the black box gave back empty without trying again, and the round that came
            # back whole with the press landing just as it did -- whose calls do not run.
            if stops.wanted(project_id, chat_id):
                cut_short = True
                break
            if answer.failed:
                failure = answer
                break

            said.append(answer.text)
            # Reaching the end of what the model asked for is an end, the same way the round limit
            # is.
            if not answer.calls:
                break

            calls = list(answer.calls)
            conversation.append({"role": "assistant", "content": answer.text, "tool_calls": calls})
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
                result = run_tool(writes, project_id, tool, call["function"]["arguments"])
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
    except Exception as broken:
        # The black box answers for the model, so what reaches here is the turn's own code -- a
        # tool, the disk. The half answer is not kept: an answer either exists or does not.
        raise EngineFailed(str(broken)) from broken
    finally:
        # However this ended. Left standing, the flag would cut the next answer as it was born, and
        # a decision nobody spent would settle the next question before it was asked.
        stops.clear(project_id, chat_id)
        permissions.clear(project_id, chat_id)

    # Everything said across the rounds becomes one message: the user read one answer. A stopped
    # turn keeps no words (Madde 440, the user: "atılsın") -- none of it was on screen yet, and none
    # of it was checked -- but it is still written, empty: a press that leaves no trace reads as a
    # press that did nothing, and the chat's last word would otherwise still be the user's, which
    # means owed an answer, which means asked for again on the next reload. A failed turn's words
    # are the failure's own, so the card can say them. The steps and the files stay either way:
    # they happened.
    if failure:
        text = failure.text
    elif cut_short:
        text = ""
    else:
        text = "".join(said)
    yield append_message(
        chat_store,
        project_id,
        chat_id,
        text,
        now,
        role="ai",
        files=born,
        calls=made,
        stopped=cut_short,
        usage=spent,
        failed=failure.failed if failure else "",
        wrote=writes.wrote,
    )
