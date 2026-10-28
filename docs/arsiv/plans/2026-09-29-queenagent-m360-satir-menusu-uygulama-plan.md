# Madde 360 — Satırın `⋯` menüsü · uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test turunun kırmızı testlerini yeşile çeviren kod: All projects satırının `⋯` menüsü, yerinde
rename, pin/unpin, silme sorusu; kenar çubuğunda `⋯` yok.

**Architecture:** Satır kendi dosyasında (`ProjectRow.jsx`); menünün açıklığı App'in `menuFor`'u,
rename'in açıklığı satırın kendi durumu. Yazma sonrası liste sunucudan yeniden okunur.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [2026-09-29-queenagent-m360-satir-menusu-uygulama-design.md](../specs/2026-09-29-queenagent-m360-satir-menusu-uygulama-design.md)

## Global Constraints

- UI metni İngilizce, tasarımın sözleriyle: `Rename`, `Pin`, `Unpin`, `Delete`, `Actions for <ad>`,
  `Project name`.
- Yorum NEDEN'i ve yalnız bugünü söyler; ölü kod kalmaz.
- `dist` derlenmez (Claude derler); tarayıcı kullanılmaz.
- Süit yalnız dört satırla, paralel.

---

### Task 1: `Menu.jsx` — `divided`

**Files:** Modify `queen-agent/frontend/src/features/workspace/Menu.jsx`

- [ ] `import { Fragment, useLayoutEffect, useRef, useState } from "react";`; öğeler
  `<Fragment key={item.label}>{item.divided ? <hr className="menu__divider" /> : null}<button …/></Fragment>`
  olur, `button`'dan `key` kalkar. Başlık yorumu: *the All projects row's ⋯ menu, the model and Skills menus*.

### Task 2: `ProjectRow.jsx`

**Files:** Create `queen-agent/frontend/src/features/workspace/ProjectRow.jsx`

- [ ] `RenameField({ name, onDone })`: `draft` durumu, `done` ref'i, `finish(save)` →
  `onDone(save ? draft.trim() : "")` bir kez. `input.all-projects__rename`, `aria-label="Project name"`,
  `autoFocus`, Enter → `finish(true)` (`preventDefault`), Escape → `finish(false)`, `onBlur` →
  `finish(true)`.
- [ ] `ProjectRow`: `more` ref'i, `renaming` durumu; `renaming` ise `RenameField` (`onDone={(name) => {
  setRenaming(false); if (name) onRename?.(project.id, name); }}`), değilse bugünkü açan düğme;
  `button.all-projects__row-more` `aria-label={\`Actions for ${project.name}\`}`, `⋯`,
  `onClick={() => onOpenMenu?.(project.id)}`; `menuOpen` ise `<Menu anchor={more.current}
  onClose={onCloseMenu} items={[Rename, Pin|Unpin, Delete (danger, divided)]} />`.

### Task 3: `AllProjectsScreen.jsx`

**Files:** Modify `queen-agent/frontend/src/features/workspace/AllProjectsScreen.jsx`

- [ ] `Section({ label, projects, row })` → `projects.map(row)`; `ProjectList({ projects, query, row })`.
- [ ] Ekran yeni prop'ları alır, `const row = (project) => <ProjectRow key={project.id} project={project}
  menuOpen={menuFor === project.id} onOpen={onOpenProject} onOpenMenu={onOpenMenu}
  onCloseMenu={onCloseMenu} onRename={onRenameProject} onPin={onPinProject}
  onDelete={onDeleteProject} />`. `relativeTime` ve `countOf` importları satıra gider.
- [ ] Başlık yorumu: `The Archived tab is an item of its own (363), and so are the spinner …`.

### Task 4: `useProjects.js`, `App.jsx`, `Sidebar.jsx`

- [ ] `editProject`: `const edited = await patchJson(…); await reload(); return edited;` — yorum: yeri
  sunucunun sırası.
- [ ] `App.jsx`: Task 3'ün prop'ları; `Sidebar`'dan beş menü prop'u, `askForName` ve
  `deleteProject`'in `navigate` dalı kalkar; `askToDelete`'in `confirmLabel`'ı `Delete`, `onConfirm`
  `setConfirming(null); removeProject(id);`.
- [ ] `Sidebar.jsx`: `useRef`, `Menu`, `trigger`, `⋯` ve sarmalayıcı `div` kalkar; `key` düğmeye.

### Task 5: `workspace.css`

- [ ] `.sidebar__row`, `.sidebar__row-more` (+ hover/odak), `.sidebar__row .menu` kalkar;
  `.all-projects__row-more` (+ hover/odak, kendi hover'ı), `.all-projects__row .menu`,
  `.all-projects__rename` `.all-projects__row-when`'den sonra, `.menu__divider` `.menu__item--danger:hover`'dan
  sonra — değerler tasarımın `kit.css`'inden.

### Task 6: Koş ve commit

- [ ] Dört satır paralel, dördü yeşil.
- [ ] `feat: Madde 360 -- the All projects row carries its ⋯: Rename in place, Pin or Unpin, Delete with
  its question; no ⋯ inside a project` + spec + plan.
