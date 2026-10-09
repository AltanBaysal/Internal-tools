# Madde 106 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m106-akis-sohbetin-testler-design.md](../specs/2026-08-28-queenagent-m106-akis-sohbetin-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `App.test.jsx` — üç yeni, 104'ün testinin hemen ardına

İkinci testin bekleyişi iki iddialı: okuma sayacı **ve** akan satırın sönmüş olması — bugün akan
satır ancak `finally` temizleyince sönüyor, o da tur sonu okumasından sonra koşuyor; yani kırmızı
iddia boyanın kesin indiği anda atılıyor, iki dünyada da deterministik.

```jsx
test("an answer streaming in one chat does not show in another", async () => {
  // Madde 106. What the stream draws belongs to the chat it runs into: standing in another chat,
  // none of it shows -- and coming back, it shows again.
  const records = {
    c1: { id: "c1", title: "First", messages: [] },
    c2: { id: "c2", title: "Second", messages: [] },
  };
  const rows = [
    { id: "c1", title: "First", lastActivity: new Date().toISOString() },
    { id: "c2", title: "Second", lastActivity: new Date().toISOString() },
  ];
  const { response, release } = gatedSse(
    `event: chat\ndata: {"chat":"c1"}\n\nevent: chunk\ndata: {"text":"Halfway there"}\n\n`,
    `event: done\ndata: {}\n\n`,
  );
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path, options) => {
      if (String(path).endsWith("/messages") && options?.method === "POST") {
        return Promise.resolve(response);
      }
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
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "go" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByText("Halfway there")).toBeTruthy());

  fireEvent.click(screen.getByText("Second", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
  expect(screen.queryByText("Halfway there")).toBeNull();
  expect(screen.queryByTestId("thinking")).toBeNull();

  fireEvent.click(screen.getByText("First", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(screen.getByText("Halfway there")).toBeTruthy());

  await act(async () => {
    release();
  });
});

test("a turn that ends in a left chat does not repaint the one the user is standing in", async () => {
  // Madde 106. The turn still ends by reading the record (Madde 89) -- what changed is that the
  // read dresses only the screen standing in the chat it landed in. The wait below is two claims
  // on purpose: the read has happened AND the streamed line has gone dark, which is the finally
  // that runs after the repaint used to land.
  const finished = {
    id: "c1",
    title: "First",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "go" },
      { role: "ai", at: new Date().toISOString(), text: "The finished answer." },
    ],
  };
  const second = {
    id: "c2",
    title: "Second",
    messages: [{ role: "user", at: new Date().toISOString(), text: "Second's own words" }],
  };
  const rows = [
    { id: "c1", title: "First", lastActivity: new Date().toISOString() },
    { id: "c2", title: "Second", lastActivity: new Date().toISOString() },
  ];
  let c1Reads = 0;
  const { response, release } = gatedSse(
    `event: chat\ndata: {"chat":"c1"}\n\nevent: chunk\ndata: {"text":"running"}\n\n`,
    `event: done\ndata: {}\n\n`,
  );
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path, options) => {
      if (String(path).endsWith("/messages") && options?.method === "POST") {
        return Promise.resolve(response);
      }
      if (String(path).endsWith("/chats/c1")) {
        c1Reads += 1;
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => (c1Reads > 1 ? finished : { id: "c1", title: "First", messages: [] }),
        });
      }
      if (String(path).endsWith("/chats/c2")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => second });
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
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "go" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByText("running")).toBeTruthy());

  fireEvent.click(screen.getByText("Second", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(screen.getByText("Second's own words")).toBeTruthy());

  await act(async () => {
    release();
  });
  await waitFor(() => {
    expect(c1Reads).toBeGreaterThan(1);
    expect(screen.queryByText("running")).toBeNull();
  });
  expect(screen.queryByText("The finished answer.")).toBeNull();
  expect(screen.getByText("Second's own words")).toBeTruthy();

  fireEvent.click(screen.getByText("First", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(screen.getByText("The finished answer.")).toBeTruthy());
});

test("coming back to a streaming chat finds its transcript and its stream", async () => {
  // Madde 106's third face. The birth guard (Madde 88) kept the load away while a stream ran; a
  // return from another chat needs it -- what stands in the state is the other chat's record, and
  // the transcript on this screen has to be this chat's own, from disk, with the stream on top.
  const first = {
    id: "c1",
    title: "First",
    messages: [{ role: "user", at: new Date().toISOString(), text: "First words on disk" }],
  };
  const second = {
    id: "c2",
    title: "Second",
    messages: [{ role: "user", at: new Date().toISOString(), text: "Second's own words" }],
  };
  const rows = [
    { id: "c1", title: "First", lastActivity: new Date().toISOString() },
    { id: "c2", title: "Second", lastActivity: new Date().toISOString() },
  ];
  const { response, release } = gatedSse(
    `event: chat\ndata: {"chat":"c1"}\n\nevent: chunk\ndata: {"text":"Live tail"}\n\n`,
    `event: done\ndata: {}\n\n`,
  );
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation((path, options) => {
      if (String(path).endsWith("/messages") && options?.method === "POST") {
        return Promise.resolve(response);
      }
      if (String(path).endsWith("/chats/c1")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => first });
      }
      if (String(path).endsWith("/chats/c2")) {
        return Promise.resolve({ ok: true, status: 200, json: async () => second });
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
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "go" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByText("Live tail")).toBeTruthy());

  fireEvent.click(screen.getByText("Second", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(screen.getByText("Second's own words")).toBeTruthy());

  fireEvent.click(screen.getByText("First", { selector: ".sidebar__chat" }));
  await waitFor(() =>
    expect(screen.getByText("First words on disk", { selector: ".msg__bubble" })).toBeTruthy(),
  );
  expect(screen.queryByText("Second's own words")).toBeNull();
  expect(screen.getByText("Live tail")).toBeTruthy();

  await act(async () => {
    release();
  });
});
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `App.test.jsx` | 3 yeni — akan satır c2'de görünüyor · bitmiş cevap c2'yi boyuyor · dönüşte c1'de c2'nin dökümü |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `useChat.js` açılmaz.
- **`dist` derlenmez.**
