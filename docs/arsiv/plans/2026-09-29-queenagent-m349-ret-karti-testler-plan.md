# Madde 349 — Sunucunun reddi de hata kartı · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reddedilen mesajın kahverengi kartı çizdiğini ve Try again'in reddedileni yeniden
gönderdiğini tutan testler, kırmızı.

**Architecture:** `ChatScreen.test.jsx`'teki ret testi tersine döner. `App.test.jsx`'teki ret testi
kartı bekler; iki yeni test Try again'in ne gönderdiğini tutar.

**Tech Stack:** vitest, Testing Library, jsdom.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m349-ret-karti-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce.
- Bu turda `ChatScreen.jsx`, `useChat.js` ve `workspace.css` değişmez; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Ret kartı, kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` — *"a message that was never sent is not told as an answer that never came"*
- Modify: `queen-agent/frontend/src/App.test.jsx` — *"the user bubble shows before the server answers, and a refusal hands the words back"*, ve arkasına iki yeni test

**Interfaces:**
- Consumes: `ChatScreen`'in `refused` ve `onRetry` özellikleri; kartın `.failure__detail`'i;
  `App.test.jsx`'in `sseResponse`'u.
- Produces: uygulama turunun karşılayacağı şey — `refused` kartı çizer, `.refused` yok; Try again
  reddedilen isteği aynen gönderir, ve ret sonraki gönderişe taşınmaz.

- [ ] **Step 1: ChatScreen'in ret testini ters çevir**

```jsx
test("a refused message draws the failure card with the server's words", () => {
  // Design item 193: a message the server refused and an answer that never came are one card --
  // the same sentence, the server's own words under it, and Try again.
  const onRetry = vi.fn();
  const { container } = render(
    <ChatScreen project={PROJECT} chat={CHAT} refused="a message needs text" onRetry={onRetry} />,
  );
  expect(screen.getByText("Couldn't get a response.")).toBeTruthy();
  expect(container.querySelector(".failure__detail").textContent).toBe("a message needs text");
  expect(container.querySelector(".refused")).toBeNull();
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  expect(onRetry).toHaveBeenCalled();
});
```

- [ ] **Step 2: App'in ret testi kartı beklesin**

Son üç `expect`'in yerine (balonun gittiği ve cümlenin kutuya döndüğü satırlar kalır):

```js
  // The server's own sentence, not the method and the code the browser used to write instead --
  // under the same card a failed answer draws (design item 193).
  expect(screen.getByText("a message needs text")).toBeTruthy();
  expect(screen.getByText("Couldn't get a response.")).toBeTruthy();
  expect(document.querySelector(".refused")).toBeNull();
```

- [ ] **Step 3: İki yeni test, `sseResponse`'un arkasına**

```js
// Madde 349: the card says no answer came, and what it came for is the refused sentence -- a
// request with no text would ask the server to answer a question that was never written.
function stubRefusingChat(answers) {
  const chat = { id: "c1", title: "Hi", messages: [] };
  let posts = 0;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      posts += 1;
      return Promise.resolve(answers(posts));
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");
  return fetch;
}

const NOT_FOUND = {
  ok: false,
  status: 404,
  text: async () => JSON.stringify({ error: "chat not found" }),
};

const messagePosts = (fetch) =>
  fetch.mock.calls
    .filter(([path, options]) => path.endsWith("/messages") && options?.method === "POST")
    .map(([, options]) => JSON.parse(options.body));

test("Try again after a refusal sends the refused message again", async () => {
  const fetch = stubRefusingChat(() => NOT_FOUND);
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("chat not found");

  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await waitFor(() => expect(messagePosts(fetch)).toHaveLength(2));
  const [first, again] = messagePosts(fetch);
  expect(again.text).toBe("hello");
  expect(again).toEqual(first);
  // Refused again, the card stands again with what the server said this time.
  expect(await screen.findByText("chat not found")).toBeTruthy();
});

test("a refusal is not carried into a later send's Try again", async () => {
  const fetch = stubRefusingChat((post) =>
    post === 1 ? NOT_FOUND : sseResponse('event: error\ndata: {"error":"401 bad key"}\n\n'),
  );
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("chat not found");

  fireEvent.change(box, { target: { value: "again" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("401 bad key");

  // The question is on disk now, and it is what Try again asks about -- not the sentence refused
  // two sends ago.
  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await waitFor(() => expect(messagePosts(fetch)).toHaveLength(3));
  expect(messagePosts(fetch)[2]).toEqual({ chat: "c1" });
});
```

- [ ] **Step 4: Dört satırı paralel koş, kırmızıyı gör**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent'ın ön ucu 695 − 1 + 1 + 2 = 697 test; kırmızılar ChatScreen'in yeni testi, App'in
güncellenen ret testi ve *"Try again after a refusal…"* — bugün ret kırmızı satır, kart ve Try again
yok. *"a refusal is not carried…"* bugün geçebilir (ret satırının Try again'i yok); uygulamanın
getireceği hatırlamayı kilitler. Öteki süitler yeşil.

- [ ] **Step 5: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx queen-agent/frontend/src/App.test.jsx docs/specs/2026-09-29-queenagent-m349-ret-karti-testler-design.md docs/plans/2026-09-29-queenagent-m349-ret-karti-testler-plan.md
git commit -m @'
test(queen-agent): Madde 349 red -- a refused message draws the failure card, and Try again sends it again

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```

---

### Task 2: İkinci geçiş — kutu tek sahip, kart sohbetinde kalır; kırmızı

**Files:**
- Modify: `queen-agent/frontend/src/App.test.jsx` — `stubRefusingChat` ve arkasına üç test
- Modify: `queen-agent/frontend/src/features/workspace/useChat.js` — yükleme etkisindeki iki
  `setRefused(null)` ve yorumu çıkar (uygulama turunda geri gelir; testsiz yazılmışlardı)

**Interfaces:**
- Consumes: Task 1'in `stubRefusingChat`, `NOT_FOUND`, `messagePosts`, `sseResponse`.
- Produces: uygulama turunun karşılayacağı şey — kabul edilen Try again'den sonra kutu boş; ret
  kartı başka sohbette ve taslakta yok.

- [ ] **Step 1: `stubRefusingChat` iki sohbet taşısın**

```js
function stubRefusingChat(answers) {
  const records = {
    c1: { id: "c1", title: "Hi", messages: [] },
    c2: { id: "c2", title: "Other", messages: [] },
  };
  const rows = Object.values(records).map(({ id, title }) => ({
    id,
    title,
    lastActivity: new Date().toISOString(),
  }));
  let posts = 0;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      posts += 1;
      return Promise.resolve(answers(posts));
    }
    const record = records[path.match(/\/chats\/(\w+)$/)?.[1]];
    if (record) return Promise.resolve({ ok: true, status: 200, json: async () => record });
    if (path.endsWith("/chats")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => rows });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");
  return fetch;
}
```

- [ ] **Step 2: Üç test, *"a refusal is not carried…"*'nın arkasına**

```js
// The box is the refused sentence's one owner, so Try again is the box sending it -- left behind
// there as well, it would be sent a second time.
test("a sentence sent again by Try again does not stay in the box", async () => {
  const fetch = stubRefusingChat((post) =>
    post === 1 ? NOT_FOUND : sseResponse('event: chat\ndata: {"chat":"c1"}\n\nevent: done\ndata: {}\n\n'),
  );
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("chat not found");
  expect(box.value).toBe("hello");

  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await waitFor(() => expect(messagePosts(fetch)).toHaveLength(2));
  expect(messagePosts(fetch)[1].text).toBe("hello");
  await waitFor(() => expect(screen.queryByText("Couldn't get a response.")).toBeNull());
  expect(box.value).toBe("");
});

async function refuseInFirstChat() {
  stubRefusingChat(() => NOT_FOUND);
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("chat not found");
}

// Design APP-BUGS 3: the card's Try again sends the box, so pressed in another chat it would write
// the refused sentence there.
test("a refusal's card stays in the chat it was said in", async () => {
  await refuseInFirstChat();
  fireEvent.click(await screen.findByText("Other", { selector: ".sidebar__chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c2"));
  expect(screen.queryByText("Couldn't get a response.")).toBeNull();
});

test("a refusal's card does not follow the user into the draft", async () => {
  await refuseInFirstChat();
  fireEvent.click(document.querySelector(".sidebar__new-chat"));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
  expect(screen.queryByText("Couldn't get a response.")).toBeNull();
});
```

- [ ] **Step 3: `useChat`'in yükleme etkisinden testsiz iki satırı çıkar**

`// A refusal belongs to the chat it was said in…` yorumu ve iki `setRefused(null);`.

- [ ] **Step 4: Dört satırı paralel koş, kırmızıyı gör**

Beklenen: queen-agent'ın ön ucu 700 test, üç kırmızı — üç yeni test. Öteki süitler yeşil.

- [ ] **Step 5: Kırmızıyı commit'le**

```powershell
git add queen-agent/frontend/src/App.test.jsx queen-agent/frontend/src/features/workspace/useChat.js docs/specs/2026-09-29-queenagent-m349-ret-karti-testler-design.md docs/plans/2026-09-29-queenagent-m349-ret-karti-testler-plan.md
git commit -m @'
test(queen-agent): Madde 349 red -- a sentence Try again sends does not stay in the box, and a refusal stays in its chat

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
