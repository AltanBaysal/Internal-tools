# Madde 105 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m105-skill-sohbetin-testler-design.md](../specs/2026-08-28-queenagent-m105-skill-sohbetin-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `useRemembered.test.jsx` — import genişler, sona üç test

Import satırı `import { useRemembered, useRememberedMap } from "./remembered.js";` olur. Dosyanın
sonuna:

```jsx
// The map: one browser key, one entry per chat -- Madde 105's shape for the skill selection.
function MapHost({ chat }) {
  const [skills, remember] = useRememberedMap("chat-skills");
  return (
    <div>
      <span data-testid="value">{skills[chat] ?? "none"}</span>
      <button type="button" onClick={() => remember(chat, "picked")}>
        pick
      </button>
    </div>
  );
}

test("a map keeps each key to itself", () => {
  const first = render(<MapHost chat="c1" />);
  fireEvent.click(screen.getByText("pick"));
  first.unmount();

  render(<MapHost chat="c2" />);
  expect(screen.getByTestId("value").textContent).toBe("none");
});

test("what a key kept comes back on the next mount", () => {
  const first = render(<MapHost chat="c1" />);
  fireEvent.click(screen.getByText("pick"));
  first.unmount();

  render(<MapHost chat="c1" />);
  expect(screen.getByTestId("value").textContent).toBe("picked");
});

test("a memory that is not even JSON is an empty map, not a crash", () => {
  // Storage is shared with every past version of the app: what is read must never be trusted to
  // parse.
  window.localStorage.setItem("queenagent.chat-skills", "{broken");
  render(<MapHost chat="c1" />);
  expect(screen.getByTestId("value").textContent).toBe("none");
});
```

## B. `App.test.jsx`

### Ölçüsü değişen — `a new chat is born with the last skill picked in this session`

Adı ve son iddiası döner; kurulumu aynı kalır:

```jsx
test("a skill picked in a chat does not ride into a chat born on the project screen", async () => {
  // Madde 105 overturned Madde 86 here: the selection was the session's, so a skill picked in one
  // chat rode into every chat born after it. The selection is the chat's own now.
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Generate prompts+"));
  await waitFor(() => expect(screen.getByRole("button", { name: /Generate prompts/ })).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: "← Old" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1"));
  const box = screen.getByPlaceholderText("Start a new chat in this project...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(JSON.parse(sent[1].body).skill).toBe("");
  });
});
```

### Yeni — hemen ardına

```jsx
test("a skill picked in one chat stays that chat's own", async () => {
  // Madde 105. Two chats, one picker: what is picked while standing in the first shows only
  // there -- and is still standing when the user comes back.
  const records = {
    c1: { id: "c1", title: "First", messages: [] },
    c2: { id: "c2", title: "Second", messages: [] },
  };
  const rows = [
    { id: "c1", title: "First", lastActivity: new Date().toISOString() },
    { id: "c2", title: "Second", lastActivity: new Date().toISOString() },
  ];
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path) => {
      if (String(path).endsWith("/chats/c1")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => records.c1 });
      }
      if (String(path).endsWith("/chats/c2")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => records.c2 });
      }
      if (String(path).endsWith("/chats")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => rows });
      }
      if (String(path).endsWith("/files")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => [] });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
    }),
  );
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Generate prompts+", { selector: ".menu__item-name" }));
  await waitFor(() =>
    expect(screen.getByRole("button", { name: /Generate prompts/ })).toBeTruthy(),
  );

  fireEvent.click(screen.getByText("Second", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
  expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Generate prompts/ })).toBeNull();

  fireEvent.click(screen.getByText("First", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  expect(screen.getByRole("button", { name: /Generate prompts/ })).toBeTruthy();
});

test("a second draft does not wear the first one's skill", async () => {
  // Madde 105. The draft's selection is what the chat about to be born will own; once it is born,
  // the next draft starts with nothing.
  const born = { id: "c1", title: "Write it", skill: "generate-prompts-plus", messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(`event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n`),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => born });
    }
    if (String(path).endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());
  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Generate prompts+", { selector: ".menu__item-name" }));

  const box = screen.getByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "Write it" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));

  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy();
  expect(screen.queryByRole("button", { name: /Generate prompts/ })).toBeNull();
});
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `useRemembered.test.jsx` | 3 — `useRememberedMap` henüz yok |
| `App.test.jsx` | 3 — ölçüsü değişen `skill === ""` + iki yeni |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `remembered.js`, `App.jsx` açılmaz.
- **`a skill picked survives the app being mounted again` ve reload testi ellenmez** — ikisi de
  gerçek sohbette geçiyor, yeni sınırda da yeşil kalmaları beklenir.
- **`dist` derlenmez.**
