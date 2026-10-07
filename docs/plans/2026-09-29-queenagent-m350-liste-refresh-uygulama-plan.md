# Madde 350 — Dosya listesinde yazılı Refresh, başlığın satırında · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Listenin `Refresh`'i yazılı bir `ghost` düğme olur ve başlığın satırına, sağına geçer; kutu
ilk dosyayla başlar.

**Architecture:** `RefreshFiles` yalnız düğmeyi çizer; FileRail onu başlıkla birlikte `rail__bar`
satırına koyar, proje ekranı kendi kutusundaki `file-list__bar`'a. CSS'te `rail__bar` gelir,
`rail__head` satırı paylaşır, `file-list__refresh`'in çerçeveyi silen kuralları kalkar.

**Tech Stack:** React 18, CSS; vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m350-liste-refresh-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod ve yorum İngilizce; yorum nedeni söyler, yalnız bugün doğru olanı.
- `workspace.css`'te yalnız bu parçanın kuralları değişir; başkalarının kuralları yerinde.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Düğme başlığın satırında, kutu ilk dosyayla başlar

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/FileRail.jsx` — `RefreshFiles`, `FileList`, `FileRail`'in açık hâli
- Modify: `queen-agent/frontend/src/features/workspace/ProjectScreen.jsx` — dosya kutusunun ilk satırı
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` — `.rail__bar` yeni; `.rail__head`, `.rail__head--still`, `.file-list__bar`'ın yorumu; `.file-list__refresh` ve `:hover` kalkar

**Interfaces:**
- Consumes: test turunun kırmızısı `c1842c6d`.
- Produces: `RefreshFiles({ onRefresh })` — `<button type="button" className="ghost file-list__refresh">Refresh</button>`.

- [ ] **Step 1: `RefreshFiles` yalnız düğme**

```jsx
// Madde 192 gave the list a Refresh; Madde 350 (the design's items 154 and 175) wrote it out, framed
// like the reader's, and put it on the heading's row. Beside the heading rather than inside it: the
// heading is the fold control, and a button cannot stand inside a button. Where it stands is the
// caller's -- the project screen puts the same button in a row of its own.
export function RefreshFiles({ onRefresh }) {
  return (
    <button type="button" className="ghost file-list__refresh" onClick={onRefresh}>
      Refresh
    </button>
  );
}
```

- [ ] **Step 2: `FileList` düğmeyi çizmez**: imzadan `onRefresh`, gövdeden `<RefreshFiles onRefresh={onRefresh} />`
  kalkar; `FileRail`'in `<FileList ... onRefresh={onRefresh} />` çağrısından da.

- [ ] **Step 3: `FileRail`'in açık hâlinde başlık `rail__bar`'ın içinde**

```jsx
      {/* Folded, there is no list on screen for Refresh to be about, so the row is the heading
          alone -- and the click that opens the rail brings it back. */}
      <div className="rail__bar">
        {/* Folded because the shell has no room for both, ... (bugünkü yorum) */}
        {foldedByWidth ? ( ...bugünkü etiket... ) : ( ...bugünkü düğme... )}
        {collapsed ? null : <RefreshFiles onRefresh={onRefresh} />}
      </div>
```

- [ ] **Step 4: `ProjectScreen.jsx`**

```jsx
                  {/* The rail's own button (Madde 192, 350), in a row at the top of the box: this
                      screen's heading is not a control for it to stand beside. */}
                  <div className="file-list__bar">
                    <RefreshFiles onRefresh={onRefresh} />
                  </div>
```

- [ ] **Step 5: `workspace.css`**

`.rail__head--still`'in önüne:

```css
/* Madde 350 (the design's item 175): the heading and Refresh on one row, Refresh at the right. The 12
   above the list is the row's, so it holds whether the row carries Refresh or, folded, only the
   heading. */
.rail__bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
```

`.rail__head--still`'den `margin-bottom: 12px;` kalkar. `.rail__head`'den `width: 100%;` ve
`margin-bottom: 12px;` kalkar, `flex: 1;` gelir; yorumu: *The heading is the control: the header
when the rail is open, the strip when it is folded. It takes what Refresh leaves of the row.*

`.file-list__refresh` ve `.file-list__refresh:hover` kuralları silinir. `.file-list__bar`'ın yorumu:

```css
/* Madde 192: the list and the open file come back fresh on their own when a turn ends, and Refresh is
   the same action reached by hand -- for a file the user put in the Drive folder themselves, or a
   look taken while a long turn is still running. The rail's stands on its heading's row (Madde 350);
   this row is the project screen's, whose heading is not a control to stand beside. */
```

- [ ] **Step 6: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü yeşil; queen-agent'ın ön ucu 703.

- [ ] **Step 7: Commit**

```powershell
git add queen-agent/frontend/src/features/workspace/FileRail.jsx queen-agent/frontend/src/features/workspace/ProjectScreen.jsx queen-agent/frontend/src/features/workspace/workspace.css docs/specs/2026-09-29-queenagent-m350-liste-refresh-uygulama-design.md docs/plans/2026-09-29-queenagent-m350-liste-refresh-uygulama-plan.md
git commit -m @'
feat: Madde 350 -- the file list's Refresh is a written ghost on the heading's row, and the box starts with the first file

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
