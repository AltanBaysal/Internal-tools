# Madde 354 — Cevabın altında cached ve missed · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Biten cevabın altında `saat · N cached · N missed` yazdığını, renklerin sınıflarını,
`answered`'ın görünmediğini ve eski cevapta yalnız saatin kaldığını tutan testler, kırmızı.

**Architecture:** `Stamp.test.jsx`'in cevap testi dört teste bölünür; `ChatScreen.test.jsx`'in Madde 68
bölümü ve `App.test.jsx`'in tur sonu testi yeni satırı okur; `workspace.css.test.js`'e iki rengin
kilidi. Kod değişmez.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m354-cached-missed-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; UI metni İngilizce: `cached`, `missed`.
- Renkler tasarımınki: `#536747`, `var(--destructive)`; sınıflar `msg__stamp-cached`, `msg__stamp-missed`.
- Bu turda `Stamp.jsx`, `workspace.css` ve `routes.py` değişmez; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Cached ve missed'in testleri, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/Stamp.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` (Madde 68 bölümü)
- Modify: `queen-agent/frontend/src/App.test.jsx` (`when the turn ends the strip is gone…`)
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js`

**Interfaces:**
- Consumes: `Stamp({ at, usage, children })`, `clockTime`; `ChatScreen`'in `CHAT`'i ve `withUsage`'ı;
  `App.test`'in `_turnThatReports`'u; css testinin `rule`'u.
- Produces: uygulama turunun karşılayacağı şeyler — `Stamp` `usage.sent` sıfır değilken sözlerin
  `span`'ının içinde saatten sonra ` · `, `span.msg__stamp-cached` (`${shorten(cached)} cached`), ` · `,
  `span.msg__stamp-missed` (`${shorten(sent - cached)} missed`) çizer; `answered`'ı ve `tokens`
  kelimesini çizmez. CSS'te `.msg__stamp-cached { color: #536747; }` ve
  `.msg__stamp-missed { color: var(--destructive); }`.

- [ ] **Step 1: `Stamp.test.jsx` — "an answer's stamp says when and what it spent" yerine**

```jsx
// Madde 354 (design items 189, 192): under a finished answer what it sent, split into the part the
// service already had and the part it did not. What the model wrote is not shown.
const SPLIT = { sent: 61240, cached: 49152, answered: 684 };
const wordsOf = (container) => container.querySelector(".msg__stamp").firstElementChild;

test("a finished answer's stamp says what came from the cache and what missed it", () => {
  const { container } = render(<Stamp at={AT} usage={SPLIT} />);
  expect(wordsOf(container).textContent).toBe(`${clockTime(AT)} · 49.2k cached · 12.1k missed`);
});

test("cached and missed each wear a class of their own, inside the words", () => {
  // The class is what the stylesheet colours them by: green for cached, red for missed.
  const { container } = render(<Stamp at={AT} usage={SPLIT} />);
  const words = wordsOf(container);
  expect(words.querySelector(".msg__stamp-cached")?.textContent).toBe("49.2k cached");
  expect(words.querySelector(".msg__stamp-missed")?.textContent).toBe("12.1k missed");
});

test("what the model wrote is not on the row", () => {
  const { container } = render(<Stamp at={AT} usage={SPLIT} />);
  const row = container.querySelector(".msg__stamp").textContent;
  expect(row).not.toContain("684");
  expect(row).not.toContain("tokens");
});

test("an answer the cache served whole still says what it missed", () => {
  const { container } = render(<Stamp at={AT} usage={{ sent: 3072, cached: 3072, answered: 58 }} />);
  expect(wordsOf(container).textContent).toBe(`${clockTime(AT)} · 3.1k cached · 0 missed`);
});
```

"nothing spent leaves the time alone" yerinde kalır.

- [ ] **Step 2: `ChatScreen.test.jsx` — Madde 68'in dört testi**

Bölümün başı ve dört testi yerine:

```jsx
// --- what the answer spent (Madde 68, Madde 354) -------------------------------------------------
//
// The number is 68's; where it is drawn is 83's and 348's. Madde 354 (design items 189, 192) split
// it: what came from the cache and what missed it, and nothing for what the model wrote.

const withUsage = (usage) => ({
  ...CHAT,
  messages: [CHAT.messages[0], { ...CHAT.messages[1], usage }],
});
const answerWords = (container) =>
  container.querySelector(".msg--ai .msg__stamp").firstElementChild.textContent;

test("an answer says what came from the cache and what missed it, beside when it was said", () => {
  const { container } = render(
    <ChatScreen project={PROJECT} chat={withUsage({ sent: 12400, cached: 9100, answered: 842 })} />,
  );
  expect(answerWords(container)).toBe("11:05 · 9.1k cached · 3.3k missed");
});

test("a small answer is not dressed up as a big one", () => {
  const { container } = render(
    <ChatScreen project={PROJECT} chat={withUsage({ sent: 300, cached: 0, answered: 42 })} />,
  );
  expect(answerWords(container)).toBe("11:05 · 0 cached · 300 missed");
});

test("an answer nobody measured still says when it was said", () => {
  // Zero is what an answer from before this existed reads back as, and a count under it would claim
  // a measurement nobody took. The time is not a measurement -- it was said at a time either way.
  render(<ChatScreen project={PROJECT} chat={withUsage({ sent: 0, cached: 0, answered: 0 })} />);
  expect(screen.getByText("11:05").parentElement.className).toBe("msg__stamp");
  expect(screen.queryByText(/cached|missed/)).toBeNull();
});

test("the user's own message never carries a count", () => {
  // Spending is what an answer does. A number under the question would read as its price.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={withUsage({ sent: 300, cached: 0, answered: 42 })} />,
  );
  expect(screen.getByText("11:04").parentElement.className).toBe("msg__stamp");
  const question = container.querySelector(".msg--user").textContent;
  expect(question).not.toContain("cached");
  expect(question).not.toContain("missed");
});
```

- [ ] **Step 3: `App.test.jsx` — tur bitince**

```jsx
  // What it cost rather than how big it got, and that difference is on purpose: the strip answers
  // how big the turn got, the stamp what came from the cache and what missed it (Madde 354). 9000
  // sent, 3000 of it cached; the 100 the model wrote is not shown.
  expect(screen.getByText("3.0k cached")).toBeTruthy();
  expect(screen.getByText("6.0k missed")).toBeTruthy();
```

- [ ] **Step 4: `workspace.css.test.js` — satırın bölümünün sonuna**

```js
test("cached is the design's darker green and missed the destructive red", () => {
  // Madde 354, design items 189 and 192: the app's only green, darkened to read on the canvas, and
  // the red that marks a cost here rather than a destruction.
  expect(rule(".msg__stamp-cached")).toContain("color: #536747");
  expect(rule(".msg__stamp-missed")).toContain("color: var(--destructive)");
});
```

- [ ] **Step 5: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` kırmızı — Step 1'in dördü, Step 2'nin ilk ikisi,
Step 3, Step 4. Step 2'nin son ikisi ve "nothing spent leaves the time alone" yeşil. Arka uçlar ve
queen-editor'ün ön ucu yeşil.

- [ ] **Step 6: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/Stamp.test.jsx queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx queen-agent/frontend/src/App.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js docs/specs/2026-09-29-queenagent-m354-cached-missed-testler-design.md docs/plans/2026-09-29-queenagent-m354-cached-missed-testler-plan.md
git commit -m @'
test(queen-agent): Madde 354 red -- a finished answer says what came from the cache and what missed it, and not what the model wrote

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
