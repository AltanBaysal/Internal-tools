# Madde 146 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [Tur 1 tasarımı](2026-09-02-queenagent-m146-model-secimi-testler-design.md) ·
[v6 yol haritası](../plans/2026-09-01-v6-roadmap.md), Madde 146
**Dal:** `feat/v6` · **Kırmızı commit:** `769e2e7` *(38 kırmızı, 1218 yeşil)*

Bu tur yeni bir davranış tarif etmiyor — kırmızı commit'in tarif ettiğini yazıyor. Burada karara
bağlanan tek şey **kodun şekli**.

## Katman katman

### `config.py` — id'nin anlamı

`XAI_MODEL` gidiyor, yerine üçlü tablo ve bir çözücü geliyor:

```python
MODELS = {
    "grok-build-0.1":    {"base_url": "https://api.x.ai/v1",     "key": "XAI_API_KEY"},
    "deepseek-v4-flash": {"base_url": "https://api.deepseek.com", "key": "DEEPSEEK_API_KEY"},
    "deepseek-v4-pro":   {"base_url": "https://api.deepseek.com", "key": "DEEPSEEK_API_KEY"},
}
DEFAULT_MODEL = "grok-build-0.1"
```

`engine_for(model_id)` → `(model_id, base_url, api_key)`; tanınmayan ve boş id varsayılana düşer.
`skills.py`'nin `instruction_for`'u ile aynı sözleşme, aynı sebeple.

**Anahtar adı tabloda, değeri değil.** Satır `"XAI_API_KEY"` yazıyor, `os.environ`'dan okumayı
`engine_for` yapıyor — böylece tablo bir eşleme olarak kalıyor ve sır taşımıyor.

### `main.py` — üç istemci, bir motor

Bileşim kökü `MODELS` üzerinde dönüp her id için bir `XaiClient` kuruyor ve haritayı motora
veriyor. Anahtar hâlâ bir fonksiyon olarak geçiyor — nereden geldiği bu dosyanın kararı, ve
istemci o karar değişince değişmeyecek şekilde yazılmıştı.

### `xai_engine.py` — hangi taşıyıcı konuşacak

`XaiEngine(clients, default)`. `stream(..., model="")` haritadan seçiyor, bulamazsa varsayılan.
Rol çevirisi olduğu gibi kalıyor — motorun kazandığı tek iş bu seçim.

### `client.py` — iki sağlayıcının iki farkı

**`_spent()` iki şekli de tanıyor.** Bugünkü `prompt_tokens_details.cached_tokens` duruyor,
yanına `prompt_cache_hit_tokens` geliyor. Hangisi varsa o okunuyor; ikisi de yoksa sıfır.

**Sohbet başlığı adrese bakıyor.** `x-grok-conv-id` yalnız xAI'nin adresine gidiyor, ve bunu
söyleyen şey `base_url`. Bir bayrak eklenmedi çünkü bayrak ikinci bir doğruluk kaynağı olurdu:
adres zaten hangi servise konuşulduğunu söylüyor, ve başlık o servisin kendi başlığı.

### `chat.py` ve `file_chat_store.py` — kaydı

`Message.model: str = ""`, `skill`'in yanında ve aynı gerekçe yorumuyla. Diske yazılması da
skill'in kuralı: **boşsa alan hiç yazılmıyor**, böylece bugünkü kayıtlar bir göç istemiyor.

**Sohbetin kökündeki `model` okunmamaya devam ediyor.** Madde 82 onu kaldırdı; bu madde onu geri
getirmiyor. İki alan aynı adı taşıyor, farklı yerlerde duruyor, ve `test_the_two_model_fields_are_
not_the_same_field` ikisinin karışmadığını çiviliyor.

### `routes.py` ve `stream_answer.py` — yolu

Uçta `model=payload.get("model", "")`, `skill`'in yanında; cevapta `"model": message.model`.
Kullanım durumunda `_current_model(chat)` — `_current_skill`'in birebir aynısı, en yeni **kullanıcı**
mesajından geriye doğru. Turun bütün turlarında aynı model konuşuyor: seçim ilk turdan önce
okunuyor ve hiçbir tur onu değiştirmiyor.

### Ön yüz

**`models.js`** — `skills.js`'in aynası: `MODELS`, `DEFAULT_MODEL`, `modelName(id)`. Boş id
varsayılanın adını veriyor.

**`ModelPicker.jsx`**, `ModelLabel.jsx`'in yerine. `SkillPicker`'ın şekli, iki farkla: seçili satıra
basmak temizlemiyor *(dönülecek boş hâl yok)*, ve düğüm sıcak ton almıyor *(`picker--on` bir
seçimin varlığını işaret ediyor, model her zaman var)*.

**`App.jsx`** — `pickerOpen` üçüncü değeri alıyor: `"model"`. Karşılıklı dışlama ve Escape sırası
bedava geliyor, çünkü zaten tek değer. Seçim `draftModel` / `lastModel` olarak App'te duruyor,
`draftSkill` / `lastMode` ile aynı raftan.

**`useChat.js`** — `send(text, skill, mode, model)`, gövdeye `model` ekleniyor.

## Defter

`DEEPSEEK_API_KEY` Secrets'tan okunuyor, `assert` ile şart koşuluyor, `SERVE` hücresinde env'e
giriyor. Üçü de `XAI_API_KEY`'in yanında ve aynı biçimde.

**Giriş hücresi de değişiyor:** açılış metni tek anahtardan söz ediyor, artık iki tane var.

## Belgeler

**[FOUNDATION](../../../queen-agent/FOUNDATION.md) Decision 6** bugün *"xAI Grok is the engine"*
diyor ve gerekçesi *"the vendor behind them should be replaceable without touching either"*.
Vaat tutuldu; cümle artık iki sağlayıcıyı anlatacak şekilde yazılıyor. **Gerekçe değişmiyor** — o
cümle bu maddenin sebebi.

**Yol haritası Madde 146** iki yerinden düzeltiliyor: *"defter seçtirir"* ve *"ekran değişmiyor"*.
Ve **Turlar** satırı ekleniyor.

## `dist`

Ön yüz değişiyor, yani `npm run build --prefix queen-agent/frontend` ve `dist` **aynı commit'te**
gidiyor *(FOUNDATION Decision 3)*. Defter klonluyor ve derlemiyor; bir commit geç kalan paket
kaynağın söylediği hakkında yalan.

## Kapsam dışı

Tur 1'in listesi aynen geçerli: `services/xai/` adlandırması, modelin mesaj başına çizilmesi, 200k
eşiğinin ölçülmesi, sohbet düzeyinde model. Buna bir tane ekleniyor: **`XAI_MODEL` çevre
değişkeni**. Yerini `DEFAULT_MODEL` alıyor ve ezilebilir olmaktan çıkıyor — üç modelden birini
seçmenin yolu artık menü, ve iki yol bir soruya iki cevap demek.
