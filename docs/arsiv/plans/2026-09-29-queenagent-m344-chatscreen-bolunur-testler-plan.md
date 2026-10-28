# Madde 344 — ChatScreen.jsx bölünür · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mesajı çizen sekiz bileşenin beş yeni dosyadan tek başına çizildiğini ve `ChatScreen.jsx`'in
onları artık tanımlamadığını tutan testler, kırmızı.

**Architecture:** `queen-agent/frontend/src/features/workspace/` altında beş yeni test dosyası, her biri
bileşeni yeni evinden import eder. `ChatScreen.test.jsx`'e dosyayı diskten okuyan bir kilit.

**Tech Stack:** vitest + jsdom + Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m344-chatscreen-bolunur-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; ön ucun testleri iddialara mesaj yazmıyor, yenileri de yazmaz.
- `ChatScreen.test.jsx`'in bugünkü testleri değişmez; kilit iki düzen testinin hemen altına girer.
- Bu turda `ChatScreen.jsx` değişmez ve beş kaynak dosya yazılmaz; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Beş yeni test dosyası ve kilit, kırmızı

**Files:**
- Create: `queen-agent/frontend/src/features/workspace/ToolCalls.test.jsx`
- Create: `queen-agent/frontend/src/features/workspace/Stamp.test.jsx`
- Create: `queen-agent/frontend/src/features/workspace/MessageFoot.test.jsx`
- Create: `queen-agent/frontend/src/features/workspace/EditMessage.test.jsx`
- Create: `queen-agent/frontend/src/features/workspace/FileCard.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` — iki `node:` importu, ve
  27. satırdan sonra kilit

**Interfaces:**
- Produces (uygulama turunun karşılayacağı): `./ToolCalls.jsx` varsayılan `ToolCalls({ calls, running })`;
  `./Stamp.jsx` varsayılan `Stamp({ at, usage })` ve adıyla `LiveStrip({ round, of, tokens })`;
  `./MessageFoot.jsx` varsayılan `MessageFoot({ standing, onVersion, onEdit })`; `./EditMessage.jsx`
  varsayılan `EditMessage({ text, onConfirm, onCancel })`; `./FileCard.jsx` varsayılan
  `FileCard({ name, selected, onOpen })` ve adıyla `CreatingFile()`. `ChatScreen.jsx`'te sekiz adın
  hiçbiri `function <ad>(` olarak geçmez.

- [ ] **Step 1: `ToolCalls.test.jsx`**

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import ToolCalls from "./ToolCalls.jsx";

// Madde 344 moved the door out of ChatScreen.jsx. Every branch of it is still held by the screen's
// own tests; these hold that it draws from its own file, alone.

const CALLS = [
  { tool: "list_files", target: "", outcome: "No files" },
  { tool: "read_file", target: "aylin.json", outcome: "45 lines" },
];

test("a turn that called nothing draws no door", () => {
  const { container } = render(<ToolCalls calls={[]} />);
  expect(container.firstChild).toBeNull();
});

test("shut it counts the steps, and open it lists them", () => {
  const { container } = render(<ToolCalls calls={CALLS} />);
  fireEvent.click(screen.getByRole("button", { name: /2 steps/ }));
  const heads = [...container.querySelectorAll(".tool-call__head")].map((head) => head.textContent);
  expect(heads).toEqual(["⏺ list_files", "⏺ read_file(aylin.json)"]);
  expect(screen.getByText("45 lines")).toBeTruthy();
});

test("while the turn runs the shut door names the last call", () => {
  render(<ToolCalls calls={CALLS} running />);
  expect(screen.getByRole("button", { name: /read_file\(aylin\.json\)/ })).toBeTruthy();
});
```

- [ ] **Step 2: `Stamp.test.jsx`**

```jsx
import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { clockTime } from "../../shared/time.js";
import Stamp, { LiveStrip } from "./Stamp.jsx";

// Madde 344: the stamp and the strip that stands in its place while a turn runs share one file,
// because they share one place, one class and one way of shortening a count.

const AT = new Date(2026, 7, 9, 11, 5).toISOString();

test("without a time there is no stamp", () => {
  const { container } = render(<Stamp at={null} />);
  expect(container.firstChild).toBeNull();
});

test("an answer's stamp says when and what it spent", () => {
  render(<Stamp at={AT} usage={{ sent: 1000, answered: 200 }} />);
  expect(screen.getByText(`${clockTime(AT)} · 1.2k tokens`)).toBeTruthy();
});

test("nothing spent leaves the time alone", () => {
  const { container } = render(<Stamp at={AT} usage={{ sent: 0, answered: 0 }} />);
  expect(container.querySelector(".msg__stamp").textContent).toBe(clockTime(AT));
});

test("the live strip says the round and the tokens", () => {
  render(<LiveStrip round={2} of={16} tokens={1234} />);
  expect(screen.getByText("round 2/16 · 1.2k tokens", { exact: false })).toBeTruthy();
});
```

- [ ] **Step 3: `MessageFoot.test.jsx`**

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import MessageFoot from "./MessageFoot.jsx";

// Madde 344: the line under a bubble, and the version arrows that only it draws, in one file.

const BESIDE = { index: 0, of: 2, versions: ["", "l2"] };

test("a lone message with no pencil draws no line", () => {
  const { container } = render(<MessageFoot standing={{ index: 0, of: 1, versions: [""] }} />);
  expect(container.firstChild).toBeNull();
});

test("the pencil asks for the edit", () => {
  const onEdit = vi.fn();
  render(<MessageFoot onEdit={onEdit} />);
  fireEvent.click(screen.getByRole("button", { name: "Edit message" }));
  expect(onEdit).toHaveBeenCalled();
});

test("the arrows hand over the version beside this one", () => {
  const onVersion = vi.fn();
  render(<MessageFoot standing={BESIDE} onVersion={onVersion} />);
  expect(screen.getByText("1/2")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Previous version" }).disabled).toBe(true);
  fireEvent.click(screen.getByRole("button", { name: "Next version" }));
  expect(onVersion).toHaveBeenCalledWith("l2");
});
```

- [ ] **Step 4: `EditMessage.test.jsx`**

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import EditMessage from "./EditMessage.jsx";

// Madde 344: the field a question is corrected in, drawn from its own file.

test("Enter confirms the sentence without its edges", () => {
  const onConfirm = vi.fn();
  render(<EditMessage text="Write the intro" onConfirm={onConfirm} onCancel={vi.fn()} />);
  const field = screen.getByRole("textbox");
  fireEvent.change(field, { target: { value: "  Write the outro  " } });
  fireEvent.keyDown(field, { key: "Enter" });
  expect(onConfirm).toHaveBeenCalledWith("Write the outro");
});

test("Escape gives up", () => {
  const onCancel = vi.fn();
  render(<EditMessage text="Write the intro" onConfirm={vi.fn()} onCancel={onCancel} />);
  fireEvent.keyDown(screen.getByRole("textbox"), { key: "Escape" });
  expect(onCancel).toHaveBeenCalled();
});

test("an empty draft cannot be confirmed", () => {
  render(<EditMessage text="Write the intro" onConfirm={vi.fn()} onCancel={vi.fn()} />);
  fireEvent.change(screen.getByRole("textbox"), { target: { value: "   " } });
  expect(screen.getByRole("button", { name: "Confirm edit" }).disabled).toBe(true);
});
```

- [ ] **Step 5: `FileCard.test.jsx`**

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import FileCard, { CreatingFile } from "./FileCard.jsx";

// Madde 344: the card a turn leaves behind, and the skeleton it is drawn as while it is being born,
// in one file.

test("the card is a door into the file", () => {
  const onOpen = vi.fn();
  render(<FileCard name="outline.md" onOpen={onOpen} />);
  expect(screen.getByText("md")).toBeTruthy();
  expect(screen.getByText("✓ saved to project")).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: /outline\.md/ }));
  expect(onOpen).toHaveBeenCalledWith("outline.md");
});

test("the open card says so and points nowhere", () => {
  render(<FileCard name="outline.md" selected />);
  expect(screen.getByText("open")).toBeTruthy();
  expect(screen.queryByText("Open ›")).toBeNull();
});

test("a card about to be born says what is happening", () => {
  render(<CreatingFile />);
  expect(screen.getByText("creating file…")).toBeTruthy();
});
```

- [ ] **Step 6: `ChatScreen.test.jsx`'e kilit**

Dosyanın başı:

```jsx
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { act, fireEvent, render, screen } from "@testing-library/react";
```

`with nothing open the layout says nothing` testinin hemen altına:

```jsx
// Madde 344: the screen is the screen, and what draws one message lives in files of its own. A lock
// rather than a behaviour -- every test below still draws the screen and looks at what it does.
// Read off disk, like workspace.css.test.js: vitest hands back neither import.meta.url nor `?raw`.
test("the message's parts are drawn from their own files", () => {
  const source = readFileSync(resolve(process.cwd(), "src/features/workspace/ChatScreen.jsx"), "utf8");
  const parts = [
    "ToolCalls",
    "Stamp",
    "LiveStrip",
    "EditMessage",
    "Versions",
    "MessageFoot",
    "CreatingFile",
    "FileCard",
  ];
  expect(parts.filter((part) => source.includes(`function ${part}(`))).toEqual([]);
});
```

- [ ] **Step 7: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` beş dosya import ettiği dosyayı bulamadan düşer, ve
kilit sekiz adın hepsini `ChatScreen.jsx`'te bularak kırmızı; öteki 652 test yeşil.
`python -m pytest queen-editor -q` 377'nin bilinen iki kırmızısı. Öteki iki süit yeşil.

- [ ] **Step 8: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/ToolCalls.test.jsx queen-agent/frontend/src/features/workspace/Stamp.test.jsx queen-agent/frontend/src/features/workspace/MessageFoot.test.jsx queen-agent/frontend/src/features/workspace/EditMessage.test.jsx queen-agent/frontend/src/features/workspace/FileCard.test.jsx queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx docs/specs/2026-09-29-queenagent-m344-chatscreen-bolunur-testler-design.md docs/plans/2026-09-29-queenagent-m344-chatscreen-bolunur-testler-plan.md
git commit -m @'
test(queen-agent): Madde 344 red -- each part of a message draws from its own file, and ChatScreen.jsx no longer defines them

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
