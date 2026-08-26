# Madde 89 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m89-sohbetin-sekli-tek-yerde-testler-design.md](../specs/2026-08-27-queenagent-m89-sohbetin-sekli-tek-yerde-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. Ölçüsü değişen test

`the draft streams its first answer and moves to the new address` *(App.test.jsx, 88'de yazıldı)*.
Son satırı:

```jsx
  expect(fetch.mock.calls.filter(([path]) => String(path).endsWith("/chats/c1"))).toHaveLength(0);
```

olur:

```jsx
  // Read once, at the end of the turn -- Madde 89. Twice would mean the loading effect stepped in
  // while the answer was still arriving, which is what 88's guard exists to prevent.
  await waitFor(() =>
    expect(fetch.mock.calls.filter(([path]) => String(path).endsWith("/chats/c1"))).toHaveLength(1),
  );
```

Sahtesine `/chats/c1` dalı eklenir — bugün yok, çünkü hiç okunmuyordu.

## B. Kırmızıya dönenler

### 1. `test_chats_api.py` — iki

```python
def test_the_closing_frame_carries_nothing(tmp_path):
    # Madde 89: the record has one home, and it is the read endpoint. The stream says a turn is
    # over; what the turn wrote is a question asked separately.
    client = _client(tmp_path)
    _pid, _cid, body = _first_turn(client)
    closing = [block for block in body.split("\n\n") if block.startswith("event: done")]
    assert closing == ["event: done\ndata: {}"]


def test_no_frame_in_the_stream_carries_the_record(tmp_path):
    # Not only the last one: a shape that leaks anywhere is a second place it can drift from.
    client = _client(tmp_path)
    _pid, _cid, body = _first_turn(client)
    assert "messages" not in body
```

### 2. `App.test.jsx` — dört

```jsx
test("when the turn ends the record is read, and what it says is what is drawn", async () => {
  // Madde 89: what streamed is a guess and what was written is the record, so the screen ends up
  // showing the one the server can still hand back. The two are made to differ here on purpose.
  const empty = { id: "c1", title: "hello", messages: [] };
  const written = {
    id: "c1",
    title: "hello",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "What the record says." },
    ],
  };
  let read = 0;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(
          `event: chat\ndata: {"chat":"c1"}\n\n` +
            `event: chunk\ndata: {"text":"What the stream said."}\n\n` +
            `event: done\ndata: {}\n\n`,
        ),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      read += 1;
      return Promise.resolve({ ok: true, status: 200, json: async () => (read > 1 ? written : empty) });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText("What the record says.")).toBeTruthy());
  expect(screen.queryByText("What the stream said.")).toBeNull();
});

test("a chat that was just born is read by the id the first frame gave", async () => {
  const written = {
    id: "c1",
    title: "hello",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "Done." },
    ],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(`event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n`),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => written });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    if (String(path).endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText("Done.")).toBeTruthy());
});

test("a turn that ended in a fault is read back too", async () => {
  // The answer never came, but the question did reach disk -- and it has to stay on the screen.
  const written = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(
          `event: chat\ndata: {"chat":"c1"}\n\nevent: error\ndata: {"error":"401 bad key"}\n\n`,
        ),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => written });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText("401 bad key")).toBeTruthy());
  expect(screen.getByText("hello", { selector: ".msg__bubble" })).toBeTruthy();
  // Twice: once on opening, once when the turn closed.
  expect(fetch.mock.calls.filter(([path]) => String(path).endsWith("/chats/c1"))).toHaveLength(2);
});

test("a record that cannot be read back says so in the read's own words", async () => {
  const empty = { id: "c1", title: "hello", messages: [] };
  let read = 0;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(
        sseResponse(`event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n`),
      );
    }
    if (String(path).endsWith("/chats/c1")) {
      read += 1;
      if (read > 1) {
        return Promise.resolve({
          ok: false,
          status: 500,
          text: async () => JSON.stringify({ error: "the disk went away" }),
        });
      }
      return Promise.resolve({ ok: true, status: 200, json: async () => empty });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  // The read's own sentence, not a guess about what went wrong.
  await waitFor(() => expect(screen.getByText("the disk went away")).toBeTruthy());
});
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_chats_api.py` | 2 — boş kapanış karesi, akışta kayıt yok |
| `App.test.jsx` | 4 yeni + 1 ölçüsü değişen |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.**
- **`_chat_json` ve `_chat_summary` açılmaz.** Kendileri değişmiyor.
- **`stream_answer.py` açılmaz.**
- **`/stop` testlerine dokunulmaz.** 90'ın işi.
- **`dist` derlenmez.**
