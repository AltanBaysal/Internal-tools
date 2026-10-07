# Madde 72 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-26-queenagent-m72-grok-build-tek-model-uygulama-design.md](../specs/2026-08-26-queenagent-m72-grok-build-tek-model-uygulama-design.md)
**Kırmızı testler:** `cac7d39` — arka uçta 1, ön yüzde 6.
**Test komutları (değişmez, ikisi de) — ayrı ayrı koşulur:**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sıra

### 1. `backend/config.py` — varsayılan Grok Build

Değer ve üstündeki gerekçe birlikte:

```python
# What a chat that picked no model of its own answers with. Every chat may carry its own choice, so
# this is the starting point rather than the only model.
#
# Grok Build since Madde 72: $1/$2 per 1M against grok-4.3's $1.25/$2.50, and 256k of context
# against its 1M. The window is a quarter of what it was and the runs here are long -- a structure
# file, a scenario and a frame list pile up in one chat. That cost was named and accepted; the
# context work is Madde 71. Prices verified against xAI's documentation on 2026-08-18.
XAI_MODEL = os.environ.get("XAI_MODEL", "grok-build-0.1")
```

Bugünkü yorum *"yarı fiyat ve iki katı bağlam"* diyor ve ikincisi artık tersine döndü. Bir açıklama
yalnız bugün doğru olanı söyler *(CLAUDE.md)*.

*Yeşile döner:* `test_config.py::test_the_default_model_is_grok_build`.

### 2. `frontend/.../models.js` — liste tek satır

Dosyanın başındaki üç paragraf ve liste birlikte değişiyor:

```js
// The one model this app offers. Grok Build since Madde 72: it costs less than what came before
// ($1/$2 per 1M against grok-4.3's $1.25/$2.50) and the run stands on one model rather than on a
// choice nobody was making. Its window is 256k -- a quarter of grok-4.3's, named and accepted when
// the row was chosen. Which model a chat that picked nothing answers with is still the server's
// setting and arrives from GET /api/model; the name and the price are text, and text lives here.
//
// The row says what it costs rather than what it is for. The design wrote a sentence under each
// name, but those names -- Grok 4 Fast, Heavy, Code -- do not exist, and the documentation
// describes only one of the real models.
//
// Price is per million tokens, input / output, for a prompt under 200k. Above that it doubles.
export const MODELS = [{ id: "grok-build-0.1", name: "Grok Build", detail: "$1 / $2 per 1M · 256k" }];

// A chat may carry an id this list does not know -- every chat opened before Madde 72 does, and
// XAI_MODEL can be set to anything at all. It is shown as it is: a button saying nothing would be
// worse, and a display name for a model the menu no longer offers would imply it can still be
// picked.
export function modelName(id) {
  if (!id) return "Model";
  return MODELS.find((model) => model.id === id)?.name ?? id;
}
```

`modelName`'in gövdesi değişmiyor — yalnız üstündeki açıklama, çünkü o davranış artık istisna değil
kural: kullanıcının diskindeki her eski sohbet o yoldan geçiyor.

*Yeşile döner:* `models.test.js`'in ikisi, `ModelPicker.test.jsx`'in biri, `App.test.jsx`'in üçü.

### 3. `dist` derlenir

`npm run build --prefix queen-agent/frontend`, kaynakla **aynı commit'e**.

## Beklenen yeşil

Ön yüzde **513**. Arka uçta **2 failed, 443 passed** — ikisi defterin dalı.

**Düşmemesi gerekenler:**

| Ne | Neyi kanıtlıyor |
|---|---|
| `Menu.test.jsx` — `"Grok 4.6"` yazan ikisi | Menü bileşeni `MODELS`'ı görmüyor |
| `Composer.test.jsx` — `"Grok 4.5"` yazan biri | Yazma kutusu da görmüyor |
| `test_model_api.py` — ikisi | Sunucu varsayılanı enjekte ediliyor, `config`'ten okunmuyor |
| `models.test.js` — `modelName("grok-9000")` | Bilinmeyen id yolu duruyor |

Biri düşerse liste görmemesi gereken bir yere sızmış demektir, ve o zaman **kod düzelir, test
değil**.

## Bilerek yapılmayanlar

- **`ModelPicker.jsx` açılmıyor.** Seçici tek satırla duruyor — kullanıcının kendi kararı.
- **Diskteki kayıtlara dokunulmuyor.** `grok-4.3` taşıyan sohbet o modelle cevaplamaya devam
  ediyor; Grok Build'e almanın yolu menüyü açıp tek satıra basmak.
- **`stream_answer.py`, `routes.py`, `file_chat_store.py` açılmıyor.** Sunucu `MODELS`'ı bilmiyor.
- **`modelName`'in gövdesi değişmiyor.** Zaten doğru davranıyor.
