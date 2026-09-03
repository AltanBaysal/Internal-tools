# Madde 149 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [Tur 1 tasarımı](2026-09-03-queenagent-m149-ikinci-yol-testler-design.md)
**Kırmızı commit:** `8c02872` *(13 kırmızı — 10 Python, 3 JS; 685 + 584 yeşil)*

## Şekli

Beş dosya, ve hiçbiri ötekinin işini yapmıyor.

### `config.py` — tablo bir alan büyüyor

`OPENROUTER_API_KEY`, öteki iki anahtarın satırının aynısı. İki yeni satır
`https://openrouter.ai/api/v1` adresinde, ve ikisi de `extra` taşıyor.

`engine_for` dördüncü olarak `wiring.get("extra")` veriyor — doğrudan giden satırlarda `None`.
`get`, çünkü alan üç satırda yok ve olmaması bir eksiklik değil, o satırın söyleyecek bir şeyi
olmaması.

### `client.py` — `extra` gövdeye katılıyor

`__init__` bir `extra=None` alıyor, `opener`'ın önüne — bugünkü bütün çağrılar `opener`'ı adıyla
veriyor, yani sıra kimseyi bozmuyor.

`_request`'te **önce** `extra`, **sonra** istemcinin kendi alanları:

```python
payload = {**self._extra, "model": self._model, **body}
```

Yasak alan listesi tutulmuyor. Sıra kuralı liste tutmaktan üstün: liste, ileride eklenen her alan
için güncellenmesi gereken ikinci bir yer olurdu, ve güncellenmediği gün sessizce açık kalırdı.

`self._extra` boşken `{}` — `None` ile yayılamıyor. Yani dışarıda `None`, içeride `{}`; dönüşüm
`__init__`'te bir kez oluyor ve `_request` koşul taşımıyor.

### `main.py` — dördüncüyü aktarıyor

`extra=config.engine_for(model)[3]`. `engine_for` satır başına üç kez çağrılmış oluyor; bugün de iki
kez çağrılıyor ve fonksiyon saf — bir sözlük araması ve bir `globals()` okuması. Tek çağrıya
indirmek sözlük kurgusuna bir `for` gövdesi ya da bir yardımcı fonksiyon sokardı, ve bu dosyanın
okunurluğu maliyetten kıymetli.

### `models.js` — beş satır

Çiftler yan yana. Ad iki yolu ayıran şey, çünkü model ikisinde de aynı.

### Defter — üçüncü anahtar

Secrets okuması, `assert`'i, açılış cümlesi ve SERVE'ün `env`'i. Madde 146'nın gerekçesi aynen
geçerli: menü beş satır çiziyor, eksik anahtarla açılan bir koşu vaat ettiğini veremezdi.

## Bilerek kabul edilen

**`extra` bir tablo satırından geliyor, yani veriden.** Sıra kuralı `model` ile `messages`'ı
koruyor; `tools` **korumuyor**, çünkü o `_request`'te `body`'den sonra yazılıyor ve zaten üstte
kalıyor. Bir satır `stream` ya da `stream_options` yazabilir — `body`'den geldikleri için onlar da
üstte. Geriye kalan her alan gerçekten eklenebilir, ve bu alanın var olma sebebi tam olarak bu.

**Adres ile sabitleme ayrı iki bilgi ve tabloda iki kez yazılıyor.** OpenRouter satırı hem
`openrouter.ai` adresini hem `deepinfra` sabitlemesini taşıyor. Birleştirilebilirdi — *"adres
OpenRouter ise sabitle"* — ama o, adresin ne olduğunu okuyan ikinci bir yer demek olurdu;
`x-grok-conv-id` bugün tam olarak öyle çalışıyor ve orada gerekçesi var *(başlığın kendisi o
servisin)*. Burada gerekçe yok: hangi sağlayıcıya sabitleneceği tablonun kararı, adresinden
çıkarılacak bir şey değil.

## Değişmeyen

`stream_answer` ve yukarısı, `xai_engine.py`, `Message.model`, `ModelPicker.jsx`, `App.jsx`, damga.
Madde 148'in `_Calls`'ı ve `_spent`'in iki önbellek şekli olduğu gibi duruyor.

`DEFAULT_MODEL` = `grok-build-0.1`. Madde 146 öncesi yazılmış her mesaj ona çözülüyor.

## Doğrulama

Dört komut, sabit hâlleriyle. Beklenen: queen-agent'ın iki takımı da yeşil, **defterin `BRANCH`
kırmızısı hariç** — o kullanıcının Colab denemesi bitince kapanıyor ve bu turun işi değil.

`dist` aynı commit'te derleniyor: `models.js` değişiyor, ve defter derlemiyor.
