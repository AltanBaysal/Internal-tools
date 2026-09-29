# Madde 340 — Yüklenirken spinner, önce dosya listesinde · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dosya listesi yüklenirken iskeletin yerine tasarımın spinner'ı döner; `1a3a498b`'nin
kırmızıları yeşile döner.

**Architecture:** Yeni `Spinner.jsx` yalnız halkayı çizer; `FileRail.jsx`'in `FileList`'i onu
`file-list__spinner` kutusunda, iskeletin yerinde çizer; `workspace.css` iki kural kazanır.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m340-spinner-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod ve yorum İngilizce; yorum neden'i söyler.
- `Skeleton.jsx`, testi ve `.skeleton` kuralları değişmez; `.msg__spinner` ve `@keyframes msg-spin`
  değişmez. Başka kuralların sırası ve biçimi değişmez.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Spinner, dosya listesinde

**Files:**
- Create: `queen-agent/frontend/src/features/workspace/Spinner.jsx`
- Modify: `queen-agent/frontend/src/features/workspace/FileRail.jsx` — import ve `FileList`'in yükleniş satırı
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` — `.msg__spinner`'ın keyframe'inin altına `.spinner`, `.file-list__empty`'nin altına `.file-list__spinner`
- Test: `Spinner.test.jsx`, `FileRail.test.jsx`, `workspace.css.test.js` (kırmızı turda yazıldı)

**Interfaces:**
- Produces: `export default function Spinner()` — prop almaz; v9-2l ve v9-2u aynısını kendi
  kutularına koyar.

- [ ] **Step 1: `Spinner.jsx`'i yaz**

```jsx
// The design's one waiting ring (items 173 and 181). It is only the ring: each place that waits
// wraps it in a box of its own, so where it stands and how much room it gets is that place's.
// It says nothing -- the heading and the buttons left standing around it say what is loading.
export default function Spinner() {
  return <span className="spinner" aria-hidden="true" data-testid="spinner" />;
}
```

- [ ] **Step 2: `FileRail.jsx`'te iskeletin yerine spinner**

`import Skeleton from "./Skeleton.jsx";` satırı `import Spinner from "./Spinner.jsx";` olur (importlar
alfabetik: `FilePanel`, `FileRow`'dan sonra, `railWidth.js`'ten önce). `FileList`'te:

```jsx
      {loading ? <Skeleton rows={3} /> : null}
```

yerine:

```jsx
      {loading ? (
        <div className="file-list__spinner">
          <Spinner />
        </div>
      ) : null}
```

- [ ] **Step 3: `workspace.css`'e iki kural**

`@keyframes msg-spin { … }`'in altına:

```css
/* Madde 340: the design's spinner, the ring above at twice the size, standing alone where a loading
   list will be while the heading and buttons around it stay drawn. A rule of its own rather than a
   second selector on .msg__spinner, which belongs to the chat's live row. */
.spinner {
  flex: none;
  width: 20px;
  height: 20px;
  border: 1.5px solid var(--line);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: msg-spin 0.8s linear infinite;
}
```

`.file-list__empty { … }`'nin altına:

```css
/* Where the rows will be while the list loads (Madde 340): only this spot waits, the heading and
   Refresh above it stay. */
.file-list__spinner {
  display: flex;
  justify-content: center;
  padding: 24px 12px;
}
```

- [ ] **Step 4: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent arka ucu 933, ön ucu 658 yeşil; queen-editor arka ucu 377'nin iki kırmızısı,
ön ucu 749 yeşil.

- [ ] **Step 5: Commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/Spinner.jsx queen-agent/frontend/src/features/workspace/FileRail.jsx queen-agent/frontend/src/features/workspace/workspace.css docs/superpowers/specs/2026-09-29-queenagent-m340-spinner-uygulama-design.md docs/superpowers/plans/2026-09-29-queenagent-m340-spinner-uygulama-plan.md
git commit -m @'
feat: Madde 340 -- the file list turns the design's spinner while it loads, and the ring is there for the next screens

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
