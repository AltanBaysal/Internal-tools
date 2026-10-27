# Madde 288 · `sound()`'un ffprobe ayıracı — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

**Hiçbir şey.** Gereken tek şey zaten geldi: kullanıcının Colab'da aldığı hata metni.

## Teşhis, ve nereye kadar doğrulandı

Kullanıcının gördüğü *(21 Eylül, Colab)*:

> Export başarısız — `[csv @ 0x...] Failed to parse option string 's=:p=0' provided to writer context`

**Sebep koddan okundu, tahmin yok.** `sound()` ffprobe'a `-of csv=s=:p=0` veriyor
*([ffmpeg_video_exporter.py:150](../../../queen-editor/backend/features/photo_generation/data/ffmpeg_video_exporter.py#L150))*.
ffprobe yazıcının seçenek dizesini **`:` ile** `anahtar=değer` çiftlerine bölüyor, yani `s=:p=0`
dizesi `s=` ve `p=0` oluyor: `s=`'nin değeri boş kalıyor ve yazıcı dizeyi reddediyor. **Hata
ayıracın kendisini ayıracın sınırlayıcısı seçmekti** — `:` hem istediğimiz alan ayıracı, hem de
seçenek dizesinin kendi sınırlayıcısı.

**İkizi neden sağlam:** `size()` aynı kalıbı `csv=s=x:p=0` ile kullanıyor, ve `x` bir sınırlayıcı
değil *(satır 131)*. İki satır aynı gün, aynı elden çıktı; biri çalıştı, öbürü çıkmaz sokağa girdi.

**Etkisi tam, ve tek yönlü:** `sound()` sıfırdan farklı çıkışta `RuntimeError` fırlatıyor, ve
`merge()` parçaları birleştirmeden **önce** herkese sesini soruyor — yani **birleşik export daha
ilk adımda düşüyor**. Tekli export etkilenmiyor: orada `sound()` hiç çağrılmıyor *(madde 261 ayrı
export'u saf kopyaya döndürdü)*.

**Doğrulanamayan tek şey:** bu makinede ffmpeg yok, o yüzden düzeltilmiş komutun ffprobe'da
koştuğu burada gösterilemez. Gösterilebilen şey komutun **ne olduğu**, ve bu maddenin tamamı o.

## Maddenin asıl dersi: ikiz komutu cevaplıyor, denetlemiyor

Bozuk satır **takımdan geçti**, ve nasıl geçtiği bu turun şeklini belirliyor. `FakeRun` bir ffprobe
çağrısını görünce `"a:0"` var mı diye bakıp hazır bir cevap dönüyor
*([test_export.py:539](../../../queen-editor/backend/tests/test_export.py#L539))* — komutun
**geçerli olup olmadığına** bakmıyor, çünkü bakamaz: o ffprobe değil.

Ve hiçbir test komutun kendisini okumuyordu. `sound_calls()` yalnız *"soruldu mu"* diye süzüyor,
`size_calls()` da öyle. Yani bozuk bir ffmpeg/ffprobe argümanı, bu ikizin **yapısı gereği**
göremeyeceği şey.

**Görülebilir hâle gelmesinin tek yolu komutu birebir çivilemek.** İkizi komut doğrulayan bir şeye
çevirmek — argümanları ayrıştırıp ffprobe'un kurallarını uygulamak — ffprobe'un bir kopyasını
yazmak olurdu: bedeli gerçek, ve yakaladığı şey tek bir `assert`'ün yakaladığından fazla değil
*(FOUNDATION 3)*.

## Karar: ayıraç `csv`'nin kendi varsayılanı

`-of csv=p=0`. `s=` hiç yazılmıyor, ve csv varsayılan olarak **virgülle** ayırıyor — yani cevap
`48000,stereo` gibi geliyor, `sound()` da virgülden bölüyor.

**Neden bu, `s=|` gibi başka bir sınırlayıcı-olmayan karakter değil:** yazılmayan bir seçenek
yanlış yazılamaz. Bu maddenin sebebi fazladan bir seçenekti; onu düzeltmek yerine **kaldırmak**,
aynı hatanın bir daha girebileceği yeri de kaldırıyor.

**`size()`'ın ayıracına dokunulmuyor.** `s=x` çalışıyor, ve `848x480` ffprobe'un o soruya verdiği
alışıldık cevap — ölçüyü okuyan gözün beklediği biçim.

## Çivilenen olgular

**1 · `sound()`'un komutu birebir okunuyor.** Tek test, tam argüman listesi:
`ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate,channel_layout -of csv=p=0 <dosya>`.
Süzgeçten geçmiş bir parça değil, listenin kendisi — çünkü bu maddeyi doğuran şey tam olarak
listenin bir parçasıydı.

**2 · İkiz `size()`'ın komutu da birebir okunuyor, ve bu test doğuştan yeşil.** Bekçi: iki satır
aynı kalıptan çıktı, ve kalıbın kendisi kırıldı. `size()` bugün doğru, ve bu test onu doğru
tutuyor. *(m286'nın doğuştan yeşil iki testiyle aynı gerekçe: bedava kalan bir kuralın bekçisi.)*

**3 · İkizin cevabı yeni ayıracı konuşuyor.** `FakeRun`'ın `sounds` sözlüğü `"48000,stereo"` gibi
değerler veriyor — ffprobe'un düzeltilmiş komuta gerçekten yazacağı şey. Bugünkü kod cevabı
**iki nokta**dan böldüğü için `rate` bütün dizeyi yutuyor ve sessizlik `anullsrc=r=48000,stereo:cl=`
diye yazılmaya kalkıyor: sessizlik testleri bunu görüp düşüyor.

**4 · Sessizliğin ölçüsü yine sesi olan parçadan geliyor.** m286'nın kuralı değişmiyor; değişen
yalnız o ölçünün hangi ayıraçla okunduğu.

## Kırmızı beklentisi: üç kırmızı, bir doğuştan yeşil

| Test | Bugün |
|---|---|
| `sound()`'un komutu *(olgu 1)* | **kırmızı** — kod `csv=s=:p=0` diyor |
| Sessiz parçaya sessizlik yazılıyor *(olgu 3)* | **kırmızı** — `48000,stereo` iki noktadan bölünemiyor |
| Sessizlik sesi olanın ölçüsüne uyuyor *(olgu 3, 4)* | **kırmızı** — aynı sebep |
| `size()`'ın komutu *(olgu 2)* | **yeşil** — bekçi, ve bilerek |

**Hepsi sesli** ve **hiçbiri sesli** setlerin testleri yeşil kalıyor: ilkinde okunan ölçü hiç
kullanılmıyor, ikincisinde hiç okunmuyor.

## Kapsam dışı, ve bilerek

**`ffmpeg_audio.py`'nin ffprobe çağrısı.** O `-of default=noprint_wrappers=1:nokey=1` kullanıyor,
ve `default` yazıcısında `:` sınırlayıcı değil de seçenek ayracı olarak doğru yerde duruyor —
belirti yok, ve dokunmak sebebi olmayan bir değişiklik olurdu *(FOUNDATION 3)*.

**Komutu doğrulayan bir ikiz.** Yukarıda: ffprobe'un kopyasını yazmak.
