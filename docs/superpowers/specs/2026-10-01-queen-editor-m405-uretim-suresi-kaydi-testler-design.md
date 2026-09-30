# Madde 405 — Her katmanın üretim süresi kaydedilir, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 5 · **Parça:** 405 · v8-2a · **Tur:** 1/2 — yalnız testler, kırmızı
commit'lenir.

**Kullanıcıdan gereken — yok.** Madde `ALIGNED`, kararlar yol haritasının *v8-2 — Üretim süresi*
bölümünde: fotoğrafın, videonun ve sesin her birinin üretim süresi kaydedilir; **yalnız üretimin
kendisi**, modelin o katmanda çalıştığı süre — sırada bekleme sayılmaz *(kullanıcı kararı, 28 Eylül)*;
**eski kareler süresiz kalır** *(kullanıcı — "eski kareler gösterilmesin sıkıntı yok")*. Süreyi ekranda
göstermek, ve katman üretilirken canlı ilerleyen sayaç, 408 · v8-2b'nin işi: bu parça yalnız kaydeder
ve kartta okunur kılar.

## Bugün ne oluyor

Hiçbir katmanın süresi kaydedilmiyor. Döngü *(`domain/run_loop.py`, `make_job`)* yalnız bir log satırı
için ölçüyor: `started = clock()` turun başında, kaynağın Drive'dan okunmasından önce; `rendered =
clock()` üretimden sonra; satır `⏱ <dosya> · render X sn · drive Y sn`. Sayı hiçbir yere yazılmıyor,
ve `render` diye anılan sayıya kaynağın Drive'dan okunması da giriyor. 403'ten beri döngü bazı turlarda
üretmiyor, prompt yazıyor; yazılan prompt kayda kendi satırı olarak giriyor *(`status: "written"`)*.

## Kurallar

1. **Süre, üretilen katmanın kendi satırında durur**: `photos.jsonl`'daki üretilen satıra
   `"renderSeconds"` alanı — saniye, onda bire yuvarlanmış sayı *(`46.3`)*. Log satırının saniyeleri
   de onda bir; ekran `m:ss` gösterecek ve bundan inceye ihtiyacı yok. Kaydın satırı "bu katman burada"
   demek, ve süre o katmanın başına gelenlerden biri: dördüncü bir dosya ikinci bir okuma yeri olurdu.
2. **Yalnız modelin çalıştığı süre sayılır**: saat üreticinin çağrısından hemen önce ve hemen sonra
   okunur. Sayılmayan:
   - **Sırada bekleme** — önündeki işlerin üretimi, yazılan prompt'lar, döngünün boşta beklediği her an.
   - **Prompt'un yazılması** — 403'ten beri o kendi turu; yazan model katmanı üreten model değil.
   - **Katmanın kaynağının ve referans havuzunun Drive'dan okunması** — model henüz çalışmıyor.
   - **Dosyanın Drive'a yazılması** — log satırı onu zaten ayrı sayıyor (`drive Y sn`).

   Log satırının `render` sayısı artık kaydedilenle aynı: ikisi aynı iki okumadan.
3. **Yeniden denenen katmanın süresi, onu üreten denemenin süresi.** Başarısız bir deneme katmanı
   üretmedi; üç denemeyi toplamak bir fotoğrafın ne kadar sürdüğünü değil, kaç kez düştüğünü ölçerdi —
   kullanıcı süreye kartları karşılaştırmak için bakacak *(v8-4: A100 ve T4, önce ve sonra)*.
4. **Kaydın okuyucusu süreyi katmanın hücresine taşır**: `slots()` hücresinde `renderSeconds`, yalnız
   satır onu taşıyorsa — `mode` ve `endsOn` gibi.
5. **Kart her katmanın süresini söyler**: `GET /api/projects/<p>/frames`'in her kartında
   `"renderSeconds": {katman: saniye}` — `modes` ve `endsOn` ile aynı biçim, yalnız süresi olan
   katmanlar. 408 açık sekmenin katmanını buradan okur.
6. **Süresiz olan süresiz kalır, hiçbir şey geriye doldurulmaz**: bu parçadan önce üretilmiş katman,
   kırmızı katman *(son satırı `failed`)*, silinmiş ya da yeniden sıraya konmuş katman — haritada yok.
   Yokluk "süre yok" okunur.
7. **Kopya kare taşır**: kopya kare kaynağının dosyasını tutar *(madde 102)*, ve `copy_frame` o dosyanın
   modunu ve vardığı resmi zaten taşıyor — "bir dosya, onu tutan iki kare". Süre de aynı dosyanın
   süresi; taşınmazsa ikizin kartı süresiz, kaynağınki süreli okunurdu.
8. **Videodan çekilen resmin süresi yok**: fotoğrafı olmayan kareye videonun ilk karesi resim olur
   *(madde 296)*; o resmi hiçbir model üretmedi, satırı süre taşımaz. Bugün de satır elle kuruluyor ve
   yalnız belirli alanları taşıyor — test yazılmaz, uygulama o satıra dokunmaz.

## Yazılacak testler

Saat testlerde sahte: `Clock` yalnız biri "zaman geçti" deyince ilerler — üretici, Drive'ın okuması,
yazar kendi saniyelerini ekler, ve test o saniyelerin kimin olduğunu adıyla söyler. Hiçbir test gerçek
bir saniye beklemez.

### `test_photo_record.py` — kayıt

1. **Süresini söyleyen satır onu hücreye taşıyor** — `renderSeconds: 46.3` taşıyan video satırı →
   `slots()["0_a"]["video"]["renderSeconds"] == 46.3`.

### `test_photo_usecases.py` — döngü neyi sayıyor

`FakeRecord.slots()` gerçeğinin katladığı gibi `renderSeconds`'ı taşır.

2. **Üretilen katman modelin çalıştığı süreyi taşıyor** — üretici 46.34 sn sürüyor → fotoğrafın satırı
   `renderSeconds == 46.3`.
3. **Sırada bekleme katmanın süresine girmiyor** — iki fotoğraf, biri 30, öteki 50 sn → `[30.0, 50.0]`;
   ikincisi birincinin üretimini beklemiş olsa da.
4. **Katmanın kaynağını okumak süresine girmiyor** — videonun fotoğrafını Drive'dan okumak 5 sn, video
   40 sn → videonun satırı `40.0`.
5. **Prompt'u yazmak katmanın süresine girmiyor** — prompt'suz video; yazar 20 sn, video 40 sn →
   videonun satırı `40.0`.
6. **Yeniden denenen katman onu üreten denemenin süresini taşıyor** — ilk iki deneme düşüyor, her deneme
   10 sn → satır `10.0`.
7. **Kart her katmanının süresini söylüyor** — fotoğraf 46.3, video 212.0 →
   `renderSeconds == {"photo": 46.3, "video": 212.0}`.
8. **Süresi kaydedilmeden üretilmiş kare süresiz** — satırlarında süre yok → `renderSeconds == {}`.
9. **Kırmızı katmanın süresi yok** — fotoğraf 46.3; video önce 212.0 ile üretilmiş, sonra yeniden
   üretilirken kırmızı → `{"photo": 46.3}`.
10. **İkiz kaynağının sürelerini taşıyor** — kaynağın videosu 212.0 → `copy_frames` → ikizin video
    hücresinde `renderSeconds == 212.0`.

**Değişen test:** `test_each_produced_photo_gets_a_record_row` satırları birebir karşılaştırıyor ve
`start_batch` gerçek saatle koşuyor: süre alanı karşılaştırmanın dışında tutulur ve sayı olduğu
ayrıca söylenir. Öteki alanlar bugünkü gibi birebir.

**Bekçiler — değişmeden yeşil kalıyor:** log satırının iki testi
*(`test_the_render_and_the_writes_are_measured_apart`, `test_every_produced_frame_gets_its_own_line` —
saatin okunma sırası başla → üretildi → yazıldı olarak kalıyor)*; 403'ün yazma testleri; üretilen
satırın mod, `endsOn`, tohum testleri; 296'nın ilk kare testleri; `test_producer_contract.py`.

### `test_photo_routes.py` — uç

11. **Listelenen kart katmanlarının süresini taşıyor** — kayda `renderSeconds: 46.3` taşıyan fotoğraf
    satırı → `GET /api/projects/düğün/frames`'in kartında `renderSeconds == {"photo": 46.3}`.

### Frontend

Değişmez: süreyi 408 gösterir.

## Bitti sayılır

Dört test satırı koşulur. `queen-editor` pytest'inde 1–7 ve 9–11 kırmızı, doğru sebeple: kayıt hücreye
süre taşımıyor, döngü satıra süre yazmıyor, kart süre söylemiyor. 8 de kırmızı (`KeyError`: kartta alan
yok). Değişen satır testi de kırmızı (`KeyError`: satırda alan yok). `queen-agent`'ın iki satırı ve `queen-editor` vitest'i yeşil.
