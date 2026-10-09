# Madde 82 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-26-queenagent-m82-model-secimi-sokulur-testler-design.md](../specs/2026-08-26-queenagent-m82-model-secimi-sokulur-testler-design.md)
**Bu turda kod yazılmaz.** Yalnız testler; tur kırmızı commit'lenir.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## A. Silinen dosyalar

- `queen-agent/backend/tests/test_model_api.py`
- `queen-agent/frontend/src/features/workspace/models.test.js`
- `queen-agent/frontend/src/features/workspace/ModelPicker.test.jsx`

Üçü de yalnızca sökülen şeyi sınıyor.

`test_set_chat_choices.py`'nin **model testleri gidiyor**, skill testleri kalıyor.

**Dosyanın ve modülün adı bu turda değişmiyor** *(koşarken öğrenildi)*. `set_chat_skill` diye bir
modül henüz yok, ve olmayan bir modülü import eden bir test dosyası pytest'in **toplama** aşamasını
düşürüyor — o zaman hiçbir test koşmuyor ve turun bütün kırmızıları görünmez oluyor. Ad değişikliği
kodla birlikte, uygulama turunda.

## B. Silinen testler

| Dosya | Giden |
|---|---|
| `test_chats_api.py` | `..._born_with_the_model_it_was_sent` · `..._picked_nothing_answers_with_the_apps_default` · `..._model_can_be_changed_mid_conversation` · `..._model_of_a_chat_that_is_not_there_is_404` · `..._asked_for_with_the_chats_own_model` |
| `test_set_chat_skill.py` | `..._keeps_the_model_it_was_given` · `..._skill_leaves_the_model_alone` · `..._model_leaves_the_skill_alone` · `..._nothing_puts_the_chat_back_on_the_default_model` |
| `test_start_chat.py` | `..._born_with_the_model_that_was_picked` · `..._born_without_a_pick_carries_none`; `_start`'ın `model` parametresi |
| `test_file_chat_store.py` | `..._model_a_chat_chose_is_written_and_read_back` · `..._chose_nothing_writes_no_model`; `..._before_models_existed_still_reads`'in `model` satırı |
| `test_xai_client.py` | `..._given_for_the_call_replaces_the_configured_one` · `..._carries_its_own_model_too` |
| `test_xai_engine.py` | `..._model_travels_with_the_call`; `FakeClient`'ın `model` alanı |
| `App.test.jsx` | `picking a model writes it...` · `a new chat is born with the last model picked...` · `picking a model closes the menu` · `pressing the model already in use...` · `in a draft, picking a model...` · `with nothing picked yet a draft follows the server's own setting` |
| `ChatScreen.test.jsx` | `the composer says which model this chat answers with` · `picking another one is passed up rather than kept here` |
| `ProjectScreen.test.jsx` | `picking a model is passed up rather than kept here` |

`test_set_chat_skill.py`'de kalan skill testleri `set_chat_choices(...)` yerine
`set_chat_skill(store, "p1", "c1", "verify")` çağırıyor — konumsal, çünkü tek alan kaldı.

## C. Kırmızıya dönenler

### 1. `test_chats_api.py` — dört yeni

**`_client` ve paylaşılan sahte motorlar bu turda değişmiyor** *(koşarken öğrenildi)*.
`_client`'tan `default_model`'i çıkarmak `make_workspace_bp`'yi bir argüman eksik çağırıyor, ve o
dosyadaki **seksen testin hepsi** aynı `TypeError` ile düşüyor. Paylaşılan sahte motordan `model`
parametresini almak da aynı şeyi yapıyor. İkisi de gerçek kırmızı değil — kodun şeklini takip eden
fixture'lar, ve yerleri uygulama turu.

Yerine: yeni davranışı **kendi katı sahtesi** taşıyor, yalnız onu kullanan testte. Paylaşılanlar
`model=None` kabul edip yok saymaya devam ediyor.

Yeni testler:

```python
def test_the_model_endpoint_is_gone(tmp_path):
    # Madde 82: one model, so there is nothing to ask about. Flask answers a route nobody
    # registered, and that answer is the test.
    assert _client(tmp_path).get("/api/model").status_code == 404


def test_a_chat_carries_no_model(tmp_path):
    client = _client(tmp_path)
    pid, cid = _chat(client)
    assert "model" not in client.get(f"/api/projects/{pid}/chats/{cid}").get_json()


def test_a_patch_carrying_only_a_model_is_refused(tmp_path):
    # The one field a chat still carries is its skill. A model arriving here is not a change that
    # failed quietly -- it is a request this route no longer understands.
    client = _client(tmp_path)
    pid, cid = _chat(client)
    assert client.patch(f"/api/projects/{pid}/chats/{cid}", json={"model": "x"}).status_code == 400


def test_the_engine_is_asked_without_a_model(tmp_path):
    # The fake's stream takes no model. If the route still passes one this dies with a TypeError,
    # which is the point: there is one model and the wiring names it once.
    engine = Recording()
    client = _client(tmp_path, engine=engine)
    pid, cid = _chat(client)
    client.post(f"/api/projects/{pid}/chats/{cid}/answer")
    assert engine.seen is not None
```

`_chat(client)` bu dosyada zaten var *(bakıldı)*; yoksa aynı iki satır yazılır.

### 2. `test_chat.py` — bir yeni

`Chat`'te model diye bir alan kalmadığını tutan tek satır. Dosya yoksa `test_chat.py` açılır:

```python
from dataclasses import fields

from backend.features.workspace.domain.chat import Chat


def test_a_chat_carries_no_model():
    # Madde 82 took the field out rather than leaving it unread: a field nothing writes and nothing
    # reads is a question every future reader has to answer for themselves.
    assert "model" not in [field.name for field in fields(Chat)]
```

### 3. `ModelLabel.test.jsx` — yeni dosya

```jsx
import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import ModelLabel from "./ModelLabel.jsx";

test("it says which model answers", () => {
  render(<ModelLabel />);
  expect(screen.getByText("Grok Build")).toBeTruthy();
});

test("it is not something to press", () => {
  // Madde 82: one model, so there is nothing to choose. A control that opens nothing would be a
  // promise the app cannot keep.
  render(<ModelLabel />);
  expect(screen.queryByRole("button")).toBeNull();
});
```

### 4. `ChatScreen.test.jsx` — ayak testleri

`the foot carries Skills, the model and Send, in that order` yerine:

```jsx
test("the foot carries Skills, the model's name and Send, in that order", () => {
  // karar 1's order stands; the middle one stopped being a control in Madde 82.
  const { container } = render(<ChatScreen project={PROJECT} chat={CHAT} />);
  const foot = container.querySelector(".composer__foot");
  expect(foot.textContent).toBe("Skills⌄Grok Build↑");
  expect(foot.querySelectorAll("button").length).toBe(2);
});
```

Akan cevabınki de aynı kalıpta, sonu `⏹`.

### 5. `ProjectScreen.test.jsx` — aynı ayak testi

`the composer here carries both pickers, in the chat screen's order` aynı şekle geçiyor: metin
`Skills⌄Grok Build↑`, iki düğme.

### 6. `App.test.jsx` — iki yeni

```jsx
test("the app never asks which model to use", () => {
  // Madde 82: the setting has one value and the wiring names it once, in config.py.
  const fetch = withChat();
  window.history.pushState(null, "", "/p/p1/c/c1");
  render(<App />);
  return waitFor(() => {
    expect(screen.getByText("Grok Build")).toBeTruthy();
    expect(fetch.mock.calls.filter(([path]) => String(path) === "/api/model")).toHaveLength(0);
  });
});

test("a chat is born without a model", () => {
  // Nothing to send: there is one, and the server already knows which.
  ...POST /chats gövdesinde "model" anahtarı yok
});
```

`withModel` → **`withChat`** olarak yeniden adlandırılıyor ve `model` parametresi gidiyor: adı
artık taşımadığı şeyi söylüyor. `/api/model` dalı fixture'dan çıkıyor, sohbetin `model` alanı da.

### 7. `App.test.jsx` — Escape sırası kısalıyor

`Escape closes the pickers in the design's order` → `Escape closes the picker`: model adımı
gidiyor, çevresindekiler yerinde kalıyor. `one menu closes the other` de gidiyor — kapatacak ikinci
bir menü kalmadı.

**`picker` → `skillsOpen` adlandırması bu turda yapılmıyor**, aynı sebeple: prop adı kodun şeklini
takip ediyor ve iki ekranın testlerini toptan düşürürdü. Uygulama turunda, kodla birlikte.

## Koşulan kırmızı

**Arka uç: 10 failed / 422 passed** — sekizi bu maddenin, ikisi defterin dalı:

| Nerede | Ne söylüyor |
|---|---|
| `test_chat.py` | `Chat`'te `model` alanı yok |
| `test_chats_api.py` | `/api/model` 404 · sohbet JSON'u `model` taşımıyor · yalnız model taşıyan PATCH 400 · motor modelsiz çağrılıyor |
| `test_file_chat_store.py` | Diskte `model` taşıyan eski kayıt okunabiliyor ve alan gelmiyor |
| `test_stream_answer.py` | Motor modelsiz çağrılıyor |
| `test_xai_engine.py` | Motor modeli aktarmıyor |

**Ön yüz:** kırmızılar geliyor ve görülenler amaçlananlar — `ProjectScreen.test.jsx` ikisi.
**Toplam okunamıyor:** vitest her düşen `getByText` için tüm DOM'u basıyor ve çıktı sınırı aşılıyor.
Yeşil koşuda çıktı kısa olacağı için toplam orada okunur.

## Toplu değiştirme yok

`model` kelimesi iki düzine dosyada geçiyor ve çoğu bu maddeyle ilgisiz — `image model`,
`the model returned nothing`, `models write the sentence`. **`replace_all` kullanılmıyor.**

## Bilerek yapılmayanlar

- **Kod yazılmaz.** Hiçbir kaynak dosya açılmıyor.
- **`dist` derlenmez.**
- **`test_config.py` açılmıyor.** `config.XAI_MODEL` kalıyor ve testi de.
- **`SkillPicker.test.jsx` ve `Menu.test.jsx` açılmıyor.** Skill seçimi duruyor.
