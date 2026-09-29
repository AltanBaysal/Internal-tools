# Madde 365 — Search chats · uygulama turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kırmızı commit'in testlerini koddan yeşile çevirmek: `Search chats`, katlanmış sütunun
arama düğmesi, ve Enter'in açtığı sohbetin yazma kutusuna odak.

**Architecture:** Arama kuralı `matches.js`'te tek; All projects ve kenar çubuğu onu kullanır. Sorgu
ve tuşları kenar çubuğunun; hangi sohbetin kutusuna odak verileceği App'in (`replyFor`), veren
ChatScreen, Composer'ın `focus()`'uyla.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [2026-09-29-queenagent-m365-sohbet-arama-uygulama-design.md](../specs/2026-09-29-queenagent-m365-sohbet-arama-uygulama-design.md)

## Global Constraints

- UI metni İngilizce: `Search chats`, `No chats match "…".`, `No chats yet.`
- Yorum NEDEN'i söyler; `OLD`/`NEW` izi yok.
- `dist` derlenmez (koşuyu yöneten derler).
- Süit yalnız CLAUDE.md'deki dört satırla, paralel.

---

### Task 1: Kural tek yerde

**Files:** Create `queen-agent/frontend/src/features/workspace/matches.js`; Modify `AllProjectsScreen.jsx`

**Produces:** `matches(text: string, query: string): boolean`

- [ ] **Step 1:** `matches.js`:

```js
// Case and accents do not count, as in the design's data.js and shell.js: "cafe" finds "Café". One
// rule for every search in the app -- All projects and Search chats -- so the two cannot drift.
const fold = (text) => text.normalize("NFD").replace(/\p{M}/gu, "").toLowerCase();

// An empty query is everything.
export function matches(text, query) {
  return fold(text).includes(fold(query.trim()));
}
```

- [ ] **Step 2:** `AllProjectsScreen.jsx`: `fold` ve yorumu kalkar; `import { matches } from "./matches.js";`;
  `const found = shown.filter((project) => matches(project.name, query));`

### Task 2: Kenar çubuğu

**Files:** Modify `Sidebar.jsx`

**Consumes:** `matches`. **Produces:** `onOpenChat(id, { focusReply: true })` Enter'de.

- [ ] **Step 1:** Import'lar: `useEffect, useRef, useState` ve `matches`.
- [ ] **Step 2:** Bileşenin başında:

```jsx
const [query, setQuery] = useState("");
const search = useRef(null);
const seeking = useRef(false);
useEffect(() => {
  if (collapsed || !seeking.current) return;
  seeking.current = false;
  search.current.focus({ preventScroll: true });
}, [collapsed]);
```

- [ ] **Step 3:** Katlı dal, `+`'nın ardına:

```jsx
<button type="button" className="sidebar__search-toggle" aria-label="Search chats"
  onClick={() => { seeking.current = true; onToggle(); }}>
  <span className="sidebar__search-icon" />
</button>
```

- [ ] **Step 4:** Açık dal: `shown = chats.filter((chat) => matches(chat.title, query))`,
  `asked = query.trim()`; `New chat`'in ardına `input` (Enter → `shown[0]` varsa
  `onOpenChat(shown[0].id, { focusReply: true })`; Escape → `setQuery("")`); liste `shown`, boş
  cümle `asked ? \`No chats match "${asked}".\` : "No chats yet."`.
- [ ] **Step 5:** Baştaki ve `Fold`'un yorumu arama düğmesini anar.

### Task 3: Odak yazma kutusuna

**Files:** Modify `Composer.jsx`, `ChatScreen.jsx`, `App.jsx`

**Produces:** Composer handle `{ submit, focus }`; ChatScreen props `focusReply`, `onReplyFocused`.

- [ ] **Step 1:** Composer: `const field = useRef(null);` textarea'ya `ref={field}`;
  `useImperativeHandle(ref, () => ({ submit, focus: () => field.current.focus({ preventScroll: true }) }));`
- [ ] **Step 2:** ChatScreen: prop'lar; `box` ref'inin altında:

```jsx
useEffect(() => {
  if (!focusReply) return;
  box.current.focus();
  onReplyFocused();
}, [focusReply]);
```

- [ ] **Step 3:** App: `const [replyFor, setReplyFor] = useState(null);`; Sidebar'ın
  `onOpenChat={(chatId, how) => { setReplyFor(how?.focusReply ? chatId : null); openChat(route.projectId, chatId); }}`;
  ChatScreen'e `focusReply={replyFor !== null && chat.chat?.id === replyFor}`,
  `onReplyFocused={() => setReplyFor(null)}`.

### Task 4: CSS

**Files:** Modify `workspace.css`

- [ ] **Step 1:** `.sidebar__new-chat--icon`'un ardına `.sidebar__search` (spec'teki sekiz değer).
- [ ] **Step 2:** `.sidebar__fold {` → `.sidebar__search-toggle,\n.sidebar__fold {`; hover da.
- [ ] **Step 3:** `.sidebar__search-icon` ve `::after` (spec'teki değerler).
- [ ] **Step 4:** `.sidebar--collapsed` yorumu arama düğmesini anar.

### Task 5: Koş ve commit

- [ ] **Step 1:** Dört satır paralel; dördü de yeşil.
- [ ] **Step 2:** Uygulama spec'i, plan ve kod tek commit:
  `feat: Madde 365 -- Search chats narrows the sidebar, Enter opens the first match into its reply box, and the folded column searches`
