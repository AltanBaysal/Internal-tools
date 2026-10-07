# Madde 351 — Kenar çubuğunu katlama · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Katlama düğmesi kenar çubuğunun sağ altında bir panel ikonu; katlanınca `+` ve aynı ikon bir
sütunda kalıyor; `Ctrl + .` her yerde açıp kapıyor — test turunun kırmızıları yeşil.

**Architecture:** `Sidebar.jsx`'in `Fold`'u kendi `sidebar__foot` satırını çizer ve iki hâlde de son
çocuktur; katlı hâl proje açıkken bir `+` taşır. `App.jsx`'in tek `keydown` dinleyicisi `Ctrl + .`'da
App'in `sidebarCollapsed`'ini çevirir. `workspace.css` tasarımın dört kuralını alır.

**Tech Stack:** React 18, düz CSS, vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m351-katlama-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod ve yorum İngilizce; arayüz yazısı İngilizce. Yorum *neden*i söyler, yalnız bugün doğru olanı.
- `workspace.css`'te yalnız kenar çubuğunun kendi kuralları değişir; başkalarının kuralları yerinden
  oynamaz.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Katlama, yeşil

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/Sidebar.jsx` — `Fold`, katlı hâl, açık hâlin sırası, baştaki not
- Modify: `queen-agent/frontend/src/App.jsx` — `keydown` dinleyicisi
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` — kenar çubuğunun katlama kuralları

**Interfaces:**
- Consumes: test turunun testleri (`1373dc7b`).
- Produces: `Sidebar`'ın imzası değişmez.

- [ ] **Step 1: `Sidebar.jsx` — `Fold` ve baştaki not**

```jsx
// One button, never a drag: claude.ai's behaviour rather than the rail's, and the user asked for it
// by that name. It stands in the sidebar's own last row, open and folded alike, so a press never
// moves out from under the pointer (design 187, Claude Code's place for it). Folded, the sidebar is
// not hidden: an icon column stands where it was, + for New chat above and this fold at its foot
// (design 174); the rows are names and titles, and have no icon forms to fold into.
function Fold({ collapsed, onToggle }) {
  return (
    <div className="sidebar__foot">
      <button
        type="button"
        className="sidebar__fold"
        aria-label={collapsed ? "Show the sidebar" : "Hide the sidebar"}
        onClick={onToggle}
      >
        {/* Drawn in CSS, as .dot is: the app carries no icon files. */}
        <span className="sidebar__panel-icon" />
      </button>
    </div>
  );
}
```

- [ ] **Step 2: `Sidebar.jsx` — katlı hâl ve açık hâlin sırası**

```jsx
  if (collapsed) {
    return (
      <aside className="sidebar sidebar--collapsed">
        {activeProjectId ? (
          <button
            type="button"
            className="sidebar__new-chat sidebar__new-chat--icon"
            aria-label="New chat"
            onClick={onNewChat}
          >
            <span className="sidebar__plus">+</span>
          </button>
        ) : null}
        <Fold collapsed onToggle={onToggle} />
      </aside>
    );
  }
```

Açık hâlde `<Fold onToggle={onToggle} />` `aside`'ın başından çıkar ve sohbetlerin bloğundan sonra,
`</aside>`'ın hemen önüne gelir.

- [ ] **Step 3: `App.jsx` — `Ctrl + .`**

`onKey`'in başı:

```js
    const onKey = (event) => {
      // Ctrl + . folds the sidebar and brings it back from anywhere, the composer included (Madde
      // 351, claude.ai's key). Held with Ctrl a key types nothing into a field, and taking the
      // default leaves the browser nothing else to do with it.
      if (event.ctrlKey && event.key === ".") {
        event.preventDefault();
        setSidebarCollapsed((folded) => !folded);
        return;
      }
      if (event.key !== "Escape") return;
```

- [ ] **Step 4: `workspace.css` — kenar çubuğunun kuralları**

`.sidebar--collapsed`'in notu:

```css
/* Folded to an icon column rather than hidden: + for New chat, and the fold at its foot. Every other
   row here is a name or a title, and has no icon form. 52 wide above a 1000 shell only: the steps
   below it name two classes, so they outweigh this one and keep their own width. */
```

`.sidebar__fold`, notu ve `:hover`'ı; `.sidebar--collapsed .sidebar__fold` kalkar:

```css
/* The fold's own row, the sidebar's last (design 187): right of the chat list while open, and pushed
   to the bottom by margin-top: auto whatever stands above it. Folded, the column's align-items:
   center narrows the row to its one button and centres it under the +. */
.sidebar__foot {
  display: flex;
  justify-content: flex-end;
  margin-top: auto;
}

/* A 30 square holding the panel icon: the same square the folded + is. */
.sidebar__fold {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: none;
  width: 30px;
  height: 30px;
  border: none;
  border-radius: var(--radius-control);
  background: transparent;
  cursor: pointer;
}

.sidebar__fold:hover {
  background: #e5dfd5;
}

/* A panel: a square with a line near its left edge, the design's own mark (174, 187). */
.sidebar__panel-icon {
  position: relative;
  display: block;
  width: 16px;
  height: 16px;
  box-sizing: border-box;
  border: 1.5px solid var(--ink);
  border-radius: 3px;
}

.sidebar__panel-icon::after {
  content: "";
  position: absolute;
  top: -1.5px;
  bottom: -1.5px;
  left: 6px;
  border-left: 1.5px solid var(--ink);
}
```

`.sidebar__plus`'tan sonra — `.sidebar__new-chat`'in payını ezsin diye ondan sonra:

```css
/* Folded, New chat is this square alone (design 174): the same filled button, its word gone. */
.sidebar__new-chat--icon {
  width: 30px;
  height: 30px;
  padding: 0;
  justify-content: center;
  flex: none;
}
```

- [ ] **Step 5: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü yeşil; queen-agent'ın ön ucu 706.

- [ ] **Step 6: Commit'le**

```powershell
git add queen-agent/frontend/src docs/specs/2026-09-29-queenagent-m351-katlama-uygulama-design.md docs/plans/2026-09-29-queenagent-m351-katlama-uygulama-plan.md
git commit -m @'
feat: Madde 351 -- the fold is a panel icon at the sidebar's bottom right, folded it leaves + and itself in an icon column, and Ctrl + . folds it from anywhere

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
