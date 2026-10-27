# Madde 104 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m104-taslak-isinlanmasi-testler-design.md](../specs/2026-08-28-queenagent-m104-taslak-isinlanmasi-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız test; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. Yeni test — `App.test.jsx`

`the skill picked in a draft survives landing in the chat it created` testinin hemen ardına:

```jsx
test("a draft's first answer never wears the old chat's transcript", async () => {
  // Madde 104. The screen stood in an old chat, moved to the draft, and sent. The address follows
  // the newborn chat (Madde 88); what must not follow is the old chat's record, which the hook was
  // still holding and the first bubble was appended to. The stream is held open so the assertion
  // lands mid-answer, where the wrong transcript used to show.
  const old = {
    id: "c1",
    title: "The old chat",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "old question" },
      { role: "ai", at: new Date().toISOString(), text: "The old answer." },
    ],
  };
  const born = {
    id: "c2",
    title: "hello",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "Fresh." },
    ],
  };
  const { response, release } = gatedSse(
    `event: chat\ndata: {"chat":"c2"}\n\nevent: chunk\ndata: {"text":"Fresh"}\n\n`,
    `event: done\ndata: {}\n\n`,
  );
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve(response);
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => old });
    }
    if (String(path).endsWith("/chats/c2")) {
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
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("The old answer.")).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: /New chat/ }));
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  // The address moves to the newborn while the answer still runs...
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
  // ...and the screen is the newborn's: the user's own sentence, never the chat that was left.
  expect(screen.queryByText("The old answer.")).toBeNull();
  expect(screen.getByText("hello", { selector: ".msg__bubble" })).toBeTruthy();

  await act(async () => {
    release();
  });
  await waitFor(() => expect(screen.getByText("Fresh.")).toBeTruthy());
});
```

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `App.test.jsx` | 1 yeni — `queryByText("The old answer.")` bugün ekranda |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `useChat.js` ve `App.jsx` bu turda açılmaz.
- **106'nın sohbet-geçişi senaryosu yazılmaz.**
- **`dist` derlenmez.**
