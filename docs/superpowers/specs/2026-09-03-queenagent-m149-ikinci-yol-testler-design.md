# Madde 149 · Tur 1 (test) — Tasarım

**Kaynak:** [v6 yol haritası](../plans/2026-09-01-v6-roadmap.md), Madde 149
**Dal:** `feat/v6` · **Bu tur yalnız test yazar.**

## Problem

Seçici üç satır çiziyor ve hepsi tek yoldan gidiyor: model id'si hangi sağlayıcıya ait ise oraya.
Aynı ağırlığın başka bir sağlayıcıda çalışan hâli bugün seçilemiyor — tablo satırı yalnız
`{base_url, key}` taşıyor, ve OpenRouter'a gitmek isteğin **gövdesine** bir alan koymayı
gerektiriyor.

Bu bir konfor eksiği değil, bir ölçüm eksiği: DeepSeek'in senaryo yazmayı reddetmesinin sağlayıcıdan
mı ağırlıklardan mı geldiği, aynı modeli iki yoldan koşmadan bilinemiyor.

## Şekli

Üç dosyada değişiklik, ve üçü de birbirine bağlı.

**`config.MODELS` satırı üçüncü bir alan kazanıyor: `extra`.** Bu modelin isteğine eklenecek gövde
alanları. Sağlayıcıdan bağımsız bir ad, çünkü tablo üç sağlayıcıya birden hizmet ediyor;
OpenRouter'ın sabitlemesi onun bir örneği.

**`engine_for` dördüncü bir şey döndürüyor.** Bugün `(model, base_url, key)`; yarın
`(model, base_url, key, extra)`. Bileşim kökünün tabloyu kendisi okuması alternatifi reddedildi:
config'in yorumu *"engine_for is the one place"* diyor, ve ikinci bir yol o cümleyi bozardı.

**`XaiClient` bir `extra` alıyor** ve gövdeye katıyor. `opener`'ın önüne, adlandırılmış parametre
olarak — bugünkü bütün çağrılar `opener`'ı adıyla veriyor, yani sıra kimseyi bozmuyor.

## Yol haritasının bıraktığı iki karar

**Satırların sırası: eşleşen çiftler yan yana.** Grok, sonra Flash ve onun Infra hâli, sonra Pro ve
onun Infra hâli. Bu iki satırın var olma sebebi aynı isteği arka arkaya koşmak, ve sağlayıcıya göre
gruplamak karşılaştırmayı bir tıktan bir kaydırmaya çevirirdi.

**`extra`'nın boş hâli: alan satırda hiç yok.** Boş sözlük değil — beş satırın üçünde hiçbir şey
söylemeyen bir alan olurdu. `engine_for` o satırlar için `None` veriyor, `XaiClient`'ın varsayılanı
da `None`. Testler yokluğu *"doğru değil"* diye soruyor, yani `None` ile `{}` arasındaki farkı
uygulama turuna bırakmıyor, ikisini de kabul ediyor: iddia edilen şey **başka bir modelin
sabitlemesini taşımadığı**.

## Kırmızıya dönecek iddialar

### `config.py`

1. **Beş model, ve ikisi OpenRouter'a çözülüyor.** `deepseek/deepseek-v4-flash-0731` ile
   `deepseek/deepseek-v4-pro-0813`, `https://openrouter.ai/api/v1` adresinde.
2. **İkisi de `OPENROUTER_API_KEY` harcıyor.** Öteki üçü bugünkü anahtarlarında kalıyor.
3. **`OPENROUTER_API_KEY` çevreden geliyor**, ve yoksa boş — öteki iki anahtarın kuralı.
4. **OpenRouter satırları DeepInfra'ya sabitlenmiş.** `extra`, tam olarak
   `{"provider": {"order": ["deepinfra"], "allow_fallbacks": False}}`. **Sabitlemenin kendisi
   çivileniyor, süs olduğu için değil:** `allow_fallbacks` düşerse istek Together AI'a düşebilir ve
   o sağlayıcının sözleşmesi bu işi açıkça yasaklıyor. Yani bu iddia bir sözleşme iddiası.
5. **Doğrudan giden üç satırın `extra`'sı yok.**
6. **`engine_for` dördüncü olarak `extra`'yı veriyor**, ve tanınmayan bir id yine varsayılana
   düşüyor — dördüncü alanıyla birlikte.

### `client.py`

7. **`extra` isteğin gövdesine giriyor.** Verilen alanlar gönderilen JSON'da duruyor.
8. **İstemcinin kendi alanları üstte.** `extra` içine `model` ya da `messages` konulursa gövdedeki
   gerçek değer kazanıyor. Elle düzenlenmiş bir tablo satırı hangi modele gidildiğini ele
   geçiremesin.
9. **`extra` yokken gövde bugünkünün aynısı.** Fazladan tek anahtar yok — Grok ve doğrudan DeepSeek
   yolları bu maddede hiç değişmiyor.
10. **`extra` akışa da giriyor**, yalnız `complete`'e değil. Asıl kullanım akış.

### `main.py`

11. **Bileşim kökü her istemciye kendi `extra`'sını veriyor.** Bugünkü iki iddia — anahtar
    config'ten gelir, kök çevreyi kendisi okumaz — yeşil kalıyor.

### `models.js`

12. **Beş satır, ve sırası eşleşen çiftleri okunur kılıyor.**
13. **Her satırın adı ve fiyatı var**, ve iki yolu ayıran şey ad.
14. **Yeni id'ler kendi adlarıyla okunuyor**, `modelName` üzerinden.

## Yeşil kalması gerekenler

- **Bütün `test_xai_client.py`** — özellikle jeton sayıları, kesme, `x-grok-conv-id`'nin adrese
  bağlı olması, ve Madde 148'in parça birleştiricisi.
- **Bütün `test_stream_answer.py`** — bu madde o dosyaya dokunmuyor.
- **`test_config.py`'nin `DEFAULT_MODEL` iddiası.** `grok-build-0.1` kalıyor: o sabit Madde 146
  öncesi yazılmış her mesajın çözüldüğü yer, ve değiştirmek eski kayıtları geriye dönük olarak
  başka bir modelin cevabı gibi gösterirdi.
- **`test_composition.py`'nin ikisi de.**

## Bilerek kapsam dışı

- **Reddin gerçekten kalkıp kalkmadığı.** Test bunu söyleyemez — sağlayıcıya gerçek bir istek
  gerekir. Maddenin ölçüsü kullanıcının kendi karşılaştırması.
- **`stream_answer` ve yukarısı.** Tek satır değişmiyor; değişmek zorunda kalırsa düzeltme yanlış
  katmandadır.
- **Defterin kendisi.** Üçüncü anahtar uygulama turunda, `test_notebook.py` ile birlikte.
- **`DEFAULT_MODEL`'in hangisi olacağı.** Karşılaştırmadan sonra, kendi maddesinde.
- **`services/xai/` adının yalan olması.** 146'da kayda geçti, orada duruyor.
