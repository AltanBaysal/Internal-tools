# Madde 357 — Kırpılmış sohbette çizgi · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kaydın `trimmed`'ının gösterdiği yerde çizgiyi, görünüşünü ve `Continue here`'den sonra
çıkışını tutan testler, kırmızı.

**Architecture:** Yalnız ön uç: `ChatScreen`'e çizginin yeri, `workspace.css`'e görünüşü ve
yapışıklığı, `App`'e 352'nin kırpma yoluyla uçtan uca çıkışı. Arka uç `trimmed`'ı 345'ten beri
veriyor.

**Tech Stack:** vitest, Testing Library, jsdom.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m357-kirpma-cizgisi-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; çizginin metni tam olarak
  `Messages above this line are no longer sent to the model`.
- Bu turda yalnız test dosyaları ve bu iki belge değişir; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Çizginin yeri

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` — dosyanın sonuna

**Interfaces:**
- Consumes: dosyanın `CHAT`, `PROJECT`'i.
- Produces: uygulama turunun karşılayacağı şey — `ChatScreen` `chat.trimmed`'ı okur; sıfırdan büyükse
  `chat__column`'un doğrudan çocuğu olarak, `trimmed` sıradaki mesajın hemen önünde bir `p.trimmed`.

- [ ] **Step 1: İki test**

```jsx
// --- the trim's line (Madde 357) -----------------------------------------------------------------

const TRIMMED = {
  ...CHAT,
  trimmed: 2,
  messages: [
    ...CHAT.messages,
    { role: "user", at: new Date(2026, 7, 9, 11, 6).toISOString(), text: "Shorter" },
    { role: "ai", at: new Date(2026, 7, 9, 11, 7).toISOString(), text: "Shorter it is." },
  ],
};

test("a trimmed chat draws the line before the first message still sent", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={TRIMMED} />);
  const lines = container.querySelectorAll(".trimmed");
  expect(lines).toHaveLength(1);
  const [line] = lines;
  expect(line.tagName).toBe("P");
  expect(line.parentElement.className).toBe("chat__column");
  expect(line.textContent).toBe("Messages above this line are no longer sent to the model");
  // The record's number is where the model starts reading: the first turn above, the second below.
  expect(line.previousElementSibling.textContent).toContain("Here it is.");
  expect(line.nextElementSibling.querySelector(".msg__bubble").textContent).toBe("Shorter");
});

test("a chat nobody trimmed draws no line", () => {
  const { container, rerender } = render(
    <ChatScreen project={PROJECT} chat={{ ...TRIMMED, trimmed: 0 }} />,
  );
  expect(container.querySelector(".trimmed")).toBeNull();
  // A record from before Madde 345 carries no number at all.
  rerender(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(container.querySelector(".trimmed")).toBeNull();
});
```

### Task 2: Görünüşü

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — dosyanın sonuna

**Interfaces:**
- Consumes: dosyanın `rule` ve `grouped`'ı.
- Produces: uygulama turunun karşılayacağı şey — `.trimmed` kuralı ve gruplu
  `.trimmed::before,\n.trimmed::after` kuralı, tasarımın `kit.css`'indeki gibi.

- [ ] **Step 1: İki test**

```js
// Madde 357 (the design's items 147 and 182, kit.css's .trimmed). jsdom lays nothing out, so the
// hold at the chat's lower edge is locked here as the rule that makes it; the browser shows it.
test("the trim's line holds at the chat's lower edge on the page's own ground", () => {
  const line = rule(".trimmed");
  expect(line).toContain("position: sticky");
  expect(line).toContain("bottom: 0");
  // Without a ground of its own the words scrolling under it would show through.
  expect(line).toContain("background: var(--canvas)");
  expect(line).toContain("display: flex");
  expect(line).toContain("padding: 8px 0");
});

test("the trim's line reads as a note between two rules", () => {
  const line = rule(".trimmed");
  expect(line).toContain("font-family: var(--font-mono)");
  expect(line).toContain("font-size: 11.5px");
  expect(line).toContain("color: #6b6259");
  expect(grouped(".trimmed::before,")).toContain("border-top: 1px solid var(--line)");
});
```

### Task 3: Uçtan uca

**Files:**
- Modify: `queen-agent/frontend/src/App.test.jsx` — dosyanın sonuna, 352'nin bölümünün arkasına

**Interfaces:**
- Consumes: 352'nin `stubFullChat`'i — kırpma kapısı kaydı `trimmed: 2` yapar; mesajlar `go on`,
  `First answer.`, `go on`, `Last answer.`.
- Produces: hiçbir yeni ad; App kaydı olduğu gibi `ChatScreen`'e verir.

- [ ] **Step 1: Bir test**

```jsx
// --- the trim's line (Madde 357) -----------------------------------------------------------------

test("after Continue here a line parts the messages no longer sent from the rest", async () => {
  stubFullChat();
  const { container } = render(<App />);
  await screen.findByText("This chat is full.");
  expect(container.querySelector(".trimmed")).toBeNull();

  fireEvent.click(screen.getByRole("button", { name: "Continue here" }));
  const line = await screen.findByText("Messages above this line are no longer sent to the model");
  // The trimmed record says 2: the first turn stays on screen above the line, the last below it.
  expect(line.previousElementSibling.textContent).toContain("First answer.");
  expect(line.nextElementSibling.querySelector(".msg__bubble").textContent).toBe("go on");
});
```

### Task 4: Kırmızıyı gör ve commit'le

- [ ] **Step 1: Dört satırı paralel koş**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent'ın ön ucunda dört kırmızı — ChatScreen'in *"a trimmed chat draws the line…"*'ı,
iki CSS kilidi ve App'in testi. *"a chat nobody trimmed draws no line"* bugün de geçer, kilit. Arka uç
ve queen-editor'ün iki süiti yeşil.

- [ ] **Step 2: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js queen-agent/frontend/src/App.test.jsx docs/superpowers/specs/2026-09-29-queenagent-m357-kirpma-cizgisi-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m357-kirpma-cizgisi-testler-plan.md
git commit -m @'
test(queen-agent): Madde 357 red -- a trimmed chat draws its line before the first message still sent

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
