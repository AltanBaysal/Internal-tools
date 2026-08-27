# Madde 91 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-27-queenagent-m91-kip-gelir-uygulama-design.md](../specs/2026-08-27-queenagent-m91-kip-gelir-uygulama-design.md)
**Bu turda yeni test yazılmaz.** `de61402`'nin on dokuz kırmızısı yeşile döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
`npm run build --prefix queen-agent/frontend`

---

## 1. `backend/features/workspace/domain/tools.py`

`WRITES_FILES`'a giriyor:

```python
# Which tools can bring a file into being. The chat draws a card for each, so an edit is not in
# here: the file was already there. write_plan is, because the first one brings a file into being.
WRITES_FILES = {"create_file", "build_prompts", "write_plan"}
```

`TOOL_SPECS`'in sonuna:

```python
    {
        "type": "function",
        "function": {
            "name": "write_plan",
            "description": (
                "Break the work into numbered steps and save the plan. Writes over the plan of "
                "that name if there is one, so read it first and hand back the whole plan rather "
                "than the part you changed. The turn ends here: the user reads the plan, fixes it "
                "in the file if they want to, and runs it themselves."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "What the plan is for, as in bar-scene.",
                    },
                    "content": {"type": "string", "description": "The plan itself."},
                },
                "required": ["name", "content"],
            },
        },
    },
```

`safe_name`'in altına:

```python
def plan_name(name):
    """A plan is named so that it reads as one, and so the tool cannot write anything else.

    Runs after safe_name: cleaning what came from the model is that one's job, naming is this one's.
    """
    stem = name.rsplit(".", 1)[0]
    return f"{stem}.md" if stem.endswith("-plan") else f"{stem}-plan.md"
```

`run_tool`'da, `create_file`'ın altına:

```python
    if name == "write_plan":
        wanted = plan_name(safe_name(args.get("name")))
        # Overwrites where create_file numbers. A second plan sitting in bar-scene-plan-2.md would
        # lose which of the two is the one to follow.
        born = file_store.read(project_id, wanted) is None
        written = file_store.write(project_id, wanted, args.get("content", ""))
        # A card only the first time: after that the file was already there, which is the rule
        # edit_file follows too.
        return ToolResult(
            f"Saved as {written}.", written if born else None, written, "Saved" if born else "Rewritten"
        )
```

## 2. `backend/features/workspace/domain/modes.py` — yeni

```python
"""Which tools each mode puts in the request.

What the model may do used to be a sentence inside a skill's text -- "do not create a file" -- and
a sentence is a request. The verify skill is the proof of what that is worth: it says it fixes
nothing and then fixes things. Here the rule is the tool list, and a tool that is not in the
request cannot be called.
"""
from backend.features.workspace.domain.tools import TOOL_SPECS

PLAN = "plan"
ASK = "ask"
EDIT = "edit"
DEFAULT = EDIT

READS = ("list_files", "read_file")

_OFFERED = {
    ASK: READS,
    # Reading, and one way to write -- a plan. Given create_file it could write the plan and the
    # deliverable in the same turn, which is doing the work instead of planning it.
    PLAN: READS + ("write_plan",),
    EDIT: READS + ("create_file", "edit_file", "build_prompts"),
}


def tools_for(mode):
    """The specs this mode offers the model. A mode nobody knows is the default one.

    Not an empty list for an unknown mode: an older browser, or a body with no mode in it at all,
    would lose its tools silently -- and a model with no tools looks exactly like a model that
    decided not to use them.
    """
    allowed = _OFFERED.get(mode, _OFFERED[DEFAULT])
    return [spec for spec in TOOL_SPECS if spec["function"]["name"] in allowed]


def ends_the_turn(mode, tool):
    """Whether this call is where the turn stops.

    One pair rather than a count: the rule is not "write once", it is "the plan is written, so the
    next move is the user's". The same tool in another mode is an ordinary write.
    """
    return mode == PLAN and tool == "write_plan"
```

## 3. `backend/features/workspace/domain/usecases/stream_answer.py`

Import:

```python
from backend.features.workspace.domain.modes import EDIT, ends_the_turn, tools_for
```

İmza ve iki kullanım:

```python
def stream_answer(chat_store, file_store, engine, project_id, chat_id, now, stops, mode=EDIT):
```

```python
                for piece in engine.stream(
                    conversation,
                    tools=tools_for(mode),
```

Araç döngüsünde, `yield step`'ten sonra, `conversation.append`'in ardından:

```python
                conversation.append(
                    {"role": "tool", "tool_call_id": call["id"], "content": result.text}
                )
                if ends_the_turn(mode, tool):
                    # The plan reached disk and the next move is the user's. Kept apart from
                    # cut_short: a stopped turn is written down as stopped, and this one simply
                    # finished.
                    done = True
                    break
            if done:
                break
```

`done = False` döngüden önce, `cut_short`'un yanında.

## 4. `backend/features/workspace/presentation/routes.py`

`post_message`'ın son satırı:

```python
        return Response(
            _sse(
                chat.id,
                stream_answer(
                    chat_store,
                    file_store,
                    engine,
                    project_id,
                    chat.id,
                    _now(),
                    stops,
                    # Travels with the request and ends there: which tools were offered is decided
                    # now, and nothing ever reads it back.
                    payload.get("mode", ""),
                ),
            ),
            mimetype="text/event-stream",
        )
```

## 5. `frontend/src/features/workspace/modes.js` — yeni

```js
// The three modes, in the order the item names them. What the model may do is a control now rather
// than a sentence in a skill's text -- and the second line says what each one costs the model.
export const MODES = [
  { id: "plan", name: "Plan", detail: "Break the work into steps and write the plan to a file." },
  { id: "ask", name: "Ask", detail: "Read and answer. Nothing is written." },
  { id: "edit", name: "Edit", detail: "Read, write and build. The full set." },
];

// Edit is what the app did before there were modes, so it is what it still does by default.
export const DEFAULT_MODE = "edit";

// Unlike a skill, there is no such thing as no mode -- so this never answers with a placeholder.
export function modeName(id) {
  return MODES.find((mode) => mode.id === id)?.name ?? modeName(DEFAULT_MODE);
}
```

> `modeName`'in özyinelemesi bir kere iniyor: `DEFAULT_MODE` listede var.

## 6. `frontend/src/features/workspace/ModePicker.jsx` — yeni

```jsx
import { useRef } from "react";

import Menu from "./Menu.jsx";
import { MODES, modeName } from "./modes.js";

// What the model may do at all, in the composer's foot to the left of the skill -- that question
// comes before which job it is doing, and the row reads outermost first.
//
// The skill picker's twin, with one difference that comes from what the two things are: a chat may
// have no skill and usually does not, so pressing the selected row there clears it. There is no
// such thing as no mode, so pressing it here just picks it again. The button takes no --on tone
// for the same reason: that tone means something is selected, and here something always is.
export default function ModePicker({ mode, open, onToggle, onChange }) {
  const trigger = useRef(null);

  return (
    <>
      <button type="button" ref={trigger} className="picker" onClick={() => onToggle?.()}>
        <span className="picker__name">{modeName(mode)}</span>
        <span className="picker__chevron">⌄</span>
      </button>
      {open ? (
        <Menu
          header="MODE"
          anchor={trigger.current}
          onClose={() => onToggle?.()}
          items={MODES.map((candidate) => ({
            label: candidate.name,
            detail: candidate.detail,
            checked: candidate.id === mode,
            onChoose: () => onChange?.(candidate.id),
          }))}
        />
      ) : null}
    </>
  );
}
```

## 7. `frontend/src/App.jsx`

`skillsOpen` yerine tek bir değer:

```jsx
  // Which picker is open, if either. One value rather than a boolean each: two booleans can both
  // be true, and then two menus stand over the same corner of the screen. Here rather than inside
  // a picker, because App's one listener owns Escape and it can only close what it can see.
  const [pickerOpen, setPickerOpen] = useState(null);
  // The last mode picked, and what the next turn is sent in. Held for the session like the skill:
  // nothing on the server reads a mode back.
  const [lastMode, setLastMode] = useState(DEFAULT_MODE);
```

Escape:

```jsx
      // The design's order, fark 67: project menu → confirm box → the open picker → open panel.
      else if (pickerOpen) setPickerOpen(null);
```

ve bağımlılık listesinde `skillsOpen` yerine `pickerOpen`.

Açma:

```jsx
  const togglePicker = (which) => setPickerOpen((open) => (open === which ? null : which));
```

İki ekrana giden props:

```jsx
            skill={lastSkill}
            skillsOpen={pickerOpen === "skills"}
            onToggleSkills={() => togglePicker("skills")}
            onSkillChange={setLastSkill}
            mode={lastMode}
            modeOpen={pickerOpen === "mode"}
            onToggleMode={() => togglePicker("mode")}
            onModeChange={setLastMode}
```

ve gönderme:

```jsx
            onSend={(text) => chat.send(text, lastSkill, lastMode)}
```

`toggleSkills` tanımı düşüyor; `import { DEFAULT_MODE } from "./features/workspace/modes.js";`
giriyor.

## 8. `useChat.js`

```jsx
  const send = useCallback(
    async (text = null, skill = "", mode = "") => {
```

ve gövde:

```jsx
      const body = text === null ? { chat: chatId } : { chat: chatId ?? "", text, skill, mode };
```

Metinsiz yol kip taşımıyor: sunucu tanımadığı kipi düzenle sayıyor, ve tekrar denemek zaten
yazılmış bir soruyu cevaplatmak.

## 9. İki ekran

`ChatScreen.jsx` ve `ProjectScreen.jsx`, `foot`'un **başına**:

```jsx
            foot={
              <>
                <ModePicker
                  mode={mode}
                  open={modeOpen}
                  onToggle={onToggleMode}
                  onChange={onModeChange}
                />
                <SkillPicker ... />
```

İkisi de yeni propsları imzalarına alıyor, ve `ModePicker`'ı import ediyor.

## Beklenen yeşil

`de61402`'nin on dokuz kırmızısının hepsi, ve o turda yazılıp bugün de yeşil olan ikisi yeşil
kalır.

**İki kırmızı kalır ve bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` derlenip **aynı commit'e** giriyor.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **Skill metinlerine dokunulmaz** — 94'ün işi.
- **Yönergenin yeri değişmez** — 93'ün işi.
- **`Message`'a alan eklenmez.**
