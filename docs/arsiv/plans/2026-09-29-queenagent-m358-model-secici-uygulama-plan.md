# Madde 358 — Model seçici kalkar, ve model hiçbir yerde görünmez · uygulama turunun planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `cf708b6a`'nın kırmızı testlerini yeşile çeviren kod: seçici ve `models.js` gider, tarayıcı
model göndermez, sunucu her turu `config.DEFAULT_MODEL`'e verir, FOUNDATION'ın 6. kararı güncellenir.

**Architecture:** Ön uçta iki dosya silinir, üç dosyadan model yolu çıkar. Arka uçta modelin yolu
route → `append_message` → `stream_answer` → `Engine.stream` boyunca kesilir; `Message.model` kayıt
olarak kalır. `engine_for` varsayılana düşmez.

**Tech Stack:** React 18 + vitest; Flask + pytest.

**Spec:** [uygulama turunun spec'i](../specs/2026-09-29-queenagent-m358-model-secici-uygulama-design.md)

## Global Constraints

- Testler yalnız CLAUDE.md'deki dört satırla koşar, yazıldığı gibi, paralel.
- Kod ve yorum İngilizce; yorum NEDEN'i ve bugünü söyler.
- Kırmızı testler değişmez; `dist` derlenmez.
- Commit mesajında çift tırnak yok; amend yok.

---

### Task 1: Ön uç

**Files:**
- Delete: `queen-agent/frontend/src/features/workspace/ModelPicker.jsx`, `models.js`
- Modify: `queen-agent/frontend/src/App.jsx` (19, 71–80, 316–322, 152–155)
- Modify: `queen-agent/frontend/src/features/workspace/ChatScreen.jsx` (11, 52–55, 341–346, 368–374)
- Modify: `queen-agent/frontend/src/features/workspace/useChat.js` (108, 161)
- Modify: `queen-agent/frontend/src/features/workspace/workspace.css` (1881–1921)
- Modify (yorum): `Composer.jsx`, `Menu.jsx`, `SkillPicker.jsx`, `shared/menuPlacement.js`

**Interfaces:**
- Produces: `useChat().send(text = null, skill = "", mode = "", from = null)`; gövde `{ chat, text, skill, mode, ...(from === null ? {} : { from }) }`.

- [ ] **Step 1:** `git rm` iki dosya.
- [ ] **Step 2:** `App.jsx` — `import { DEFAULT_MODEL } ...` ve `lastModel` durumu silinir; `pickerOpen` yorumu `null, "skills" or "mode"`; `ChatScreen`'den dört model prop'u çıkar; `onSend={(text, from) => chat.send(text, skillInForce, lastMode, from)}`; Escape yorumu: *"It named two pickers, Madde 82 took one out and Madde 91 put another back; the model's went for good in Madde 358."*
- [ ] **Step 3:** `ChatScreen.jsx` — `import ModelPicker` ve dört prop çıkar; `<ModelPicker … />` silinir; yorum: *"karar 1's order, with Madde 91's mode in front of it: Mode · Skills · Send. … No model is named anywhere since Madde 358: there is one, and the server names it."*
- [ ] **Step 4:** `useChat.js` — imza `async (text = null, skill = "", mode = "", from = null)`; gövdeden `model,` çıkar.
- [ ] **Step 5:** `workspace.css` — `.model-label { … }` ve yorumu silinir; `.composer__gauge` yorumu *"the pickers and Send are separate items in that row"*; `.picker` yorumu *"The foot's pickers."* ile başlar, *"It was the model's button too until Madde 82."* çıkar.
- [ ] **Step 6:** Yorumlar — `Composer.jsx:11` *"Mode · Skills · Send"*; `Menu.jsx:5` *"the Mode and Skills menus"*; `SkillPicker.jsx:6–8` *"to the right of the mode"* ve *"Two differences from the mode picker"* (farkları okuyup doğrula); `menuPlacement.js:8` model menüsü yerine *"four described rows"*.

### Task 2: Arka uç

**Files:**
- Modify: `queen-agent/backend/features/workspace/presentation/routes.py` (129, 379)
- Modify: `queen-agent/backend/features/workspace/domain/usecases/append_message.py` (26, 60)
- Modify: `queen-agent/backend/features/workspace/domain/usecases/stream_answer.py` (86–97, 219–221, 269–272)
- Modify: `queen-agent/backend/features/workspace/domain/ports.py` (47–74)
- Modify: `queen-agent/backend/features/workspace/data/xai_engine.py`
- Modify: `queen-agent/backend/config.py` (28–87)
- Modify (yorum): `domain/chat.py:59–63`, `data/file_chat_store.py:68–69`

**Interfaces:**
- Produces: `Engine.stream(messages, tools=None, on_open=None, conversation_id="")`;
  `config.engine_for(model_id) -> (model_id, base_url, key)`, bilinmeyen kimlikte `KeyError`.

- [ ] **Step 1:** routes — `model=payload.get("model", ""),` ve `"model": message.model,` silinir.
- [ ] **Step 2:** append_message — `model=""` parametresi ve `model=model,` silinir.
- [ ] **Step 3:** stream_answer — `_current_model` fonksiyonu, `model = _current_model(chat)` ve yorumu, `model=model,` ve yorumu silinir.
- [ ] **Step 4:** ports — `model: str = ""` çıkar; sınıf belgesi: *"Which model it answers with is settled when it is built (config.DEFAULT_MODEL): there is one, and nothing on the screen names it (Madde 358)."*
- [ ] **Step 5:** xai_engine —

```python
    def stream(self, messages, tools=None, on_open=None, conversation_id=""):
        return self._clients[self._default].stream(
            self._for_xai(messages),
            tools=tools,
            on_open=on_open,
            conversation_id=conversation_id,
        )
```

`_chosen` silinir; sınıf ve `write_once` belgeleri turun modelinin varsayılan olduğunu söyler.
- [ ] **Step 6:** config —

```python
def engine_for(model_id):
    """Which model, over which address, spending which key -- for a row of the table above."""
    wiring = MODELS[model_id]
    return model_id, wiring["base_url"], globals()[wiring["key"]]
```

Yorumlar: tablo *"which models exist"*, `models.js` yok; `DEFAULT_MODEL` *"what answers every turn"*; `PROMPT_MODEL` *"no picker"* yerine iki rolün ayrı olduğu; deepseek satırının *"answered by the default"* cümlesi *"kept as a record and steer nothing"*.
- [ ] **Step 7:** chat.py ve file_chat_store yorumları: `Message.model` 146–357'nin kaydı.

### Task 3: Belgeler

- [ ] **Step 1:** `FOUNDATION.md` Karar 6 — spec'teki *Consequence* paragrafı olduğu gibi.
- [ ] **Step 2:** `CODE-STANDARD.md` — `chats/<id>.json` satırı: *"after each message, on opening a version, and on a trim"*.
- [ ] **Step 3:** `queenagent.ipynb` Serve hücresi — *"Which of\n# the two a turn spends is decided by the model picked in the composer, and config.py's table is\n# what turns that choice into a key."* → *"Which\n# model a turn spends is config.py's to say, and its table is what turns that into a key."*

### Task 4: Yeşili gör ve commit et

- [ ] **Step 1:** Dört satır, paralel; hepsi yeşil.
- [ ] **Step 2:** `grep` ile `models.js`, `ModelPicker`, `lastModel`, `Queen Flash`, `model-label` kaynakta kalmadı mı bakılır (dist hariç).
- [ ] **Step 3:** Commit — `feat: Madde 358 -- the model picker and the model name are gone, and the server names the model every turn goes to`, spec ve planla birlikte.
