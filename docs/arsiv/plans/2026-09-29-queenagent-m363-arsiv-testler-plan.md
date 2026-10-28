# Madde 363 — Arşiv · test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 363'ün davranışını tutan testleri yazmak — yalnız testleri — ve süiti kırmızı commit etmek.

**Architecture:** Satırın iki hâli — arşivde olan ve olmayan — ve menüleri `ProjectRow.test.jsx`'te;
sekmeler, boş cümleler ve `Undo` satırının ömrü `AllProjectsScreen.test.jsx`'te, prop'ları elle
değiştirerek (`rerender`); sunucuyla gidip gelen akış `App.test.jsx`'te, 360'ın sırasını tutan sahte
sunucuyla. CSS kilitleri `workspace.css.test.js`'te.

**Tech Stack:** vitest + jsdom + Testing Library (React 18).

**Spec:** [2026-09-29-queenagent-m363-arsiv-testler-design.md](../specs/2026-09-29-queenagent-m363-arsiv-testler-design.md)

## Global Constraints

- Test adları ve yorumları İngilizce; yorum NEDEN'i söyler.
- `skip`, `.todo`, `xfail` yok.
- Süit yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşulur.
- `ProjectRow`'un yeni prop'u: `onArchive(id, archived)`; arşivde olduğunu `project.archived` söyler.
- `AllProjectsScreen`'in yeni prop'u: `onArchiveProject(id, archived)` — bir promise döndürebilir
  (App'te `editProject`'in).
- Sekme bir `button.all-projects__tab`: yazısı `Projects` ya da `Archived`, ardından
  `span.all-projects__count`; erişilebilir adı `Projects 2` gibi. Açık olan `is-on`.
- `Undo` satırı `.all-projects__row.all-projects__undo`: `<strong>ad</strong> archived · ` ve `Undo`
  düğmesi; `textContent` `Night market archived · Undo`.
- Arşivdeki satırın gövdesi `.all-projects__row-text` (düğme değil), içinde `.all-projects__row-name`,
  `-meta`, `-when`.

---

### Task 1: `ProjectRow.test.jsx` (R2, R3, P1–P5)

**Files:** Modify `queen-agent/frontend/src/features/workspace/ProjectRow.test.jsx`

- [ ] **Step 1:** Baştaki yorum: Rename, Pin, Archive ve Delete burada; arşivdeki satır 363'ün.
  Sabit `SHELVED = { ...PROJECT, archived: true }`.
- [ ] **Step 2:** R2 `the menu holds Rename, Pin, Archive and, under a line, a red Delete` —
  `["Rename", "Pin", "Archive", "Delete"]`, `items[3]` kırmızı, önceki kardeşi `.menu__divider`, tek
  çizgi. R3 `["Rename", "Unpin", "Archive", "Delete"]`.
- [ ] **Step 3:** P1 `Archive asks for the project to be archived` → `onArchive("p2", true)`.
- [ ] **Step 4:** P2 `an archived row is not a way into its project` — `.all-projects__row-open` yok;
  `.all-projects__row-text` `.all-projects__row-name` `Night market`'ı, `.all-projects__row-meta`
  `1 chat · 1 file`'ı ve bir `.all-projects__row-when` taşır; ona basmak `onOpen`'ı çağırmaz;
  `Actions for Night market` var.
- [ ] **Step 5:** P3 `an archived row's menu holds Rename, Unarchive and, under a line, a red Delete`.
  P4 `Unarchive asks for the project to come back` → `onArchive("p2", false)`.
  P5 `an archived row is renamed in its own place too` — `Rename` → alan → `Harbour` + Enter →
  `onRename("p2", "Harbour")`.

### Task 2: `AllProjectsScreen.test.jsx` (T1–T8, U1–U7)

**Files:** Modify `queen-agent/frontend/src/features/workspace/AllProjectsScreen.test.jsx`

- [ ] **Step 1:** *the search stands under the head* testinin yorumu: sekmeler aynı satırda. Sabit
  `SHELVED = { id: "p5", name: "Shelved reel", chats: 2, files: 4, pinned: false, archived: true,
  lastActivity: ago(3) }`. Yardımcılar: `tab(name)` → `screen.getByRole("button", { name: new
  RegExp(`^${name}`) })`; `rowTexts(container)` → `.all-projects__row`'ların `textContent`'i.
- [ ] **Step 2:** T1–T8, spec'teki gibi. T1'de sekmeler `.all-projects__tools` içinde kutudan sonra
  (`tabs.previousElementSibling === search()`), adları `Projects 3` ve `Archived 1`
  (`[PINNED, RECENT, OLDER, SHELVED]`). T8 `loading` ile: sekmeler var, `.all-projects__count`'ların
  yazısı boş.
- [ ] **Step 3:** U1–U7. Ekran `menuFor` prop'unu App'ten alır; testler menüyü `menuFor="p2"` ile açık
  verir ve `Archive`'a basar. U2 ve U4 listeyi `rerender` ile değiştirir (sunucunun cevabı). U4'te
  `onArchiveProject` bir promise döndürür; `Undo`'dan sonra, promise çözülmeden, `Undo` satırı durur;
  `rerender` arşivsiz liste ve `await act(resolve)` sonrası satır `Night market` açan düğmesiyle
  döner. U5: `Undo` varken `Actions for Old pier`'e basmak `onOpenMenu("p3")`'ü çağırır ve `Undo` satırı
  gider (liste arşivli). U6: `Archived`'a, sonra `Projects`'e basınca `Undo` yok. U7: `Archived`'da
  `menuFor="p5"` → `Unarchive` → `onArchiveProject("p5", false)`, `.all-projects__undo` yok.

### Task 3: `App.test.jsx` (B1–B6)

**Files:** Modify `queen-agent/frontend/src/App.test.jsx` (Madde 360 bölümünün sonuna)

- [ ] **Step 1:** `// --- the archive (Madde 363)` bölümü. `serverForRows` olduğu gibi yeter: PATCH gövdeyi
  projeye katıyor, `archived` sırayı değiştirmiyor. `tab(name)` yardımcısı.
- [ ] **Step 2:** B1–B6 spec'teki gibi. B1'de `sections(container)` `{ Recent: ["Thesis"] }` değil —
  `Undo` satırında `.all-projects__row-name` yok — o yüzden `Recent` bölümünün satırlarının
  `textContent`'i okunur: `["Thesis…", "Notes archived · Undo"]`. B6: `ROWS`'un ikisi de `archived:
  true`; `Every project is archived.`; `+ New project` → `Name your project`, çubukta `Cancel`.

### Task 4: CSS kilitleri

**Files:** Modify `queen-agent/frontend/src/features/workspace/workspace.css.test.js` (sona)

- [ ] **Step 1:** C1 `the tabs are the design's quiet buttons, the open one lit` —
  `.all-projects__tab` `padding: 7px 12px`, `font-size: 13px`; `rule(".all-projects__tab.is-on")`
  `background: #e5dfd5`; `.all-projects__count` `var(--font-mono)`, `font-size: 11px`.
- [ ] **Step 2:** C2 `an archived row's text takes the opener's room` — `.all-projects__row-text`
  `flex: 1`, `min-width: 0`.
- [ ] **Step 3:** C3 `the Undo row is a quiet line whose one action is Undo` — `.all-projects__undo`
  `color: #6b6259`; `rule(".all-projects__undo button")` `color: var(--accent)`.

### Task 5: Koş ve commit

- [ ] **Step 1:** Dört satır paralel. Beklenen: queen-agent frontend'de yukarıdaki yeni ve değişen
  testler kırmızı, öteki üç süit yeşil.
- [ ] **Step 2:** Spec, plan ve testler tek commit:
  `test(queen-agent): Madde 363 red -- the archive: Archive with Undo in the row's place, the Projects and Archived tabs, Unarchive`
