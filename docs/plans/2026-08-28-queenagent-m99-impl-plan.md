# Madde 99 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-28-queenagent-m99-izin-uygulama-design.md](../specs/2026-08-28-queenagent-m99-izin-uygulama-design.md)
**Tur 1:** otuz beş kırmızı commit'lendi *(`27abf7f`)*. Bu turda test yazılmaz.
**Komut:** `python -m pytest queen-agent -q`

---

## 1 · `domain/permission.py` — yeni dosya

```python
"""What a paused turn is made of: the question, the beat, and the answer.

Its own module rather than a corner of tools.py: none of this is a tool's own work. The gate opens
in front of a tool, and a tool never learns it was gated.
"""
from dataclasses import dataclass


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
    """What the model is told when the user says no.

    A wall with nothing written on it is a wall the model walks into again, so three things are
    said: what was refused, that the mode is where the refusal came from, and -- when the user
    wrote one -- their own words.
    """
    said = f' They said: "{reason.strip()}"' if reason and reason.strip() else ""
    return (
        f"The user did not allow {tool}. The mode has not changed, so this tool is still out of "
        f"reach: carry on without writing.{said}"
    )
```

## 2 · `domain/modes.py` — baştan

```python
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
    # Everything, which is the mode's whole meaning: here the app does what it can do, and stops
    # for nothing.
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
```

## 3 · `domain/ports.py` — beşinci port

`Stops`'un altına, ve dosyanın başına `from backend.features.workspace.domain.permission import Decision`:

```python
class Permissions(Protocol):
    """The answer a paused turn is waiting for. Held in memory, exactly like a stop.

    What has to survive a restart is the message, and it does. A question lives as long as the turn
    that asked it: if the process dies the turn dies with it, and there is nothing left to answer.
    """

    def answer(self, project_id: str, chat_id: str, allowed: bool, reason: str) -> None:
        """Leave the user's decision. Wakes the turn if one is waiting, and keeps if not."""

    def wait(self, project_id: str, chat_id: str, tick: float) -> Decision | None:
        """Block until the decision arrives or `tick` seconds pass, and spend what is found.

        None means nothing was decided -- the tick ran out, or somebody woke the wait. Spending is
        what keeps a second question in the same turn a question.
        """

    def wake(self, project_id: str, chat_id: str) -> None:
        """End the wait without a decision. What a stop reaches for: there is no socket to cut
        while a turn is paused here."""

    def clear(self, project_id: str, chat_id: str) -> None:
        """Forget the question and the answer. Left standing, an answer would settle the next
        turn's question before anybody was asked."""
```

## 4 · `data/memory_permissions.py` — yeni dosya

```python
"""MemoryPermissions -- the answer a paused turn is waiting for, for as long as it waits.

Sibling of MemoryStops and deliberately the same shape: in memory rather than on disk, keyed by
chat, reached by two threads at once -- the one streaming the answer and the one carrying the
decision. Hence the lock.

On disk it would outlive its turn and settle the next one's question without anybody being asked.
"""
import threading

from backend.features.workspace.domain.permission import Decision


class MemoryPermissions:
    def __init__(self):
        self._decided = {}
        # One event per chat, so a decision wakes exactly the turn it belongs to.
        self._events = {}
        self._lock = threading.Lock()

    def answer(self, project_id, chat_id, allowed, reason):
        # Which of the two comes first is nobody's to arrange: an answer can be left before the
        # question is asked, and that is not a mistake -- it is the race hold() carries too.
        with self._lock:
            self._decided[(project_id, chat_id)] = Decision(bool(allowed), reason or "")
            event = self._events.get((project_id, chat_id))
        # Outside the lock, like the cut a stop hands out: waking is somebody else's code.
        if event:
            event.set()

    def wait(self, project_id, chat_id, tick):
        event = self._event_for(project_id, chat_id)
        # Looked at before waiting as well as after: the answer may already be here, and a wait
        # that only looked afterwards would sit out a whole tick with the decision in its hand.
        decision = self._spend(project_id, chat_id)
        if decision is not None:
            return decision
        event.wait(tick)
        return self._spend(project_id, chat_id)

    def wake(self, project_id, chat_id):
        with self._lock:
            event = self._events.get((project_id, chat_id))
        if event:
            event.set()

    def clear(self, project_id, chat_id):
        # Every turn clears on its way out, asked or not -- the same as a stop does.
        with self._lock:
            self._decided.pop((project_id, chat_id), None)
            self._events.pop((project_id, chat_id), None)

    def _event_for(self, project_id, chat_id):
        with self._lock:
            event = self._events.get((project_id, chat_id))
            if event is None:
                event = threading.Event()
                self._events[(project_id, chat_id)] = event
            return event

    def _spend(self, project_id, chat_id):
        """Take the decision rather than read it, and leave the event ready for the next question.

        A turn may ask twice, and the second question is a question -- not something the first
        answer already settled.
        """
        with self._lock:
            decision = self._decided.pop((project_id, chat_id), None)
            event = self._events.get((project_id, chat_id))
            if event:
                event.clear()
        return decision
```

## 5 · `domain/usecases/stream_answer.py`

### 5a · Importlar

```python
from backend.features.workspace.domain.chat import ToolCall, Usage
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.modes import EDIT, ends_the_turn, needs_permission
from backend.features.workspace.domain.permission import PermissionWanted, Waiting, refusal_text
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.domain.tools import (
    MAX_ROUNDS,
    TOOL_SPECS,
    WRITES_FILES,
    FileStarted,
    FileWritten,
    run_tool,
)
```

`tools_for` importu gidiyor.

### 5b · Sabit ve alt üretici

`_asked`'in altına:

```python
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
    button would do nothing for as long as the question stood. `hold` carries the other half --
    a press that landed before we got here runs the moment it is given.
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
```

### 5c · İmza ve gövde

```python
def stream_answer(
    chat_store, file_store, engine, project_id, chat_id, now, stops, permissions, mode=EDIT
):
```

`engine.stream` çağrısındaki `tools=tools_for(mode)` → `tools=TOOL_SPECS`, ve yorumu:

```python
                for piece in engine.stream(
                    _asked(conversation, instruction),
                    # Every tool, in every mode. Since Madde 99 the mode is not what the request
                    # carries -- it is what runs out of it without a question.
                    tools=TOOL_SPECS,
```

Araç döngüsünün başı:

```python
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
                    # working, and ending the turn would take that back.
                    mode = EDIT
                # The dashed card goes up before the tool runs: the name is not settled until it
                # has, and the design's card carries no name anyway.
                if tool in WRITES_FILES:
                    yield FileStarted()
```

Döngünün sonu — `if done: break` yerine:

```python
            # cut_short as well as done: a stop that landed in the tool loop is asked about only at
            # the top of the next round, so without this the turn would send one more request
            # before noticing.
            if done or cut_short:
                break
```

`finally`:

```python
    finally:
        # However this ended. Left standing, the flag would cut the next answer as it was born, and
        # a decision nobody spent would settle the next question before it was asked.
        stops.clear(project_id, chat_id)
        permissions.clear(project_id, chat_id)
```

## 6 · `presentation/routes.py`

Import: `from backend.features.workspace.domain.permission import PermissionWanted, Waiting`.

Kurucu: `def make_workspace_bp(project_store, chat_store, file_store, engine, stops, permissions):`

`stream_answer` çağrısına `stops`'un ardından `permissions`.

`_sse`'de, `ToolCall` dalının ardına:

```python
            elif isinstance(piece, PermissionWanted):
                yield _frame("permission", {"tool": piece.tool, "arguments": piece.arguments})
            elif isinstance(piece, Waiting):
                # No event line, which is why the browser's parser drops it -- and dropping it is
                # the whole job. This frame exists to be bytes on a connection that has gone quiet.
                yield ": waiting\n\n"
```

Durdurma kapısının ardına:

```python
    @workspace_bp.post("/api/projects/<project_id>/chats/<chat_id>/permission")
    def post_permission(project_id, chat_id):
        # The stop's sibling: its own request on its own connection, because the turn it answers is
        # still streaming down another one.
        if chat_store.get(project_id, chat_id) is None:
            return jsonify({"error": "chat not found"}), 404
        payload = request.get_json(silent=True) or {}
        permissions.answer(
            project_id, chat_id, bool(payload.get("allowed")), payload.get("reason", "")
        )
        # Left, not acted on: what the decision amounts to is seen in the stream it unblocks.
        return jsonify({})
```

## 7 · `main.py`

`from backend.features.workspace.data.memory_permissions import MemoryPermissions`, ve
`MemoryStops(),` satırının ardına `MemoryPermissions(),`.

## 8 · Test kurulumları

`test_stream_answer.py`:

```python
def _run(tmp_path, rounds, stops=NEVER, **kwargs):
    # The same run with nothing to ask. Edit mode is what the app defaults to, and it stops for
    # nothing -- so UNASKED raising is the guard rather than an inconvenience.
    return _gated(tmp_path, rounds, stops=stops, mode="edit", **kwargs)
```

`test_chats_api.py` ve `test_files_api.py`: `from backend.features.workspace.data.memory_permissions import MemoryPermissions`, ve `_client` içinde `MemoryStops(),` satırının ardına `MemoryPermissions(),`.

## 9 · Koş

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: otuz beş kırmızı yeşil. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 10 · Commit

```
feat(queen-agent): the gate moves from the tool list to the moment of running
```
