# Madde 87 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-26-queenagent-m87-mesaj-tek-kapidan-testler-design.md](../specs/2026-08-26-queenagent-m87-mesaj-tek-kapidan-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. Silinen dosya

- `queen-agent/backend/tests/test_start_chat.py`

Kural ölüyor. İddiaları kaybolmuyor — başlığın cümleden gelmesi, boş metnin reddi ve skill'in mesaja
yazılması C.2'de `append_message`'ın testlerine geçiyor.

**`start_chat.py` bu turda silinmiyor.** `test_append_message.py` onu modül düzeyinde import ediyor;
modül gidince pytest'in toplama aşaması düşer ve turun bütün kırmızıları görünmez olur. Modül
uygulama turunda gider.

## B. Fixture'lara dokunulmuyor

`_started` *(test_chats_api.py:80)* ve `_chat`/`_seeded` *(test_append_message.py:18-27)* eski kapıyı
ve `start_chat`'i çağırıyor. **Bu turda ikisi de olduğu gibi kalıyor** — yeni kapı henüz yok, taşımak
seksen küsur testi aynı anda düşürür ve on iki gerçek kırmızıyı gizler. Uygulama turunda, kodla
birlikte taşınırlar.

Yeni kapının testleri kendi çağrılarını yazıyor.

## C. Kırmızıya dönenler

### 1. `test_chats_api.py` — sekiz

`test_a_chat_is_created_with_its_first_message`, `test_an_empty_message_is_refused` ve
`test_an_unknown_project_is_404` yeni kapıya yazılıyor; kalanı yeni:

```python
def test_the_one_door_creates_a_chat_when_none_is_named(tmp_path):
    # Madde 87: one address for every sentence a user says. No chat in the body means there is no
    # chat yet, so the server makes one -- a chat is still born with its first message.
    client = _client(tmp_path)
    pid = _project(client)
    resp = client.post(f"/api/projects/{pid}/messages", json={"text": "Write the intro"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "Write the intro"
    assert body["id"].startswith("c")
    assert [(m["role"], m["text"]) for m in body["messages"]] == [("user", "Write the intro")]


def test_the_one_door_appends_when_a_chat_is_named(tmp_path):
    # The same address, and the only difference is one field in the body.
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": "Write the intro"}).get_json()[
        "id"
    ]
    resp = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": "and more"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert [m["text"] for m in body["messages"]] == ["Write the intro", "and more"]
    # The title belongs to the message that started the chat and never moves.
    assert body["title"] == "Write the intro"


def test_the_old_creating_door_is_gone(tmp_path):
    # That address is a list of chats now and answers GET, so Flask's answer is not 404 -- it is
    # that this address does not know this method.
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/chats", json={"text": "hi"}).status_code == 405


def test_the_old_appending_door_is_gone(tmp_path):
    # Nothing is registered at that address any more, so this one really is a 404.
    client = _client(tmp_path)
    pid = _project(client)
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": "hi"}).get_json()["id"]
    sent = client.post(f"/api/projects/{pid}/chats/{cid}/messages", json={"text": "more"})
    assert sent.status_code == 404


def test_a_chat_that_is_not_there_is_404_and_nothing_is_created(tmp_path):
    # Empty means "there is no chat yet". A name that is simply wrong is not the same thing, and
    # creating one here would turn a typo into a second chat nobody asked for.
    client = _client(tmp_path)
    pid = _project(client)
    assert (
        client.post(f"/api/projects/{pid}/messages", json={"chat": "nope", "text": "hi"}).status_code
        == 404
    )
    assert client.get(f"/api/projects/{pid}/chats").get_json() == []


def test_an_empty_message_is_refused(tmp_path):
    # Both ways in: with nothing to append to, and with a chat waiting for it.
    client = _client(tmp_path)
    pid = _project(client)
    assert client.post(f"/api/projects/{pid}/messages", json={"text": "   "}).status_code == 400
    assert client.get(f"/api/projects/{pid}/chats").get_json() == []
    cid = client.post(f"/api/projects/{pid}/messages", json={"text": "hi"}).get_json()["id"]
    refused = client.post(f"/api/projects/{pid}/messages", json={"chat": cid, "text": " "})
    assert refused.status_code == 400


def test_an_unknown_project_is_404(tmp_path):
    assert (
        _client(tmp_path).post("/api/projects/nope/messages", json={"text": "hi"}).status_code == 404
    )


def test_the_start_chat_use_case_is_gone():
    # append_message took creating over: one rule for a message arriving, whether or not there is a
    # chat to put it in. The same shape as the rename use case that went before it.
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.start_chat  # noqa: F401
```

`test_a_message_carries_the_skill_it_was_sent_with` de yeni kapıya yazılıyor — gövdesi
`{"chat": cid, "text": "more", "skill": "verify"}` oluyor, iddiası aynı kalıyor.

### 2. `test_append_message.py` — iki

Dosyanın başına eklenir; `_seeded` ve `start_chat` importu **bu turda dokunulmadan kalır**:

```python
def test_with_no_chat_named_the_rule_creates_one(tmp_path):
    # Madde 87: start_chat's job moved here. A message with no chat to land in makes the chat, and
    # the id it is given is the id it gets -- minting one is the route's job, not this rule's.
    projects, chats = _stores(tmp_path)
    create_project(projects, new_id="p1", now="2026-08-09T11:04:00.000+00:00")
    chat = append_message(
        chats,
        "p1",
        "",
        "Write the intro",
        "2026-08-09T11:04:00.000+00:00",
        skill="create-scenario",
        project_store=projects,
        new_id="c9",
    )
    assert chat.id == "c9"
    assert chat.title == "Write the intro"
    assert [(m.role, m.text, m.skill) for m in chat.messages] == [
        ("user", "Write the intro", "create-scenario")
    ]
    # And it is on disk, not just in the returned object.
    assert [c.id for c in list_chats(chats, "p1")] == ["c9"]


def test_with_no_chat_named_an_empty_message_is_still_refused(tmp_path):
    projects, chats = _stores(tmp_path)
    create_project(projects, new_id="p1", now="2026-08-09T11:04:00.000+00:00")
    with pytest.raises(EmptyMessage):
        append_message(
            chats,
            "p1",
            "",
            "   ",
            "2026-08-09T11:04:00.000+00:00",
            project_store=projects,
            new_id="c9",
        )
    assert list_chats(chats, "p1") == []
```

`create_project`, `list_chats`, `EmptyMessage` ve `pytest` bu dosyada zaten import edilmiş
*(bakıldı: 1-10. satırlar)*.

### 3. `App.test.jsx` — iki

```jsx
test("the first sentence goes through the one door with no chat named", async () => {
  // Madde 87: the browser stopped choosing between two addresses. A draft has no chat yet, and
  // that is a field in the body rather than a different endpoint.
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/messages") && options?.method === "POST") {
      return Promise.resolve({
        ok: true,
        status: 201,
        json: async () => ({ id: "c1", title: "hello", messages: [] }),
      });
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
  window.history.pushState(null, "", "/p/p1");

  render(<App />);
  const box = await screen.findByPlaceholderText("Start a new chat in this project...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(String(sent[0])).toBe("/api/projects/p1/messages");
    expect(JSON.parse(sent[1].body).chat).toBeFalsy();
  });
});

test("a reply goes through the same door and names its chat", async () => {
  // The other half: same address, and the chat's id is what tells the two apart.
  const fetch = withStoredSkill("");
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "more" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const sent = fetch.mock.calls.find(
      ([path, options]) => String(path).endsWith("/messages") && options?.method === "POST",
    );
    expect(sent).toBeTruthy();
    expect(String(sent[0])).toBe("/api/projects/p1/messages");
    expect(JSON.parse(sent[1].body).chat).toBe("c1");
  });
});
```

`withStoredSkill` 86'da yazıldı ve `/chats/c1/messages`'a cevap veriyor. **Bu turda genişletilir:**
`/messages` ile biten her POST'a aynı sohbeti döndüren bir dal eklenir, yoksa ikinci test bugün
istek atamadan düşer ve kırmızı yanlış sebepten gelir.

## Beklenen kırmızı

| Nerede | Ne söylüyor |
|---|---|
| `test_chats_api.py` | Tek kapı yaratıyor · tek kapı ekliyor · eski yaratma ucu 405 · eski ekleme ucu 404 · tanınmayan sohbet 404 ve hiçbir şey doğmuyor · boş metin iki yoldan da 400 · tanınmayan proje 404 · `start_chat` modülü yok |
| `test_append_message.py` | Kural sohbeti yaratıyor · yaratırken de boş metni reddediyor |
| `App.test.jsx` | Taslak tek kapıya, sohbetsiz · cevap aynı kapıya, sohbetiyle |

**On iki kırmızı** — sekizi uçta, ikisi kuralda, ikisi ön yüzde.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi, defterdeki `BRANCH` yüzünden.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** Hiçbir kaynak dosya açılmıyor.
- **`start_chat.py` silinmez.** Testi silinir, modülü uygulama turunda gider.
- **`_started`, `_chat`, `_seeded` taşınmaz.** Fixture kodun şeklini takip eder; uygulama turunda.
- **`/answer` ve `/stop` testlerine dokunulmaz.** O adresler 88 ile 90'ın işi.
- **`useChatLists.js` ve `useChat.js` açılmaz.** Kod, uygulama turunda.
