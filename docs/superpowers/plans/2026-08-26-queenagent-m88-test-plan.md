# Madde 88 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-26-queenagent-m88-cevabi-sunucu-baslatir-testler-design.md](../specs/2026-08-26-queenagent-m88-cevabi-sunucu-baslatir-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

**Bu madde bölünmüyor.** Yarısı uygulanırsa tarayıcı hem yeni akışı hem eski efekti koşturur ve her
cümle iki cevap üretir. Büyüklüğü bilinerek kabul ediliyor.

---

## A. Ölen testler

Varlık sebepleri kalkıyor — sildikleri şey artık yok:

| Nerede | Ne | Neden ölüyor |
|---|---|---|
| `App.test.jsx` | `a stopped answer is not asked for all over again` | Bastırılacak bir kendiliğinden istek yok |
| `App.test.jsx` | `a chat whose last word is a stopped answer is not asked again` | Aynı |

İkisinin yerini C.11 alıyor: **hiçbir sohbet açılışta tur başlatmıyor**, durmuş olsun ya da olmasın.

## B. Yeniden kurulan testler

Beşi de gerçek davranış sınıyor ve kalıyor. Değişen tek şey **turun nasıl başladığı**: bugün sohbeti
açmak başlatıyor, bundan sonra bir cümle göndermek başlatıyor.

Uygulanan kural her birinde aynı:

- Sahte sunucunun `/answer` dalı **`/messages`** olur.
- Sohbet `messages: []` ile başlar — cevap borçlu değil, çünkü artık borç diye bir şey yok.
- Test, ekran geldikten sonra **Reply kutusuna yazıp Enter'a basar**; akış oradan gelir.

| Nerede | Ne |
|---|---|
| `App.test.jsx` | `a call arrives in the stream and is still there once the record lands` |
| `App.test.jsx` | `a chat that is owed an answer streams one and keeps the server's record` → adı `sending a sentence streams the answer and keeps the server's record` olur |
| `App.test.jsx` | `a file born mid-answer reaches the rail without a reload` |
| `App.test.jsx` | `a fault inside the stream shows the card and Try again asks again` |
| `App.test.jsx` | `a broken engine is reported once and not asked again` → adı `a broken engine is reported and nothing asks again by itself` olur |
| `App.test.jsx` | `offline, no answer is asked for; back online, one is` → ikinci yarısı düşer, adı `offline, nothing is sent; coming back online sends nothing either` olur |

Biri baştan sona, kalıbı göstermek için:

```jsx
test("sending a sentence streams the answer and keeps the server's record", async () => {
  // Madde 88: one request. The sentence goes out and the answer comes back down the same
  // connection -- nothing opens a second one, and opening the chat starts nothing.
  const empty = { id: "c1", title: "hello", messages: [] };
  const answered = {
    ...empty,
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "Done." },
    ],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (path.endsWith("/messages") && options?.method === "POST") {
      return sse(
        `event: chat\ndata: {"chat":"c1"}\n\n`,
        `event: chunk\ndata: {"text":"Done."}\n\n`,
        `event: done\ndata: ${JSON.stringify(answered)}\n\n`,
      );
    }
    if (path.endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => empty });
    }
    if (path.endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(screen.getByText("Done.")).toBeTruthy());
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "POST")).toHaveLength(1);
});
```

`sse(...)` bu dosyada zaten var *(SSE gövdesi döndüren yardımcı; adı koşarken doğrulanır ve
farklıysa o ad kullanılır)*.

## C. Kırmızıya dönenler

### Arka uç — `test_chat.py`, bir

```python
def test_a_chat_is_owed_an_answer_when_the_last_word_is_the_users():
    # Madde 88 moved this question out of the browser. It used to live in useChat, where it ran on
    # a reload and on a reconnection -- moments nobody asked for an answer in.
    at = "2026-08-09T11:04:00.000+00:00"
    asked = Chat(id="c1", title="hi", created_at=at, messages=(Message(role="user", at=at, text="hi"),))
    answered = replace(asked, messages=asked.messages + (Message(role="ai", at=at, text="Done."),))
    assert is_owed_an_answer(asked)
    assert not is_owed_an_answer(answered)
    assert not is_owed_an_answer(Chat(id="c1", title="hi", created_at=at))
```

### Arka uç — `test_chats_api.py`, sekiz

```python
def _frames(body):
    # The event names in order, so a test can say what the stream said without matching bytes.
    return [line[len("event: ") :] for line in body.splitlines() if line.startswith("event: ")]


def test_a_sentence_is_answered_in_the_same_request(tmp_path):
    # Madde 88: one request. The message is written and the answer streams back down the
    # connection that brought it.
    client = _client(tmp_path)
    pid = _project(client)
    resp = client.post(f"/api/projects/{pid}/messages", json={"text": "hello"})
    assert resp.mimetype == "text/event-stream"
    body = resp.get_data(as_text=True)
    assert "Done." in body
    assert _frames(body)[-1] == "done"


def test_the_first_frame_names_the_chat_that_was_born(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    body = client.post(f"/api/projects/{pid}/messages", json={"text": "hello"}).get_data(
        as_text=True
    )
    assert _frames(body)[0] == "chat"
    named = json.loads(body.split("data: ", 1)[1].splitlines()[0])["chat"]
    assert named.startswith("c")


def test_the_first_frame_names_the_chat_on_a_follow_up_too(tmp_path):
    # Sent every time rather than only when it is news: no condition on the server, and the browser
    # changes the address only when what it hears differs from what it holds.
    client = _client(tmp_path)
    pid, cid = _started(client)
    body = client.post(
        f"/api/projects/{pid}/messages", json={"chat": cid, "text": "more"}
    ).get_data(as_text=True)
    assert _frames(body)[0] == "chat"
    assert json.loads(body.split("data: ", 1)[1].splitlines()[0])["chat"] == cid


def test_the_separate_answering_door_is_gone(tmp_path):
    # 405 rather than 404: the SPA fallback claims every path for GET.
    client = _client(tmp_path)
    pid, cid = _started(client)
    assert client.post(f"/api/projects/{pid}/chats/{cid}/answer").status_code == 405


def test_a_body_with_no_text_answers_without_writing_a_message(tmp_path):
    # Try again: the sentence is already on disk and must not be written twice.
    client = _client(tmp_path)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/messages", json={"chat": cid}).get_data()
    said = client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]
    assert [m["role"] for m in said] == ["user", "ai"]


def test_a_body_with_neither_a_chat_nor_text_is_400(tmp_path):
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/messages", json={}).status_code == 400


def test_asking_again_for_a_chat_that_was_already_answered_is_400(tmp_path):
    # Nothing is waiting, so there is nothing to answer -- and answering anyway would write a
    # second reply to a question that already has one.
    client = _client(tmp_path)
    pid, cid = _started(client)
    client.post(f"/api/projects/{pid}/messages", json={"chat": cid}).get_data()
    again = client.post(f"/api/projects/{pid}/messages", json={"chat": cid})
    assert again.status_code == 400
    assert len(client.get(f"/api/projects/{pid}/chats/{cid}").get_json()["messages"]) == 2


def test_a_blank_sentence_is_refused_before_the_stream_starts(tmp_path):
    # Blank is not the same as absent: someone leaned on the space bar, and no stream begins.
    client = _client(tmp_path)
    pid, cid = _started(client)
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "   "})
    assert refused.status_code == 400
    assert refused.mimetype != "text/event-stream"
```

`test_an_empty_message_is_refused` 87'de yazılmıştı ve ikinci yarısı bununla örtüşüyor; o yarı
silinir, ilk yarısı *(sohbetsiz boş metin)* kalır.

`test_the_one_door_creates_a_chat_when_none_is_named` ve
`test_the_one_door_appends_when_a_chat_is_named` **akışa göre yeniden yazılır**: gövde artık JSON
değil, ve 201/200 ayrımı düşüyor. İddiaları aynı — sohbet doğuyor, başlık cümleden geliyor, mesaj
ekleniyor — ama `done` karesinin taşıdığı kayıttan okunuyor.

### Ön yüz — `App.test.jsx`, beş

```jsx
test("nothing asks for an answer by itself when a chat is opened", async () => {
  // Madde 88: the rule that used to do this lived here and ran on a reload. It lives on the
  // server now, where only a request can reach it.
  const owed = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  const fetch = vi.fn().mockImplementation((path) => {
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  await waitFor(() => expect(screen.getByText("hello")).toBeTruthy());
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "POST")).toHaveLength(0);
});

test("Try again asks through the one door with no sentence", async () => {
  // The button stays; what went is its finger pressing itself. No text means the question on disk
  // is the question, and it is not written a second time.
  const owed = {
    id: "c1",
    title: "hello",
    messages: [{ role: "user", at: new Date().toISOString(), text: "hello" }],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return sse(`event: error\ndata: {"error":"boom"}\n\n`);
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => owed });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  window.history.pushState(null, "", "/p/p1/c/c1");

  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });
  await waitFor(() => expect(screen.getByText("Try again")).toBeTruthy());

  fireEvent.click(screen.getByText("Try again"));
  await waitFor(() => {
    const posts = fetch.mock.calls.filter(([, options]) => options?.method === "POST");
    expect(posts).toHaveLength(2);
    expect(JSON.parse(posts[1][1].body)).toEqual({ chat: "c1" });
  });
});

test("the draft streams its first answer and moves to the new address", async () => {
  // The first frame carries the id, so the address changes while the answer is still arriving --
  // and what has already arrived stays on the screen rather than being reloaded away.
  const answered = {
    id: "c1",
    title: "hello",
    messages: [
      { role: "user", at: new Date().toISOString(), text: "hello" },
      { role: "ai", at: new Date().toISOString(), text: "Done." },
    ],
  };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return sse(
        `event: chat\ndata: {"chat":"c1"}\n\n`,
        `event: chunk\ndata: {"text":"Done."}\n\n`,
        `event: done\ndata: ${JSON.stringify(answered)}\n\n`,
      );
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

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  expect(screen.getByText("Done.")).toBeTruthy();
  // The address changed under a running stream and nothing went back to disk to re-read it.
  expect(fetch.mock.calls.filter(([path]) => String(path).endsWith("/chats/c1"))).toHaveLength(0);
});
```

Kalan ikisi B'deki yeniden kurulanların içinde: `offline...` testinin ikinci yarısı düşerek
*"bağlantı geri gelmek hiçbir şey göndermiyor"* olur, ve `a broken engine...` testi *"bir kere
bildirilir, kendiliğinden ikinci kez sorulmaz"* hâline gelir.

## Beklenen kırmızı

| Nerede | Kaç |
|---|---|
| `test_chat.py` | 1 — `is_owed_an_answer` |
| `test_chats_api.py` | 8 — akış, iki ilk kare, ölen uç, metinsiz cevap, iki 400, boş metin |
| `App.test.jsx` | 5 yeni + 6 yeniden kurulan |

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.**
- **`stream_answer.py` açılmaz.** Turun içi değişmiyor.
- **`/stop` testlerine dokunulmaz.** 90'ın işi.
- **`dist` derlenmez.**
