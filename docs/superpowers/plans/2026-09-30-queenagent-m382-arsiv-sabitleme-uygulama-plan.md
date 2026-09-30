# Madde 382 — Arşive giden projenin sabitlemesi kalkar · uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test turunun kırmızı commit'indeki testleri yeşile çıkarmak — o testlerin söylediği kadar, fazlası değil.

**Architecture:** Sunucuda üç satır: arşivdeki proje sabitli okunmaz, liste onu sabitlemesinin yerinde
tutar, `Unarchive` `pinned: true` istenmedikçe sabitleme dosyasını siler. Tarayıcıda `Undo` projenin
arşivden önceki sabitlemesini hatırlar ve onu `onRestoreProject(id, pinned)` ile geri ister.

**Tech Stack:** Flask (sync), React 18, vitest.

**Spec:** [2026-09-30-queenagent-m382-arsiv-sabitleme-uygulama-design.md](../specs/2026-09-30-queenagent-m382-arsiv-sabitleme-uygulama-design.md)

## Global Constraints

- Kod ve yorumlar İngilizce; yorum NEDEN'i ve yalnız bugün doğru olanı söyler.
- Port (`ProjectStore`) ve rotalar değişmez.
- `dist` derlenmez; koşuyu yöneten derler.
- Süit yalnız CLAUDE.md'deki dört satırla, paralel.

---

### Task 1: Sunucu

**Files:** Modify `queen-agent/backend/features/workspace/domain/project.py`,
`.../domain/usecases/list_projects.py`, `.../domain/usecases/edit_project.py`,
`.../data/file_project_store.py` (yalnız yorum)

- [ ] **Step 1:** `project.py`:

```python
    # Each read from a file of its own beside project.json (Madde 339): each answers a question of
    # its own and is written at a moment of its own. pinned_at is the pin file's mtime, empty when
    # there is none. An archive leaves the file (Madde 382): its moment is the project's place among
    # the pins, which Undo gives back -- but an archived project is not pinned.
    pinned_at: str = ""
    archived: bool = False
    ...
    @property
    def pinned(self):
        return bool(self.pinned_at) and not self.archived
```

- [ ] **Step 2:** `list_projects.py`: blok `project.pinned_at` ile:

```python
    # By the pin's moment rather than by `pinned`: an archived project is not pinned, but it keeps
    # its place among the pins, and that is where its Undo line stands (Madde 382).
    pinned = sorted(
        (project for project in projects if project.pinned_at),
        key=lambda project: (project.pinned_at, project.id),
    )
    recent = sorted(
        (project for project in projects if not project.pinned_at),
        ...
```

- [ ] **Step 3:** `edit_project.py`, `archived` işaretinden sonra:

```python
    if archived is not None:
        store.set_archived(project_id, archived)
    # The archive left the pin file as the project's place (Madde 382). Undo asks for the pin with
    # the unarchive and keeps that place; Unarchive does not, and the project comes back unpinned.
    if archived is False and current.archived and not pinned:
        store.set_pinned(project_id, False)
```

- [ ] **Step 4:** `file_project_store.py`'nin `PINNED_FILE` yorumu: dosya arşivde kalır, yeri tutar.

### Task 2: Tarayıcı

**Files:** Modify `queen-agent/frontend/src/features/workspace/AllProjectsScreen.jsx`,
`queen-agent/frontend/src/App.jsx`

- [ ] **Step 1:** `AllProjectsScreen` yeni prop `onRestoreProject`. `undoing` `{ id, pinned }`:

```js
  const shown =
    tab === "archived"
      ? archived
      : projects
          .filter((project) => !project.archived || project.id === undoing?.id)
          .map((project) =>
            project.id === undoing?.id ? { ...project, pinned: undoing.pinned } : project,
          );
  ...
  const archive = (id, toArchive) => {
    if (toArchive) setUndoing({ id, pinned: projects.find((project) => project.id === id).pinned });
    onArchiveProject?.(id, toArchive);
  };
  const undo = async ({ id, pinned }) => {
    await onRestoreProject?.(id, pinned);
    setUndoing((current) => (current?.id === id ? null : current));
  };
  // row: project.id === undoing?.id ? <UndoRow ... onUndo={() => undo(undoing)} /> : ...
```

- [ ] **Step 2:** `App.jsx`: `onRestoreProject={(id, pinned) => editProject(id, { archived: false, pinned })}`.

### Task 3: Belge

**Files:** Modify `queen-agent/CODE-STANDARD.md`

- [ ] **Step 1:** Tablonun `pinned` satırı:
  `| \`pinned\` | is this project pinned, and since when | on pin; removed on unpin and on unarchive — an archive leaves it as the place Undo gives back, and an archived project reads as unpinned |`

### Task 4: Koş ve commit

- [ ] **Step 1:** Dört satır paralel; dördü de yeşil.
- [ ] **Step 2:** Spec, plan ve kod tek commit:
  `feat: Madde 382 -- an archive lets the pin go; Unarchive brings the project back into Recent, Undo into its place among the pins`
