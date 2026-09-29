# Madde 362 — Kenar çubuğunda yalnız New chat ve sohbetler · uygulama turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Commit edilmiş kırmızı testleri yeşile çevirmek: kenar çubuğu dolu `+ New chat` ve projenin
bütün sohbetleri; proje listesi, `Recent chats`, `+` ve onların CSS'i, prop'ları, durumu gider.

**Architecture:** Yalnız ön uç. `Sidebar` proje bilmez olur; App ona açık projenin sohbetlerini verir.
Ad sorma ekranına tek yol All projects kaldığı için App'in `namingFrom`'u gider.

**Tech Stack:** React 18, Vite, vitest.

**Spec:** [2026-09-29-queenagent-m362-kenar-cubugu-sohbetler-uygulama-design.md](../specs/2026-09-29-queenagent-m362-kenar-cubugu-sohbetler-uygulama-design.md)

## Global Constraints

- Kod, yorum, UI İngilizce; yorum NEDEN'i ve bugün doğru olanı söyler.
- Testlere dokunulmaz; yazılan kod testlerin istediği kadar.
- `dist` derlenmez.
- Süit yalnız CLAUDE.md'deki dört satırla, paralel.

---

### Task 1: `Sidebar.jsx`

- [ ] **Step 1:** Dosyanın gövdesi:

```jsx
// Inside a project the sidebar is the project's own (design 151, 152, 168): a filled + New chat
// first, then every chat it holds. Projects are listed on All projects, and the open one's name is
// in the bar, so none is listed here. App draws the sidebar only with a project open.

// Fold: bugünkü hâli; yalnız yorumdaki "as .dot is" gider.

export default function Sidebar({ chats = [], activeChatId, onNewChat, onOpenChat, collapsed, onToggle }) {
  if (collapsed) {
    return (
      <aside className="sidebar sidebar--collapsed">
        <button type="button" className="sidebar__new-chat sidebar__new-chat--icon" aria-label="New chat" onClick={onNewChat}>
          <span className="sidebar__plus">+</span>
        </button>
        <Fold collapsed onToggle={onToggle} />
      </aside>
    );
  }
  return (
    <aside className="sidebar">
      <button type="button" className="sidebar__new-chat" onClick={onNewChat}>
        <span className="sidebar__plus">+</span>
        New chat
      </button>
      <div className="sidebar__chats">
        {chats.length ? chats.map((chat) => (/* bugünkü sidebar__chat düğmesi */)) : (
          <p className="sidebar__empty">No chats yet.</p>
        )}
      </div>
      <Fold onToggle={onToggle} />
    </aside>
  );
}
```

### Task 2: `App.jsx`

- [ ] **Step 1:** `<Sidebar>`: `chats={projectChats}`, `activeChatId`, `onNewChat={openDraft}`,
  `onOpenChat`, `collapsed`, `onToggle`.
- [ ] **Step 2:** `namingFrom`/`setNamingFrom` silinir;
  `const askForNewProject = () => navigate("/new");`,
  `const leaveNaming = () => navigate("/", { replace: true });`. Escape dalı bugünkü gibi kendi
  `navigate("/", { replace: true })`'sunu yazar — `leaveNaming` her render'da yeni, bağımlılık
  listesine girse dinleyici her render'da yeniden takılırdı —; listeden `namingFrom` çıkar.

### Task 3: `useChatLists.js`

- [ ] **Step 1:** `useProjectChats`'in yorumu: *The open project's chats, for the sidebar, which lists
  them all.*

### Task 4: `workspace.css`

- [ ] **Step 1:** Spec'in *Gider* listesindeki kurallar silinir; `.sidebar__chats`'in yorumu:
  *The chats fill what New chat leaves, and scroll inside themselves.*
- [ ] **Step 2:** `.sidebar__chat--active` kuralının ardına:

```css
/* No chats yet (design 168), in .file-list__empty's kind, sized for the sidebar. */
.sidebar__empty {
  padding: 10px 12px;
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}
```

### Task 5: Koş ve commit

- [ ] **Step 1:** Dört satır paralel; dördü de yeşil.
- [ ] **Step 2:** Uygulama spec'i, plan ve kod tek commit:
  `feat: Madde 362 -- the sidebar holds New chat and every chat of the project, and no projects list`
