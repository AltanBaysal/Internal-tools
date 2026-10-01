# Madde 405 — Her katmanın üretim süresi kaydedilir, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 5 · **Parça:** 405 · v8-2a · **Tur:** 2/2 — kırmızı testleri yeşile
çeviren kod. **Testler:** [m405 test turu](2026-10-01-queen-editor-m405-uretim-suresi-kaydi-testler-design.md).

**Kullanıcıdan gereken — yok.** Kararlar test spec'inde; buradakiler kodun nasıl yazılacağı.

## Seçilen yol

Döngü zaten log satırı için ölçüyor; ölçümün başı üreticinin çağrısının hemen önüne taşınır, ve aynı
sayı üretilen satıra `renderSeconds` olarak yazılır. Kayıt onu hücreye, galeri karta taşır.

Bırakılan yollar:
- **Ölçümü turun başında bırakmak** — kaynağın ve havuzun Drive'dan okunması süreye girerdi; Colab'da
  Drive'ın okuması saniyeler sürebilir ve v8-4'ün ölçümüne gürültü katar. Modelin çalıştığı süre değil.
- **Duvar saatiyle (`now()`) başlangıç ve bitiş yazmak** — iki alan ve bir çıkarma, ve duvar saati geri
  alınabilir. `clock` monotonik ve testlerde zaten sahte.
- **Üç denemenin toplamı** — test spec'inin 3. kuralı.
- **Dördüncü bir dosya** — süre üretilen katmanın başına gelenlerden biri, ve satır zaten "bu katman
  burada" demek.

## Parçalar

### 1. Döngü — `domain/run_loop.py`

- `started = clock()` turun başından kalkar; üretim kolunda, `producer.generate(...)`'ten hemen önce
  okunur. Yazma kolu saati hiç okumaz. `rendered = clock()` yerinde kalır.
- Üretilen satıra `"renderSeconds": round(rendered - started, 1)`.
- Log satırı aynı iki okumayı kullanır; yorumu ve `make_job`'un `log` paragrafı süre satırını da anar.
- Videodan çekilen resmin satırı değişmez: süre yok.

### 2. Kayıt — `data/photo_record.py`

`slots()` hücreye `renderSeconds`'ı taşır, yalnız satır bir sayı taşıyorsa — `mode` ve `endsOn` gibi.
Docstring'i anar. Port'un (`domain/ports.py`) `slots` docstring'i de.

### 3. Galeri — `domain/usecases/list_frames.py`

Karta `"renderSeconds": _per_layer(cells, "renderSeconds")`. `_per_layer`'ın docstring'i üç kullanıcıyı
anar. Kayıttan okunan bir kartın `base`'i üretilen satırın kendisi, ve satırın tek sayılık
`renderSeconds`'ı `**base` ile karta düşüyordu: açık anahtar arkadan geldiği için harita onu ezer.

### 4. Kopya — `domain/copy_frame.py`

`CARRIED`'a `("renderSeconds", "renderSeconds")`; yorumu süreyi de anar.

## Bilinçli olarak yapılmayan

- Frontend değişmez: süreyi 408 gösterir. Dist kurulmaz.
- Durum raporuna (`runner.report`) üretimin başladığı an eklenmez: 408'in canlı sayacının işi.
- Eski satırlara dokunulmaz.

## Bitti sayılır

Dört satır yeşil.
