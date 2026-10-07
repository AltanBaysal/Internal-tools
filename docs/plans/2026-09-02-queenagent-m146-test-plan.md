# Madde 146 · Tur 1 (test) — Uygulama Planı

> **Bu tur yalnız test yazar.** Hiçbir üretim dosyası ellenmez; tur tek bir **kırmızı commit** ile
> biter. Depo kuralı gereği alt-ajan kullanılmaz — planı bu oturum yürütür.

**Goal:** Madde 146'nın davranışını, hiçbiri bugün doğru olmayan iddialar hâlinde çivilemek.

**Architecture:** Model seçimi skill'in ayrımını birebir alıyor — gördüğü liste frontend'de
(`models.js`), id'nin motor için anlamı backend'de (`config.py`), seçimin kendisi hiçbir yerde, ve
kaydı `Message.model`'de. Seçim en yeni kullanıcı mesajından geri okunuyor, tıpkı
`_current_skill` gibi.

**Tech Stack:** pytest · vitest + React Testing Library

**Spec:** [m146 test turu tasarımı](../specs/2026-09-02-queenagent-m146-model-secimi-testler-design.md)

## Global Constraints

- **Yalnız test.** `models.js`, `ModelPicker.jsx`, `config.py`, `chat.py`, `routes.py`,
  `xai_engine.py`, `client.py`, `main.py` ve defter bu turda **değişmez**.
- **`skip` / `xfail` yasak** — kırmızı, kırmızı olarak commit'lenir.
- Üç id sabittir: `grok-build-0.1`, `deepseek-v4-flash`, `deepseek-v4-pro`.
- Varsayılan `grok-build-0.1`.
- Adresler: xAI `https://api.x.ai/v1`, DeepSeek `https://api.deepseek.com` *(sonda `/v1` yok)*.
- Anahtar adları: `XAI_API_KEY`, `DEEPSEEK_API_KEY`.
- Menüdeki detaylar birebir: `$1 / $2 per 1M`, `$0.22 / $0.66 per 1M`, `$0.66 / $1.98 per 1M`.
- Türkçe yalnız kullanıcının gördüğü yerde; test adları ve yorumlar İngilizce *(CLAUDE.md)*.

---

### Task 1: `models.js` — gördüğü liste

**Files:**
- Test: `queen-agent/frontend/src/features/workspace/models.test.js` *(yeni)*

**Interfaces:**
- Produces: `MODELS` — `{id, name, detail}[]`; `modelName(id)`; `DEFAULT_MODEL`.
- `skills.js`'in aynası, **tek farkla**: boş id varsayılanın adını verir, `"Skills"` gibi bir
  boş hâl yoktur.

- [ ] **Step 1: Testi yaz**

```js
import { describe, expect, test } from "vitest";

import { DEFAULT_MODEL, MODELS, modelName } from "./models.js";

test("three models are offered", () => {
  expect(MODELS.map((model) => model.id)).toEqual([
    "grok-build-0.1",
    "deepseek-v4-flash",
    "deepseek-v4-pro",
  ]);
});

test("every row carries a name and a price", () => {
  expect(MODELS.map((model) => [model.name, model.detail])).toEqual([
    ["Grok Build", "$1 / $2 per 1M"],
    ["DeepSeek Flash", "$0.22 / $0.66 per 1M"],
    ["DeepSeek Pro", "$0.66 / $1.98 per 1M"],
  ]);
});

test("the default is the one the app opened on", () => {
  expect(DEFAULT_MODEL).toBe("grok-build-0.1");
});

test("a known id reads as its name", () => {
  expect(modelName("deepseek-v4-flash")).toBe("DeepSeek Flash");
});

// Where this parts from skillName: no skill is an ordinary state and reads as "Skills", but every
// answer is given by some model, so nothing is the default rather than a gap.
test("no id reads as the default's name", () => {
  expect(modelName("")).toBe("Grok Build");
});

// A record from before Madde 72 can still name one of the five that were dropped.
test("an unknown id says itself", () => {
  expect(modelName("grok-4.3")).toBe("grok-4.3");
});
```

- [ ] **Step 2: Kırmızıyı gör**

Run: `npm test --prefix queen-agent/frontend`
Expected: FAIL — `Failed to resolve import "./models.js"`

---

### Task 2: `ModelPicker` — tıklanan seçici

**Files:**
- Test: `queen-agent/frontend/src/features/workspace/ModelPicker.test.jsx` *(yeni)*
- Sil: `queen-agent/frontend/src/features/workspace/ModelLabel.test.jsx`

**Interfaces:**
- Consumes: Task 1'in `MODELS` / `modelName`'i.
- Produces: `ModelPicker({ model, open, onToggle, onChange })` — `SkillPicker`'ın şekli.
- **`SkillPicker`'dan tek farkı:** seçili satıra basmak temizlemez, seçer. Modelin boş hâli yok.

- [ ] **Step 1: Testi yaz**

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import ModelPicker from "./ModelPicker.jsx";

test("the foot shows the selected model and can be pressed", () => {
  render(<ModelPicker model="deepseek-v4-flash" />);
  expect(screen.getByRole("button", { name: /DeepSeek Flash/ })).toBeTruthy();
});

test("pressing it asks to be opened", () => {
  const onToggle = vi.fn();
  render(<ModelPicker model="grok-build-0.1" onToggle={onToggle} />);
  fireEvent.click(screen.getByRole("button", { name: /Grok Build/ }));
  expect(onToggle).toHaveBeenCalled();
});

test("open, it lists three rows with their prices", () => {
  render(<ModelPicker model="grok-build-0.1" open />);
  expect(screen.getByText("DeepSeek Pro")).toBeTruthy();
  expect(screen.getByText("$0.22 / $0.66 per 1M")).toBeTruthy();
});

test("the selected row is marked", () => {
  const { container } = render(<ModelPicker model="deepseek-v4-pro" open />);
  const checked = container.querySelectorAll(".menu__item--checked");
  expect(checked.length).toBe(1);
  expect(checked[0].textContent).toContain("DeepSeek Pro");
});

test("choosing a row reports the id", () => {
  const onChange = vi.fn();
  render(<ModelPicker model="grok-build-0.1" open onChange={onChange} />);
  fireEvent.click(screen.getByText("DeepSeek Flash"));
  expect(onChange).toHaveBeenCalledWith("deepseek-v4-flash");
});

// Where this parts from SkillPicker, which clears on the selected row: there is no way back to no
// model, so the press is an ordinary choice.
test("choosing the selected row keeps it rather than clearing", () => {
  const onChange = vi.fn();
  render(<ModelPicker model="deepseek-v4-flash" open onChange={onChange} />);
  fireEvent.click(screen.getByText("DeepSeek Flash"));
  expect(onChange).toHaveBeenCalledWith("deepseek-v4-flash");
});
```

- [ ] **Step 2: `ModelLabel.test.jsx`'i sil**

`ModelLabel` bileşeni Tur 2'de gidiyor; testi burada gidiyor, yoksa kırmızı iki sebepten kırmızı
olur ve hangisinin hangisi olduğu okunamaz.

- [ ] **Step 3: Kırmızıyı gör**

Run: `npm test --prefix queen-agent/frontend`
Expected: FAIL — `Failed to resolve import "./ModelPicker.jsx"`

---

### Task 3: Ayaktaki sıra ve üçüncü menü

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.test.jsx` *(≈634-644)*
- Modify: `queen-agent/frontend/src/features/workspace/ProjectScreen.test.jsx` *(≈208, 228-229)*

**Interfaces:**
- Consumes: `ModelPicker`.
- Produces: her iki ekran `model`, `modelOpen`, `onToggleModel`, `onModelChange` alır.

- [ ] **Step 1: İki "tıklanamaz" kilidini tersine çevir**

`ChatScreen.test.jsx` ve `ProjectScreen.test.jsx`'te bugün duran çift:

```jsx
expect(screen.getByText("Grok Build")).toBeTruthy();
expect(screen.queryByRole("button", { name: /Grok Build/ })).toBeNull();
```

şununla değişir — **silinmez, tersine çevrilir**; kilit kaldırılırken yerine karşıtı konmazsa
davranış sessizce serbest kalır:

```jsx
expect(screen.getByRole("button", { name: /Grok Build/ })).toBeTruthy();
```

- [ ] **Step 2: Ayak metnini şapkalı hâline getir**

İki dosyada da `foot.textContent` iddiası:

```jsx
expect(foot.textContent).toBe("Edit⌄Skills⌄Grok Build⌄↑");
```

*(bugün `"Edit⌄Skills⌄Grok Build↑"` — model artık bir düğüm, şapkası var.)*

- [ ] **Step 3: Üçüncü menünün ötekileri kapattığını çivile**

`ChatScreen.test.jsx`'e yeni:

```jsx
test("opening the model menu closes the skills menu", () => {
  const onToggleModel = vi.fn();
  renderChat({ skillsOpen: true, onToggleModel });
  fireEvent.click(screen.getByRole("button", { name: /Grok Build/ }));
  expect(onToggleModel).toHaveBeenCalled();
});
```

*(Dosyanın kendi `renderChat` yardımcısı kullanılır; adı ve imzası yazarken okunur.)*

- [ ] **Step 4: Kırmızıyı gör**

Run: `npm test --prefix queen-agent/frontend`
Expected: FAIL — ayak metni `Grok Build↑` ile bitiyor, düğüm yok

---

### Task 4: Seçim mesajla gidiyor

**Files:**
- Modify: `queen-agent/frontend/src/features/workspace/useChat.js` **testi**
  *(`useChat` testinin bulunduğu dosya; yoksa `useChat.test.js` açılır)*

**Interfaces:**
- Produces: `send(text, skill, mode, model)` — gövde `{ chat, text, skill, mode, model }`.
- `useChat.js:130`'daki bugünkü gövde `{ chat, text, skill, mode }`.

- [ ] **Step 1: Testi yaz**

```js
test("the chosen model rides on the message, beside the skill", async () => {
  const fetched = [];
  globalThis.fetch = vi.fn((url, options) => {
    fetched.push(JSON.parse(options.body));
    return Promise.resolve({ ok: true, body: null, json: () => Promise.resolve({}) });
  });
  // ... hook is rendered and send() called with the model
  expect(fetched[0].model).toBe("deepseek-v4-flash");
  expect(fetched[0].skill).toBe("");
});
```

*(Dosyanın kendi fetch sahtesi varsa o kullanılır — yeni bir kalıp uydurulmaz.)*

- [ ] **Step 2: Kırmızıyı gör**

Run: `npm test --prefix queen-agent/frontend`
Expected: FAIL — `fetched[0].model` `undefined`

---

### Task 5: `config.py` — id'nin anlamı

**Files:**
- Modify: `queen-agent/backend/tests/test_config.py`

**Interfaces:**
- Produces: `config.MODELS` — `{id: {"base_url": str, "key": str}}`; `config.DEFAULT_MODEL`;
  `config.engine_for(model_id)` → `(model_id, base_url, api_key)`.
- `skills.py`'nin `instruction_for`'unun aynası: tanınmayan id sessizce varsayılana düşer.

- [ ] **Step 1: Testi yaz**

```python
def test_the_three_models_resolve_to_their_provider():
    assert config.MODELS["grok-build-0.1"]["base_url"] == "https://api.x.ai/v1"
    # No /v1 on this one -- DeepSeek's documented base, and the client appends
    # /chat/completions itself.
    assert config.MODELS["deepseek-v4-flash"]["base_url"] == "https://api.deepseek.com"
    assert config.MODELS["deepseek-v4-pro"]["base_url"] == "https://api.deepseek.com"


def test_each_model_names_the_key_it_spends():
    assert config.MODELS["grok-build-0.1"]["key"] == "XAI_API_KEY"
    assert config.MODELS["deepseek-v4-flash"]["key"] == "DEEPSEEK_API_KEY"


def test_the_default_is_grok_build():
    # Madde 82 named one model here and Madde 146 made it the default of three. What the app
    # answers with when nothing was chosen must not move quietly.
    assert config.DEFAULT_MODEL == "grok-build-0.1"


def test_an_unknown_model_falls_back_to_the_default():
    # A record written before Madde 146 names no model at all, and one from before Madde 82 names
    # grok-4.3. Neither may stop a chat from being answered.
    assert config.engine_for("")[0] == "grok-build-0.1"
    assert config.engine_for("grok-4.3")[0] == "grok-build-0.1"


def test_the_deepseek_key_comes_from_the_environment(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "ds-from-the-environment")
    assert _reloaded().DEEPSEEK_API_KEY == "ds-from-the-environment"
```

*(`_reloaded()` dosyanın kendi yardımcısı — `test_config.py:18`'de zaten kullanılıyor.)*

- [ ] **Step 2: Kırmızıyı gör**

Run: `python -m pytest queen-agent/backend/tests/test_config.py -q`
Expected: FAIL — `AttributeError: module 'backend.config' has no attribute 'MODELS'`

---

### Task 6: `Message.model` — kaydı

**Files:**
- Modify: `queen-agent/backend/tests/test_chat.py`
- Modify: `queen-agent/backend/tests/test_file_chat_store.py`

**Interfaces:**
- Produces: `Message.model: str = ""`, `skill`'in yanında.

- [ ] **Step 1: Testi yaz**

```python
def test_a_message_remembers_which_model_was_chosen():
    # Kept on the message for the reason skill is: changing the selection later must not make an
    # older turn look as though the new model answered it.
    assert Message(role="user", at=AT, text="hi", model="deepseek-v4-flash").model == (
        "deepseek-v4-flash"
    )


def test_a_message_without_a_model_carries_the_empty_one():
    assert Message(role="user", at=AT, text="hi").model == ""
```

ve store tarafında:

```python
def test_a_message_model_survives_a_write_and_a_read(tmp_path):
    store = FileChatStore(Store(str(tmp_path)))
    # ... a chat is written with a user message carrying a model
    assert store.get("p1", "c1").messages[0].model == "deepseek-v4-pro"


def test_a_message_written_before_this_field_reads_as_empty(tmp_path):
    raw = Store(str(tmp_path))
    raw.write_text(
        "p1/chats/old.json",
        '{"title": "Old", "createdAt": "2026-08-09T11:04:00+00:00",'
        ' "messages": [{"role": "user", "at": "2026-08-09T11:04:00+00:00", "text": "hi"}]}',
    )
    assert FileChatStore(raw).get("p1", "old").messages[0].model == ""
```

- [ ] **Step 2: Yeşil kalması gerekeni doğrula**

`test_a_chat_that_still_carries_a_model_on_disk_is_read_without_it` **yeşil kalmalı.** O test
sohbetin **kökündeki** `model` anahtarını konu ediyor; bu alan **mesajın** içinde. Kırmızıya
dönerse alan yanlış yere konmuş demektir — planın en iyi bekçisi budur.

- [ ] **Step 3: Kırmızıyı gör**

Run: `python -m pytest queen-agent/backend/tests/test_chat.py queen-agent/backend/tests/test_file_chat_store.py -q`
Expected: FAIL — `TypeError: Message.__init__() got an unexpected keyword argument 'model'`

---

### Task 7: Uçta girip çıkması

**Files:**
- Modify: `queen-agent/backend/tests/test_chats_api.py`

**Interfaces:**
- Consumes: Task 6'nın `Message.model`'i.
- Produces: `routes.py` gövdeden `payload.get("model", "")` okur *(`skill`'in yanında, satır ≈115)*
  ve mesaj JSON'unda `"model"` döndürür *(≈317)*.

- [ ] **Step 1: Testi yaz**

```python
def test_the_model_rides_in_with_the_message(client):
    # The selection is the session's and the server holds none: it arrives with each message, the
    # way skill has since Madde 86.
    sent = client.post("/api/projects/p1/messages", json={
        "chat": "", "text": "hi", "skill": "", "mode": "edit", "model": "deepseek-v4-flash",
    })
    assert sent.status_code == 200


def test_the_model_comes_back_out_with_the_message(client):
    # ... the chat is read back
    assert body["messages"][0]["model"] == "deepseek-v4-flash"


def test_a_message_sent_without_a_model_is_still_accepted(client):
    # Every client that predates this field, and the tests that predate it too.
    sent = client.post("/api/projects/p1/messages", json={"chat": "", "text": "hi"})
    assert sent.status_code == 200
```

*(Uç adı ve `client` fixture'ı dosyanın kendisinden okunur — yukarıdaki yol örnektir.)*

- [ ] **Step 2: Kırmızıyı gör**

Run: `python -m pytest queen-agent/backend/tests/test_chats_api.py -q`
Expected: FAIL — `KeyError: 'model'`

---

### Task 8: Motor modeli mesajdan okuyor

**Files:**
- Modify: `queen-agent/backend/tests/test_xai_engine.py`
- Modify: `queen-agent/backend/tests/test_stream_answer.py`

**Interfaces:**
- Produces: `XaiEngine(clients, default)` — `clients` bir `{model_id: client}` eşlemesi;
  `stream(..., model="")` hangi istemcinin konuşacağını seçer.
- Produces: `stream_answer` içinde `_current_model(chat)` — `_current_skill`'in aynası, en yeni
  **kullanıcı** mesajından geri okuyor.

- [ ] **Step 1: Motorun testini yaz**

```python
def test_the_engine_speaks_through_the_chosen_model():
    grok, flash = Spy(), Spy()
    engine = XaiEngine({"grok-build-0.1": grok, "deepseek-v4-flash": flash},
                       default="grok-build-0.1")
    list(engine.stream([{"role": "user", "content": "hi"}], model="deepseek-v4-flash"))
    assert flash.called and not grok.called


def test_an_unknown_model_speaks_through_the_default():
    grok, flash = Spy(), Spy()
    engine = XaiEngine({"grok-build-0.1": grok, "deepseek-v4-flash": flash},
                       default="grok-build-0.1")
    list(engine.stream([{"role": "user", "content": "hi"}], model="grok-4.3"))
    assert grok.called and not flash.called
```

- [ ] **Step 2: Turun testini yaz**

```python
def test_the_turn_is_answered_by_the_model_its_question_named():
    # Read back off the newest user message, the way _current_skill is: a record does not always
    # end with the question waiting for an answer.
    # ... a chat whose last user message carries deepseek-v4-pro
    assert engine.asked_model == "deepseek-v4-pro"
```

- [ ] **Step 3: Kırmızıyı gör**

Run: `python -m pytest queen-agent/backend/tests/test_xai_engine.py queen-agent/backend/tests/test_stream_answer.py -q`
Expected: FAIL — `XaiEngine.__init__() takes 2 positional arguments but 3 were given`

---

### Task 9: İstemcinin iki sağlayıcısı

**Files:**
- Modify: `queen-agent/backend/tests/test_xai_client.py`

**Interfaces:**
- Produces: `_spent()` iki usage şeklini de tanır; `x-grok-conv-id` yalnız xAI adresine gider.

- [ ] **Step 1: Testi yaz**

```python
def test_a_deepseek_cache_hit_is_read_as_cached():
    # xAI nests it under prompt_tokens_details; DeepSeek sends two flat counts. Both are the same
    # question -- what did not have to be paid for twice.
    frame = {"choices": [], "usage": {
        "prompt_tokens": 1200, "completion_tokens": 40,
        "prompt_cache_hit_tokens": 900, "prompt_cache_miss_tokens": 300,
    }}
    assert _spent(frame) == {"sent": 1200, "cached": 900, "answered": 40}


def test_an_xai_cache_hit_is_still_read_as_cached():
    frame = {"choices": [], "usage": {
        "prompt_tokens": 1200, "completion_tokens": 40,
        "prompt_tokens_details": {"cached_tokens": 900},
    }}
    assert _spent(frame) == {"sent": 1200, "cached": 900, "answered": 40}


def test_deepseek_is_not_sent_the_grok_conversation_header():
    # xAI routes a request to its cache with this; DeepSeek matches prefixes on its own and
    # documents no such header.
    seen = {}
    client = XaiClient(lambda: "key", "deepseek-v4-flash", "https://api.deepseek.com",
                       opener=_recording(seen))
    list(client.stream([{"role": "user", "content": "hi"}], conversation_id="c1"))
    assert seen["conv"] is None


def test_xai_is_still_sent_the_conversation_header():
    seen = {}
    client = XaiClient(lambda: "key", "grok-build-0.1", "https://api.x.ai/v1",
                       opener=_recording(seen))
    list(client.stream([{"role": "user", "content": "hi"}], conversation_id="c1"))
    assert seen["conv"] == "c1"
```

*(`_recording` dosyanın 291 ve 304. satırlarındaki mevcut kalıptan çıkarılır.)*

- [ ] **Step 2: Kırmızıyı gör**

Run: `python -m pytest queen-agent/backend/tests/test_xai_client.py -q`
Expected: FAIL — DeepSeek usage'ı `cached: 0` okunuyor; başlık her iki adrese de gidiyor

---

### Task 10: Defterin ikinci anahtarı

**Files:**
- Modify: `queen-agent/backend/tests/test_notebook.py`

**Interfaces:**
- Produces: defter `DEEPSEEK_API_KEY`'i Secrets'tan okur, env'de geçirir, basmaz, ve **ikisini de**
  şart koşar.

- [ ] **Step 1: Testi yaz**

```python
def test_the_deepseek_key_comes_from_secrets():
    assert 'userdata.get("DEEPSEEK_API_KEY")' in _source(), "DeepSeek anahtarı Secrets'tan okunmuyor"


def test_a_missing_deepseek_key_says_what_to_do():
    # Both keys, not one of them (kullanıcı kararı, 2 Eylül): the menu draws three rows, so a run
    # opened on one key promises two models it cannot answer with.
    said = _cell("assert DEEPSEEK_API_KEY")
    assert said, "DeepSeek anahtarı yokken defter sessizce devam ediyor"
    assert "Secrets" in said and "DEEPSEEK_API_KEY" in said, "Ne yapılacağı söylenmiyor"


def test_the_deepseek_key_travels_to_the_app_in_the_environment():
    assert '"DEEPSEEK_API_KEY": DEEPSEEK_API_KEY' in _cell(SERVE), "Anahtar uygulamaya geçirilmiyor"
```

- [ ] **Step 2: Basılmama kilidini ikinci anahtara genişlet**

`test_the_xai_key_is_never_printed` bugün tek anahtara bakıyor; iki anahtar üzerinde dönen bir
döngüye çevrilir. Kilidin sorusu değişmiyor — **adı** çıktıda olabilir, **değeri** asla.

- [ ] **Step 3: Kırmızıyı gör**

Run: `python -m pytest queen-agent/backend/tests/test_notebook.py -q`
Expected: FAIL — defter `DEEPSEEK_API_KEY` kelimesini hiç geçirmiyor

---

### Task 11: Turu kırmızı kapat

- [ ] **Step 1: Dört satırın hepsini koş**

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

queen-editor'ün iki satırı **yeşil kalmalı** — bu madde ona hiç dokunmuyor. Kırmızıya dönerse
yanlış depoya yazılmış demektir.

- [ ] **Step 2: Kırmızının doğru sebepten olduğunu oku**

Her kırmızı, kendi iddiasının yokluğundan kırmızı olmalı — import hatası, eksik alan, eksik
anahtar. Bir test **başka** bir sebeple düşüyorsa o test yanlış yazılmıştır.

- [ ] **Step 3: Kırmızıyı commit'le**

```bash
git add queen-agent/backend/tests queen-agent/frontend/src
git commit
```

Mesaj: `test(m146): red locks the model the message names`. Sayılar mesaja yazılır —
*(N kırmızı, M yeşil)* — yol haritasının **Turlar** satırı onları alacak.

---

## Öz-denetim

**Spec kapsaması.** Spec'in 13 iddiası: 1-2 → Task 5; 3 → Task 6; 4 → Task 7; 5 → Task 8;
6-7 → Task 9; 8-9 → Task 1; 10 → Task 2; 11-13 → Task 3 ve 4. Defterin iki anahtarı → Task 10.
Ölecek testler → Task 2 *(silme)* ve Task 3 *(tersine çevirme)*. Boşluk yok.

**Tip tutarlılığı.** `model` her katmanda aynı adı taşıyor: gövdede `model`, `Message.model`,
`engine.stream(model=)`, `config.engine_for(model_id)`, `modelName(id)`. `DEFAULT_MODEL` iki
tarafta da aynı yazılıyor — Python'da `config.DEFAULT_MODEL`, JS'te `models.js`'in kendi sabiti.
**İkisi birbirini okuyamaz**, ve `ModelLabel.jsx`'in bugünkü yorumu bunu zaten söylüyor: aralarında
duran tek şey bir cümle. O cümle `models.js`'e taşınacak *(Tur 2)*.

**Yer tutucu taraması.** Task 4 ve 7'de test gövdeleri dosyanın kendi yardımcılarına yaslanıyor
*(`renderChat`, `client`, fetch sahtesi)*; adları yazarken okunuyor. Bu bir yer tutucu değil, kasıtlı
bir bağ — yeni bir kalıp uydurmak deponun kendi test biçimini bozardı.
