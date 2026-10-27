# Madde 116 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-28-queenagent-m116-sohbet-adi-testler-design.md](../specs/2026-08-28-queenagent-m116-sohbet-adi-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız test; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. `queen-agent/frontend/src/features/workspace/chatTitle.test.js` — yeni dosya

```js
import { expect, test } from "vitest";

import { chatTitle } from "./chatTitle.js";

test("a short first message is the title, stripped", () => {
  expect(chatTitle("  Write the intro  ")).toBe("Write the intro");
});

test("a long first message is cut at the server's own limit", () => {
  // Pinned to chat_title in chat.py: 42, and the mark only on a message that lost something.
  expect(chatTitle("m".repeat(80))).toBe("m".repeat(42) + "…");
  expect(chatTitle("m".repeat(42))).toBe("m".repeat(42));
});
```

## B. `queen-agent/frontend/src/App.test.jsx` — doğum testlerinin yanına

```jsx
test("a newborn chat is named by the trimmed first message, not the whole of it", async () => {
  // Madde 116: the record stood up for the draft carried the whole message as its title. The
  // server's trimmed name only arrives when the turn ends -- minutes later in a flow run -- so
  // the window this test stands in is the turn still running after the first frame moved the
  // address.
  const first = "m".repeat(80);
  const { response } = gatedSse('event: chat\ndata: {"chat":"c1"}\n\n', "event: done\ndata: {}\n\n");
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path === "/api/projects/p1/messages" && options?.method === "POST") {
      return Promise.resolve(response);
    }
    if (path === "/api/projects/p1/chats") {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/new");

  render(<App />);
  await waitFor(() => expect(screen.getByPlaceholderText("Reply...")).toBeTruthy());
  fireEvent.change(screen.getByPlaceholderText("Reply..."), { target: { value: first } });
  fireEvent.keyDown(screen.getByPlaceholderText("Reply..."), { key: "Enter" });

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  expect(document.querySelector(".chat__title").textContent).toBe("m".repeat(42) + "…");
});
```

Taslak adresinde beklemek işe yaramaz: orada başlık zaten sabit `New chat`. Yanlış ad, ilk frame
adresi taşıdıktan sonra görünür — doğum koruması diskten okumayı atlar ve ayağa dikilen kayıt
başlık olur. Bu yüzden akış `gatedSse` ile açık tutulur ve adres taşındıktan sonra bakılır.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `chatTitle.test.js` | dosya — `./chatTitle.js` henüz yok |
| `App.test.jsx` | 1 — başlık bugün mesajın tamamı |

## Bilerek yapılmayanlar

- **`chatTitle.js` yazılmaz, `useChat.js` açılmaz** — tur 2'nin işi.
- **`dist` derlenmez.**
