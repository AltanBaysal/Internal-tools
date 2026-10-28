# Madde 358 — Model seçici kalkar, ve model hiçbir yerde görünmez · test turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ayakta model seçicisinin ve adının olmadığını, tarayıcının model göndermediğini, sunucunun
turu bir modelle yönlendirmediğini ve eski kaydın modelini tarayıcıya vermediğini tutan testler,
kırmızı.

**Architecture:** Ön uçta `App.test.jsx`, `ChatScreen.test.jsx` ve `workspace.css.test.js` yeni hâli
okur; `ModelPicker.test.jsx` ile `models.test.js` silinir. Arka uçta sahte motorlar `model` almaz,
yolun ve motorun yeni testleri eklenir, Madde 146'nın yönlendirme testleri silinir. Kaynak kod değişmez.

**Tech Stack:** vitest + jsdom, Testing Library; pytest.

**Spec:** [test turunun spec'i](../specs/2026-09-29-queenagent-m358-model-secici-testler-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod, yorum ve test adı İngilizce.
- Bu turda kaynak kod, `FOUNDATION.md` ve defter değişmez; `dist` derlenmez.
- Hiçbir test susturulmaz; kaldırılan davranışın testi davranışla birlikte silinir.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Ön ucun testleri

**Files:**
- Delete: `queen-agent/frontend/src/features/workspace/ModelPicker.test.jsx`
- Delete: `queen-agent/frontend/src/features/workspace/models.test.js`
- Modify: `queen-agent/frontend/src/App.test.jsx` (`one model, and nothing asks about it` bölümü; `a draft says which model will answer it`; `Escape closes the picker`'ın yorumu)
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` (916–980, 493–498, 1235–1243)
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css.test.js`
- Modify (yalnız yorum): `Composer.test.jsx`, `Menu.test.jsx`, `SkillPicker.test.jsx`

**Interfaces:**
- Consumes: `App.test`'in `withChat`, `chatOpened`; `ChatScreen.test`'in `PROJECT`, `CHAT`; css testinin `CSS`'i.
- Produces: uygulama turunun karşılayacağı şeyler — ayak `ModePicker`, `SkillPicker`, Send; `ChatScreen`
  `model`, `modelOpen`, `onToggleModel`, `onModelChange` almaz; mesaj gövdesi `{ chat, text, skill,
  mode, from? }`; `.model-label` yok.

- [ ] **Step 1: App testleri.** 1861–1931 arası şu üç testle değişir:

```jsx
test("the app never asks which model to use", async () => {
  // One model, and it is the server's to name (Madde 358): there is nothing to ask about.
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();
  expect(fetch.mock.calls.filter(([path]) => String(path) === "/api/model")).toHaveLength(0);
});

test("no model is named on the chat screen", async () => {
  // Madde 358, the user's words: no model is to be seen. Not as a picker, and not as a label.
  withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  await chatOpened();
  expect(screen.queryByText(/Queen Flash/)).toBeNull();
  expect(screen.queryByText("MODELS")).toBeNull();
});

test("a chat is born naming no model", async () => {
  // Which model answers is the server's rule (FOUNDATION, Decision 4), so the message carries none.
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1/c/new");
  render(<App />);
  const box = await screen.findByPlaceholderText("Reply...");
  fireEvent.change(box, { target: { value: "hello" } });
  fireEvent.keyDown(box, { key: "Enter" });

  await waitFor(() => {
    const born = fetch.mock.calls.find(
      ([path, options]) => options?.method === "POST" && String(path).endsWith("/messages"),
    );
    expect(born).toBeTruthy();
    expect("model" in JSON.parse(born[1].body)).toBe(false);
  });
});
```

`a draft says which model will answer it` silinir. Bölüm başlığı `one model, and the server names it (Madde 358)` olur.

- [ ] **Step 2: ChatScreen testleri.** 916–953'teki dört model testi silinir; yerine:

```jsx
test("a model an older message was sent with is not drawn", () => {
  // Madde 146 to 357 wrote it onto the message. It stays on disk as a record and is shown nowhere.
  const old = { ...CHAT, messages: [{ ...CHAT.messages[0], model: "grok-4.3" }] };
  render(<ChatScreen project={PROJECT} chat={old} />);
  expect(screen.queryByText(/grok-4.3/)).toBeNull();
});
```

Ayak testleri: `"Edit⌄Skills⌄↑"`, `buttons.length` 3, `buttons[2]` `Send`; süren cevapta
`"Edit⌄Skills⌄⏹"`, 3, `buttons[2]` `Stop`; kapalı seçiciler `[true, true]`; seçici adları
`["Plan", "Skills"]`. Yorumlar Mode · Skills · Send der.

- [ ] **Step 3: CSS testi.**

```js
test("nothing in the stylesheet draws a model's name", () => {
  // Madde 358: no model is shown anywhere, and this rule has drawn nothing since Madde 82.
  expect(CSS).not.toContain(".model-label");
});
```

- [ ] **Step 4: Silinecek iki test dosyası silinir; üç yorum (`Composer.test`, `Menu.test`, `SkillPicker.test`) bugünü söyler.**

### Task 2: Arka ucun testleri

**Files:**
- Modify: `queen-agent/backend/tests/test_chats_api.py` (sahte motorlar; 580–613)
- Modify: `queen-agent/backend/tests/test_stream_answer.py` (`ScriptedEngine`; 708–746; 926–932; 1464–1474)
- Modify: `queen-agent/backend/tests/test_xai_engine.py` (130–137; 193–203)
- Modify (yalnız yorum): `test_chat.py`, `test_file_chat_store.py`, `test_config.py`, `test_notebook.py`

**Interfaces:**
- Consumes: `FileChatStore`, `Store`, `Chat`, `Message`, `XaiEngine`.
- Produces: `Engine.stream(messages, tools=None, on_open=None, conversation_id="")`; `_chat_json`'ın
  mesajlarında `model` yok; `Message.model` alanı yerinde.

- [ ] **Step 1: test_chats_api.** `FakeEngine`'den `self.model` ve `stream`'in `model=""`'ı, `ScriptedEngine.stream`'in `model=""`'ı çıkar. 580–613 şununla değişir:

```python
def test_a_model_sent_with_a_message_is_not_kept(tmp_path):
    # Madde 358. The server names the model every turn goes to, so a field a browser still sends is
    # read by nothing and written nowhere.
    client = _client(tmp_path)
    pid = _project(client)
    cid = _named(
        client.post(
            f"/api/projects/{pid}/messages", json={"text": "hello", "model": "grok-4.3"}
        ).get_data(as_text=True)
    )
    assert "model" not in _record(client, pid, cid)["messages"][0]


def test_a_message_on_the_wire_names_no_model_even_when_its_record_does(tmp_path):
    # Madde 146 to 357 wrote the model onto the message. The record keeps it; the screen shows no
    # model, so nothing sends it there.
    client = _client(tmp_path)
    pid = _project(client)
    FileChatStore(Store(str(tmp_path))).add(
        pid,
        Chat(
            id="c1",
            title="Old",
            created_at="2026-09-02T10:00:00+00:00",
            messages=(
                Message(
                    role="user", at="2026-09-02T10:00:00+00:00", text="hi", model="deepseek-v4-pro"
                ),
            ),
        ),
    )
    assert "model" not in _record(client, pid, "c1")["messages"][0]
```

(`Chat` ve `Message` `backend.features.workspace.domain.chat`'tan içe aktarılır.)

- [ ] **Step 2: test_stream_answer.** `ScriptedEngine`'den `self.models` ve `stream`'in `model=""`'ı çıkar; Madde 146 bölümü (`_answered_by` ve üç testi) silinir; `test_the_engine_is_asked_without_a_model`'in yorumu Madde 358'i söyler; `test_the_skill_and_the_model_come_from_the_open_lines_newest_question` `test_the_skill_comes_from_the_open_lines_newest_question` olur, `model=` ve `engine.models` satırı çıkar.

- [ ] **Step 3: test_xai_engine.** İki yönlendirme testi şunlarla değişir:

```python
def test_the_turn_names_no_model():
    # Madde 358. One model, and config.py names it: the engine is not told which one to speak with.
    assert "model" not in inspect.signature(XaiEngine.stream).parameters


def test_every_turn_is_spoken_by_the_default():
    grok, flash = FakeClient(), FakeClient()
    engine = _engine(grok, **{"deepseek-v4-flash": flash})
    list(engine.stream(CONVERSATION))
    assert grok.seen is not None
    assert flash.seen is None
```

- [ ] **Step 4: test_config ve test_last_activity.** Varsayılana düşme testi şununla değişir (`import pytest` eklenir); `test_last_activity.py`'nin `FakeEngine.stream`'i `model` almaz:

```python
def test_an_id_the_table_does_not_hold_is_a_wiring_fault():
    with pytest.raises(KeyError):
        config.engine_for("a-model-nobody-wired")
```

- [ ] **Step 5: Yorumlar.** `test_chat.py` ve `test_file_chat_store.py`: `Message.model` bir kayıt, bir seçim değil; `test_config.py`: `models.js` ve düğme yerine ekranın hiçbir model adlandırmadığı; `test_notebook.py`: DeepSeek anahtarı her turun ona gittiği için gerekli.

### Task 3: Kırmızıyı gör ve commit et

- [ ] **Step 1:** Dört satır, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` · `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
  Beklenen: queen-agent'ın iki satırı spec'teki numaralarda kırmızı; queen-editor yeşil.
- [ ] **Step 2:** Commit — `test(queen-agent): Madde 358 red -- no model picker, no model name, and the browser names no model`, spec ve planla birlikte.
