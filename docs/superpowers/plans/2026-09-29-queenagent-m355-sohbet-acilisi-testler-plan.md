# Madde 355 — Sohbet açılırken açılmış gibi görünür · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kaydı gelmemiş sohbetin kendi çerçevesinde — başlık, kapalı kutu, dosya paneli — ve
mesajların yerinde spinner'la durduğunu tutan testler, kırmızı.

**Architecture:** `ChatScreen.test.jsx` çerçeveyi, `App.test.jsx` başlığın kenar çubuğundaki
satırdan geldiğini, `workspace.css.test.js` tasarımın ölçülerini tutar. `App.test.jsx`'in kayıt
okunmuş sohbette yazan ya da seçici açan testleri tek bir yardımcıyla açık kutuyu bekler.

**Tech Stack:** vitest + jsdom, Testing Library.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m355-sohbet-acilisi-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce.
- Bu turda `ChatScreen.jsx`, `Composer.jsx`, seçiciler, `App.jsx` ve `workspace.css` yazılmaz.
- `dist` derlenmez. Commit mesajında çift tırnak yok; amend yok.
- `workspace.css` çalışma ağacında CRLF: bir seçicinin içine `\n` yazılmaz.

---

### Task 1: Açılışın testleri, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` — *a chat that does not
  exist* testi spinner'ı sorar; *a chat still on its way draws blocks* kalkar, yerine altı test
- Modify: `queen-agent/frontend/src/App.test.jsx` — `chatOpened` yardımcısı, onu bekleyen testler, bir
  yeni test
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — üç test

**Interfaces:**
- Produces: uygulama turunun karşılayacakları — `ChatScreen`'in yeni `loadingTitle` prop'u (kenar
  çubuğundaki satırın adı; yoksa boş); `chat={null}` ve `missing` değilken `.chat-layout` çerçevesi,
  `.chat__column`'da tek çocuk `<div className="chat__spinner">` ve içinde Spinner; `Reply...`
  kutusu ve `.composer__foot .picker`'lar `disabled`; `.back` yok. `App.jsx` `loadingTitle`'ı
  `projectChats`'teki satırdan verir. `workspace.css`'te satır başında `.chat__spinner {` ve
  `.composer__input:disabled,` / `.picker:disabled {`; `.skeleton--message` yok.

- [ ] **Step 1: `ChatScreen.test.jsx`** — bugünkü iki test:

```jsx
test("a chat that does not exist says so instead of crashing", () => {
  render(<ChatScreen project={PROJECT} chat={null} missing />);
  expect(screen.getByText("That chat does not exist.")).toBeTruthy();
  expect(screen.queryByTestId("skeleton")).toBeNull();
});

test("a chat still on its way draws blocks", () => {
  render(<ChatScreen project={PROJECT} chat={null} />);
  expect(screen.getByTestId("skeleton")).toBeTruthy();
});
```

yerine:

```jsx
test("a chat that does not exist says so, under the way back", () => {
  // The design keeps ← back over the missing line (item 194 takes it only from a chat opening).
  render(<ChatScreen project={PROJECT} chat={null} missing />);
  expect(screen.getByText("That chat does not exist.")).toBeTruthy();
  expect(screen.getByRole("button", { name: "← back" })).toBeTruthy();
  expect(screen.queryByTestId("spinner")).toBeNull();
});

// --- a chat while it opens (Madde 355) -----------------------------------------------------------
//
// Design item 194: until the record comes the chat's own frame stands -- its title, a shut box and
// the rail -- and only where the messages will be does the spinner turn.

const RAIL = [{ name: "outline.md", ext: "md", modifiedAt: NOW }];

test("a chat still on its way stands in its own frame", () => {
  const { container } = render(
    <ChatScreen project={PROJECT} chat={null} loadingTitle="Write the intro" files={RAIL} />,
  );
  // The sidebar row's own name: the list was read before the record, and says the same.
  expect(container.querySelector(".chat__header").textContent).toBe("Write the intro");
  expect(screen.getByTestId("file-rail").textContent).toContain("outline.md");
  expect(screen.getByPlaceholderText("Reply...")).toBeTruthy();
});

test("where the messages will be, the spinner turns and nothing else", () => {
  // Not even a turn still running into this chat: opening draws no turn (design item 194).
  const { container } = render(
    <ChatScreen project={PROJECT} chat={null} thinking streamingText="Half" />,
  );
  const column = container.querySelector(".chat__column");
  expect(column.children).toHaveLength(1);
  expect(column.firstElementChild.className).toBe("chat__spinner");
  expect(column.firstElementChild.firstElementChild).toBe(screen.getByTestId("spinner"));
  expect(screen.queryByTestId("skeleton")).toBeNull();
});

test("nothing in the box can be written or picked yet", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={null} />);
  expect(screen.getByPlaceholderText("Reply...").disabled).toBe(true);
  const pickers = [...container.querySelectorAll(".composer__foot .picker")];
  expect(pickers.map((picker) => picker.disabled)).toEqual([true, true, true]);
});

test("no way back stands alone while it opens", () => {
  render(<ChatScreen project={PROJECT} chat={null} onBack={vi.fn()} />);
  expect(screen.queryByRole("button", { name: "← back" })).toBeNull();
});

test("a chat whose row has not come either opens with a blank title", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={null} />);
  expect(container.querySelector(".chat__title").textContent).toBe("");
});

test("a sentence left in one chat's box does not follow into the next", () => {
  // The box is born afresh with each chat, as it was when opening took the box away: what was typed
  // in one chat is never offered to another.
  const { rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  fireEvent.change(screen.getByPlaceholderText("Reply..."), { target: { value: "for the first" } });
  rerender(<ChatScreen project={PROJECT} chat={null} />);
  rerender(<ChatScreen project={PROJECT} chat={{ ...CHAT, id: "c2", title: "Other" }} />);
  expect(screen.getByPlaceholderText("Reply...").value).toBe("");
});
```

- [ ] **Step 2: `App.test.jsx`'te `chatOpened`** — `stubProjects`'in altına:

```jsx
// Madde 355: a chat's frame stands from the moment it opens, its box and pickers shut until the
// record is read. What a test types or picks in a chat waits for the box to open.
const chatOpened = () =>
  waitFor(() => {
    const box = screen.getByPlaceholderText("Reply...");
    expect(box.disabled).toBe(false);
    return box;
  });
```

ve kayıt okunmuş sohbette yazan ya da seçici açan beklemeler ona döner (hepsi, aynı metinle):

- `await screen.findByPlaceholderText("Reply...")` → `await chatOpened()`
- `await waitFor(() => expect(screen.getByPlaceholderText("Reply...")).toBeTruthy());` → `await chatOpened();`
- `const box = screen.getByPlaceholderText("Reply...");` → `const box = await chatOpened();`
- `await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());` → `await chatOpened();`
- `await waitFor(() => expect(screen.getByRole("button", { name: /Queen Flash/ })).toBeTruthy());` → `await chatOpened();`
- *the mode in force* ve *Escape closes the mode picker too*'daki `Edit` seçicisinin beklemesi →
  `await chatOpened();`
- `reborn()`'un `Skills|Edit prompts` beklemesi → `return chatOpened();`

Taslak sohbette (`/c/new`) kutu hep açık, yardımcı orada da hemen döner.

- [ ] **Step 3: `App.test.jsx`'e yeni test**, *a newborn chat is named by the trimmed first message*'ın
  üstüne:

```jsx
// Madde 355, design item 194: a chat opening looks opened -- the sidebar row's name over it, the
// rail beside it, the box shut -- and only where its messages will be does anything wait.
test("a chat whose record has not come yet stands in its own frame", async () => {
  const row = { id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() };
  const file = { name: "plan.md", ext: "md", modifiedAt: new Date().toISOString() };
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (path.endsWith("/chats/c1")) return new Promise(() => {});
      if (path.endsWith("/chats")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [row] });
      }
      if (path.endsWith("/files")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [file] });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
    }),
  );
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  expect(await screen.findByText("Write the intro", { selector: ".chat__title" })).toBeTruthy();
  await waitFor(() => expect(screen.getByTestId("file-rail").textContent).toContain("plan.md"));
  expect(document.querySelector(".chat__spinner [data-testid=spinner]")).toBeTruthy();
  expect(screen.getByPlaceholderText("Reply...").disabled).toBe(true);
  expect(screen.queryByRole("button", { name: "← back" })).toBeNull();
});
```

- [ ] **Step 4: `workspace.css.test.js`'e üç test**, *in the file list the spinner stands centred*'ın
  altına:

```js
// Madde 355, design item 194: a chat opening turns the same ring where its messages will be.
test("in a chat that is opening the spinner stands centred where the messages will be", () => {
  const spot = rule(".chat__spinner");
  expect(spot).toContain("display: flex");
  expect(spot).toContain("justify-content: center");
  expect(spot).toContain("padding: 40px 12px");
});

test("the box and its pickers, shut while the chat opens, fade like every shut control", () => {
  expect(CSS).toMatch(/\n\.composer__input:disabled,\r?\n\.picker:disabled \{/);
  const shut = rule(".picker:disabled");
  expect(shut).toContain("cursor: default");
  expect(shut).toContain("opacity: 0.4");
});

test("the message skeleton is gone with its one place", () => {
  expect(CSS).not.toContain(".skeleton--message");
});
```

- [ ] **Step 5: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `npm test --prefix queen-agent/frontend` kırmızı — ChatScreen'in açılış testlerinden beşi
(çerçeve, spinner, kapalı kutu, `← back` yok, boş başlık), App'in yeni testi, CSS'in üç testi.
*A chat that does not exist*, *a sentence left in one chat's box* ve `chatOpened`'a geçen testler
yeşil. Öteki üç süit bugünkü hâlinde.

- [ ] **Step 6: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx queen-agent/frontend/src/App.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js docs/superpowers/specs/2026-09-29-queenagent-m355-sohbet-acilisi-testler-design.md docs/superpowers/plans/2026-09-29-queenagent-m355-sohbet-acilisi-testler-plan.md
git commit -m @'
test(queen-agent): Madde 355 red -- a chat opening stands in its own frame, the spinner where its messages will be

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
