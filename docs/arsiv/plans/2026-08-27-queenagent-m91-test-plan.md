# Madde 91 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m91-kip-gelir-testler-design.md](../specs/2026-08-27-queenagent-m91-kip-gelir-testler-design.md)
**Bu turda kod yazılmaz.** Yirmi test kırmızıya döner, birinin ölçüsü değişir.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sözleşme — testlerin varsaydığı isimler

Bu turda **yazılmıyorlar**; testler onları çağırdığı için kırmızı oluyor.

```python
# backend/features/workspace/domain/tools.py
"write_plan"                                    # altıncı araç, TOOL_SPECS içinde
def plan_name(name) -> str                      # "x.md" -> "x-plan.md", "x-plan.md" aynı kalır

# backend/features/workspace/domain/modes.py -- yeni
PLAN, ASK, EDIT = "plan", "ask", "edit"
DEFAULT = EDIT
def tools_for(mode) -> list[dict]               # TOOL_SPECS'in kipe düşen alt kümesi
def ends_the_turn(mode, tool) -> bool           # yalnız (PLAN, "write_plan")

# stream_answer -- son parametre
def stream_answer(chat_store, file_store, engine, project_id, chat_id, now, stops, mode=EDIT)

# POST /api/projects/<p>/messages gövdesi
{"chat": ..., "text": ..., "skill": ..., "mode": "plan"}
```

```jsx
// frontend/src/features/workspace/modes.js -- yeni
export const MODES = [{ id, name, detail }, ...]   // plan, ask, edit -- bu sırayla
export const DEFAULT_MODE = "edit"
export function modeName(id)

// frontend/src/features/workspace/ModePicker.jsx -- yeni
<ModePicker mode={mode} open={open} onToggle={...} onChange={...} />
// Menu header'ı "MODE"; düğme .picker sınıfını taşır, .picker--on taşımaz -- bir kip hep seçili

// iki ekran da yeni props alır: mode, modeOpen, onToggleMode, onModeChange
// useChat.send(text, skill, mode)
```

---

## 1. `backend/tests/test_tools.py` — üç yeni test, bir ölçü

Import satırına `plan_name` girmiyor: dosya toplanamazsa bu turun bütün kırmızıları görünmez olur.
`write_plan` bir dize olduğu için `run_tool` üzerinden çağrılabiliyor; `plan_name` doğrudan
sınanmıyor, davranışı üç testin içinden okunuyor.

`create_file` testlerinin altına:

```python
# --- the plan tool (Madde 91) --------------------------------------------------------------------


def test_a_plan_is_written_under_a_name_that_says_it_is_one(tmp_path):
    # Two jobs in one rule: a plan is recognisable on disk, and the tool cannot be turned into a
    # way of writing the deliverable it was supposed to be planning.
    files = _files(tmp_path)
    assert "bar-scene-plan.md" in _call(files, "write_plan", name="bar-scene.md", content="1. ...")
    assert _call(files, "read_file", name="bar-scene-plan.md") == "1. ..."


def test_writing_a_plan_again_replaces_it(tmp_path):
    # Unlike create_file, which never overwrites. A second plan sitting in bar-scene-plan-2.md
    # would lose which of the two is the one to follow.
    files = _files(tmp_path)
    _call(files, "write_plan", name="bar-scene", content="first")
    _call(files, "write_plan", name="bar-scene", content="second")
    assert _call(files, "read_file", name="bar-scene-plan.md") == "second"
    assert _call(files, "list_files") == "bar-scene-plan.md"


def test_only_the_first_plan_reports_a_born_file(tmp_path):
    # The card says a file came into being. The second write changes one that was already there --
    # the same rule edit_file follows.
    files = _files(tmp_path)
    born = run_tool(files, "p1", "write_plan", json.dumps({"name": "a", "content": "x"}))
    again = run_tool(files, "p1", "write_plan", json.dumps({"name": "a", "content": "y"}))
    assert born.created == "a-plan.md"
    assert again.created is None
```

`test_a_plan_is_written_under_a_name_that_says_it_is_one`'un içinde üçüncü iddia olarak ad ikilenmesi
de duruyor:

```python
    # A name that already says it is a plan is not made to say it twice.
    assert "bar-scene-plan.md" in _call(files, "write_plan", name="bar-scene-plan.md", content="x")
```

**Ölçüsü değişen:** `test_every_tool_is_declared_to_the_model` kümesine `"write_plan"` ekleniyor.

## 2. `backend/tests/test_modes.py` — yeni dosya, beş test

```python
"""What each mode puts in the request. The rule that used to be a sentence in a skill's text."""
from backend.features.workspace.domain.modes import ASK, EDIT, PLAN, ends_the_turn, tools_for

READS = {"list_files", "read_file"}


def _offered(mode):
    return {spec["function"]["name"] for spec in tools_for(mode)}


def test_ask_mode_can_only_read():
    # The item in one line: a model in this mode does not create a file because it has no tool
    # that creates one -- not because it was asked nicely and held itself back.
    assert _offered(ASK) == READS


def test_plan_mode_can_write_a_plan_and_nothing_else():
    # Given create_file it could write the plan and the deliverable in the same turn, which is
    # doing the work instead of planning it.
    assert _offered(PLAN) == READS | {"write_plan"}


def test_edit_mode_carries_the_five_it_always_had():
    # And not write_plan: in this mode a plan is an ordinary file, and edit_file changes it.
    assert _offered(EDIT) == READS | {"create_file", "edit_file", "build_prompts"}


def test_a_mode_nobody_knows_is_the_default_one():
    # An older browser, or a body with no mode in it at all. Losing the tools silently would look
    # exactly like a model that decided not to use them.
    assert _offered("") == _offered(EDIT)
    assert _offered("something-else") == _offered(EDIT)


def test_only_a_written_plan_ends_the_turn():
    # The plan reached disk and the next move is the user's. Nothing else stops a turn early --
    # the same tool in edit mode is an ordinary write.
    assert ends_the_turn(PLAN, "write_plan")
    assert not ends_the_turn(EDIT, "write_plan")
    assert not ends_the_turn(PLAN, "read_file")
```

## 3. `backend/tests/test_stream_answer.py` — üç test

`ScriptedEngine` gördüğü araç listesini saklamıyor; bir satır ekleniyor. Bu bir sahte
değişikliği, iddia değil:

```python
    def __init__(self, rounds, blow_up_after=None):
        ...
        self.tools = []
```

```python
    def stream(self, messages, tools=None, on_open=None):
        self.seen.append(list(messages))
        self.tools.append([spec["function"]["name"] for spec in tools or []])
```

Testler, `_run`'ın `**kwargs`'ı `ScriptedEngine`'e gittiği için kipi doğrudan
`stream_answer`'a veren kendi çağrılarını yapıyor:

```python
# --- which tools the mode puts in the request (Madde 91) -----------------------------------------


def _in_mode(tmp_path, rounds, mode):
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine(rounds)
    produced = list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER, mode))
    return chats, engine, produced


def test_the_mode_decides_which_tools_the_request_carries(tmp_path):
    _, engine, _ = _in_mode(tmp_path, [[{"text": "Hi"}]], "ask")
    assert set(engine.tools[0]) == {"list_files", "read_file"}


def test_a_turn_that_names_no_mode_carries_all_five(tmp_path):
    # The retry road sends no mode of its own, and so does every caller written before this item.
    chats, files = _seeded(tmp_path)
    engine = ScriptedEngine([[{"text": "Hi"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER))
    assert "create_file" in engine.tools[0]


def test_in_plan_mode_the_turn_ends_when_the_plan_is_written(tmp_path):
    # The plan is on disk and the next move is the user's: they read it, fix it in the file, then
    # run it in edit mode. A second round here would be the model starting to run its own plan.
    rounds = [
        [{"tool_calls": [call("write_plan", name="bar-scene", content="1. ...")]}],
        [{"text": "never reached"}],
    ]
    _, engine, _ = _in_mode(tmp_path, rounds, "plan")
    assert len(engine.seen) == 1
```


## 4. `backend/tests/test_chats_api.py` — iki test

Dosyanın sonuna:

```python
# --- the mode a turn was sent in (Madde 91) ------------------------------------------------------


def test_the_mode_reaches_the_request_as_a_tool_list(tmp_path):
    # The browser sends a word; what it turns into is which tools the model is offered. Read off
    # the engine, because that is the only place the word becomes a consequence.
    engine = ScriptedEngine([[{"text": "Done."}]])
    client = _client(tmp_path, engine)
    pid = _project(client)
    client.post(f"/api/projects/{pid}/messages", json={"text": "hello", "mode": "ask"}).get_data()
    assert engine.tools == [["list_files", "read_file"]]


def test_the_mode_is_not_written_to_the_record(tmp_path):
    # Unlike the skill, which the record keeps because a later turn rebuilds its instruction from
    # it. Nothing ever reads a mode back, and a field nothing reads is a question every later
    # reader has to answer for themselves.
    client = _client(tmp_path)
    pid = _project(client)
    body = client.post(
        f"/api/projects/{pid}/messages", json={"text": "hello", "mode": "plan"}
    ).get_data(as_text=True)
    kept = _record(client, pid, _named(body))
    assert not any("mode" in message for message in kept["messages"])
```

Bunun için `test_chats_api.py`'deki `ScriptedEngine` de gördüğü araçları saklıyor — aynı iki satır.

## 5. `frontend/src/features/workspace/ModePicker.test.jsx` — yeni dosya, üç test

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ModePicker from "./ModePicker.jsx";

// Madde 91. The skill picker's twin, with one difference that comes from what the two things are:
// a chat may have no skill and usually does not, but there is no such thing as no mode.

test("the button names the mode in force", () => {
  render(<ModePicker mode="plan" />);
  expect(screen.getByText("Plan", { selector: ".picker__name" })).toBeTruthy();
});

test("choosing a mode hands it up", () => {
  const onChange = vi.fn();
  render(<ModePicker mode="edit" open onChange={onChange} />);
  fireEvent.click(screen.getByText("Ask"));
  expect(onChange).toHaveBeenCalledWith("ask");
});

test("pressing the mode already in force does not clear it", () => {
  // Where the skill picker clears, this one holds: there is no way back to no mode, so a press
  // that emptied the button would leave the row saying something that cannot be true.
  const onChange = vi.fn();
  render(<ModePicker mode="ask" open onChange={onChange} />);
  fireEvent.click(screen.getByText("Ask"));
  expect(onChange).toHaveBeenCalledWith("ask");
});
```

## 6. `frontend/src/features/workspace/ChatScreen.test.jsx` — bir test

```jsx
test("the foot puts the mode before the skill", () => {
  // Mode · Skills · model · Send. The mode governs what the model may do at all, which is a
  // question that comes before which job it is doing -- so the row reads outermost first.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} mode="plan" />);
  const names = [...container.querySelectorAll(".composer__foot .picker__name")];
  expect(names.map((name) => name.textContent)).toEqual(["Plan", "Skills"]);
});
```

## 7. `frontend/src/App.test.jsx` — üç test

`withChat()` sahtesinin yanına, dosyanın skill bölümünün altına:

```jsx
// --- which mode a turn is sent in (Madde 91) -----------------------------------------------------

test("the mode in force is what the message is sent with", async () => {
  const fetch = withChat();
  render(<App />);
  await openTheChat();

  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  fireEvent.click(screen.getByText("Ask"));
  fireEvent.change(screen.getByPlaceholderText("Reply..."), { target: { value: "hello" } });
  fireEvent.keyDown(screen.getByPlaceholderText("Reply..."), { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(JSON.parse(sent[1].body).mode).toBe("ask");
  });
});

test("opening one picker closes the other", async () => {
  // One listener owns Escape and one value owns which picker is open: two booleans could both be
  // true, and then two menus would stand over the same corner of the screen.
  withChat();
  render(<App />);
  await openTheChat();

  fireEvent.click(screen.getByText("Skills", { selector: ".picker__name" }));
  expect(screen.getByText("SKILLS")).toBeTruthy();
  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  expect(screen.queryByText("SKILLS")).toBeNull();
  expect(screen.getByText("MODE")).toBeTruthy();
});

test("Escape closes whichever picker is open", async () => {
  withChat();
  render(<App />);
  await openTheChat();

  fireEvent.click(screen.getByText("Edit", { selector: ".picker__name" }));
  expect(screen.getByText("MODE")).toBeTruthy();
  fireEvent.keyDown(window, { key: "Escape" });
  expect(screen.queryByText("MODE")).toBeNull();
});
```

`openTheChat()` diye bir yardımcı dosyada yoksa, skill testlerinin sohbete girmek için kullandığı
adımlar aynen tekrarlanır — hangi yardımcının var olduğu testler yazılırken dosyadan okunur.

---

## Beklenen kırmızı

**Yirmi test**, ve `test_every_tool_is_declared_to_the_model`'in yeni ölçüsü. Sayıyı koşarak değil
şuradan türetiyoruz: `write_plan`, `modes.py`, `stream_answer`'ın kip parametresi, gövdedeki `mode`
alanı, `modes.js` ve `ModePicker.jsx` — hiçbiri yok.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `tools.py`, `stream_answer.py`, `routes.py`, `App.jsx`, iki ekran bu turda
  açılmaz; `modes.py`, `modes.js`, `ModePicker.jsx` yaratılmaz.
- **Skill metinlerine dokunulmaz** — 94'ün işi.
- **Yönergenin yeri değişmez** — 93'ün işi.
- **`dist` derlenmez.**
