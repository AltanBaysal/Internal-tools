# Madde 351 — Kenar çubuğunu katlama · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Katlama düğmesinin kenar çubuğunun sağ altında bir panel ikonu olduğunu, katlanınca `+` ile
aynı ikonun bir sütunda kaldığını, ve `Ctrl + .`'nın her yerde — yazarken de — açıp kapadığını tutan
testler, kırmızı.

**Architecture:** Üç test dosyası. `Sidebar.test.jsx` düğmenin yerini ve biçimini, ikon sütununu;
`App.test.jsx` kısayolu; `workspace.css.test.js` tasarımın ölçülerini kilitler. Katlanmanın App'te
tutulması değişmez; bugünkü iki test (*"the fold still leads the sidebar"*, *"folded, nothing is left
but the way back"*) ve iki kontrolü birlikte tutan stil testi yeni hâle göre değişir.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m351-katlama-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; arayüz yazısı İngilizce (`Hide the sidebar`, `Show the sidebar`,
  `New chat`).
- Bu turda `src/` altında yalnız test dosyaları değişir; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Testler, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/Sidebar.test.jsx` — Madde 51 notu, bir testin
  adı, bir test kalkar, beş test gelir
- Modify: `queen-agent/frontend/src/App.test.jsx` — *"the sidebar folds away and comes back…"*in
  altına üç test
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — bir testin daralması,
  dört test

**Interfaces:**
- Produces (uygulama turunun karşılayacağı): `Sidebar`'ın imzası aynı (`collapsed`, `onToggle`,
  `onNewChat`, `activeProjectId` …). Sınıflar: kenar çubuğunun son çocuğu `div.sidebar__foot`, içinde
  `button.sidebar__fold` > `span.sidebar__panel-icon`; katlı sütunda `button.sidebar__new-chat
  sidebar__new-chat--icon` (`aria-label="New chat"`, yazısı `+`). App'in `window` dinleyicisi
  `Ctrl + .`'da varsayılanı engeller ve `sidebarCollapsed`'i çevirir.

- [ ] **Step 1: `Sidebar.test.jsx`'i değiştir**

İlk satırdaki içe aktarmaya `within` eklenir:

```jsx
import { fireEvent, render, screen, within } from "@testing-library/react";
```

Madde 51 notu şöyle olur:

```jsx
// Madde 51: one button, never a drag -- claude.ai's behaviour rather than the rail's. Madde 351
// (design 174, 187): the button is a panel icon in the sidebar's own last row, and folded the
// sidebar is an icon column -- + for New chat, and the same icon at its foot.
```

*"folded, nothing is left but the way back"* şöyle olur:

```jsx
test("folded, the projects and chats are gone", () => {
  render(<Sidebar projects={PROJECTS} activeProjectId="p1" collapsed onToggle={vi.fn()} />);
  expect(screen.queryByText("Projects")).toBeNull();
  expect(screen.queryByText("Thesis research")).toBeNull();
  expect(screen.queryByText("Recent chats")).toBeNull();
});
```

*"the fold still leads the sidebar"* ve üstündeki `// Madde 338: …` notu yerinde kalır ama not
yalnız markayı anlatır; test silinir, yerine:

```jsx
// Madde 351: Claude Code's place for it -- the sidebar's bottom right, and there in both states, so
// a press never moves out from under the pointer.
test("the fold is the sidebar's last row", () => {
  const { container } = render(
    <Sidebar projects={PROJECTS} activeProjectId="p1" onToggle={vi.fn()} />,
  );
  const foot = container.querySelector(".sidebar").lastElementChild;
  expect(foot.className).toBe("sidebar__foot");
  expect(within(foot).getByRole("button", { name: "Hide the sidebar" })).toBeTruthy();
});

test("folded, the fold is still the last row", () => {
  const { container } = render(
    <Sidebar projects={PROJECTS} activeProjectId="p1" collapsed onToggle={vi.fn()} />,
  );
  const foot = container.querySelector(".sidebar").lastElementChild;
  expect(foot.className).toBe("sidebar__foot");
  expect(within(foot).getByRole("button", { name: "Show the sidebar" })).toBeTruthy();
});

test("the fold is a panel icon rather than an arrow, open or folded", () => {
  const { rerender } = render(
    <Sidebar projects={PROJECTS} activeProjectId="p1" onToggle={vi.fn()} />,
  );
  const open = screen.getByRole("button", { name: "Hide the sidebar" });
  expect(open.querySelector(".sidebar__panel-icon")).toBeTruthy();
  expect(open.textContent).toBe("");
  rerender(<Sidebar projects={PROJECTS} activeProjectId="p1" collapsed onToggle={vi.fn()} />);
  const folded = screen.getByRole("button", { name: "Show the sidebar" });
  expect(folded.querySelector(".sidebar__panel-icon")).toBeTruthy();
  expect(folded.textContent).toBe("");
});

test("folded, New chat stays as a + of its own", () => {
  const onNewChat = vi.fn();
  render(
    <Sidebar
      projects={PROJECTS}
      activeProjectId="p1"
      collapsed
      onToggle={vi.fn()}
      onNewChat={onNewChat}
    />,
  );
  const plus = screen.getByRole("button", { name: "New chat" });
  expect(plus.className).toContain("sidebar__new-chat--icon");
  expect(plus.textContent).toBe("+");
  fireEvent.click(plus);
  expect(onNewChat).toHaveBeenCalled();
});

test("folded with no project open, the fold stands alone", () => {
  // Open, New chat is there only with a project; folded, its + follows the same rule.
  const { container } = render(
    <Sidebar projects={PROJECTS} activeProjectId={null} collapsed onToggle={vi.fn()} />,
  );
  expect(screen.queryByRole("button", { name: "New chat" })).toBeNull();
  expect(container.querySelectorAll(".sidebar button").length).toBe(1);
});
```

- [ ] **Step 2: `App.test.jsx`'e üç testi ekle** (*"the sidebar folds away and comes back, and stays
  folded across an address"*in hemen altına)

```jsx
// Madde 351: Ctrl + . folds the sidebar and brings it back, as on claude.ai (design 174, 187) --
// wherever the focus stands, the composer included.
test("Ctrl + . folds the sidebar and brings it back", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByText("Projects")).toBeTruthy());

  fireEvent.keyDown(window, { key: ".", ctrlKey: true });
  await waitFor(() => expect(screen.queryByText("Projects")).toBeNull());
  expect(screen.getByRole("button", { name: "Show the sidebar" })).toBeTruthy();

  fireEvent.keyDown(window, { key: ".", ctrlKey: true });
  await waitFor(() => expect(screen.getByText("Projects")).toBeTruthy());
});

test("Ctrl + . works while typing, and types nothing", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });

  // false: the default was prevented, so the browser has nothing of its own left to do with it.
  expect(fireEvent.keyDown(box, { key: ".", ctrlKey: true })).toBe(false);
  await waitFor(() => expect(screen.queryByText("Projects")).toBeNull());
  expect(box.value).toBe("hello");
});

test("a full stop typed alone is only a full stop", async () => {
  withRail();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  expect(fireEvent.keyDown(box, { key: "." })).toBe(true);
  expect(screen.getByText("Projects")).toBeTruthy();
});
```

- [ ] **Step 3: `workspace.css.test.js`'i değiştir**

*"both folding controls are big enough and dark enough to find"* şöyle olur:

```js
test("the rail's folding control is big enough and dark enough to find", () => {
  // It was too faint to see -- 15px of muted grey on a surface nearly the same colour. The
  // sidebar's fold was the other half of this rule until Madde 351 made it an icon.
  expect(rule(".rail__chevron")).toContain("font-size: 20px");
  expect(rule(".rail__chevron")).toContain("color: var(--ink)");
});
```

*"a folded sidebar is a strip, and it gets there by its own transition"*in altına:

```js
// Madde 351 (design 174, 187): the fold is a panel icon in the sidebar's own last row.
test("the fold's row keeps to the sidebar's bottom right", () => {
  const foot = rule(".sidebar__foot");
  expect(foot).toContain("display: flex");
  expect(foot).toContain("justify-content: flex-end");
  expect(foot).toContain("margin-top: auto");
});

test("the fold is a square button with no glyph of its own", () => {
  const fold = rule(".sidebar__fold");
  expect(fold).toContain("width: 30px");
  expect(fold).toContain("height: 30px");
  expect(fold).toContain("background: transparent");
  expect(fold).not.toContain("font-size");
});

test("the panel icon is a square with a line near its left edge", () => {
  const icon = rule(".sidebar__panel-icon");
  expect(icon).toContain("width: 16px");
  expect(icon).toContain("height: 16px");
  expect(icon).toContain("border: 1.5px solid var(--ink)");
  expect(icon).toContain("border-radius: 3px");
  const line = rule(".sidebar__panel-icon::after");
  expect(line).toContain("left: 6px");
  expect(line).toContain("border-left: 1.5px solid var(--ink)");
});

test("folded, New chat is a square holding only its plus", () => {
  const plus = rule(".sidebar__new-chat--icon");
  expect(plus).toContain("width: 30px");
  expect(plus).toContain("height: 30px");
  expect(plus).toContain("padding: 0");
  expect(plus).toContain("justify-content: center");
});
```

- [ ] **Step 4: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` kırmızı — Sidebar'ın ilk dört yeni testi, App'in
ilk iki yeni testi ve stilin dört yeni testi düşer; *"folded with no project open…"* ve *"a full stop
typed alone…"* yeşil. Öteki üç satır yeşil.

- [ ] **Step 5: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src docs/superpowers/specs/2026-09-29-queenagent-m351-katlama-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m351-katlama-testler-plan.md
git commit -m @'
test(queen-agent): Madde 351 red -- the fold is a panel icon at the sidebar's bottom right, folded it leaves an icon column, and Ctrl + . folds it from anywhere

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
