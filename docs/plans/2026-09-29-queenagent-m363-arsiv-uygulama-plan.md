# Madde 363 — Arşiv · uygulama turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `4a3adfd3`'ün 30 kırmızı testini, testlerin tarif ettiğinden fazlasını yazmadan yeşile getirmek.

**Architecture:** Satır arşivi bilir (`ProjectRow`); ekran sekmeyi ve `Undo`'nun teklifini tutar
(`AllProjectsScreen`); App arşivi `editProject`'e bağlar; stiller tasarımın `kit.css`'inden.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [2026-09-29-queenagent-m363-arsiv-uygulama-design.md](../specs/2026-09-29-queenagent-m363-arsiv-uygulama-design.md)

## Global Constraints

- UI metni İngilizce; yorum NEDEN'i ve yalnız bugünü söyler.
- Sunucuya, `useProjects`'e ve `Menu`'ye dokunulmaz.
- Testler değişmez — dayandığı durumu bu parçanın kaldırdığı tek kilit dışında (Task 3, Step 3); süit yalnız CLAUDE.md'deki dört satırla, paralel koşulur.
- `dist` derlenmez (Claude derler).

---

### Task 1: `ProjectRow.jsx`

**Interfaces:** Produces `ProjectRow` prop'u `onArchive(id, archived)`; adlı export
`UndoRow({ name, onUndo })`.

- [ ] **Step 1:** `Columns({ project })` — bugünkü üç `span`.
- [ ] **Step 2:** Gövde: `renaming` → `RenameField`; `project.archived` →
  `<div className="all-projects__row-text"><Columns …/></div>`; değilse bugünkü düğme, içinde `Columns`.
- [ ] **Step 3:** Menü öğeleri:

```jsx
const remove = { label: "Delete", danger: true, divided: true, onChoose: () => onDelete?.(project.id) };
const items = project.archived
  ? [rename, { label: "Unarchive", onChoose: () => onArchive?.(project.id, false) }, remove]
  : [
      rename,
      project.pinned ? unpin : pin,
      { label: "Archive", onChoose: () => onArchive?.(project.id, true) },
      remove,
    ];
```

- [ ] **Step 4:** `UndoRow`:

```jsx
export function UndoRow({ name, onUndo }) {
  return (
    <div className="all-projects__row all-projects__undo">
      <span>
        <strong>{name}</strong> archived
      </span>
      {" · "}
      <button type="button" autoFocus onClick={onUndo}>
        Undo
      </button>
    </div>
  );
}
```

### Task 2: `AllProjectsScreen.jsx`

**Interfaces:** Consumes `ProjectRow`'un `onArchive`'ı, `UndoRow`. Produces prop
`onArchiveProject(id, archived)` (promise döndürebilir).

- [ ] **Step 1:** `ProjectList({ any, shown, archivedTab, query, row })` — spec'in cümle sırası.
- [ ] **Step 2:** Durum `tab`, `undoing`; `archived`, `open`, `shown`; sarmalayıcılar:

```jsx
const openMenu = (id) => { setUndoing(null); onOpenMenu?.(id); };
const archive = (id, archived) => { if (archived) setUndoing(id); onArchiveProject?.(id, archived); };
const undo = async (id) => {
  await onArchiveProject?.(id, false);
  setUndoing((current) => (current === id ? null : current));
};
const switchTab = (next) => { setUndoing(null); setTab(next); };
```

- [ ] **Step 3:** Sekmeler `.all-projects__tools`'ta aramadan sonra; sayı `loading ? "" : n`.
- [ ] **Step 4:** Baştaki yorum bugünü anlatır.

### Task 3: `App.jsx` ve `workspace.css`

- [ ] **Step 1:** `AllProjectsScreen`'e `onArchiveProject={(id, archived) => editProject(id, { archived })}`.
- [ ] **Step 2:** `workspace.css`: `kit.css` 1993–2027'nin sekme kuralları (`[data-hover]`'sız),
  2081–2088'in `.all-projects__row-text`'i, 2158–2177'nin `Undo` kuralları; `.all-projects__tools`'un
  yorumu bugünü söyler.
- [ ] **Step 3:** `app.css.test.js`'in *accent-coloured text takes the text hover*'ı:
  `WORKSPACE`'in `--accent-link-hover` içermediği yerine `.all-projects__undo button:hover`'ın onu
  kullandığı; yorum `Undo`'nun geri geldiğini söyler (spec, *app.css.test.js'in bir kilidi*).

### Task 4: Koş, kontrol et, commit

- [ ] **Step 1:** Dört satır paralel; hepsi yeşil.
- [ ] **Step 2:** Farkı FOUNDATION, CODE-STANDARD, tasarım ve satırın *Bitti sayılır*'ına karşı oku.
- [ ] **Step 3:** Spec, plan ve kod tek commit:
  `feat: Madde 363 -- the archive: Archive leaves Undo in the row's place, the Projects and Archived tabs, Unarchive from the row's menu`
