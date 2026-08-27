# Madde 99 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m99-izin-testler-design.md](../specs/2026-08-28-queenagent-m99-izin-testler-design.md)
**Tur:** ikiden birincisi — **yalnız testler**. Kod yazılmıyor, kırmızı commit'leniyor.
**Komut:** `python -m pytest queen-agent -q`

---

## Bu turun kuralı: toplama patlamasın

Yeni modüller henüz yok. Bir test dosyasının **başında** olmayan bir modülü import etmek o dosyanın
toplanmasını bozar, ve bozulan dosyanın bütün testleri görünmez olur — turun kırmızıları dahil.
Bu yüzden `permission`, `memory_permissions` ve `needs_permission` **testin içinden** import
ediliyor. `test_modes.py` bunu bugün de yapıyor ve sebebini kendi başlığında yazıyor.

Aynı sebeple **var olan yardımcılar bu turda değişmiyor**. `_run` sekiz argümanla çağırmaya devam
ediyor; yeni testler kendi yardımcısını kullanıyor. Değişselerdi bu iki dosyanın bütün testleri
`TypeError` ile düşerdi ve turun kendi kırmızıları o yığının içinde kaybolurdu.

## Tur 2'nin ayrıca dokunacağı yerler

Bu turda bilerek bırakılıyor, uygulama turunda düzeliyor — sürprize dönüşmesin diye burada yazılı:

- `test_stream_answer.py`'nin `_run`'ı, `_gated`'e devrederek izin kaydını da geçirecek.
- `test_chats_api.py` ve `test_files_api.py`'nin `_client`'ları `make_workspace_bp`'ye altıncı
  argümanı verecek.

---

## 1 · `queen-agent/backend/tests/test_modes.py` — baştan

Dosyanın başlığı yeni soruyu söylüyor. `tools_for`'un üç testi gidiyor: sordukları işlev kalkıyor.
`test_only_a_written_plan_ends_the_turn` **olduğu gibi kalıyor**.

Dosyanın tamamı:

```python
"""What a mode lets through without asking. The rule that used to be a sentence in a skill's text.

The modes are named here the way the wire names them, and the module is imported inside each test
rather than at the top: a module that does not exist yet fails this whole file's collection, and
then none of the turn's other reds are visible anywhere in the suite.
"""
READS = ("list_files", "read_file", "read_schema")
WRITES = ("create_file", "edit_file", "build_prompts", "build_character_prompts", "write_plan")


def _asks(mode, tool):
    from backend.features.workspace.domain.modes import needs_permission

    return needs_permission(mode, tool)


def test_ask_mode_asks_before_it_writes():
    # The item in one line: since Madde 99 the model is offered the tool either way, and the gate
    # is the running of it rather than the list it was handed.
    assert all(_asks("ask", tool) for tool in WRITES)


def test_ask_mode_reads_without_asking():
    # read_schema is among them since Madde 96: it opens no file and changes nothing.
    assert not any(_asks("ask", tool) for tool in READS)


def test_edit_mode_asks_for_nothing():
    # The mode's whole meaning. Asked of every tool there is rather than of a list written here --
    # a ninth tool must join this claim by existing, not by somebody remembering to add it.
    from backend.features.workspace.domain.tools import TOOL_SPECS

    assert not any(_asks("edit", spec["function"]["name"]) for spec in TOOL_SPECS)


def test_plan_mode_writes_a_plan_without_asking_and_asks_for_the_rest():
    # Given create_file it could write the plan and the deliverable in the same turn, which is
    # doing the work instead of planning it.
    assert not _asks("plan", "write_plan")
    assert _asks("plan", "create_file")


def test_a_mode_nobody_knows_is_the_default_one():
    # An older browser, or a body with no mode in it at all. A question nobody expected would stop
    # a turn that used to run.
    assert not _asks("", "create_file")
    assert not _asks("something-else", "create_file")


def test_a_tool_nobody_knows_is_never_asked_about():
    # It will not run whatever the answer is, so asking would put a name this app does not have in
    # front of the user and make them approve it.
    assert not _asks("ask", "delete_everything")


def test_only_a_written_plan_ends_the_turn():
    # The plan reached disk and the next move is the user's. Nothing else stops a turn early -- the
    # same tool in edit mode would be an ordinary write.
    from backend.features.workspace.domain.modes import ends_the_turn

    assert ends_the_turn("plan", "write_plan")
    assert not ends_the_turn("edit", "write_plan")
    assert not ends_the_turn("plan", "read_file")
```

## 2 · `queen-agent/backend/tests/test_permissions.py` — yeni dosya

```python
"""The registry a paused turn reads its answer from.

Its sibling is MemoryStops and the shape is deliberately the same: held in memory, keyed by chat,
reached by two threads at once. The waits here are measured in hundredths of a second -- the tick
is the caller's, and only the app passes fifteen.
"""
import threading
import time

TICK = 0.01


def _registry():
    from backend.features.workspace.data.memory_permissions import MemoryPermissions

    return MemoryPermissions()


def test_an_answer_left_before_the_question_is_picked_up_at_once():
    # The race hold() exists for, on this side of the app: which of the two comes first is nobody's
    # to arrange, and a decision that landed early must not be lost.
    permissions = _registry()
    permissions.answer("p1", "c1", True, "")
    assert permissions.wait("p1", "c1", TICK).allowed


def test_waiting_with_no_answer_comes_back_with_nothing():
    permissions = _registry()
    assert permissions.wait("p1", "c1", TICK) is None


def test_an_answer_wakes_whoever_is_waiting():
    # Read off the clock rather than the value: what is claimed is that the wait ended when the
    # answer arrived, not that it ran out of tick.
    permissions = _registry()
    threading.Timer(TICK, lambda: permissions.answer("p1", "c1", True, "")).start()
    began = time.monotonic()
    decision = permissions.wait("p1", "c1", 5)
    assert decision.allowed
    assert time.monotonic() - began < 1


def test_a_wake_ends_the_wait_without_a_decision():
    # How a stop gets out. There is no socket to cut while a turn waits here -- the xAI request
    # closed before the tool call was ever read -- so the wait itself is what a stop has to reach.
    permissions = _registry()
    threading.Timer(TICK, lambda: permissions.wake("p1", "c1")).start()
    assert permissions.wait("p1", "c1", 5) is None


def test_one_chat_is_answered_without_answering_its_neighbour():
    permissions = _registry()
    permissions.answer("p1", "c1", True, "")
    assert permissions.wait("p1", "c2", TICK) is None


def test_the_reason_travels_with_a_refusal():
    permissions = _registry()
    permissions.answer("p1", "c1", False, "that file is mine")
    decision = permissions.wait("p1", "c1", TICK)
    assert (decision.allowed, decision.reason) == (False, "that file is mine")


def test_an_answer_is_spent_once():
    # A turn may ask twice, and the second question is a question -- not something the first answer
    # already settled. This is also why there is no separate "open a question" call: the answer
    # being consumed is what keeps the two apart.
    permissions = _registry()
    permissions.answer("p1", "c1", True, "")
    permissions.wait("p1", "c1", TICK)
    assert permissions.wait("p1", "c1", TICK) is None


def test_clearing_forgets_the_answer():
    # Every turn clears on its way out. Left standing, an answer would settle the next turn's
    # question before anybody was asked.
    permissions = _registry()
    permissions.answer("p1", "c1", True, "")
    permissions.clear("p1", "c1")
    assert permissions.wait("p1", "c1", TICK) is None
```

## 3 · `queen-agent/backend/tests/test_stream_answer.py` — sahteler ve on beş kırmızı

### 3a · Sahteler

`NeverStops`'un altına, `CUT`'tan önce:

```python
class NeverAsked:
    """The permission registry as most tests need it: in edit mode nothing ever reaches here.

    Raising rather than answering is the point -- a turn that started asking in a mode that asks
    for nothing is a broken gate, and a fake that quietly said yes would hide it.
    """

    def answer(self, project_id, chat_id, allowed, reason):
        raise AssertionError("the turn answered its own question")

    def wait(self, project_id, chat_id, tick):
        raise AssertionError("nothing in this mode should have been asked")

    def wake(self, project_id, chat_id):
        raise AssertionError("nothing in this mode should have been asked")

    def clear(self, project_id, chat_id):
        # Every turn clears on its way out, asked or not.
        pass


UNASKED = NeverAsked()


class Answers:
    """A registry with its decisions written out, one per question.

    A None in the list is a tick that passed with nobody answering, which is what makes the beat
    visible. Running out raises: a gate that asks forever would otherwise spin this test until the
    suite is killed.
    """

    def __init__(self, *decisions, on_wait=None):
        self.decisions = list(decisions)
        self.on_wait = on_wait
        self.asked = []
        self.cleared = []

    def answer(self, project_id, chat_id, allowed, reason):
        raise AssertionError("the turn answered its own question")

    def wait(self, project_id, chat_id, tick):
        self.asked.append((project_id, chat_id))
        if self.on_wait:
            self.on_wait()
        if not self.decisions:
            raise AssertionError("the turn asked more than this test answers")
        return self.decisions.pop(0)

    def wake(self, project_id, chat_id):
        pass

    def clear(self, project_id, chat_id):
        self.cleared.append((project_id, chat_id))


class StopsWhileWaiting:
    """A stop that lands while the turn is paused on a question.

    Cut says yes to `wanted` from the first breath, which ends the round before the tool loop is
    ever reached -- so it cannot describe this moment. Here the press happens on the way into the
    wait, which is the one stretch of a turn with no socket to cut.
    """

    def __init__(self):
        self.pressed = False
        self.woke = None

    def hold(self, project_id, chat_id, cut):
        self.woke = cut

    def want(self, project_id, chat_id):
        self.pressed = True
        self.woke()

    def wanted(self, project_id, chat_id):
        return self.pressed

    def clear(self, project_id, chat_id):
        pass
```

`Decision`'ı kuran iki yardımcı, `_run`'ın altına:

```python
def allowed():
    from backend.features.workspace.domain.permission import Decision

    return Decision(True, "")


def refused(reason=""):
    from backend.features.workspace.domain.permission import Decision

    return Decision(False, reason)


def _gated(tmp_path, rounds, stops=NEVER, permissions=UNASKED, mode="ask", **kwargs):
    """_run's sibling, with the registry the turn reads its answer from.

    Its own helper for one turn only: _run's shape belongs to the tests already written, and
    breaking every one of them would bury this turn's reds. They meet in the implementation tour.
    """
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine(rounds, **kwargs)
    produced = list(stream_answer(chats, files, engine, "p1", "c1", NOW, stops, permissions, mode))
    return chats, files, engine, produced


def _write_round(name="plan.md"):
    return [{"tool_calls": [call("create_file", name=name, content="x")]}]
```

### 3b · Kırmızılar

Dosyanın sonuna:

```python
# --- permission asked in the middle of a turn (Madde 99) -----------------------------------------


def test_a_call_the_mode_does_not_cover_is_asked_about(tmp_path):
    permissions = Answers(allowed())
    _gated(tmp_path, [_write_round(), [{"text": "done"}]], permissions=permissions)
    assert permissions.asked == [("p1", "c1")]


def test_the_question_carries_the_tool_and_its_arguments(tmp_path):
    # Raw, the way the model wrote them. Parsing here would be a second parser beside run_tool's,
    # and the two would drift on the first change to either.
    from backend.features.workspace.domain.permission import PermissionWanted

    _, _, _, produced = _gated(
        tmp_path, [_write_round(), [{"text": "done"}]], permissions=Answers(allowed())
    )
    asked = [piece for piece in produced if isinstance(piece, PermissionWanted)]
    assert asked == [
        PermissionWanted("create_file", json.dumps({"name": "plan.md", "content": "x"}))
    ]


def test_an_allowed_call_runs(tmp_path):
    _, files, _, _ = _gated(
        tmp_path, [_write_round(), [{"text": "done"}]], permissions=Answers(allowed())
    )
    assert files.list_names("p1") == ["plan.md"]


def test_an_allowed_call_changes_the_mode_for_the_rest_of_the_turn(tmp_path):
    # One answer for two writes. Measured by the registry running out if it is asked twice, which
    # is exactly what a mode that did not change would do.
    rounds = [
        [
            {
                "tool_calls": [
                    call("create_file", call_id="a", name="one.md", content="x"),
                    call("create_file", call_id="b", name="two.md", content="y"),
                ]
            }
        ],
        [{"text": "done"}],
    ]
    permissions = Answers(allowed())
    _, files, _, _ = _gated(tmp_path, rounds, permissions=permissions)
    assert len(permissions.asked) == 1
    assert sorted(files.list_names("p1")) == ["one.md", "two.md"]


def test_a_refused_call_does_not_run(tmp_path):
    _, files, _, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], permissions=Answers(refused())
    )
    assert files.list_names("p1") == []


def test_a_refused_call_tells_the_model_why(tmp_path):
    # A wall with nothing written on it is a wall the model walks into again.
    _, _, engine, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], permissions=Answers(refused())
    )
    said = engine.seen[1][-1]
    assert said["role"] == "tool"
    assert said["tool_call_id"] == "t1"
    assert "create_file" in said["content"]
    assert "mode has not changed" in said["content"]


def test_the_users_own_reason_reaches_the_model(tmp_path):
    _, _, engine, _ = _gated(
        tmp_path,
        [_write_round(), [{"text": "ok"}]],
        permissions=Answers(refused("that file is mine")),
    )
    assert "that file is mine" in engine.seen[1][-1]["content"]


def test_a_refused_call_is_still_a_card(tmp_path):
    # Madde 84 and 85 do not bend for a refusal: what the turn did is what the chat shows. No file
    # name, because no file was touched.
    chats, _, _, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], permissions=Answers(refused())
    )
    assert chats.get("p1", "c1").messages[-1].calls == (ToolCall("create_file", "", "Not allowed"),)


def test_a_refusal_does_not_end_the_turn(tmp_path):
    _, _, engine, _ = _gated(
        tmp_path, [_write_round(), [{"text": "ok"}]], permissions=Answers(refused())
    )
    assert len(engine.seen) == 2


def test_a_stop_while_waiting_ends_the_turn(tmp_path):
    stops = StopsWhileWaiting()
    permissions = Answers(None, on_wait=lambda: stops.want("p1", "c1"))
    chats, files, engine, _ = _gated(
        tmp_path,
        [_write_round(), [{"text": "never"}]],
        stops=stops,
        permissions=permissions,
    )
    assert files.list_names("p1") == []
    assert len(engine.seen) == 1
    assert chats.get("p1", "c1").messages[-1].stopped


def test_a_tick_with_no_answer_beats_and_keeps_waiting(tmp_path):
    # The beat is what keeps a tunnel from closing a silent stream, and what notices a tab that
    # went away. Then the answer arrives and the turn carries on as if nothing happened.
    from backend.features.workspace.domain.permission import Waiting

    _, files, _, produced = _gated(
        tmp_path, [_write_round(), [{"text": "done"}]], permissions=Answers(None, allowed())
    )
    assert [piece for piece in produced if isinstance(piece, Waiting)] == [Waiting()]
    assert files.list_names("p1") == ["plan.md"]


def test_edit_mode_never_reaches_the_registry(tmp_path):
    # UNASKED raises when it is touched, so this is measured rather than asserted.
    _, files, _, _ = _gated(tmp_path, [_write_round(), [{"text": "done"}]], mode="edit")
    assert files.list_names("p1") == ["plan.md"]


def test_every_mode_is_offered_every_tool(tmp_path):
    # The mode stopped being the request's tool list here. What it decides now is which of them run
    # without a question.
    from backend.features.workspace.domain.tools import TOOL_SPECS

    _, _, engine, _ = _gated(tmp_path, [[{"text": "hi"}]])
    assert engine.tools == [[spec["function"]["name"] for spec in TOOL_SPECS]]


def test_the_question_comes_before_the_dashed_card(tmp_path):
    # The other way round the card would stand there through the whole wait, saying a file is on
    # its way while nobody has agreed to it yet.
    from backend.features.workspace.domain.permission import PermissionWanted

    _, _, _, produced = _gated(
        tmp_path, [_write_round(), [{"text": "done"}]], permissions=Answers(allowed())
    )
    kinds = [type(piece) for piece in produced]
    assert kinds.index(PermissionWanted) < kinds.index(FileStarted)


def test_the_registry_is_cleared_however_the_turn_ends(tmp_path):
    permissions = Answers(refused())
    _gated(tmp_path, [_write_round(), [{"text": "ok"}]], permissions=permissions)
    assert permissions.cleared == [("p1", "c1")]
```

## 4 · `queen-agent/backend/tests/test_chats_api.py` — kapı

### 4a · Var olan testin iddiası değişiyor

`test_the_mode_reaches_the_request_as_a_tool_list` **yerine**:

```python
def test_every_mode_is_offered_every_tool(tmp_path):
    # Until Madde 99 the mode was the request's tool list. Now everything is offered and the mode
    # decides what runs without asking -- so the word's consequence moved, and this is where it is
    # no longer visible.
    from backend.features.workspace.domain.tools import TOOL_SPECS

    engine = ScriptedEngine([[{"text": "Done."}]])
    client = _client(tmp_path, engine)
    pid = _project(client)
    client.post(f"/api/projects/{pid}/messages", json={"text": "hello", "mode": "ask"}).get_data()
    assert engine.tools == [[spec["function"]["name"] for spec in TOOL_SPECS]]
```

### 4b · Yeni kırmızılar

Dosyanın sonuna:

```python
# --- the door the answer comes in by (Madde 99) --------------------------------------------------


def _asking(tmp_path):
    """A client whose second turn wants to write, and a first turn to be born in.

    The chat has to exist before the answer can be left at its door, and a chat is born by being
    answered -- so the first round is an ordinary sentence with no tool in it.
    """
    engine = ScriptedEngine(
        [
            [{"text": "hi"}],
            [{"tool_calls": [_tool_call("create_file", name="plan.md", content="x")]}],
            [{"text": "ok"}],
        ]
    )
    return _client(tmp_path, engine)


def _write(client, pid, cid):
    return client.post(
        f"/api/projects/{pid}/messages", json={"chat": cid, "text": "write it", "mode": "ask"}
    ).get_data(as_text=True)


def test_the_answer_left_at_the_door_lets_the_turn_finish(tmp_path):
    # Answered before the question is asked, on purpose: the registry carries that race already,
    # and the alternative here is a second thread whose timing decides whether the test passes.
    client = _asking(tmp_path)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/permission", json={"allowed": True})
    body = _write(client, pid, cid)
    assert _frames(body) == ["chat", "permission", "file-start", "file", "call", "chunk", "done"]
    assert [file["name"] for file in client.get(f"/api/projects/{pid}/files").get_json()] == [
        "plan.md"
    ]


def test_the_question_names_the_tool_and_its_arguments(tmp_path):
    client = _asking(tmp_path)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/permission", json={"allowed": True})
    body = _write(client, pid, cid)
    asked = json.loads(body.split("event: permission\ndata: ", 1)[1].splitlines()[0])
    assert asked["tool"] == "create_file"
    assert json.loads(asked["arguments"]) == {"name": "plan.md", "content": "x"}


def test_a_refusal_at_the_door_writes_no_file_and_the_turn_still_ends(tmp_path):
    client = _asking(tmp_path)
    pid, cid = _started(client)
    client.post(
        f"/api/projects/{pid}/chats/{cid}/permission",
        json={"allowed": False, "reason": "not that one"},
    )
    body = _write(client, pid, cid)
    assert _frames(body) == ["chat", "permission", "call", "chunk", "done"]
    assert client.get(f"/api/projects/{pid}/files").get_json() == []


def test_answering_a_chat_that_is_not_there_is_a_404(tmp_path):
    # The words as well as the number: an address nobody serves answers 404 too, and without the
    # body this test would pass today for a reason that has nothing to do with the item.
    client = _client(tmp_path)
    pid = _project(client)
    answered = client.post(f"/api/projects/{pid}/chats/nope/permission", json={"allowed": True})
    assert answered.status_code == 404
    assert answered.get_json() == {"error": "chat not found"}


def test_the_beat_is_a_frame_the_browser_drops(tmp_path):
    # parseFrame keeps only what carries an event line, so a beat has to carry none. Measured on
    # this side because the front end is Madde 102's work and nothing here touches it. Reached
    # through _sse rather than over HTTP: a real beat costs fifteen seconds of waiting.
    from backend.features.workspace.domain.permission import Waiting
    from backend.features.workspace.presentation.routes import _sse

    written = "".join(_sse("c1", iter([Waiting()])))
    beat = written.split("\n\n")[1]
    assert beat and not beat.startswith("event:")
```

## 5 · Koş

```
python -m pytest queen-agent -q
python -m pytest queen-editor -q
npm test --prefix queen-agent/frontend
npm test --prefix queen-editor/frontend
```

Beklenen kırmızılar: `test_modes.py`'den 6, `test_permissions.py`'den 8, `test_stream_answer.py`'den
15, `test_chats_api.py`'den 6 — toplam **35**. Ön yüzün ikisi ve queen-editor bu turda hiç
etkilenmiyor.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi — defterin `BRANCH`'i koşu bitince
`main`'e dönecek.

Toplama hatası **beklenmiyor**: yeni adların hepsi testin içinden import ediliyor. Bir toplama
hatası görülürse sebebi bu kuralın kaçırıldığı bir satırdır, ve düzeltmesi importu gövdeye almaktır.

## 6 · Commit

```
test(queen-agent): red for a permission asked in the middle of a turn
```
