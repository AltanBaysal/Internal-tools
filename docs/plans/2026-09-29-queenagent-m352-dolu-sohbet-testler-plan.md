# Madde 352 — Dolan sohbette *burada devam et* · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sunucunun `full`'unu, yazma kutusunun yerindeki bildirimi ve `Continue here`'in kırpmasını
tutan testler, kırmızı.

**Architecture:** Arka uçta kaydın `full`'u için üç test. Ön uçta `ChatScreen`'e bildirimin kendisi,
`workspace.css`'e şekli, `App`'e hook'la birlikte uçtan uca yol.

**Tech Stack:** pytest, Flask test client; vitest, Testing Library, jsdom.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m352-dolu-sohbet-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce; arayüz metni İngilizce.
- Bu turda yalnız test dosyaları ve bu iki belge değişir; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Kayıt dolu olduğunu söyler

**Files:**
- Modify: `queen-agent/backend/tests/test_chats_api.py` — dosyanın sonuna, 345'in bölümünün arkasına

**Interfaces:**
- Consumes: dosyanın `_client`, `_started`, `_record`, `_answering`, `LONG`, `_filled`'ı.
- Produces: uygulama turunun karşılayacağı şey — `/chats/<id>` her zaman `"full": bool` taşır.

- [ ] **Step 1: Üç test**

```python
# --- whether the chat is full, said by the server (Madde 352) ------------------------------------


def test_a_chat_below_the_ceiling_says_it_is_not_full(tmp_path):
    # The notice stands on this field alone: the screen counts nothing (FOUNDATION, Decision 4).
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert _record(client, pid, cid)["full"] is False


def test_a_full_chat_says_so_before_anything_is_refused(tmp_path):
    client = _answering(tmp_path, LONG)
    pid, cid = _started(client)
    assert _record(client, pid, cid)["full"] is True


def test_a_trimmed_chat_is_not_full_any_more(tmp_path):
    client, pid, cid = _filled(tmp_path)
    assert _record(client, pid, cid)["full"] is True
    client.post(f"/api/projects/{pid}/chats/{cid}/trim")
    assert _record(client, pid, cid)["full"] is False
```

### Task 2: Bildirim ekranda

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` — `within` içeri alınır;
  dosyanın sonuna beş test
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js` — dosyanın sonuna bir test

**Interfaces:**
- Consumes: `CHAT`, `PROJECT`; `workspace.css.test.js`'in `rule`'u.
- Produces: `ChatScreen`'in yeni özellikleri `onNewChat()` ve `onContinue()`; `chat.full`'u okur.
  Sınıflar: `.full`, `.full__text`, `.full__line`, `.full__detail`, `.full__actions`,
  `ghost full__new`, `ghost full__continue`.

- [ ] **Step 1: ChatScreen'in testleri**

```jsx
// --- the full chat's notice (Madde 352) ----------------------------------------------------------

const FULL = { ...CHAT, full: true, context: { sent: 50000, ceiling: 50000 } };

test("a full chat stands a notice where the box was", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={FULL} />);
  const notice = container.querySelector(".chat__composer .full");
  expect(notice.querySelector(".full__line").textContent).toBe("This chat is full.");
  expect(notice.querySelector(".full__detail").textContent).toBe(
    "Continue here sends only the latest messages to the model; the older ones stay on screen.",
  );
  // Nothing sends from a full chat: there is no box to type in and no button to press.
  expect(screen.queryByRole("textbox")).toBeNull();
  expect(screen.queryByRole("button", { name: "Send" })).toBeNull();
});

test("the notice's gauge stands at the left of its two buttons", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={FULL} />);
  const actions = container.querySelector(".full__actions");
  expect(actions.children).toHaveLength(3);
  const [gauge, fresh, carryOn] = actions.children;
  expect(gauge.className).toBe("composer__gauge");
  expect(within(gauge).getByRole("img").getAttribute("aria-label")).toBe("This chat is full");
  expect(fresh.textContent).toBe("New chat");
  expect(carryOn.textContent).toBe("Continue here");
  // Neither is the primary action: nothing is destroyed, somebody is being asked.
  expect(fresh.classList.contains("ghost")).toBe(true);
  expect(carryOn.classList.contains("ghost")).toBe(true);
});

test("the notice's buttons ask for a new chat and for this one to carry on", () => {
  const onNewChat = vi.fn();
  const onContinue = vi.fn();
  render(
    <ChatScreen project={PROJECT} chat={FULL} onNewChat={onNewChat} onContinue={onContinue} />,
  );
  fireEvent.click(screen.getByRole("button", { name: "New chat" }));
  expect(onNewChat).toHaveBeenCalled();
  expect(onContinue).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "Continue here" }));
  expect(onContinue).toHaveBeenCalled();
});

test("a chat that is not full keeps its box and draws no notice", () => {
  const { container } = render(<ChatScreen project={PROJECT} chat={{ ...CHAT, full: false }} />);
  expect(container.querySelector(".full")).toBeNull();
  expect(screen.getByRole("textbox")).toBeTruthy();
});

test("a sentence typed as the chat fills is still in the box once it carries on", () => {
  // FOUNDATION's first principle: a reply typed while the last answer ran does not go with the box.
  const { rerender } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  fireEvent.change(screen.getByRole("textbox"), { target: { value: "and then?" } });
  rerender(<ChatScreen project={PROJECT} chat={FULL} />);
  expect(screen.queryByRole("textbox")).toBeNull();
  rerender(<ChatScreen project={PROJECT} chat={{ ...CHAT, full: false }} />);
  expect(screen.getByRole("textbox").value).toBe("and then?");
});
```

- [ ] **Step 2: Şeklin kilidi**

```js
// Madde 352: the full chat's notice stands in the box's place in the box's own shape (design item
// 140, kit.css's .full).
test("the full chat's notice is shaped like the box it stands in for", () => {
  const notice = rule(".full");
  expect(notice).toContain("max-width: 720px");
  expect(notice).toContain("border-radius: 14px");
  expect(notice).toContain("padding: 14px 16px 10px");
  expect(rule(".full__line")).toContain("font-size: 14px");
  expect(rule(".full__detail")).toContain("font-size: 13px");
  expect(rule(".full__detail")).toContain("color: #6b6259");
  expect(rule(".full__actions")).toContain("justify-content: flex-end");
});
```

### Task 3: Uçtan uca

**Files:**
- Modify: `queen-agent/frontend/src/App.test.jsx` — `within` içeri alınır; dosyanın sonuna bir yardımcı
  ve dört test

**Interfaces:**
- Consumes: dosyanın `sseResponse`'u.
- Produces: uygulama turunun karşılayacağı şey — App bildirimin `New chat`'ini taslağa, `Continue
  here`'ini `useChat`'in kırpmasına bağlar; kırpma `POST …/chats/<c>/trim`, sonra sohbeti okur, ve
  reddi temizler; kapının reddi sunucunun sözüyle görünür.

- [ ] **Step 1: Yardımcı ve dört test**

```js
// --- the full chat's notice (Madde 352) ----------------------------------------------------------

const turn = (answer) => [
  { role: "user", at: new Date().toISOString(), text: "go on" },
  { role: "ai", at: new Date().toISOString(), text: answer },
];

// A chat the server calls full until the trim door is knocked on; `trim` is what the door answers.
function stubFullChat(trim = { ok: true, status: 200, json: async () => ({}) }) {
  let record = {
    id: "c1",
    title: "Long",
    full: true,
    trimmed: 0,
    context: { sent: 50000, ceiling: 50000 },
    messages: [...turn("First answer."), ...turn("Last answer.")],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/trim") && options?.method === "POST") {
      if (trim.ok) {
        record = { ...record, full: false, trimmed: 2, context: { sent: 9000, ceiling: 50000 } };
      }
      return Promise.resolve(trim);
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => record });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");
  return fetch;
}

test("the notice's New chat opens the project's draft", async () => {
  stubFullChat();
  render(<App />);
  await screen.findByText("This chat is full.");
  fireEvent.click(within(document.querySelector(".full")).getByRole("button", { name: "New chat" }));
  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/new"));
});

test("Continue here trims the chat, and it takes messages again with every message still drawn", async () => {
  const fetch = stubFullChat();
  render(<App />);
  await screen.findByText("This chat is full.");
  expect(screen.queryByRole("textbox")).toBeNull();

  // Asked nothing first and undone by nothing after (the owner's call, 29 September).
  fireEvent.click(screen.getByRole("button", { name: "Continue here" }));
  await waitFor(() => expect(screen.queryByText("This chat is full.")).toBeNull());
  const posts = fetch.mock.calls.filter(([, options]) => options?.method === "POST");
  expect(posts.map(([path]) => path)).toEqual(["/api/projects/p1/chats/c1/trim"]);
  expect(screen.getByRole("textbox")).toBeTruthy();
  expect(screen.getByText("First answer.")).toBeTruthy();
  expect(screen.getByText("Last answer.")).toBeTruthy();
});

test("a refusal met while the chat was full goes with Continue here", async () => {
  // The question filled the chat and its answer never came; Try again then met the ceiling. What
  // the refusal said stops being true the moment the chat is trimmed.
  let record = { id: "c1", title: "Long", full: false, trimmed: 0, messages: turn("Last answer.") };
  let posts = 0;
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      posts += 1;
      if (posts === 1) {
        const asked = { role: "user", at: new Date().toISOString(), text: "and more" };
        record = { ...record, full: true, messages: [...record.messages, asked] };
        return Promise.resolve(
          sseResponse('event: chat\ndata: {"chat":"c1"}\n\nevent: error\ndata: {"error":"502 upstream"}\n\n'),
        );
      }
      return Promise.resolve({
        ok: false,
        status: 400,
        text: async () => JSON.stringify({ error: "this chat has reached its context ceiling" }),
      });
    }
    if (path.endsWith("/trim") && options?.method === "POST") {
      record = { ...record, full: false, trimmed: 2 };
      return Promise.resolve({ ok: true, status: 200, json: async () => ({}) });
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => record });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "and more" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await screen.findByText("502 upstream");
  await screen.findByText("This chat is full.");

  fireEvent.click(screen.getByRole("button", { name: "Try again" }));
  await screen.findByText("this chat has reached its context ceiling");

  fireEvent.click(screen.getByRole("button", { name: "Continue here" }));
  await waitFor(() => expect(screen.queryByText("This chat is full.")).toBeNull());
  expect(screen.queryByText("Couldn't get a response.")).toBeNull();
});

test("a trim the server refuses says so in the server's own words", async () => {
  stubFullChat({
    ok: false,
    status: 400,
    text: async () => JSON.stringify({ error: "this chat is not full" }),
  });
  render(<App />);
  await screen.findByText("This chat is full.");
  fireEvent.click(screen.getByRole("button", { name: "Continue here" }));
  expect(await screen.findByText("this chat is not full")).toBeTruthy();
});
```

### Task 4: Kırmızıyı gör ve commit'le

- [ ] **Step 1: Dört satırı paralel koş**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: arka uçta `full`'u okuyan üç test kırmızı (`KeyError`). Ön uçta kırmızılar ChatScreen'in
dört testi (*"a chat that is not full…"* bugün de geçer, kilit), CSS kilidi ve App'in dört testi.
queen-editor'ün iki süiti yeşil.

- [ ] **Step 2: Kırmızıyı commit'le**

```powershell
git add queen-agent/backend/tests/test_chats_api.py queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx queen-agent/frontend/src/features/workspace/workspace.css.test.js queen-agent/frontend/src/App.test.jsx docs/specs/2026-09-29-queenagent-m352-dolu-sohbet-testler-design.md docs/plans/2026-09-29-queenagent-m352-dolu-sohbet-testler-plan.md
git commit -m @'
test(queen-agent): Madde 352 red -- a full chat says so, and its notice offers New chat and Continue here

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
