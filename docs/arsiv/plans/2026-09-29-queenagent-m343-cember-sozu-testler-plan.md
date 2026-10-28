# Madde 343 — Çemberin sözü, ve dolmanın önceden duyurusu · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Çemberin `This chat is N% full` dediğini ve dörtte beşten itibaren yanında `N% full`
yazdığını tutan testler, kırmızı.

**Architecture:** `ContextGauge.test.jsx`'e çemberin cümlesini ve yanındaki yazıyı okuyan testler;
`workspace.css.test.js`'e yazının görünüşünü tutan iki kilit. Kod değişmez.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m343-cember-sozu-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; UI metni İngilizce (`This chat is N% full`, `N% full`).
- Bu turda `ContextGauge.jsx`, `workspace.css` ve ChatScreen.jsx değişmez; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Çemberin cümlesi ve yanındaki yazı, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ContextGauge.test.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — "the gauge pushes the rest of the foot to the far end" testinin altına iki test

**Interfaces:**
- Consumes: `ContextGauge({ sent, ceiling })`; test dosyasının `rule(selector)`'ı.
- Produces: uygulama turunun karşılayacağı şeyler — çemberin (`role="img"`) `title`'ı ve
  `aria-label`'ı `This chat is N% full` ya da `This chat is full`; yanında `span.context-gauge__words`,
  `aria-hidden="true"`, metni `N% full`; CSS'te `.context-gauge__words` kuralı ve `.composer__gauge`'te
  `gap: 6px`.

- [ ] **Step 1: `ContextGauge.test.jsx`'in açıklamasına 343'ü ekle, "past the ceiling" testine cümleyi ekle, "resting on it" testini değiştir**

```jsx
// Madde 92. A gauge rather than a control: it is read and never pressed, which is also why it sits
// at the far end of the foot from the three things that are.
//
// Madde 343 gave it its words: the sentence on the circle, and from four fifths of the ceiling the
// share written beside it (design items 146 and 182).
//
// What the tests read is the share the gauge settled on, not the shape it drew with it. The drawing
// is one CSS rule and jsdom does not run it.
```

```jsx
test("past the ceiling it is full rather than overfull", () => {
  // A circle cannot fill past full, and drawing the excess would draw a lie.
  render(<ContextGauge sent={60000} ceiling={50000} />);
  const circle = screen.getByRole("img");
  expect(circle.style.getPropertyValue("--filled")).toBe("1");
  expect(circle.getAttribute("title")).toBe("This chat is full");
});

test("resting on it says how full the chat is", () => {
  // The circle shows the share; this is what makes it readable, and a screen reader hears the same.
  render(<ContextGauge sent={41000} ceiling={50000} />);
  const circle = screen.getByRole("img");
  expect(circle.getAttribute("title")).toBe("This chat is 82% full");
  expect(circle.getAttribute("aria-label")).toBe("This chat is 82% full");
});
```

- [ ] **Step 2: Dosyanın sonuna beş testi ekle**

```jsx
test("the share is rounded down, so it never says 100 before the chat is full", () => {
  render(<ContextGauge sent={49990} ceiling={50000} />);
  expect(screen.getByRole("img").getAttribute("title")).toBe("This chat is 99% full");
});

test("a chat with an answer is at least 1% full", () => {
  // Rounded down, a small chat would say 0% beside a circle that is there.
  render(<ContextGauge sent={100} ceiling={50000} />);
  expect(screen.getByRole("img").getAttribute("title")).toBe("This chat is 1% full");
});

test("below four fifths the circle stands alone", () => {
  // 79.98% would round to 80; the words wait for the chat itself to reach four fifths.
  const { container } = render(<ContextGauge sent={39990} ceiling={50000} />);
  expect(container.querySelector(".context-gauge__words")).toBeNull();
});

test("from four fifths the share stands beside the circle", () => {
  // Hidden from a screen reader, which already reads the circle's sentence.
  const { container } = render(<ContextGauge sent={40000} ceiling={50000} />);
  const words = container.querySelector(".context-gauge__words");
  expect(words?.textContent).toBe("80% full");
  expect(words.getAttribute("aria-hidden")).toBe("true");
});

test("a full chat's circle has no words beside it", () => {
  // What a full chat says is its own notice's (Madde 352), not a line beside the circle.
  const { container } = render(<ContextGauge sent={50000} ceiling={50000} />);
  expect(container.querySelector(".context-gauge__words")).toBeNull();
});
```

- [ ] **Step 3: `workspace.css.test.js`'e iki kilit ekle**, "the gauge pushes the rest of the foot to the far end"in hemen altına:

```js
test("the gauge's words are the notes' mono in the pickers' ink", () => {
  // Madde 343, design items 146 and 182. Not --muted: that is 3.7:1 on the composer's box.
  const words = rule(".context-gauge__words");
  expect(words).toContain("font-family: var(--font-mono)");
  expect(words).toContain("font-size: 11.5px");
  expect(words).toContain("color: #6b6259");
});

test("the words stand 6 from the circle, the stamp's gap", () => {
  expect(rule(".composer__gauge")).toContain("gap: 6px");
});
```

- [ ] **Step 4: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` yedi kırmızı — `ContextGauge.test.jsx`'te "past the
ceiling", "resting on it", "rounded down", "at least 1%", "from four fifths"; `workspace.css.test.js`'te
iki kilit. "below four fifths" ve "a full chat's circle" bugün de yeşil. Arka uçlar değişmez:
queen-agent yeşil, queen-editor 377'nin bilinen iki kırmızısı. queen-editor'ün ön ucu yeşil.

- [ ] **Step 5: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/ContextGauge.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js docs/specs/2026-09-29-queenagent-m343-cember-sozu-testler-design.md docs/plans/2026-09-29-queenagent-m343-cember-sozu-testler-plan.md
git commit -m @'
test(queen-agent): Madde 343 red -- the ring says This chat is N% full, and from four fifths writes N% full beside it

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
