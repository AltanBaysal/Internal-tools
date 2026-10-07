# Madde 348 — Mesajın altındaki notlar tek satırda · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mesajın bütün notlarının tek `msg__stamp` satırında, saat önde durduğunu, ve süren cevabın
satırının saatle başladığını tutan testler, kırmızı.

**Architecture:** `ChatScreen.test.jsx`'te sözü bulan testler sözün kendi `span`'ına, 199'un `.msg__foot`
testleri `.msg__stamp`'e taşınır, canlı satırın kalıbı saatle başlar; `Stamp.test.jsx`'e ve
`MessageFoot.test.jsx`'e birer satır kuralı, `workspace.css.test.js`'e satırın kilidi. Kod değişmez.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m348-mesaj-alti-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; UI metni İngilizce.
- Bu turda `Stamp.jsx`, `MessageFoot.jsx`, `ChatScreen.jsx` ve `workspace.css` değişmez; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Tek satırın testleri, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/Stamp.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/MessageFoot.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js`

**Interfaces:**
- Consumes: `ChatScreen`'in `CHAT`, `BRANCHED`, `RUNNING_AT` ve `_editing`'i; `Stamp({ at, usage })`,
  `LiveStrip({ round, of, tokens })`, `MessageFoot({ standing, onVersion, onEdit })`; css testinin `rule`'u.
- Produces: uygulama turunun karşılayacağı şeyler — `Stamp({ at, usage, children })` bir
  `div.msg__stamp` çizer, ilk çocuğu sözlerin `span`'ı, ardından `children`; `LiveStrip({ at, round, of,
  tokens })` ilk `span`'ı `at` varken `${clockTime(at)} · ` ile başlar; `MessageFoot` kendi `div`'ini
  çizmez, `.versions` ve `.msg__edit`'i doğrudan verir; ChatScreen sorunun `MessageFoot`'unu `Stamp`'in
  içine koyar ve canlı satıra `at={askedAt}` verir; CSS'te `.msg__stamp` flex, `align-items: center`,
  `gap: 6px`, ve `.msg__foot` yok.

- [ ] **Step 1: `ChatScreen.test.jsx` — sözü bulan yedi testte `parentElement`**

`"11:04"`, `"11:05"` (iki kez), `"14:32"`, `"11:05 · 13.2k tokens"`, `"11:05 · 342 tokens"` ve
`"11:04"` (count testi) için:

```jsx
expect(screen.getByText("11:04").parentElement.className).toBe("msg__stamp");
```

- [ ] **Step 2: Canlı satırın kalıbı saatle başlar, ve yazı gelirken de**

```jsx
test("the strip carries a word that says nothing about the work", () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 7, 9, 14, 32));
  try {
    render(<ChatScreen project={PROJECT} chat={CHAT} thinking progress={RUNNING_AT} />);
    // (bugünkü yorum yerinde)
    // Madde 348: the time the wait began leads, where the record's time will stand.
    expect(screen.getByTestId("live-strip").textContent).toMatch(
      /^14:32 · round 4\/16 · 12\.3k tokens · [A-Z][a-z]+ing…$/,
    );
  } finally {
    vi.useRealTimers();
  }
});
```

"the strip rides with the answer" testinin altına:

```jsx
test("the strip keeps its time once the words start arriving", () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(2026, 7, 9, 14, 32));
  try {
    render(
      <ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Here it" progress={RUNNING_AT} />,
    );
    expect(screen.getByTestId("live-strip").textContent).toMatch(/^14:32 · round 4\/16/);
  } finally {
    vi.useRealTimers();
  }
});
```

- [ ] **Step 3: 199'un bölümü `.msg__stamp`'e taşınır**

Bölümün beş testi yerine:

```jsx
// --- the notes under a message, on one row (Madde 199, Madde 348) -------------------------------
//
// Madde 199 put the arrows and the pencil on a line of their own, and the time stayed on the line
// under it: two rows of notes under one sentence (user, 11 and 28 September). Design item 139 puts
// them all on the stamp's row, the time first.

const rowOf = (container, who) => container.querySelector(`.msg--${who} .msg__stamp`);
const partsOf = (row) => [...row.children].map((part) => part.className);

test("under an edited question the time, the arrows and the pencil stand on one row", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={BRANCHED} />);
  const row = rowOf(container, "user");
  expect(partsOf(row)).toEqual(["", "versions", "msg__edit"]);
  expect(row.firstElementChild.textContent).toBe("11:04");
  expect(container.querySelector(".msg__foot")).toBeNull();
});

test("a question with nothing beside it keeps its pencil after the time", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(partsOf(rowOf(container, "user"))).toEqual(["", "msg__edit"]);
});

test("an answer's row holds its words and nothing else", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={BRANCHED} />);
  const row = rowOf(container, "ai");
  expect(partsOf(row)).toEqual([""]);
  expect(row.textContent).toBe("11:05");
});

test("while a message is being corrected the row is the time and the strip", () => {
  // Madde 197's rule stands: the pencil withdraws. The strip does not -- which version is being
  // corrected has to stay readable while it is corrected.
  const { container } = _editing(BRANCHED);
  expect(partsOf(rowOf(container, "user"))).toEqual(["", "versions"]);
});
```

- [ ] **Step 4: `Stamp.test.jsx`'e iki test**

```jsx
test("what is handed to the stamp stands after its words, on its row", () => {
  // Madde 348: a question's arrows and pencil ride on the row its time is on.
  const { container } = render(
    <Stamp at={AT}>
      <button type="button">✎</button>
    </Stamp>,
  );
  const row = container.querySelector(".msg__stamp");
  expect([...row.children].map((part) => part.tagName)).toEqual(["SPAN", "BUTTON"]);
  expect(row.firstElementChild.textContent).toBe(clockTime(AT));
});

test("the live strip starts with the time the wait began", () => {
  render(<LiveStrip at={AT} round={2} of={16} tokens={1234} />);
  expect(screen.getByTestId("live-strip").firstElementChild.textContent).toBe(
    `${clockTime(AT)} · round 2/16 · 1.2k tokens · `,
  );
});

test("before the wait is stamped the strip starts with the round", () => {
  render(<LiveStrip round={2} of={16} tokens={1234} />);
  expect(screen.getByTestId("live-strip").firstElementChild.textContent).toBe(
    "round 2/16 · 1.2k tokens · ",
  );
});
```

- [ ] **Step 5: `MessageFoot.test.jsx`'e satırsızlık**

```jsx
test("it draws no row of its own: its parts stand in the stamp's", () => {
  const { container } = render(<MessageFoot standing={BESIDE} onEdit={vi.fn()} />);
  expect([...container.children].map((part) => part.className)).toEqual(["versions", "msg__edit"]);
});
```

- [ ] **Step 6: `workspace.css.test.js` — "the notes under a bubble share one row" yerine**

```js
test("the notes under a message share the stamp's one row", () => {
  // Madde 348, design item 139: the time, the arrows and the pencil, 6 apart. The row of 199 that
  // held the last two is gone.
  const stamp = rule(".msg__stamp");
  expect(stamp).toContain("display: flex");
  expect(stamp).toContain("align-items: center");
  expect(stamp).toContain("gap: 6px");
  expect(CSS).not.toContain(".msg__foot");
});
```

- [ ] **Step 7: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` kırmızı — Step 1'in yedisi, Step 2'nin ikisi, Step
3'ün dördü, Step 4'ün ilk ikisi, Step 5, Step 6. "before the wait is stamped" bugün de yeşil. Arka
uçlar ve queen-editor'ün ön ucu yeşil.

- [ ] **Step 8: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx queen-agent/frontend/src/features/workspace/Stamp.test.jsx queen-agent/frontend/src/features/workspace/MessageFoot.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js docs/specs/2026-09-29-queenagent-m348-mesaj-alti-testler-design.md docs/plans/2026-09-29-queenagent-m348-mesaj-alti-testler-plan.md
git commit -m @'
test(queen-agent): Madde 348 red -- a message's notes stand on the stamp's one row, the time first, and the live row starts with the time

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
