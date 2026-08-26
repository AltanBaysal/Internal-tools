# Madde 86 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-26-queenagent-m86-skill-oturumun-kipi-testler-design.md](../specs/2026-08-26-queenagent-m86-skill-oturumun-kipi-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. Silinen dosya

- `queen-agent/backend/tests/test_set_chat_skill.py`

Tamamı sökülen kuralı sınıyor. **Kuralın kendisi (`set_chat_skill.py`) bu turda silinmiyor** —
82'nin turunda öğrenildiği gibi, olmayan bir modülü import eden bir test dosyası pytest'in *toplama*
aşamasını düşürüyor ve o zaman turun bütün kırmızıları görünmez oluyor. Testi silmek güvenli, modülü
silmek uygulama turunun işi.

## B. Silinen testler

| Dosya | Giden |
|---|---|
| `test_chats_api.py` | `test_the_skill_can_be_changed_and_cleared` · `test_a_patch_carrying_only_a_model_is_refused` — ikisi de PATCH'e dayanıyor |
| `test_chats_api.py` | `test_a_chat_is_born_with_the_skill_it_was_sent` — yerini C.2 alıyor |
| `test_chat.py` | `test_a_chat_still_carries_its_skill` — yerini C.1 alıyor |
| `test_file_chat_store.py` | `test_the_skill_a_chat_selected_is_written_and_read_back` |
| `test_file_chat_store.py` | `test_a_chat_written_before_skills_existed_still_reads` — `chat.skill` satırı gider, testin geri kalanı mesaja bakar |
| `test_start_chat.py` | İki testin `chat.skill` satırları; `chat.messages[0].skill` satırları kalır |
| `App.test.jsx` | `picking a skill writes it to the chat it was picked in` — yerini C.6 alıyor |
| `ChatScreen.test.jsx` | `a chat with a skill selected says which one` — yerini C.5 alıyor |

## C. Kırmızıya dönenler

### 1. `test_chat.py` — bir kırmızı, bir bekçi

`test_a_chat_still_carries_its_skill` yerine:

```python
def test_a_chat_carries_no_skill():
    # Madde 86: the selection lives in the session, not in the record. The answer path never read
    # this field -- a field nothing reads is a question every future reader has to answer alone.
    assert "skill" not in [field.name for field in fields(Chat)]


def test_a_message_still_carries_the_skill_it_was_sent_with():
    # The half that stays, and the reason the one above is not an accident: what governed a turn is
    # written on the turn, so an older message cannot be made to look like a newer choice.
    assert "skill" in [field.name for field in fields(Message)]
```

İkincisi bugün de yeşil — kırmızı sayılmıyor, kalan yarıyı tutuyor. `Message` import satırına
eklenir.

### 2. `test_chats_api.py` — iki kırmızı

```python
def test_a_chat_carries_no_skill(tmp_path):
    # Madde 86: the field is gone from the record, so it is gone from the wire too.
    client = _client(tmp_path)
    pid = _project(client)
    born = client.post(
        f"/api/projects/{pid}/chats", json={"text": "hello", "skill": "create-scenario"}
    ).get_json()
    assert "skill" not in born
    # The message keeps it: the record still says what governed the turn.
    assert born["messages"][0]["skill"] == "create-scenario"


def test_a_chat_cannot_be_patched(tmp_path):
    # Madde 86 took the route out. The address still answers GET, so Flask's answer is not 404 --
    # it is that this address does not know this method.
    client = _client(tmp_path)
    pid, cid = _started(client)
    sent = client.patch(f"/api/projects/{pid}/chats/{cid}", json={"skill": "verify"})
    assert sent.status_code == 405
```

`_project(client)` ve `_started(client)` bu dosyada zaten var *(bakıldı: 407 ve 432. satırlar)*.

`test_a_message_carries_the_skill_it_was_sent_with` ve
`test_a_selected_skill_reaches_the_engine_as_an_instruction` **dokunulmadan kalır** — ikisi de
mesajın alanına bakıyor, ve o alan duruyor.

### 3. `test_file_chat_store.py` — bir kırmızı

```python
def test_a_chat_that_still_carries_a_skill_on_disk_is_read_without_it(tmp_path):
    # Madde 86 took the field out. Every chat written before it has a skill key sitting in its
    # JSON; nothing reads it, and nothing puts one back. The same shape Madde 82 left behind.
    raw = Store(str(tmp_path))
    raw.write_text(
        "p1/chats/old.json",
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00", "skill": "verify-prompts",'
        ' "messages": [{"role": "user", "at": "2026-08-09T11:04:00+00:00", "text": "hi",'
        ' "skill": "verify-prompts"}]}',
    )
    old = FileChatStore(raw).get("p1", "old")
    assert not hasattr(old, "skill")
    # A different field with the same name, and this one is still read.
    assert old.messages[0].skill == "verify-prompts"
```

JSON'un `id` taşımaması kasıtlı: dosyadaki `..._before_skills_existed_still_reads` aynı şekli
kullanıyor, yani id dosya adından geliyor *(bakıldı)*.

### 4. Sahte sunucu — `withStoredSkill`

Ön yüzün üç kırmızısı, **kaydında skill yazan** bir sohbet istiyor; paylaşılan `withChat` böyle bir
sohbet sunmuyor. Kendi katı sahtesi yazılır, `App.test.jsx`'e, `withChat`'in hemen altına:

```jsx
// Its own fake rather than withChat's: this one serves a chat whose record carries a skill, which
// is the only way the picker and the session can disagree.
function withStoredSkill(stored = "verify-prompts") {
  const chat = { id: "c1", title: "Write the intro", skill: stored, messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    // Today's app still PATCHes here. The fake answers it so the failure is the assertion below
    // rather than a screen that crashed on an unexpected shape.
    if (String(path).endsWith("/chats/c1") && options?.method === "PATCH") {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ ...chat, ...JSON.parse(options.body) }),
      });
    }
    if (String(path).endsWith("/chats/c1/messages") && options?.method === "POST") {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    if (String(path).endsWith("/chats/c1")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => chat });
    }
    if (String(path).endsWith("/chats")) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => [
          { id: "c1", title: "Write the intro", lastActivity: new Date().toISOString() },
        ],
      });
    }
    if (String(path).endsWith("/files")) {
      return Promise.resolve({ ok: true, status: 200, json: async () => [] });
    }
    return Promise.resolve({ ok: true, status: 200, json: async () => [PROJECT] });
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}
```

Sohbetin `messages` listesi boş: cevap borçlu olmadığı için hiçbir tur kendiliğinden başlamıyor ve
testler akışla uğraşmıyor.

### 5. `ChatScreen.test.jsx` — bir kırmızı

`a chat with a skill selected says which one` yerine:

```jsx
test("the picker shows the skill it is handed, not the chat's", () => {
  // Madde 86: the selection is the session's, and the session is App's. The screen is handed one,
  // the way ProjectScreen has always been handed one.
  render(
    <ChatScreen
      project={PROJECT}
      chat={{ ...CHAT, skill: "verify-prompts" }}
      skill="split-into-frames"
    />,
  );
  expect(screen.getByRole("button", { name: /Split into frames/ })).toBeTruthy();
});
```

Bugün ekran `chat.skill`'i okuduğu için *Verify prompts* çiziyor — kırmızı burada.

### 6. `App.test.jsx` — dört kırmızı

`picking a skill writes it to the chat it was picked in` yerine:

```jsx
test("picking a skill asks the server for nothing", async () => {
  // Madde 86: there is no field to write, so there is no request. The choice is the session's.
  const fetch = withStoredSkill("");
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());

  fireEvent.click(screen.getByRole("button", { name: /Skills/ }));
  fireEvent.click(screen.getByText("Verify prompts"));

  await waitFor(() => expect(screen.getByRole("button", { name: /Verify prompts/ })).toBeTruthy());
  expect(fetch.mock.calls.filter(([, options]) => options?.method === "PATCH")).toHaveLength(0);
});


test("a chat that stored a skill does not put it in the picker", async () => {
  // Opening an old chat says nothing about what this session picked -- and this session picked
  // nothing yet, so the picker is where it started.
  withStoredSkill();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await waitFor(() => expect(screen.getByRole("button", { name: /Skills/ })).toBeTruthy());
  expect(screen.queryByRole("button", { name: /Verify prompts/ })).toBeNull();
});


test("what the picker shows is what the message carries", async () => {
  // The bug Madde 86 closes: the picker read the record, the send read the session, and a chat
  // opened after a reload made the two say different things at the same moment.
  const fetch = withStoredSkill();
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
    expect(JSON.parse(sent[1].body).skill).toBe("");
  });
  expect(screen.queryByRole("button", { name: /Verify prompts/ })).toBeNull();
});


test("the skill picked in a draft survives landing in the chat it created", async () => {
  // The accepted cost, written down: the choice belongs to the session, so it crosses into the
  // chat that was just born even though that chat's record says otherwise.
  const born = { id: "c1", title: "Write it", skill: "verify-prompts", messages: [] };
  const fetch = vi.fn().mockImplementation((path, options) => {
    if (String(path).endsWith("/chats") && options?.method === "POST") {
      return Promise.resolve({ ok: true, status: 201, json: async () => born });
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
  fireEvent.click(screen.getByText("Split into frames", { selector: ".menu__item-name" }));

  const box = screen.getByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "Write it" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => expect(window.location.pathname).toBe("/p/p1/c/c1"));
  expect(screen.getByRole("button", { name: /Split into frames/ })).toBeTruthy();
});
```

Sonuncusu taslaktan sohbete **oturum içinde** geçiyor — yeniden `render` etmek oturumu sıfırlar ve
testin sınadığı şeyi yok ederdi. Bu geçiş yolu dosyada zaten var *(`the first message in a draft
creates the chat and takes its address`)*.

`a new chat is born with the last skill picked in this session` ve `picking a skill closes the
menu` **dokunulmadan kalır**: ikisi de bugün yeşil ve 86'dan sonra da yeşil.

## Beklenen kırmızı

| Nerede | Ne söylüyor |
|---|---|
| `test_chat.py` | `Chat`'te `skill` alanı yok |
| `test_chats_api.py` | Sohbetin JSON'u `skill` taşımıyor · sohbete PATCH 405 |
| `test_file_chat_store.py` | Diskte `skill` taşıyan eski kayıt okunuyor, alan doğmuyor |
| `ChatScreen.test.jsx` | Seçici verilen skill'i çiziyor, sohbetinkini değil |
| `App.test.jsx` | Skill seçmek istek atmıyor · kayıttaki skill seçiciye girmiyor · seçicide yazan ile gidende yazan aynı · seçim taslaktan sohbete geçiyor |

**Dokuz kırmızı** — dördü arka uçta, beşi ön yüzde.

Toplam sayı koşulunca yazılır: bir sökme turunda silinen testin sayısını önden kestirmek,
kestirmenin kendisini doğrulanacak bir şey yapar.

## Toplu değiştirme yok

`skill` kelimesi düzinelerce yerde geçiyor ve çoğu bu maddeyle ilgisiz — `skills.py`, `SkillPicker`,
`instruction_for`, ve her mesajın kendi alanı. **`replace_all` kullanılmıyor.**

## Bilerek yapılmayanlar

- **Kod yazılmaz.** Hiçbir kaynak dosya açılmıyor — `chat.py`, `routes.py`, `file_chat_store.py`,
  `App.jsx`, `useChat.js`, `ChatScreen.jsx` dahil.
- **`set_chat_skill.py` silinmez.** Testi silinir, modülü uygulama turunda gider.
- **`dist` derlenmez.**
- **`SkillPicker.test.jsx`, `Menu.test.jsx`, `skills.test.js` açılmaz.** Seçici duruyor.
- **`test_stream_answer.py` açılmaz.** Yönergeyi mesajdan alıyordu, almaya devam ediyor.
- **Proje PATCH'inin testlerine dokunulmaz.** Ad değiştirme başka bir uç.
