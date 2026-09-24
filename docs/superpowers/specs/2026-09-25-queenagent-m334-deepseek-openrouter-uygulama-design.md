# Madde 334 · uygulama turu — DeepSeek istekleri şimdilik OpenRouter'dan, DeepSeek'in kendisine

**Kaynağı:** [v9 yol haritası](../roadmaps/2026-09-21-queen-agent-v9-roadmap.md), Madde 334, ve
[test turu](2026-09-24-queenagent-m334-deepseek-openrouter-testler-design.md) — 16 kırmızı,
`c8e9e587`.

---

## Ne yazılacak

### `backend/config.py`

- **`OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")`** — öteki ikisinin satırı.
- **`DEEPSEEK_API_KEY` yerinde kalıyor**, yorumu bugün doğru olanı söylüyor: hiçbir satır onu
  harcamıyor, dönüş ayrı bir madde, ve dönüş iki satırın `https://api.deepseek.com`'a geri
  dönmesi. Adres yorumda duruyor, çünkü satırlardan çıkınca kodda başka hiçbir yerde kalmıyor.
- **`_ONLY_DEEPSEEK = {"provider": {"order": ["deepseek"], "allow_fallbacks": False}}`** — yorumu
  **neden** bir sözleşme seçimi olduğunu söylüyor *(149'un yorumunun aynı gerekçesi, sağlayıcı
  DeepSeek)*, ve neden gövde alanı: OpenRouter onu orada okuyor.
- **İki DeepSeek satırı:**

  ```python
  "deepseek-v4-flash": {
      "base_url": "https://openrouter.ai/api/v1",
      "key": "OPENROUTER_API_KEY",
      "model": "deepseek/deepseek-v4.1-flash",
      "extra": _ONLY_DEEPSEEK,
  },
  ```

  `deepseek-v4-pro` aynısı. Yorum: id'ler DeepSeek'in kendi adları ve menüyle diskteki her mesaj
  onları taşıyor; `model` OpenRouter'a söylenen ad, iki satırda da V4.1 Flash çünkü DeepSeek'in
  API'si 14 Eylül'den beri ikisine de onunla cevap veriyordu; `extra` satırın her isteğinin gövdesine
  eklediği.
- **Grok satırı değişmiyor.** `model` ve `extra` onda **yok**: sağlayıcısı modeli id'siyle tanıyor ve
  gövdeye eklenecek bir şey yok. Yorumundaki *"the notebook's third secret"* sayıyı bırakıyor —
  defterin sırları dört oluyor.
- **`engine_for` beş değer veriyor:**

  ```python
  return (
      chosen,
      wiring["base_url"],
      globals()[wiring["key"]],
      wiring.get("model", chosen),
      wiring.get("extra"),
  )
  ```

  Son ikisinde `get`: söyleyecek şeyi olmayan satır bir şey eksik değil, söyleyecek şeyi yok. Grok
  için `[3]` id'nin kendisi, `[4]` `None`.

**Alan adı `model`**, çünkü gövdedeki `model` alanına dönüşüyor. `name` reddedildi: `models.js`'te
`name` ekranda okunan ad *(Queen Flash)*, ve aynı kelime iki dosyada iki şey olurdu.

### `backend/services/xai/client.py`

- `__init__(self, read_key, model, base_url, extra=None, opener=urllib.request.urlopen)`. `opener`'ın
  önüne: bütün çağrılar `opener`'ı adıyla veriyor, sıra kimseyi bozmuyor.
- `self._extra = extra or {}` — `None` yayılamaz; bir kez çevirmek her istekte sormaktan iyi.
- `_request`: `payload = {**self._extra, "model": self._model, **body}`. Önce satırın ekledikleri,
  sonra istemcinin kendi alanları — bir satır hangi modele gidildiğine ya da konuşmaya karışamaz.
  Yasak ad listesi değil sıra: liste ikinci bir güncel tutulacak yer olurdu.
- `_request` iki yolun ortak kurucusu, yani `write_once` ve `stream` ayrıca değişmiyor.
- İstemci `extra`'nın ne dediğini bilmiyor; yalnız taşıyor. Servis hiçbir özelliği bilmiyor
  *(CODE-STANDARD)*.

### `main.py`

```python
model: XaiClient(
    lambda wiring=config.engine_for(model): wiring[2],
    config.engine_for(model)[3],
    config.engine_for(model)[1],
    extra=config.engine_for(model)[4],
)
```

Motorun sözlüğü hâlâ uygulamanın id'siyle anahtarlanıyor — `XaiEngine` bir istemciyi mesajın taşıdığı
id ile buluyor; tele giden ad sağlayıcınınki. Yorum bunu bir cümleyle söylüyor.

### `queenagent.ipynb`

- **CONFIG:** `OPENROUTER_API_KEY`, öteki sırlar gibi `try/except` ile Secrets'tan okunuyor; yoksa
  `assert` duruyor ve Türkçe söylüyor: Secrets panelinden bu adla ekle, deftere erişimi aç,
  `openrouter.ai/keys` üzerinden alınır *(adres 149'un defter metninden)*. `print` satırı dört adı
  sayıyor.
- **CONFIG yorumları:** *"All three from Colab's Secrets store"* → dört. Anahtarların neden durduğunu
  söyleyen blok bugün doğru olanı söylüyor: her cevabı OpenRouter anahtarı harcıyor *(menünün iki
  modeli de, kareyi yazan da)*; xAI ve DeepSeek anahtarları dönüş yolları olarak isteniyor — biri
  202'den beri, öteki DeepSeek'e ödeme yapılana kadar. Bugünkü blok *"xAI is still spent -- it
  writes every frame's action"* diyor, ve 202'den beri doğru değil.
- **Serve:** çevreye `"OPENROUTER_API_KEY": OPENROUTER_API_KEY`. Yorum *"Three things... the two
  keys"* → dört şey, üç anahtar.
- **Kod dışında hiçbir şey değişmiyor:** hücre sırası, öteki `print`'ler, değerler.

### `frontend/src/features/workspace/models.js` — yalnız yorum

*"An id is what the provider is told the model is called -- client.py sends it as the model field"*
DeepSeek çifti için artık doğru değil. Yeni cümle: id, `config.py`'nin tablosunun anahtarı ve diskteki
her mesajın kaydettiği şey — yeniden adlandırmak o kayıtları sahipsiz bırakır; sağlayıcıya ne
söylendiği `config.py`'nin işi, ve 334'ten beri her zaman id değil. **Kod değişmiyor**; `dist`'i
koordinatör derliyor.

### `README.md`

- Yerel çalıştırmadaki export satırı `OPENROUTER_API_KEY` oluyor. `XAI_API_KEY` satırı **yerine**, ona
  ek olarak değil: menünün ulaştığı hiçbir satır xAI anahtarını harcamıyor, ve orada duran satır
  yerelde tek başına hiçbir cevap getirmezdi. Hangi modelin hangi anahtarı harcadığı `config.py`'de —
  README onu tekrarlamıyor, dosyayı gösteriyor.
- *"The key is read at startup"* → anahtarlar; *"that, the key and every other setting"* → anahtarlar.

## Ne değişmiyor

`XaiEngine`, `stream_answer` ve yukarısı, `_spent`, `x-grok-conv-id` kuralı *(`openrouter.ai`'de
`x.ai` geçmiyor)*, ön yüzün kodu, menünün id'leri, adları ve fiyatları, `DEFAULT_MODEL`,
`PROMPT_MODEL`, Grok satırı. Commit'lenmiş testlere dokunulmuyor.

## Yeşilin nasıl görüleceği

Dört sabit test satırı, birebir. 16 kırmızı yeşile dönüyor; öteki her test yeşil kalıyor. Ön yüzün
tek değişikliği `models.js`'te bir yorum — paket büyük olasılıkla bayt bayt aynı çıkar, ama `dist`'i
derleyip kaynakla aynı commit'e koymak koordinatörün.

## Kendi kontrolü

- **16'nın her biri koda düşüyor mu?** Anahtar → `OPENROUTER_API_KEY`; adres ve anahtar → iki satır;
  `[:2]` → `engine_for`'un ilk ikisi; `[3]` → `wiring.get("model", chosen)`; `[4]` →
  `wiring.get("extra")`; istemcinin üçü → `extra` parametresi ve `_request`'in sırası; bileşimin ikisi
  → `main.py`'nin `[3]` ve `[4]`'ü; defterin üçü → CONFIG'in okuması ve `assert`'ü, Serve'ün çevresi.
- **Başka bir testin beklentisi bozuluyor mu?** `engine_for`'u üç ada açan çağıran kalmadı *(yalnız
  test turunun `[:2]`'si ve `main.py`'nin indeksleri)*. `XaiClient(...)`'ın bütün çağrıları `opener`'ı
  adıyla veriyor. `test_the_notebook_no_longer_points_at_a_settings_screen` için defterde
  *"Settings"* kelimesi yazılmıyor; `test_no_api_key_is_ever_printed` için `print` satırı adları
  süslü parantez içinde değil düz metin olarak sayıyor.
