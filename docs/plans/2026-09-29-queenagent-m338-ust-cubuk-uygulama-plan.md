# Madde 338 — Üst çubuk · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test turunun kırmızı testlerini yeşile getiren çubuk: her ekranın üstünde, solda
`QueenAgent V8`, proje açıkken ortada adı ve sağda `Exit project`; kenar çubuğunda marka yok.

**Architecture:** Yeni `Bar.jsx` App'te bir kez, `app-shell`'in ilk çocuğu olarak çizilir; kenar
çubuğu ve `main` altındaki `app-shell__body`'ye girer. Kenar çubuğunun markası ve stilleri kalkar.

**Tech Stack:** React 18, düz CSS; vitest + jsdom.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m338-ust-cubuk-uygulama-design.md)

## Global Constraints

- Arayüz yazısı İngilizce: `QueenAgent`, `Exit project`.
- Sürüm yalnız `shared/version.js`'in `VERSION`'ından okunur.
- `workspace.css`'te yalnız bu maddenin kuralları değişir; başkalarınınkine dokunulmaz, sıraları
  değişmez.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Çubuk, kabuk ve markasız kenar çubuğu

**Files:**
- Create: `queen-agent/frontend/src/features/workspace/Bar.jsx`
- Modify: `queen-agent/frontend/src/App.jsx` — import ve `return`'ün kabuğu
- Modify: `queen-agent/frontend/src/features/workspace/Sidebar.jsx` — marka bloğu ve `VERSION` importu kalkar
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` — sidebar'ın dört kuralı kalkar, çubuğun beş kuralı gelir, `.sidebar__fold`'un iki yorumu
- Modify: `queen-agent/frontend/src/shared/app.css` — `.app-shell` ve `.app-shell__body`
- Modify: `queen-agent/frontend/src/shared/version.js` — yorum
- Modify: `queen-agent/frontend/src/App.test.jsx` — yeniden adlandırma testi adı üç yerde sayar

**Interfaces:**
- Consumes: test turunun testleri; `shared/version.js`'in `VERSION`'ı; App'in `project`'i ve
  `navigate`'i.
- Produces: `Bar({ project, onExit })`.

- [ ] **Step 1: `Bar.jsx`'i yaz**

```jsx
import { VERSION } from "../../shared/version.js";

// Across the window's top, on every screen (the design's items 150, 159, 161, 166): the name and
// the run number on the left, the open project's name in the middle, and the way out of it on the
// right. With no project open the middle and the right draw nothing; the stylesheet's grid keeps
// the bar where it was.
export default function Bar({ project, onExit }) {
  return (
    <header className="bar">
      {/* Two spans with a space between, so the pair is read out as two words; the version is not
          a footnote but the name's own size and weight, as Queen Editor writes "Queen Editor 1.4.2". */}
      <span className="bar__name">
        <span className="bar__wordmark">QueenAgent</span>{" "}
        <span className="bar__version">{VERSION}</span>
      </span>
      {project ? (
        <>
          <span className="bar__project" title={project.name}>
            {project.name}
          </span>
          <button type="button" className="ghost bar__exit" onClick={onExit}>
            Exit project
          </button>
        </>
      ) : null}
    </header>
  );
}
```

- [ ] **Step 2: `App.jsx`'te çubuğu ve gövdeyi kur**

Import, `./features/workspace/ChatScreen.jsx`'in üstüne: `import Bar from "./features/workspace/Bar.jsx";`

`return`'ün kabuğu:

```jsx
    <div ref={shell} className={`app-shell ${steps}`.trim()} data-testid="app-shell">
      {/* "/" is where the app opens: the fork there decides what that is, so leaving a project
          asks it rather than repeating its rule. */}
      <Bar project={project} onExit={() => navigate("/")} />
      <div className="app-shell__body">
        <Sidebar ... />   {/* değişmeden, bir basamak içeride */}
        <main className="main"> ... </main>   {/* değişmeden, bir basamak içeride */}
      </div>

      {/* Outside main so the darkened screen covers the sidebar too. */}
      {confirming ? ( ... ) : null}
    </div>
```

- [ ] **Step 3: `Sidebar.jsx`'ten markayı kaldır**

`import { VERSION } from "../../shared/version.js";` satırı silinir. Açık hâlin başı:

```jsx
    <aside className="sidebar">
      <Fold onToggle={onToggle} />

      {activeProjectId ? (
```

- [ ] **Step 4: `workspace.css`'i değiştir**

`.sidebar__brand`, `.sidebar__wordmark`, `.sidebar__name`, `.sidebar__version` kuralları ve
yorumları silinir. `.sidebar__fold`'un yorumu:
`/* At the sidebar's head, pushed to its right edge while open, and the whole of it once folded. */`
Katlanmış hâlin yorumu:
`/* Folded, the strip centres it, and the margin that pushed it right would pull it off centre. */`

`.main`'in altına, `/* --- sidebar --- */`'ın üstüne:

```css
/* --- bar ---------------------------------------------------------------- */

/* Across the window's top, on every screen: three columns, the middle always at the window's
   centre whatever the sides hold. One height, so a project opening or closing never moves it. */
.bar {
  height: 56px;
  flex: none;
  display: grid;
  align-items: center;
  gap: 16px;
  grid-template-columns: minmax(0, 1fr) minmax(0, auto) minmax(0, 1fr);
  padding: 0 12px;
  background: var(--sidebar);
  border-bottom: 1px solid var(--line);
}

/* The name and the version on one line, in the heading face; the ink is the page's own. */
.bar__name {
  font-family: var(--font-heading);
  font-size: 21px;
  letter-spacing: 0.2px;
  white-space: nowrap;
}

/* The name's own size and ink, and its weight too: the user asked for it not to be bold. */
.bar__version {
  font-weight: 400;
}

.bar__project {
  justify-self: center;
  min-width: 0;
  max-width: 640px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font: 500 18px var(--font-heading);
  color: var(--ink);
}

/* With no project open the middle draws nothing, and without this the button would slide into the
   middle column. */
.bar__exit {
  grid-column: 3;
  justify-self: end;
}
```

- [ ] **Step 5: `app.css`'te kabuğu dik kur**

```css
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100dvh;
  width: 100%;
  overflow: hidden;
  background: var(--canvas);
}

/* The sidebar and main, side by side under the bar. Without min-height: 0 it would grow with its
   content and push the page into scrolling. */
.app-shell__body {
  flex: 1;
  min-height: 0;
  display: flex;
  overflow: hidden;
}
```

- [ ] **Step 6: `version.js`'in yorumu**

"Its own module rather than a line inside the sidebar: the sidebar draws it, it does not own it" →
"Its own module rather than a line inside the bar: the bar draws it, it does not own it".

- [ ] **Step 7: Yeniden adlandırma testi üç yeri sayar**

`App.test.jsx`'te *"a renamed project shows the new name in both places at once"*:

```jsx
test("a renamed project shows the new name in every place at once", async () => {
  ...
  // The title, the sidebar row and the bar (Madde 338) read the same array, so they cannot
  // disagree.
  await waitFor(() => expect(screen.getAllByText("New").length).toBe(3));
});
```

- [ ] **Step 8: Dört satırı paralel koş, yeşili gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent'ın iki süiti yeşil; queen-editor'ün ön ucu yeşil, arka ucu 377'nin bilinen iki
kırmızısı.

- [ ] **Step 9: Commit'le**

```powershell
git add queen-agent/frontend/src docs/specs/2026-09-29-queenagent-m338-ust-cubuk-uygulama-design.md docs/plans/2026-09-29-queenagent-m338-ust-cubuk-uygulama-plan.md
git commit -m @'
feat: Madde 338 -- a bar above every screen: QueenAgent and its version alike on the left, the open project in the middle, Exit project back to the opening; the sidebar has no brand

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
