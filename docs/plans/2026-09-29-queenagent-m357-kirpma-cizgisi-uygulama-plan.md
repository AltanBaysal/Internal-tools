# Madde 357 — Kırpılmış sohbette çizgi · uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kırpılmış sohbette, kaydın `trimmed`'ının gösterdiği mesajın önünde tasarımın yapışık
çizgisi; kırmızı testler yeşil.

**Architecture:** `ChatScreen`'in mesaj `map`'i her mesajı bir `Fragment`'la sarar ve `trimmed` sıradaki
mesajın önüne `p.trimmed` koyar. `workspace.css` tasarımın `kit.css`'indeki iki kuralı alır.

**Tech Stack:** React 18, CSS; vitest, Testing Library, jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m357-kirpma-cizgisi-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Çizginin metni tam olarak `Messages above this line are no longer sent to the model`.
- `dist` derlenmez (koşuyu yöneten Claude derler). `@keyframes` eklenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Çizgi ve görünüşü

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx` — import satırı, dosyanın
  başındaki sabitler, mesaj `map`'i
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` — `.full__actions`'ın arkası

**Interfaces:**
- Consumes: kaydın `trimmed`'ı (sayı; `0` ya da yok = kırpılmamış).
- Produces: `chat__column`'un doğrudan çocuğu `p.trimmed`.

- [ ] **Step 1: `Fragment`'ı içeri al**

```jsx
import { Fragment, useEffect, useRef, useState } from "react";
```

- [ ] **Step 2: Sabit, `STICK_WITHIN`'in arkasına**

```jsx
// The design's words for the trim (item 147). Where the line stands is the record's `trimmed` --
// the server's count, never one the screen works out (FOUNDATION, Decision 4).
const TRIMMED_LINE = "Messages above this line are no longer sent to the model";
```

- [ ] **Step 3: `map`**

Anahtar `div`'den `Fragment`'a geçer; `div`'in içi değişmez.

```jsx
{chat.messages.map((message, index) => (
  <Fragment key={`${message.at}-${index}`}>
    {/* Before the first message still sent. Zero is a chat nobody trimmed, and a record from
        before Madde 345 carries no number, which equals no index. */}
    {index > 0 && index === chat.trimmed ? <p className="trimmed">{TRIMMED_LINE}</p> : null}
    <div
      className={...}
    >
      ...
    </div>
  </Fragment>
))}
```

- [ ] **Step 4: CSS, `.full__actions`'ın arkasına**

```css
/* The trim's line (Madde 357, the design's items 147 and 182): before the first message still sent
   to the model, its words between two rules, and it wraps rather than pushing the page sideways.
   It holds at the chat's lower edge while the messages above it are read, on the page's ground so
   the words scrolling under it do not show through. #6b6259 rather than --muted: a sentence to
   read, and --muted holds 3.43:1 on the page. */
.trimmed {
  position: sticky;
  bottom: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  padding: 8px 0;
  background: var(--canvas);
  font-family: var(--font-mono);
  font-size: 11.5px;
  line-height: 1.6;
  color: #6b6259;
  text-align: center;
}

.trimmed::before,
.trimmed::after {
  content: "";
  flex: 1 1 16px;
  border-top: 1px solid var(--line);
}
```

- [ ] **Step 5: Dört satırı paralel koş**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dört süit yeşil.

- [ ] **Step 6: Commit**

```powershell
git add queen-agent/frontend/src/features/workspace/ChatScreen.jsx queen-agent/frontend/src/features/workspace/workspace.css docs/specs/2026-09-29-queenagent-m357-kirpma-cizgisi-uygulama-design.md docs/plans/2026-09-29-queenagent-m357-kirpma-cizgisi-uygulama-plan.md
git commit -m @'
feat: Madde 357 -- a trimmed chat draws its line before the first message still sent, held at the lower edge while older messages are read

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
