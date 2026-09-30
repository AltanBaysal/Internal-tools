# Madde 386 — Kenar çubuğu okuyamadığı sohbet listesine "yok" demez · uygulama turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kırmızı commit edilen 386 testlerini kodla yeşile çevirmek, ve fazlasını yapmamak.

**Architecture:** `useProjectChats` `useList`'in hatasını dışarı verir; App onu ve listeyi yeniden
okuyan `reloadProjectChats`'i kenar çubuğuna geçirir; kenar çubuğu hata varken satırların yerine
cümleyi, `Try again`'i ve `CopyButton`'ı çizer. Görünüş `workspace.css`'te.

**Tech Stack:** React 18, vitest + jsdom.

**Spec:** [2026-09-30-queenagent-m386-sohbet-listesi-okunamayinca-uygulama-design.md](../specs/2026-09-30-queenagent-m386-sohbet-listesi-okunamayinca-uygulama-design.md)

## Global Constraints

- Yorumlar İngilizce, NEDEN'i ve yalnız bugün doğru olanı söyler.
- Cümle `Couldn't load chats.`; sınıflar `sidebar__failure`, `sidebar__error`, `sidebar__actions`,
  `failure__retry`, `sidebar__copy`.
- Testlere dokunulmaz; `dist` derlenmez.

---

### Task 1: Hook ve App

**Files:** Modify `queen-agent/frontend/src/features/workspace/useChatLists.js`,
`queen-agent/frontend/src/App.jsx`

**Interfaces:** Produces `useProjectChats(projectId) → { projectChats, projectChatsError, reloadProjectChats }`.

- [ ] **Step 1:** `useChatLists.js`:

```js
// What this project holds, for the sidebar, which lists all of it (Madde 362) -- and, when the read
// failed, what came back instead (Madde 386), so the sidebar never takes a failure for no chats.
export function useProjectChats(projectId) {
  const { items, reload, error } = useList(`/api/projects/${projectId}/chats`, Boolean(projectId));
  return {
    projectChats: projectId ? items : [],
    projectChatsError: projectId ? error : null,
    reloadProjectChats: reload,
  };
}
```

- [ ] **Step 2:** `App.jsx`: `const { projectChats, projectChatsError, reloadProjectChats } =
  useProjectChats(route.projectId);` ve `<Sidebar … error={projectChatsError}
  onRetry={reloadProjectChats} … />`.

### Task 2: Kenar çubuğu

**Files:** Modify `queen-agent/frontend/src/features/workspace/Sidebar.jsx`

- [ ] **Step 1:** `import CopyButton from "./CopyButton.jsx";`; prop'lara `error`, `onRetry`.
- [ ] **Step 2:** `const shown = error ? [] : chats.filter((chat) => matches(chat.title, query));`
  — yorumu: okunamayan listenin eldeki hâli başka bir projeninki olabilir.
- [ ] **Step 3:** `.sidebar__chats`'in içi:

```jsx
{error ? (
  <div className="sidebar__failure">
    <p className="sidebar__error">Couldn&apos;t load chats.</p>
    <div className="sidebar__actions">
      <button type="button" className="failure__retry" onClick={onRetry}>
        Try again
      </button>
      <CopyButton text={error} className="sidebar__copy" />
    </div>
  </div>
) : shown.length ? (
  /* satırlar, bugünkü gibi */
) : (
  /* No chats match / No chats yet, bugünkü gibi */
)}
```

### Task 3: Görünüş

**Files:** Modify `queen-agent/frontend/src/features/workspace/workspace.css` (`.sidebar__empty`'nin altı)

- [ ] **Step 1:**

```css
/* A chat list that could not be read (Madde 386): 364's failure -- one plain sentence, Try again
   and Copy -- in No chats yet.'s place and size. The design draws none for the sidebar. */
.sidebar__failure {
  padding: 10px 12px;
}

.sidebar__error {
  margin: 0;
  font-size: 13px;
  color: #8a5237;
  line-height: 1.5;
}

/* At the narrowest sidebar the two buttons are wider than the row, so they may wrap. */
.sidebar__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.sidebar__copy[data-said="yes"] {
  color: var(--accent);
}

.sidebar__copy[data-said="no"] {
  color: var(--destructive);
}
```

### Task 4: Koş ve commit

- [ ] **Step 1:** Dört satır paralel; hepsi yeşil.
- [ ] **Step 2:** Spec, plan ve kod tek commit:
  `feat: Madde 386 -- the sidebar says a chat list it could not read could not be read, with Try again and Copy`
