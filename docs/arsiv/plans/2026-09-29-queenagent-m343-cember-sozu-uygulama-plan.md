# Madde 343 — Çemberin sözü, ve dolmanın önceden duyurusu · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Çember `This chat is N% full` der, ve dörtte beşten itibaren yanında `N% full` yazar; `c715bbda`'nın
yedi kırmızısı yeşile döner.

**Architecture:** `ContextGauge.jsx` yüzdeyi tamsayılarla hesaplar ve bir fragment döner: çember, ve
80–99 arasında yanında aria-hidden bir yazı. `workspace.css`'e yazının kuralı ve yuvanın `gap`'i.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m343-cember-sozu-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod ve yorum İngilizce; UI metni İngilizce.
- `workspace.css`'te yalnız `.composer__gauge` ve yeni `.context-gauge__words` kuralına dokunulur;
  öteki kurallar yerinden oynamaz.
- ChatScreen.jsx, Composer.jsx ve sunucu değişmez; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Çemberin sözü ve yazısı, yeşil

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ContextGauge.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` — `.composer__gauge` ve `.context-gauge`'in altı

**Interfaces:**
- Consumes: `ContextGauge({ sent, ceiling })`'ın bugünkü çağrısı (ChatScreen.jsx), ve Composer'ın
  `gauge`'i `.composer__gauge`'le sarması.
- Produces: `c715bbda`'nın testlerinin okuduğu şeyler — çemberin `title`/`aria-label`'ı,
  `span.context-gauge__words`, CSS kuralları.

- [ ] **Step 1: `ContextGauge.jsx`'i yaz**

```jsx
// Madde 92. A gauge, not a control: it is read and never pressed, which is why it sits at the far
// end of the composer's foot from the three things that are.
//
// The share is settled here and the drawing is left to one CSS rule. Not for testability -- for
// truth: how full the circle is, is a number, and an arc is only one way of saying it.
//
// Madde 343 gave it its words (design items 146 and 182): the circle's sentence, and from four fifths
// of the ceiling the share written beside it, so a chat says it is filling before it is full.

// Four fifths, in percent. A share of the ceiling the server sends with the number, not a second copy
// of it, and it decides only what is shown: whether a chat may take a turn is the server's rule.
const NEARLY_FULL = 80;

export default function ContextGauge({ sent, ceiling }) {
  // Nothing measured yet, so there is nothing to read. An empty circle would be a mark that is
  // always there and says nothing -- the gauge is born when the first answer comes back.
  if (!sent || !ceiling) return null;
  // A circle cannot fill past full, and drawing the excess would draw a lie.
  const filled = Math.min(sent / ceiling, 1);
  // In whole numbers, and rounded down: it says 100 only once the chat is full and 80 only once it
  // is nearly full. At least 1, since a circle that is drawn has something in it. Multiplied before
  // dividing, because 0.82 * 100 in floating point can land a hair under 82.
  const percent = Math.min(100, Math.max(1, Math.floor((sent * 100) / ceiling)));
  const said = percent === 100 ? "This chat is full" : `This chat is ${percent}% full`;
  return (
    <>
      <span
        className="context-gauge"
        style={{ "--filled": String(filled) }}
        /* Drawn rather than written, so it needs a name -- and the same sentence serves a mouse
           resting on it and a screen reader reaching it. */
        role="img"
        title={said}
        aria-label={said}
      />
      {/* The circle's sentence again, so a screen reader skips it. A full chat has none: what it
          says is its own notice's. */}
      {percent >= NEARLY_FULL && percent < 100 ? (
        <span className="context-gauge__words" aria-hidden="true">{`${percent}% full`}</span>
      ) : null}
    </>
  );
}
```

- [ ] **Step 2: `workspace.css`'te `.composer__gauge`'e `gap: 6px` ekle, `.context-gauge`'in altına yazının kuralını koy**

```css
/* The foot's other end since Madde 92. Not `justify-content: space-between` on the foot itself:
   Skills, the model's name and Send are three separate items in that row, and spreading the row
   would put its whole width between them. The circle and its words stand 6 apart, the stamp's gap. */
.composer__gauge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-right: auto;
}
```

```css
/* Madde 343: the share beside the circle once the chat is nearly full, in the notes' mono and the
   pickers' ink -- --muted is 3.7:1 on the composer's box. */
.context-gauge__words {
  font-family: var(--font-mono);
  font-size: 11.5px;
  color: #6b6259;
  white-space: nowrap;
}
```

- [ ] **Step 3: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent arka ucu 933 yeşil; ön ucu 659 yeşil; queen-editor arka ucu 377'nin bilinen iki
kırmızısıyla, ön ucu 749 yeşil.

- [ ] **Step 4: Commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/ContextGauge.jsx queen-agent/frontend/src/features/workspace/workspace.css docs/specs/2026-09-29-queenagent-m343-cember-sozu-uygulama-design.md docs/plans/2026-09-29-queenagent-m343-cember-sozu-uygulama-plan.md
git commit -m @'
feat: Madde 343 -- the ring says This chat is N% full, and from four fifths writes N% full beside it

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
