# Madde 354 — Cevabın altında cached ve missed · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Biten cevabın altında `saat · N cached · N missed`, cached yeşil, missed kırmızı; test
turunun kırmızı testleri yeşil.

**Architecture:** `Stamp` sözlerin `span`'ına iki renkli `span` koyar, `missed`'i `sent - cached`
diye hesaplar; `workspace.css`'e iki renk; `routes.py`'de eskiyen bir yorum düzelir.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m354-cached-missed-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod ve yorum İngilizce; UI metni `cached`, `missed`.
- Renkler: `.msg__stamp-cached { color: #536747; }`, `.msg__stamp-missed { color: var(--destructive); }`.
- `LiveStrip`, sunucunun kodu ve `Usage` değişmez; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Cached ve missed, yeşil

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/Stamp.jsx` (`Stamp` ve üstündeki yorum)
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` (`.msg__stamp`'in altı)
- Modify: `queen-agent/backend/features/workspace/presentation/routes.py:393-394` (yalnız yorum)

**Interfaces:**
- Consumes: test turunun commit'lediği testler; `shorten`, `clockTime`.
- Produces: `Stamp({ at, usage, children })` — `usage.sent` sıfır değilken sözlerin `span`'ında
  `span.msg__stamp-cached` ve `span.msg__stamp-missed`.

- [ ] **Step 1: `Stamp.jsx` — bileşen ve yorumu**

```jsx
// The notes that close a message, on one row: when it was said, and -- for an answer that was
// measured -- what it sent; then whatever the message hands over, which under a question is its
// versions and its pencil (Madde 348, design item 139). Under the message rather than over it,
// because a note about a thing is read after it. One row rather than two, and no name in it: the
// sidebar carries the name, and which side a message sits on says who wrote it.
//
// What it sent, in two parts (Madde 354, design items 189 and 192): what the service already had
// and what it did not. A cached token costs about a fiftieth of one that missed, so the one total
// this used to draw priced the two alike and said nothing about the bill. Missed is the rest of
// `sent`, because `cached` is a part of it rather than an addition to it. What the model wrote is
// not drawn: the owner asked for the two and nothing else. The counts drop when nothing was sent --
// an answer from before this existed reads back as zero, and a number there would claim a
// measurement nobody took. The time never drops: it was said at a time either way.
export default function Stamp({ at, usage, children }) {
  // The wait is stamped by an effect, so the first draw of a pending box has no time yet. Nothing
  // rather than an empty line.
  if (!at) return null;
  return (
    <div className="msg__stamp">
      {/* An element of their own, so the row's gap parts the words from the arrows and the pencil,
          and never a word from a glyph. */}
      <span>
        {clockTime(at)}
        {usage?.sent ? (
          <>
            {" · "}
            {/* A word beside each colour, so the two are told apart without it. */}
            <span className="msg__stamp-cached">{`${shorten(usage.cached)} cached`}</span>
            {" · "}
            <span className="msg__stamp-missed">{`${shorten(usage.sent - usage.cached)} missed`}</span>
          </>
        ) : null}
      </span>
      {children}
    </div>
  );
}
```

- [ ] **Step 2: `workspace.css` — `.msg__stamp`'in altına**

```css
/* Madde 354, design items 189 and 192: what an answer sent, split under it. Cached is the app's
   only green (#6f8a5f, the saved tick) darkened until it reads on the canvas: 5.7:1 there, where
   the lighter one is 3.5:1. Missed is the destructive red, marking a cost here rather than a
   destruction -- the design's own exception to red being for destruction alone. */
.msg__stamp-cached {
  color: #536747;
}

.msg__stamp-missed {
  color: var(--destructive);
}
```

- [ ] **Step 3: `routes.py` — yorum**

```python
                # The breakdown travels whole: the screen draws `sent` and `cached` under an
                # answer, and `answered` stays for the context work to read.
```

- [ ] **Step 4: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil.

- [ ] **Step 5: Commit**

```powershell
git add queen-agent/frontend/src/features/workspace/Stamp.jsx queen-agent/frontend/src/features/workspace/workspace.css queen-agent/backend/features/workspace/presentation/routes.py docs/superpowers/specs/2026-09-29-queenagent-m354-cached-missed-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m354-cached-missed-uygulama-plan.md
git commit -m @'
feat: Madde 354 -- under a finished answer, green cached and red missed, and nothing for what the model wrote

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
