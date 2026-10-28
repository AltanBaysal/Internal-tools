# Madde 347 — Sohbet başlığında yalnız sohbetin adı · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sohbet başlığında yalnız sohbetin adı olduğunu tutan iki test, kırmızı; başlığın düğmesine
basan üç App testi çubuğun `Exit project`'ine geçmiş, yeşil.

**Architecture:** `ChatScreen.test.jsx`'teki iki başlık testi tersine döner. `App.test.jsx`'te proje
ekranına `← Old` ile giden üç test oraya `Exit project` ile gider.

**Tech Stack:** vitest, Testing Library, jsdom.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m347-sohbet-basligi-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce.
- Bu turda `ChatScreen.jsx`, `App.jsx` ve `workspace.css` değişmez; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Başlıkta yalnız ad, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` — *"the breadcrumb names
  the project and the chat"* ve *"the way back to the project stays"*
- Modify: `queen-agent/frontend/src/App.test.jsx` — `name: "← Old"` geçen üç satır

**Interfaces:**
- Consumes: `ChatScreen`'in `chat` özelliği, `.chat__header`; `Bar`'ın `Exit project` düğmesi.
- Produces: uygulama turunun karşılayacağı tek şey — `.chat__header`'ın yazısı yalnız `chat.title`,
  başlıkta düğme yok, ekranda projenin adı yok.

- [ ] **Step 1: ChatScreen'in iki testini ters çevir**

```jsx
test("the chat's header holds its name and nothing else", () => {
  // Design items 152 and 168: the project's name lives in the bar alone, so the header is no longer
  // a breadcrumb.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  expect(container.querySelector(".chat__header").textContent).toBe("Write the intro");
});

test("the header offers no way back, and the project's name is nowhere on the screen", () => {
  // Leaving the project is the bar's Exit project; the sidebar already opens the project's other
  // chats.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} onBack={vi.fn()} />);
  expect(container.querySelector(".chat__header button")).toBeNull();
  expect(screen.queryByText(/Thesis research/)).toBeNull();
});
```

- [ ] **Step 2: App'in üç testini Exit project'e geçir**

Üç yerde:

```jsx
  fireEvent.click(screen.getByRole("button", { name: "← Old" }));
```

yerine

```jsx
  fireEvent.click(screen.getByRole("button", { name: "Exit project" }));
```

Beklenen yol aynı kalır: tek projeli testte `/` açılışın kuralıyla `/p/p1`'e iner.

- [ ] **Step 3: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent'ın ön ucu iki kırmızı — iki yeni test, başlıkta `← Thesis research` düğmesini
gördükleri için; 695 test. Üç App testi yeşil. Öteki süitler yeşil.

- [ ] **Step 4: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx queen-agent/frontend/src/App.test.jsx docs/specs/2026-09-29-queenagent-m347-sohbet-basligi-testler-design.md docs/plans/2026-09-29-queenagent-m347-sohbet-basligi-testler-plan.md
git commit -m @'
test(queen-agent): Madde 347 red -- the chat header holds the chat name alone, with no way back and no project name

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
