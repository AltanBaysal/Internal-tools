# Madde 356 — Açık dosya da çekilerek genişler · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sohbetin yanındaki panel okurken de App'in tuttuğu genişlikte çizilir ve sol kenarından
çekilir; tutma yeri okuyucunun üstünde durur.

**Architecture:** App'e dokunulmaz — genişlik ve kural (`railWidth`, `resizeRail`, `railWidthFor`)
zaten tek. `FileRail.jsx` okurken genişliği yazar, `rail--dragging`'i ekler ve `Grip`'i çizer;
`workspace.css` `.rail--open`'ın `560`'ını kaldırır ve `.rail__grip`'e `z-index: 1` verir.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m356-acik-dosya-genisligi-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod ve yorum İngilizce; yorum NEDEN'i ve bugünü söyler.
- Test dosyalarına dokunulmaz.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Okuyan panel tutulan genişlikte ve çekilir

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/FileRail.jsx` — baştaki yorum, `railClass`, `railStyle`, okuma dalı
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` — `.rail__grip`, `.rail--open`
- Modify: `queen-agent/frontend/src/features/workspace/railWidth.js` — `MAX_RAIL_WIDTH`'in yorumu

**Interfaces:**
- Consumes: kırmızı commit'in (`4aca3d1b`) testleri; `FileRail`'in bugünkü prop'ları (`reading`,
  `collapsed`, `width`, `onResize`).
- Produces: dışarıya yeni bir ad yok.

- [ ] **Step 1: `FileRail.jsx`, baştaki yorumun son paragrafı**

```jsx
// Madde 50 gave the rail a grip on its left edge, and Madde 356 (the design's items 158 and 177) gave
// it to the open file too: the list and the document are one width. What travels back up is the
// width that was asked for, not a decision: whether that is a width at all, or is narrow enough to
// mean closing, belongs with the folded state, which is App's (railWidth.js).
```

- [ ] **Step 2: `railClass` ve `railStyle`**

```jsx
function railClass(reading, collapsed, dragging) {
  // Said out loud because the stylesheet has to hear it: the width easing is for folding and opening,
  // and a rail following the pointer has to arrive with it -- the list's and the document's alike.
  const drag = dragging ? " rail--dragging" : "";
  if (reading?.name) return `rail rail--open${drag}`;
  if (collapsed) return "rail rail--collapsed";
  return `rail${drag}`;
}

// The list and the open file are one width (Madde 356), so the held width is written for either.
// Folded, the design's strip stands instead -- but only once nothing is being read: a document pulled
// under the minimum stays at its width, and the fold shows when it closes.
function railStyle(reading, collapsed, width) {
  if (!width || (collapsed && !reading?.name)) return undefined;
  return { width: `${width}px` };
}
```

- [ ] **Step 3: okuma dalı** — `railClass(reading, collapsed)` → `railClass(reading, collapsed, dragging)`,
  ve `FilePanel`'in önüne:

```jsx
        {onResize ? <Grip width={width} onResize={onResize} onDrag={setDragging} /> : null}
```

- [ ] **Step 4: `workspace.css`**

`.rail__grip`'in yorumunun sonuna ve kuralına:

```css
/* ... which the grip sits on top of. Above the reader as well: the reader's fadeIn (opacity) lifts it
   into the grip's paint layer, and as the later sibling it would cover the grip, so the pointer never
   reached the edge (the design's item 177). */
.rail__grip {
  ...
  width: 6px;
  z-index: 1;
  cursor: col-resize;
}
```

`.rail--open`:

```css
/* Reading empties the rail rather than splitting it: the document is the only thing in here. It
   used to share the room with the list, which cost the document 200 pixels to offer what the back
   arrow offers anyway. No width of its own: the list and the document are one width (Madde 356), so
   .rail's 320 holds until a drag and the app writes the rest inline.
   Still flex, with one child: the reader below claims the space with flex: 1. */
.rail--open {
  display: flex;
  overflow: hidden;
  /* The reader carries its own margins, so the rail adds none of its own. */
  padding: 0;
}
```

- [ ] **Step 5: `railWidth.js`**

```js
// The widest the rail goes, the list and the open file alike: they are one width (Madde 356).
export const MAX_RAIL_WIDTH = 560;
```

- [ ] **Step 6: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil.

- [ ] **Step 7: Commit**

```powershell
git add queen-agent/frontend/src/features/workspace/FileRail.jsx queen-agent/frontend/src/features/workspace/workspace.css queen-agent/frontend/src/features/workspace/railWidth.js docs/specs/2026-09-29-queenagent-m356-acik-dosya-genisligi-uygulama-design.md docs/plans/2026-09-29-queenagent-m356-acik-dosya-genisligi-uygulama-plan.md
git commit -m @'
feat: Madde 356 -- the open file is the list's width, and its edge is pulled too

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
