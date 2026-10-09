# Madde 402 — Sonrakine bağlı karede geçiş yumuşar, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 3 · **Parça:** 402 · v8-3f · **Tur:** 2/2 — kırmızı testleri yeşile
çeviren kod. **Testler:** [m402 test turu](2026-10-01-queen-editor-m402-sonrakine-bagli-testler-design.md).

**Kullanıcıdan gereken — yok.** Kararlar test spec'inde; buradakiler kodun nasıl yazılacağı.

## Seçilen yol

Döngü videonun vardığı resmi yazardan önce bulur ve **her yazara** `end` olarak verir, üreticiye
verdiği gibi; bağlı videoda iki resmi göstermek ve bağlı metni eklemek H3 yazarının kararıdır.

Bırakılan iki yol:
- **Döngü `end`'i yalnız bağlı videoda verir** — hangi modun resme ihtiyaç duyduğu yazarın kuralı;
  döngüde ikinci kez yazılırsa ikisi ayrışır. Loop'ta aynı resmin ikinci kez gitmemesi de zaten
  yazarın işi.
- **Yazar resmi kendisi okur** — `data/`'daki yazarın deposu yok, ve aynı dosya Drive'dan iki kez
  inerdi.

## Parçalar

### 1. Port — `domain/ports.py`

`PromptWriter.write(prompts, mode, source=None, end=None, scene="")`. `end` üreticinin portundaki
`end`'in kendisi — videonun vardığı resim, `(ad, bayt)`; yoksa `None`. Docstring: H3'ün yazarı bağlı
videoda onu da gösterir (madde 402); ötekiler alır ve yok sayar.

### 2. Döngü — `domain/run_loop.py`

`ending = _end_for(current, store, slots, project, fid, under)` `under`'ın hemen altına, yazarın
sorusundan önceye taşınır; aynı değer hem yazara (`end=ending`) hem üreticiye gider — dosya bir kez
okunur. Try'ın içinde kalır: `MissingEndFrame` bugünkü gibi kareyi üç denemeden sonra kırmızıya
döndürür, ve artık yazar sorulmadan. `under`'ın ve `ending`'in üstündeki yorumlar şimdi doğru olanı
söyler.

### 3. Yazarlar — `data/xai_prompt_writer.py`

- `LINKED_RULE` — `tmp/queen-editor-prompts.md`'nin "Sonrakine bağlı kare (402 — H3'e eklenir)"
  bölümü, kelimesi kelimesine; dosyanın alışkanlığıyla üç tırnağın içinde baştan ve sondan birer satır
  sonu. `LOOP_RULE`'un altında; üstündeki yorum neden yalnız H3'e eklendiğini söyler: Picture 2'yi
  anıyor, ve WAN'ın yazarına resim gösterilmiyor.
- `H3VideoPromptWriter.write(prompts, mode, source=None, end=None, scene="")`: talimat
  `asked(H3_VIDEO_INSTRUCTION, mode)`, resimler `[source]`; mod bağlıysa talimata `LINKED_RULE`
  eklenir ve resimlere `end`. Loop'un `end`'i `source`'un kendisi, o yüzden yalnız bağlı mod ekler.
- `asked()` değişmez: iki motorun ortak kuralı. `VideoPromptWriter` ve `AudioPromptWriter` `end`'i
  alır, kullanmaz; docstring'leri bunu söyler.

## Bilinçli olarak yapılmayan

- DeepSeek istemcisi değişmez: `images` zaten sırasıyla birden çok resim taşıyor.
- `main.py` değişmez: yazar haritası aynı.
- H3 üreticisinin hizalama satırı değişmez.
- Bağlı modda `end` yoksa ayrı bir koruma yok: döngü o durumda `MissingEndFrame` atar, yazara hiç
  varılmaz.

## Bitti sayılır

Dört satır yeşil; `LINKED_RULE` `tmp/queen-editor-prompts.md`'dekiyle karakteri karakterine aynı.
