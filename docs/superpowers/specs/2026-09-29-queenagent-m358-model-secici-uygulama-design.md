# Madde 358 — Model seçici kalkar, ve model hiçbir yerde görünmez · uygulama turu

**Kaynak:** [test turunun spec'i](2026-09-29-queenagent-m358-model-secici-testler-design.md) ve
kırmızı commit'i `cf708b6a`. Kararlar orada; bu tur yalnız o testlerin tarif ettiği kodu yazar.

**Kullanıcıdan gereken:** hiçbir şey.

## Ön uç

- **`ModelPicker.jsx` ve `models.js` silinir.** Başka okuyanları yok: `App.jsx` `DEFAULT_MODEL`'i,
  `ChatScreen.jsx` `ModelPicker`'ı içe aktarıyor, ikisi de gidiyor.
- **`App.jsx`:** `lastModel` durumu, `DEFAULT_MODEL`'in içe aktarılması, `ChatScreen`'e giden
  `model`, `modelOpen`, `onToggleModel`, `onModelChange` çıkar; `onSend` `chat.send(text,
  skillInForce, lastMode, from)` olur. `pickerOpen`'un yorumundaki `"model"` değeri çıkar; Escape
  yorumu açık kalan seçicileri anlatır.
- **`ChatScreen.jsx`:** dört prop ve `<ModelPicker>` çıkar; ayağın yorumu Mode · Skills · Send der.
- **`useChat.js`:** `send(text, skill, mode, from)`; gövdede `model` yok.
- **`workspace.css`:** `.model-label` kuralı silinir; `.composer__gauge`'un ve `.picker`'ın
  yorumlarındaki model adı bugünü söyler.
- **Yorumlar:** `Composer.jsx` (ayağın sırası), `Menu.jsx` (çağıranlar), `SkillPicker.jsx` (model
  seçicisiyle karşılaştırma ModePicker'a döner), `menuPlacement.js` (320'nin gerekçesi — model menüsü
  artık yok; tavan dört açıklamalı satırı tutar, Skills ve Mode menüleri de böyle satırlar).

## Arka uç

- **`routes.py`:** `append_message`'a `model=payload.get("model", "")` gitmez; `_chat_json`'ın
  mesajlarında `"model"` yok.
- **`append_message.py`:** `model` parametresi ve `Message(model=...)` çıkar.
- **`stream_answer.py`:** `_current_model` ve `engine.stream(..., model=model)` çıkar.
- **`ports.py`:** `Engine.stream`'in `model` parametresi çıkar; belge: hangi modelle cevap verildiği
  motorun kuruluşunda bellidir.
- **`xai_engine.py`:** `stream` `model` almaz, `self._clients[self._default]`'la konuşur; `_chosen`
  silinir. `write_once` değişmez.
- **`config.py`:** `engine_for` varsayılana düşmez — `MODELS[model_id]`; bilinmeyen kimlik
  `KeyError`. Tablonun, `DEFAULT_MODEL`'in ve `PROMPT_MODEL`'in yorumları `models.js`'i, düğmeyi ve
  kutuyu anmaz.
- **`chat.py`:** `Message.model` kalır; yorumu onun bir kayıt olduğunu, hiçbir şeyi
  yönlendirmediğini söyler. `file_chat_store.py` değişmez (yorum: 146–357 arası).
- **`main.py`:** kod değişmez; `engine_for`'un yorumu doğru kalır.

## Belgeler

- **`FOUNDATION.md`, Karar 6'nın *Consequence* cümleleri** şununla değişir:

  > Consequence: which models exist is `config.py`'s table, and which one answers is `config.py`'s
  > too — `DEFAULT_MODEL` for every turn, `PROMPT_MODEL` for the one question a tool asks. Nothing
  > on the screen names a model and the browser sends none (Madde 358, the owner's decision of 28
  > September: one model is left, and it is not to be seen), so no name and no price is kept for a
  > person to read. Madde 146 had made the model an input to each turn, picked in the composer and
  > written onto the message; the messages written then still carry it as a record of what
  > answered them, and nothing is steered by it. A choice put back on the screen makes it an input
  > to the turn again — never a copy of `config.py`'s ids kept in the browser.

- **`CODE-STANDARD.md`:** `chats/<id>.json` satırının *"on a model or skill choice"*'ı düşer — model
  seçimi kalmadı, skill seçimi de diske yazılmıyor (mesajla gider, Madde 86); yerine sohbeti bugün
  yeniden yazan üçüncü şey, açık sürümün değişmesi: *"after each message, on opening a version, and on
  a trim"*.
- **`queenagent.ipynb`:** Serve hücresindeki *"Which of the two a turn spends is decided by the model
  picked in the composer"* cümlesi `config.py`'nin hangi modelin cevap verdiğini söylediği cümleyle
  değişir. Kod değişmez.

## Testte bir düzeltme

Test turu `test_config.py`'nin son testini gözden kaçırdı: *"a chat that named an old deepseek id is
answered by flash"* — `engine_for`'un varsayılana düşmesini soruyordu, yani kaldırılan davranışı.
Asıl söylediği, eski kimliği taşıyan sohbetin yine cevaplandığı, doğru kalıyor; o yüzden silinmez,
yeri değişir: `test_stream_answer.py`'de *"a question that names a model since dropped is still
answered"* — diskteki mesajı `deepseek-v4-pro` taşıyan sohbet `stream_answer`'dan cevabını alır.

## Nasıl görülür

Dört satır, paralel; hepsi yeşil. `dist` derlenmez — yöneten birleştirirken derler.
Tarayıcıda: yazma kutusunun ayağı `Edit⌄ Skills⌄ ↑`; `Queen Flash` hiçbir yerde yok; bir mesaj
gönderilince cevap yine DeepSeek Flash'tan geliyor.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-29-queenagent-m358-model-secici-uygulama-plan.md).
