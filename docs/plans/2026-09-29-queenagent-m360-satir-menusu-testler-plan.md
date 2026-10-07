# Madde 360 — Satırın `⋯` menüsü · test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 360'ın davranışını tutan testleri yazmak — yalnız testleri — ve süiti kırmızı commit etmek.

**Architecture:** Satırın kendisi yeni `ProjectRow.jsx`'te sınanır (menü, yerinde rename); `Menu`'nün
çizgisi `Menu.test.jsx`'te; ekranın satırlara `menuFor`'u dağıtması `AllProjectsScreen.test.jsx`'te;
sunucuyla gidip gelen akış — silme, rename, pin, unpin, kenar çubuğunda `⋯` olmaması — `App.test.jsx`'te
kendi sırasını tutan sahte bir sunucuyla. CSS kilitleri `workspace.css.test.js` ve `app.css.test.js`'te.

**Tech Stack:** vitest + jsdom + Testing Library (React 18).

**Spec:** [2026-09-29-queenagent-m360-satir-menusu-testler-design.md](../specs/2026-09-29-queenagent-m360-satir-menusu-testler-design.md)

## Global Constraints

- Test adları ve yorumları İngilizce; yorum NEDEN'i söyler.
- `skip`, `.todo`, `xfail` yok. Tuttuğu davranış kalkan test silinir.
- Süit yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşulur.
- `ProjectRow`'un arayüzü: `project`, `menuOpen`, `onOpen(id)`, `onOpenMenu(id)`, `onCloseMenu()`,
  `onRename(id, name)`, `onPin(id, pinned)`, `onDelete(id)`.
- `AllProjectsScreen`'in yeni prop'ları: `menuFor`, `onOpenMenu`, `onCloseMenu`, `onRenameProject`,
  `onPinProject`, `onDeleteProject`.
- `Menu` öğesinin yeni alanı: `divided: true` → öğenin üstünde `<hr class="menu__divider">`.

---

### Task 1: `ProjectRow.test.jsx` (R1–R10)

**Files:** Create `queen-agent/frontend/src/features/workspace/ProjectRow.test.jsx`

- [ ] **Step 1:** Dosyayı yaz — sabitler `PROJECT` (`p2`, `Night market`, sabitsiz) ve `PINNED`; yardımcı
  `renaming(props)` menüden `Rename`'e basıp alanı döndürür. Testler:
  - R1 `the row carries a ⋯ that asks for its menu and opens nothing` — `Actions for Night market`,
    sınıfı `all-projects__row-more`, yazısı `⋯`; basınca `onOpenMenu("p2")`, `onOpen` çağrılmaz.
  - R2 `the menu holds Rename, Pin and, under a line, a red Delete` — `.menu__item`'lar
    `["Rename", "Pin", "Delete"]`, sonuncusu `menu__item--danger`, önceki kardeşi `.menu__divider`,
    tek çizgi, `Archive` yok.
  - R3 `a pinned project offers Unpin instead` — `["Rename", "Unpin", "Delete"]`.
  - R4 `Pin and Unpin ask for the mark they name` — iki test: `onPin("p2", true)`, `onPin("p2", false)`.
  - R5 `Delete asks for the project's deletion` — `onDelete("p2")`.
  - R6 `Rename turns the name into a field, in the row's own place` — `textbox` `Project name`, sınıfı
    `all-projects__rename`, değeri ad, `document.activeElement` o; `.all-projects__row-open` yok, `⋯` var.
  - R7 `Enter saves what was typed, once, and closes the field` — `"  Harbour  "` + Enter →
    `onRename("p2", "Harbour")` bir kez; alan yok, açan düğme geri.
  - R8 `Escape gives up: nothing is saved` — `onRename` yok, alan yok, `Night market` duruyor.
  - R9 `pressing anywhere else saves, as the design's settleRename does` — `fireEvent.blur` →
    `onRename("p2", "Harbour")`.
  - R10 `an empty name saves nothing` — `"   "` + Enter → `onRename` yok, alan kapalı, ad eskisi.

### Task 2: `Menu.test.jsx` (M1)

**Files:** Modify `queen-agent/frontend/src/features/workspace/Menu.test.jsx` (sona)

- [ ] **Step 1:** `an item can stand apart under a line` — `[{label:"Rename"}, {label:"Delete",
  danger:true, divided:true}]` → tek `.menu__divider`, `nextElementSibling` `Delete`.
  `a menu with no divided item draws no line` — `ITEMS` ile `.menu__divider` yok.

### Task 3: `AllProjectsScreen.test.jsx` (A1)

**Files:** Modify `queen-agent/frontend/src/features/workspace/AllProjectsScreen.test.jsx`

- [ ] **Step 1:** *pressing a row opens that project* `/^Night market/` ile arar.
- [ ] **Step 2:** Sondaki test `the screen carries no search yet` olur (yalnız arama yarısı).
- [ ] **Step 3:** A1 `every row carries its ⋯, and only the row whose menu is open has one` —
  `menuFor="p2"`; iki `Actions for …`; tek `.menu`, `closest(".all-projects__row")` `Night market`'ı içerir.

### Task 4: `App.test.jsx` (B1–B11)

**Files:** Modify `queen-agent/frontend/src/App.test.jsx`

- [ ] **Step 1:** 361–506 arasındaki blok (`TWO`, `serverWith`, `openMenuFor`, kenar çubuğundan silen
  dokuz test) ve 527–555'teki `withProjectToRename` ile rename testi, 2932–2941'deki *an empty prompt
  sends nothing* kalkar. `a list that fails…` ve `a project address that matches nothing…` yerinde kalır.
- [ ] **Step 2:** Yerine `// --- the row's ⋯ on All projects (Madde 360)` bölümü: `serverForRows(projects)`
  — DELETE listeden çıkarır; PATCH gövdeyi projeye katar, `pinned: true` gelince `pinnedAt`'i sayaçtan
  verir; GET sabitlenenleri `pinnedAt` sırasıyla, ötekileri `lastActivity` azalan sırayla döner.
  `ROWS` (`Thesis` 1 saat önce, `Notes` 5 saat önce), `actionsFor(name)`, `onAllProjects()`,
  `sections(container)` → `{ Pinned: [...], Recent: [...] }`. Testler B1–B11 spec'teki gibi.
- [ ] **Step 3:** *a row opens the project's latest chat*, *a project with no chats opens on its draft*,
  *the way into a project is written into the history once* `/^Thesis/` ile arar.

### Task 5: `Sidebar.test.jsx` (S1)

**Files:** Modify `queen-agent/frontend/src/features/workspace/Sidebar.test.jsx`

- [ ] **Step 1:** 217–270 arasındaki beş menü testi kalkar; yerine S1 `no project row carries a ⋯` —
  `/^More for/` adlı düğme yok, `.sidebar__row-more` yok, `.menu` yok.

### Task 6: CSS kilitleri

**Files:** Modify `workspace.css.test.js`, `shared/app.css.test.js`

- [ ] **Step 1:** `the sidebar's menu is the design's own width` → `the row's menu is the design's own
  width`: `rule(".all-projects__row .menu")` `width: 176px`.
- [ ] **Step 2:** Sona C1 (`.all-projects__row-more`: `width: 26px`, `height: 26px`, `opacity: 0`; CSS
  `.all-projects__row:hover .all-projects__row-more` içerir), C2 (`.all-projects__rename`: `flex: 1`,
  `min-width: 0`, `border: 1px solid var(--line)`, `font-size: 13px`), C3 (`.menu__divider`:
  `border-top: 1px solid var(--line)`, `margin: 5px 10px`).
- [ ] **Step 3:** `app.css.test.js`: `.sidebar__row-more:focus-visible` yerine
  `.all-projects__row-more:focus-visible`; `WORKSPACE` `.sidebar__row-more` içermez. Yorum ⋯'yi All
  projects'in satırına bağlar.

### Task 7: Koş ve commit

- [ ] **Step 1:** Dört satır paralel. Beklenen: queen-agent frontend'de yukarıdaki yeni testler kırmızı
  (`ProjectRow.jsx` yok → dosyanın hepsi), öteki üç süit yeşil.
- [ ] **Step 2:** Spec, plan ve testler tek commit:
  `test(queen-agent): Madde 360 red -- the row's ⋯ on All projects: Rename in place, Pin, Delete; none in the sidebar`
