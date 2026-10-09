# Madde 338 — Üst çubuk · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Çubuğun her ekranın üstünde durduğunu, solda `QueenAgent` ile sürümü aynı boy ve kalınlıkta,
proje açıkken ortada adı ve sağda `Exit project`'i taşıdığını, ve kenar çubuğunda markanın kalmadığını
tutan testler, kırmızı.

**Architecture:** Beş test dosyası. `Bar.test.jsx` yeni ve çubuğun kendisini tutar; `App.test.jsx`
çubuğun ekranların üstünde durduğunu ve `Exit project`'in açılışa döndüğünü; `Sidebar.test.jsx`
markanın gittiğini; iki stil testi tasarımın ölçülerini kilitler. Madde 209'un markayı kenar çubuğunda
tutan dört testi kalkar.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m338-ust-cubuk-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; arayüz yazısı İngilizce (`Exit project`).
- Bu turda `src/` altında yalnız test dosyaları değişir; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Testler, kırmızı

**Files:**
- Create: `queen-agent/frontend/src/features/workspace/Bar.test.jsx`
- Modify: `queen-agent/frontend/src/App.test.jsx` — "the shell renders"ın altına dört test
- Modify: `queen-agent/frontend/src/features/workspace/Sidebar.test.jsx` — üç test kalkar, iki test gelir, ilk testin adı
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — sürümün notu tutan testi yerine dört test
- Modify: `queen-agent/frontend/src/shared/app.css.test.js` — kabuğun testinin altına bir test

**Interfaces:**
- Produces (uygulama turunun karşılayacağı): `features/workspace/Bar.jsx`'in varsayılan dışa aktarımı
  `Bar({ project, onExit })` — `project` App'in bulduğu proje ya da `null`. Sınıflar: `bar`,
  `bar__name` (içinde `bar__wordmark` ve `bar__version`, arada boşluk), `bar__project`,
  `ghost bar__exit`; kabukta `app-shell__body`.

- [ ] **Step 1: `Bar.test.jsx`'i yaz**

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import { VERSION } from "../../shared/version.js";
import Bar from "./Bar.jsx";

const PROJECT = { id: "p1", name: "Thesis research", chats: 3, files: 3 };

test("the name and the run number read as one line", () => {
  // Madde 209 put the version under the name, where it read as a footnote. The user's call (v9-2,
  // and the design's 159): beside it, as Queen Editor writes "Queen Editor 1.4.2". Asked of the
  // constant rather than of "V8", for the reason version.test.js gives.
  const { container } = render(<Bar project={null} onExit={vi.fn()} />);
  expect(container.querySelector(".bar__name").textContent).toBe(`QueenAgent ${VERSION}`);
});

test("with no project open, the bar holds the brand alone", () => {
  const { container } = render(<Bar project={null} onExit={vi.fn()} />);
  expect(container.querySelector(".bar__project")).toBeNull();
  expect(screen.queryByRole("button", { name: "Exit project" })).toBeNull();
});

test("with a project open, its name stands in the middle and the way out on the right", () => {
  const { container } = render(<Bar project={PROJECT} onExit={vi.fn()} />);
  const name = container.querySelector(".bar__project");
  expect(name.textContent).toBe("Thesis research");
  // Cut on one line when it is long, so the whole of it has to be somewhere.
  expect(name.getAttribute("title")).toBe("Thesis research");
  expect(screen.getByRole("button", { name: "Exit project" }).className).toBe("ghost bar__exit");
});

test("Exit project asks to leave rather than deciding where to", () => {
  const onExit = vi.fn();
  render(<Bar project={PROJECT} onExit={onExit} />);
  fireEvent.click(screen.getByRole("button", { name: "Exit project" }));
  expect(onExit).toHaveBeenCalled();
});
```

- [ ] **Step 2: `App.test.jsx`'e dört testi ekle** ("the shell renders"ın hemen altına)

```jsx
// Madde 338: one bar across the window's top, on every screen, above the sidebar and the screen.
test("the bar stands above the sidebar and the screen while the first list loads", () => {
  vi.stubGlobal("fetch", vi.fn().mockReturnValue(new Promise(() => {})));
  render(<App />);
  expect(screen.getByTestId("skeleton")).toBeTruthy();
  const shell = screen.getByTestId("app-shell");
  expect(shell.children[0].className).toBe("bar");
  const body = shell.children[1];
  expect(body.className).toBe("app-shell__body");
  expect(shell.querySelector(".sidebar").parentElement).toBe(body);
  expect(shell.querySelector(".main").parentElement).toBe(body);
});

test("with no project at all, the bar holds the brand alone", async () => {
  stubProjects([]);
  render(<App />);
  await screen.findByText(/No projects yet/);
  const bar = screen.getByTestId("app-shell").querySelector(".bar");
  expect(bar.textContent).toContain("QueenAgent");
  expect(bar.querySelector(".bar__project")).toBeNull();
  expect(screen.queryByRole("button", { name: "Exit project" })).toBeNull();
});

// The chat is the second project's, so the opening landing on the first one is told apart from
// going back to the project's own screen.
function stubChatInSecondProject() {
  const chat = { id: "c1", title: "Draft", messages: [] };
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (path.endsWith("/chats/c1")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => chat });
      }
      if (path.endsWith("/chats") || path.endsWith("/files")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [] });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT, PROJECT_2] });
    }),
  );
  window.history.pushState(null, "", "/p/p2/c/c1");
}

test("in a chat, the bar carries the project's name and the way out of it", async () => {
  stubChatInSecondProject();
  render(<App />);
  expect(await screen.findByText("Newer", { selector: ".bar__project" })).toBeTruthy();
  expect(screen.getByRole("button", { name: "Exit project" })).toBeTruthy();
});

test("Exit project goes back to where the app opens", async () => {
  // Today the opening is the fork at "/": the first project, or the empty screen with none.
  stubChatInSecondProject();
  render(<App />);
  await screen.findByText("Newer", { selector: ".bar__project" });
  fireEvent.click(screen.getByRole("button", { name: "Exit project" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
});
```

- [ ] **Step 3: `Sidebar.test.jsx`'i değiştir**

İlk testin adı `"with no project selected only the projects remain"` olur. Şu üç test silinir:
`"folded, the version folds with the name"`, `"there is no logo mark beside the wordmark"`,
`"the sidebar says which run this is"`. Yerlerine, `"folded, it says so where the stylesheet can hear
it"`in altına:

```jsx
// Madde 338: the brand moved into the bar above the sidebar; the fold stays here until v9-2w.
test("the sidebar carries no brand", () => {
  const { container } = render(<Sidebar projects={PROJECTS} activeProjectId="p1" />);
  expect(screen.queryByText("QueenAgent")).toBeNull();
  expect(screen.queryByText(VERSION)).toBeNull();
  expect(container.querySelector(".sidebar__brand")).toBeNull();
});

test("the fold still leads the sidebar", () => {
  const { container } = render(
    <Sidebar projects={PROJECTS} activeProjectId="p1" onToggle={vi.fn()} />,
  );
  expect(container.querySelector(".sidebar").firstElementChild.getAttribute("aria-label")).toBe(
    "Hide the sidebar",
  );
});
```

- [ ] **Step 4: `workspace.css.test.js`'i değiştir**

`"the version sits under the name and reads as a note"` silinir; yerine:

```js
// Madde 338: the design's bar (queen-design v3, items 150, 159, 161, 166).
test("the bar is one height on every screen, its middle at the window's centre", () => {
  const bar = rule(".bar");
  expect(bar).toContain("height: 56px");
  expect(bar).toContain("flex: none");
  expect(bar).toContain("grid-template-columns: minmax(0, 1fr) minmax(0, auto) minmax(0, 1fr)");
});

test("the version is the name's own size and weight, never bold", () => {
  const name = rule(".bar__name");
  expect(name).toContain("font-family: var(--font-heading)");
  expect(name).toContain("font-size: 21px");
  expect(name).toContain("white-space: nowrap");
  // Nothing of its own but the weight, written out: the size and the ink are the name's.
  const version = rule(".bar__version");
  expect(version).toContain("font-weight: 400");
  expect(version).not.toContain("font-size");
  expect(version).not.toContain("color");
});

test("the project's name is cut on one line, and the way out keeps the right", () => {
  const project = rule(".bar__project");
  expect(project).toContain("max-width: 640px");
  expect(project).toContain("white-space: nowrap");
  expect(project).toContain("text-overflow: ellipsis");
  // With no project the middle draws nothing, and the button would slide into its column.
  const exit = rule(".bar__exit");
  expect(exit).toContain("grid-column: 3");
  expect(exit).toContain("justify-self: end");
});

test("the sidebar's brand is gone by every name", () => {
  for (const name of ["sidebar__brand", "sidebar__name", "sidebar__wordmark", "sidebar__version"]) {
    expect(CSS).not.toContain(`.${name}`);
  }
});
```

- [ ] **Step 5: `app.css.test.js`'e kabuğun testini ekle** ("the shell is the height of the visible window and no less"ın altına)

```js
// Madde 338: the bar stands on top, and the sidebar and main share what is left of the window.
test("the shell stacks the bar over a body that takes the rest", () => {
  expect(rule(APP, ".app-shell")).toContain("flex-direction: column");
  const body = rule(APP, ".app-shell__body");
  expect(body).toContain("display: flex");
  expect(body).toContain("flex: 1");
  // Without it the body grows with its content and the page scrolls, which the shell forbids.
  expect(body).toContain("min-height: 0");
});
```

- [ ] **Step 6: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` kırmızı — `Bar.test.jsx` `./Bar.jsx` bulunamadığı
için yüklenemez; App'in dört testi, Sidebar'ın iki testi, stilin dört testi ve kabuğun testi düşer.
queen-agent'ın arka ucu ve queen-editor'ün ön ucu yeşil; queen-editor'ün arka ucu 377'nin bilinen iki
kırmızısı.

- [ ] **Step 7: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src docs/specs/2026-09-29-queenagent-m338-ust-cubuk-testler-design.md docs/plans/2026-09-29-queenagent-m338-ust-cubuk-testler-plan.md
git commit -m @'
test(queen-agent): Madde 338 red -- a bar above every screen holds the name and version alike, the open project and Exit project; the sidebar has no brand

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
