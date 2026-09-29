# Madde 365 — Search chats · test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 365'in davranışını tutan testleri yazmak — yalnız testleri — ve süiti kırmızı commit etmek.

**Architecture:** Arama kuralı kendi modülünün testinde (`matches.test.js`); kenar çubuğunun kutusu,
boş cümlesi, Enter'i, Esc'i ve katlanmış arama düğmesi `Sidebar.test.jsx`'te, bileşen tek başına;
yazma kutusuna odağın verilmesi `ChatScreen.test.jsx`'te; üçünün birlikte çalışması — Enter'in açtığı
sohbetin kaydı gelince odak — `App.test.jsx`'te, bugünkü `serverWithProjects` ve `withRail` sahte
sunucularıyla. CSS kilitleri `workspace.css.test.js`'te.

**Tech Stack:** vitest + jsdom + Testing Library (React 18).

**Spec:** [2026-09-29-queenagent-m365-sohbet-arama-testler-design.md](../specs/2026-09-29-queenagent-m365-sohbet-arama-testler-design.md)

## Global Constraints

- Test adları ve yorumları İngilizce; yorum NEDEN'i söyler.
- `skip`, `.todo`, `xfail` yok. Tuttuğu davranış kalkan test silinir.
- Süit yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşulur.
- Kural modülü: `features/workspace/matches.js`, `export function matches(text, query)` → boolean.
- Kutu: `input type="text"`, sınıf `sidebar__search`, placeholder ve `aria-label` `Search chats`,
  `autocomplete="off"`.
- Katlanmış düğme: sınıf `sidebar__search-toggle`, `aria-label` `Search chats`, içinde
  `span.sidebar__search-icon`.
- Boş cümle: `No chats match "<kırpılmış sorgu>".`
- Enter: `onOpenChat(id, { focusReply: true })`; satır tıklaması `onOpenChat(id)`.
- ChatScreen: `focusReply` (boolean), `onReplyFocused()`.

---

### Task 1: `matches.test.js` (M1–M4)

**Files:** Create `queen-agent/frontend/src/features/workspace/matches.test.js`

- [ ] **Step 1:**

```js
import { expect, test } from "vitest";

import { matches } from "./matches.js";

test("an empty query matches every name", () => {
  expect(matches("Anything", "")).toBe(true);
  expect(matches("Anything", "   ")).toBe(true);
});

test("case does not count", () => {
  expect(matches("Harbour at dusk", "HARBOUR")).toBe(true);
});

test("accents do not count, either way round", () => {
  expect(matches("Café noir", "cafe")).toBe(true);
  expect(matches("Cafe", "café")).toBe(true);
});

test("the spaces around the query do not count, and a name without it does not match", () => {
  expect(matches("Old pier", "  pier  ")).toBe(true);
  expect(matches("Old pier", "harbour")).toBe(false);
});
```

### Task 2: `Sidebar.test.jsx` (S1–S15)

**Files:** Modify `queen-agent/frontend/src/features/workspace/Sidebar.test.jsx`

- [ ] **Step 1:** `CHATS`'e dokunulmaz; yardımcılar: `search = () => screen.getByRole("textbox", { name: "Search chats" })`,
  `rows = (container) => [...container.querySelectorAll(".sidebar__chat")].map((row) => row.textContent)`.
- [ ] **Step 2:** *under New chat stand the chats and then the fold, and nothing else* →
  S1 `under New chat stand the search, the chats and the fold, and nothing else`: sınıflar
  `["sidebar__new-chat", "sidebar__search", "sidebar__chats", "sidebar__foot"]`.
- [ ] **Step 3:** *the sidebar carries no search control* silinir.
- [ ] **Step 4:** *folded, the chats are gone and the column holds + and the fold alone* →
  S11 `folded, the chats are gone and the column holds +, the search and the fold`: `aria-label`'lar
  `["New chat", "Search chats", "Show the sidebar"]`.
- [ ] **Step 5:** *clicking a chat asks to open it* olduğu gibi kalır (S10): `toHaveBeenCalledWith("c1")`
  tam argüman listesini tutar, fazladan bir `{ focusReply }` onu kırar.
- [ ] **Step 6:** Sona yeni blok, `// Madde 365 (design 151, 168, 174)` yorumuyla:
  - S2 `the search is a box named Search chats, and the project does not open onto it` —
    placeholder `Search chats`, `getAttribute("autocomplete")` `off`, `document.activeElement` o değil.
  - S3 `typing narrows the chats by title, whatever the case and the accents` — `CHATS` + `{ id: "c3",
    title: "Café notes" }`; `missing` → `["Missing values"]`; `CAFE` → `["Café notes"]`.
  - S4 `with no match the list says so, with what was typed` — `"  zebra "` → `No chats match "zebra".`,
    sınıfı `sidebar__empty`, `closest(".sidebar__chats")` var, `.sidebar__chat` yok, `No chats yet.` yok.
  - S5 `a project with no chats says no match once something is typed` — `chats={[]}`, `x` →
    `No chats match "x".`
  - S6 `Enter asks to open the first match and to hand it the reply box` — `missing`, Enter →
    `onOpenChat` `("c2", { focusReply: true })`.
  - S7 `Enter in an empty box opens the first chat` → `("c1", { focusReply: true })`.
  - S8 `Enter with no match asks for nothing` — `zebra`, Enter → `onOpenChat` çağrılmadı.
  - S9 `Escape empties the box and brings every chat back` — `missing`, Esc → değer `""`, iki satır.
  - S12 `folded, the search is a drawn magnifier with no text` — düğme `Search chats`, sınıfı
    `sidebar__search-toggle`, `.sidebar__search-icon` var, `textContent` `""`.
  - S13 `folded, the search asks to unfold and then holds the focus` — `collapsed` render, düğmeye
    tıkla, `onToggle` çağrıldı; `rerender(<Sidebar chats={CHATS} onToggle={onToggle} />)`;
    `document.activeElement` `search()`.
  - S14 `unfolded by the fold, the search does not take the focus` — `Show the sidebar`'a tıkla,
    açık rerender; `activeElement` kutu değil.
  - S15 `folding and unfolding keeps what was typed` — `missing`, katlı rerender, açık rerender →
    değer `missing`, satırlar `["Missing values"]`.

Yazmak `fireEvent.change(search(), { target: { value } })`, tuş `fireEvent.keyDown(search(), { key })`.

### Task 3: `ChatScreen.test.jsx` (C1–C2)

**Files:** Modify `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx`

- [ ] **Step 1:** Sona, `// Madde 365` yorumuyla:
  - C1 `asked to, the screen hands the focus to the reply box and says it has` —
    `render(<ChatScreen chat={CHAT} focusReply onReplyFocused={done} />)`; `activeElement`
    `getByPlaceholderText("Reply...")`; `done` bir kez.
  - C2 `unasked, the reply box is left alone` — `focusReply` yok; `activeElement` kutu değil; `done`
    çağrılmadı.

### Task 4: `App.test.jsx` (A1–A3)

**Files:** Modify `queen-agent/frontend/src/App.test.jsx`

- [ ] **Step 1:** *inside a project the sidebar holds…* testinin ardına, `TWO_CHATS` sabiti
  (`c1` *Write the intro*, `c2` *Missing values*, `lastActivity: NOW`) ve:
  - A1 `Enter in Search chats opens the first match with its reply box in focus` —
    `serverWithProjects([THESIS], { p1: TWO_CHATS })`, `/p/p1/c/c1`, `chatOpened()`; kutuya `missing`;
    `.sidebar__chat`'ler yalnız `Missing values`; Enter; `pathname` `/p/p1/c/c2`; `waitFor`:
    `Reply...` açık ve `activeElement`.
  - A2 `a chat opened by a click leaves the focus where it was` — aynı sunucu; `Missing values`
    satırına tıkla; `pathname` `/p/p1/c/c2`; `chatOpened()`; `activeElement` kutu değil.
- [ ] **Step 2:** Katlama testlerinin ardına A3 `folded, the search icon unfolds the sidebar into its
  search box` — `withRail()`, `/p/p1/c/c1`, `sidebarOpen()` bekle; `Hide the sidebar`; kapanınca
  `getByRole("button", { name: "Search chats" })`'a tıkla; `sidebarOpen()` doğru;
  `activeElement` `getByRole("textbox", { name: "Search chats" })`.

### Task 5: CSS kilitleri (K1–K3)

**Files:** Modify `queen-agent/frontend/src/features/workspace/workspace.css.test.js`

- [ ] **Step 1:** *folded, New chat is a square…*'dan sonra:
  - K1 `the chats search is the app's plain box` — `rule(".sidebar__search")`: `width: 100%`,
    `border: 1px solid var(--line)`, `background: var(--surface)`,
    `border-radius: var(--radius-control)`, `padding: 8px 10px`, `font-size: 13px`, `color: var(--ink)`.
  - K2 `folded, the search is the fold's own square and hover` — `CSS` eşleşir
    `/\n\.sidebar__search-toggle,\r?\n\.sidebar__fold \{/` ve
    `/\n\.sidebar__search-toggle:hover,\r?\n\.sidebar__fold:hover \{/` (çalışma kopyası CRLF olabilir).
  - K3 `the magnifier is a ring with a short handle` — `rule(".sidebar__search-icon")`: `width: 12px`,
    `height: 12px`, `border: 1.5px solid var(--ink)`, `border-radius: 50%`;
    `rule(".sidebar__search-icon::after")`: `width: 5px`, `rotate(45deg)`.

### Task 6: Koş ve commit

- [ ] **Step 1:** Dört satır paralel. Beklenen: queen-agent frontend'de `matches.test.js` (modül yok),
  S1–S9, S11–S15, C1, A1, A3, K1–K3 kırmızı; S10, C2, A2 yeşil; öteki üç süit yeşil.
- [ ] **Step 2:** Spec, plan ve testler tek commit:
  `test(queen-agent): Madde 365 red -- Search chats narrows the sidebar, Enter opens the first match, the folded column searches`
