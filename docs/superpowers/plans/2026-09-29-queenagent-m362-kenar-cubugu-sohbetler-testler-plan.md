# Madde 362 — Kenar çubuğunda yalnız New chat ve sohbetler · test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 362'nin davranışını tutan testleri yazmak — yalnız testleri — ve süiti kırmızı commit etmek.

**Architecture:** Kenar çubuğunun ne çizdiği `Sidebar.test.jsx`'te, bileşen tek başına; App'in ona
açık projenin sohbetlerini verdiği ve öteki projeleri vermediği `App.test.jsx`'te, bugünkü
`serverWithProjects` sahte sunucusuyla. CSS kilitleri `workspace.css.test.js`'te.

**Tech Stack:** vitest + jsdom + Testing Library (React 18).

**Spec:** [2026-09-29-queenagent-m362-kenar-cubugu-sohbetler-testler-design.md](../specs/2026-09-29-queenagent-m362-kenar-cubugu-sohbetler-testler-design.md)

## Global Constraints

- Test adları ve yorumları İngilizce; yorum NEDEN'i söyler.
- `skip`, `.todo`, `xfail` yok. Tuttuğu davranış kalkan test silinir.
- Süit yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşulur.
- `Sidebar`'ın prop'ları: `chats`, `activeChatId`, `onNewChat`, `onOpenChat`, `collapsed`, `onToggle`.
- Sınıflar: `sidebar__new-chat`, `sidebar__chats`, `sidebar__chat` (`--active`), `sidebar__empty`,
  `sidebar__foot`. Boş cümle: `No chats yet.`

---

### Task 1: `Sidebar.test.jsx` (S1–S8)

**Files:** Modify `queen-agent/frontend/src/features/workspace/Sidebar.test.jsx`

- [ ] **Step 1:** `PROJECTS` sabiti ve bütün render'lardaki `projects=`/`activeProjectId=` kalkar.
- [ ] **Step 2:** Spec'in *Kalkan* listesindeki on üç test silinir.
- [ ] **Step 3:** Yeni testler, `CHATS` (`c1` *Write the intro*, `c2` *Missing values*) ile:
  - S1 `the sidebar leads with a filled + New chat` — `aside.firstElementChild` sınıfı
    `sidebar__new-chat`, `textContent` `+New chat`.
  - S2 `under New chat stand the chats and then the fold, and nothing else` — çocukların sınıfları
    `["sidebar__new-chat", "sidebar__chats", "sidebar__foot"]`.
  - S3 `there is no list of projects, no Recent chats and no + for a new project` — `Projects`,
    `Recent chats` yazısı yok; `New project` adlı düğme yok; `.sidebar__row-open`, `.dot` yok.
  - S4 `the project's chats are listed with no label above them, the open one marked` — iki satır,
    `Missing values` `sidebar__chat--active`; `.sidebar__chats`'in `firstElementChild`'i bir
    `.sidebar__chat`.
  - S5 `every chat of the project is listed` — 12 sohbet → 12 `.sidebar__chat`, `Chat 11` var.
  - S6 `a project with no chats says so` — `chats={[]}` → `No chats yet.`, sınıfı `sidebar__empty`,
    `closest(".sidebar__chats")` var.
  - S7 `with chats, nothing says there are none` — `No chats yet.` yok.
  - S8 `folded, the chats are gone and the column holds + and the fold alone` — `Write the intro`
    yok; `.sidebar button`'lar iki: `New chat` ve `Show the sidebar`.
- [ ] **Step 4:** Kalanlar (Settings, katlama, marka, `New chat asks…`, *clicking a chat…*, arama yok)
  prop'suz render eder.

### Task 2: `App.test.jsx` (B1–B2)

**Files:** Modify `queen-agent/frontend/src/App.test.jsx`

- [ ] **Step 1:** *the sidebar's + asks for the name too…* testi silinir.
- [ ] **Step 2:** *inside a project no ⋯ stands anywhere* `findByText("Thesis", { selector: ".bar__project" })`
  bekler.
- [ ] **Step 3:** *nothing is asked of a workspace-wide chat address*'in yorumu: *the sidebar lists
  that project's own chats*.
- [ ] **Step 4:** Katlama testleri (*the sidebar folds away…*, *Ctrl + . folds…*, *Ctrl + . works while
  typing…*, *a full stop typed alone…*) `Projects` yerine yardımcı `sidebarOpen()` —
  `screen.queryByText("Write the intro", { selector: ".sidebar__chat" })` — okur.
- [ ] **Step 5:** B1 `inside a project the sidebar holds its chats and no other project` —
  `serverWithProjects([THESIS, NOTES], { p1: [c1 Write the intro, c2 Missing values] })`, `/p/p1/c/c1`;
  `.sidebar__chat`'te iki sohbet; `Notes` sayfada yok; `Projects` yok; `New project` düğmesi yok.
- [ ] **Step 6:** B2 `a project with no chats yet says so in the sidebar` — `serverWithProjects([THESIS])`,
  `/p/p1/c/new` → `findByText("No chats yet.", { selector: ".sidebar__empty" })`.

### Task 3: CSS kilitleri

**Files:** Modify `queen-agent/frontend/src/features/workspace/workspace.css.test.js`

- [ ] **Step 1:** *every control rounds by the same variable*'dan `.sidebar__row-open` satırı ve yorumu
  kalkar.
- [ ] **Step 2:** Sona C1 `the sidebar's project list is gone by every name` (Karar 9'un sınıfları
  `.${name}` olarak yok; `\n.dot {` yok), C2 `No chats yet. is a quiet line` (`.sidebar__empty`:
  `padding: 10px 12px`, `font-size: 13px`, `color: var(--muted)`), C3 `New chat is the filled accent`
  (`.sidebar__new-chat`: `background: var(--accent)`).

### Task 4: Koş ve commit

- [ ] **Step 1:** Dört satır paralel. Beklenen: queen-agent frontend'de S1–S6, S8, B1, B2, C1, C2
  kırmızı; öteki üç süit yeşil.
- [ ] **Step 2:** Spec, plan ve testler tek commit:
  `test(queen-agent): Madde 362 red -- the sidebar holds New chat and the project's chats, and no projects list`
