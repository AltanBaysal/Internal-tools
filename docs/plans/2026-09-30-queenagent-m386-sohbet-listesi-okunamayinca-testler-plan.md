# Madde 386 — Kenar çubuğu okuyamadığı sohbet listesine "yok" demez · test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 386'nın davranışını tutan testleri yazmak — yalnız testleri — ve süiti kırmızı commit etmek.

**Architecture:** Kenar çubuğunun payı `Sidebar.test.jsx`'te: yeni iki prop, `error` (okunamayan
listenin ham sözü) ve `onRetry`. Görünüşün kilidi `workspace.css.test.js`'te. Gidiş dönüş
`App.test.jsx`'te: sohbet listesinin ilk okuması düşen, ikincisi iki sohbet veren sahte sunucuyla.

**Tech Stack:** vitest + jsdom + Testing Library (React 18).

**Spec:** [2026-09-30-queenagent-m386-sohbet-listesi-okunamayinca-testler-design.md](../specs/2026-09-30-queenagent-m386-sohbet-listesi-okunamayinca-testler-design.md)

## Global Constraints

- Test adları ve yorumları İngilizce, yorum NEDEN'i söyler.
- `skip`, `.todo`, `xfail` yok.
- Süit yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşulur.
- Cümle: `Couldn't load chats.` · düğmeler: `Try again`, `Copy`.
- Sınıflar: `sidebar__failure` (kutu), `sidebar__error` (cümle), `sidebar__actions` (düğmelerin
  satırı), `failure__retry` (Try again), `ghost sidebar__copy` (Copy).
- `Sidebar`'ın yeni prop'ları: `error` (string ya da yok), `onRetry` (fonksiyon).

---

### Task 1: `Sidebar.test.jsx`

**Files:** Modify `queen-agent/frontend/src/features/workspace/Sidebar.test.jsx` (dosyanın sonuna)

- [ ] **Step 1:** Yeni bölüm, K1–K6:

```jsx
// --- A chat list that could not be read (Madde 386; 364's pattern, the design has none) ---------

// What failure.js makes of a Flask 500 page: the code and the body, as they came.
const RAW = "HTTP 500: <!doctype html>\n<title>500 Internal Server Error</title>";

function stubClipboard(answer) {
  const writeText = vi.fn(() => answer);
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  return writeText;
}

test("a chat list that could not be read says so, not that there are none", () => {
  // The chats are on disk; only the read failed. The raw words are Copy's, not the sidebar's.
  render(<Sidebar chats={[]} error={RAW} />);
  const said = screen.getByText("Couldn't load chats.");
  expect(said.className).toBe("sidebar__error");
  expect(said.closest(".sidebar__chats")).toBeTruthy();
  expect(screen.queryByText("No chats yet.")).toBeNull();
  expect(screen.queryByText(/HTTP 500/)).toBeNull();
});

test("under the sentence stand Try again and Copy, and Try again asks for the list again", () => {
  const onRetry = vi.fn();
  const { container } = render(<Sidebar chats={[]} error={RAW} onRetry={onRetry} />);
  const buttons = [...container.querySelectorAll(".sidebar__chats button")];
  expect(buttons.map((one) => one.textContent)).toEqual(["Try again", "Copy"]);
  expect(buttons[0].className).toBe("failure__retry");
  expect(buttons[1].className).toBe("ghost sidebar__copy");
  fireEvent.click(buttons[0]);
  expect(onRetry).toHaveBeenCalled();
});

test("its Copy puts the error on the clipboard exactly as it came", async () => {
  const writeText = stubClipboard(Promise.resolve());
  render(<Sidebar chats={[]} error={RAW} />);
  fireEvent.click(screen.getByRole("button", { name: "Copy" }));
  expect(writeText).toHaveBeenCalledWith(RAW);
  expect(await screen.findByRole("button", { name: "Copied" })).toBeTruthy();
});

test("the failure stands in the rows' place, whatever was listed and whatever is typed", () => {
  // A failed read leaves the last list standing -- another project's, maybe -- so it is not shown.
  const { container } = render(<Sidebar chats={CHATS} error={RAW} />);
  expect(rows(container)).toEqual([]);
  type("zebra");
  expect(screen.queryByText('No chats match "zebra".')).toBeNull();
  expect(screen.getByText("Couldn't load chats.")).toBeTruthy();
});

test("with the list unread, Enter opens nothing", () => {
  const onOpenChat = vi.fn();
  render(<Sidebar chats={CHATS} error={RAW} onOpenChat={onOpenChat} />);
  press("Enter");
  expect(onOpenChat).not.toHaveBeenCalled();
});

test("the failure leaves the sidebar's rows where they were", () => {
  const { container } = render(<Sidebar chats={[]} error={RAW} onToggle={vi.fn()} />);
  const shape = [...container.querySelector(".sidebar").children].map((child) => child.className);
  expect(shape).toEqual(["sidebar__new-chat", "sidebar__search", "sidebar__chats", "sidebar__foot"]);
});
```

`rows`, `type`, `press` 365 bölümünün yardımcıları; bölüm onların altında.

### Task 2: `workspace.css.test.js`

**Files:** Modify `queen-agent/frontend/src/features/workspace/workspace.css.test.js` (`No chats yet.
is a quiet line`'ın altına)

- [ ] **Step 1:** C1–C3:

```js
// Madde 386: a chat list that could not be read, in No chats yet.'s place and size, in the
// failure's brown (364's .empty__error).
test("Couldn't load chats. is the failure's brown, at No chats yet.'s size", () => {
  const said = rule(".sidebar__error");
  expect(said).toContain("margin: 0");
  expect(said).toContain("font-size: 13px");
  expect(said).toContain("color: #8a5237");
});

test("Try again and Copy stand side by side, and wrap at the narrowest sidebar", () => {
  const actions = rule(".sidebar__actions");
  expect(actions).toContain("display: flex");
  expect(actions).toContain("flex-wrap: wrap");
});

test("the sidebar's Copy answers in Copy's own colours", () => {
  expect(rule('.sidebar__copy[data-said="yes"]')).toContain("color: var(--accent)");
  expect(rule('.sidebar__copy[data-said="no"]')).toContain("color: var(--destructive)");
});
```

### Task 3: `App.test.jsx`

**Files:** Modify `queen-agent/frontend/src/App.test.jsx` (`a project with no chats yet says so in
the sidebar`'ın altına)

- [ ] **Step 1:** A1:

```jsx
test("a chat list that could not be read says so in the sidebar, and Try again reads it again", async () => {
  // Madde 386: the chats are on disk, the read failed -- No chats yet. would be a false statement.
  const fetch = serverWithProjects([THESIS], { p1: TWO_CHATS });
  const answer = fetch.getMockImplementation();
  let reads = 0;
  fetch.mockImplementation((path, options) => {
    if (path === "/api/projects/p1/chats" && ++reads === 1) {
      return Promise.resolve({ ok: false, status: 500, text: async () => "" });
    }
    return answer(path, options);
  });
  window.history.pushState(null, "", "/p/p1/c/new");
  render(<App />);
  expect(await screen.findByText("Couldn't load chats.")).toBeTruthy();
  expect(screen.queryByText("No chats yet.")).toBeNull();

  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  expect(await screen.findByText("Missing values", { selector: ".sidebar__chat" })).toBeTruthy();
  expect(screen.queryByText("Couldn't load chats.")).toBeNull();
});
```

`TWO_CHATS` 365 bölümünde tanımlı, test onun altında.

### Task 4: Koş ve commit

- [ ] **Step 1:** Dört satır paralel. Beklenen: queen-agent frontend'de K1–K5, C1–C3, A1 kırmızı; K6
  yeşil; öteki üç süit yeşil.
- [ ] **Step 2:** Spec, plan ve testler tek commit:
  `test(queen-agent): Madde 386 red -- a chat list that could not be read says so in the sidebar, with Try again and Copy`
