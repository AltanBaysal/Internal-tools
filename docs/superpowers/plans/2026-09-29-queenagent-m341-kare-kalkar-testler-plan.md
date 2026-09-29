# Madde 341 — Yanıp sönen kare kalkar · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Süren cevabın yazısının sonunda kare olmadığını tutan tek test, kırmızı; kareyi anlatan
testler silinmiş.

**Architecture:** `ChatScreen.test.jsx`'teki kare testi tersine döner. `Markdown.test.jsx`'in ve
`workspace.css.test.js`'in kare testleri silinir.

**Tech Stack:** vitest, Testing Library, jsdom.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m341-kare-kalkar-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce.
- Bu turda `Markdown.jsx`, `ChatScreen.jsx` ve `workspace.css` değişmez; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Kare yok, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` — *"only the text still arriving carries a caret"*
- Modify: `queen-agent/frontend/src/features/workspace/Markdown.test.jsx` — 75–118. satırlar
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — *"the caret is the design's block…"*

**Interfaces:**
- Consumes: `ChatScreen`'in `streamingText` özelliği, süren mesajın `data-testid="streaming"`'i.
- Produces: uygulama turunun karşılayacağı tek şey — süren cevabın `.md`'si metinden başka bir şey
  taşımaz.

- [ ] **Step 1: ChatScreen'in testini ters çevir**

```jsx
test("text still arriving ends with the text and nothing after it", () => {
  // Design item 156: the live stamp's word already says the answer is running, so no square blinks
  // at the end of the words.
  const { container } = render(
    <ChatScreen project={PROJECT} chat={CHAT} thinking streamingText="Here it" />,
  );
  expect(container.querySelector("[data-testid=streaming] .md").innerHTML).toBe("<p>Here it</p>");
});
```

- [ ] **Step 2: Markdown'ın kare testlerini sil**

75. satırdaki yorumdan dosyanın sonuna kadar: yorum, `drawStreaming`, ve sekiz test (*"a finished
answer carries no caret"* – *"an answer that is still nothing but a caret still draws it"*).

- [ ] **Step 3: CSS'in kare testini sil**

`workspace.css.test.js`'teki *"the caret is the design's block and borrows the dots' blink"* testi,
bütünüyle.

- [ ] **Step 4: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent'ın ön ucu bir kırmızı — yeni test, `<p>Here it<span class="caret"></span></p>`
gördüğü için; 652 − 1 − 8 − 1 + 1 = 643 test. queen-editor'ün arka ucu 377'nin bilinen iki kırmızısı.
Öteki süitler yeşil.

- [ ] **Step 5: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx queen-agent/frontend/src/features/workspace/Markdown.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js docs/superpowers/specs/2026-09-29-queenagent-m341-kare-kalkar-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m341-kare-kalkar-testler-plan.md
git commit -m @'
test(queen-agent): Madde 341 red -- an answer still arriving ends with its text and no blinking square

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
