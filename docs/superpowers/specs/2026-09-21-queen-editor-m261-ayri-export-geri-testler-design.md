# Madde 261 · Ayrı export'tan disclaimer kalkacak — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Geri aldığı madde:** [249'un uygulaması](2026-09-21-queen-editor-m249-disclaimer-uygulama-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Bugün ne oluyor

249'dan beri ayrı export'un **her parçası** disclaimer taşıyor: `piece()` bir `disclaimer` bayrağı
alıyor, `run_export` onu `mode != MERGED` ile veriyor, ve bayrak varken parça kopyalanmak yerine
bindirmeyle **yeniden kodlanıyor**.

İki bedeli çıktı, ve kullanıcı ikisini de geri istiyor:

- **Okunmayan bir şerit.** PNG `1902 × 98`, 480 genişlikte %80'e ölçeklenince satır başına ~10
  piksel kalıyor.
- **Kopyalamanın sonu.** Ayrı export artık her kareyi kodluyor, yani saniyeler değil dakikalar.

## Seçilen yol

**Bayrak tamamen kalkıyor.** `piece()`'in imzası 249'dan önceki hâline dönüyor — üç argüman — ve
`run_export` hiçbir şey geçmiyor. Bayrağı `False` ile bırakmak da mümkündü; bırakılmıyor, çünkü
kullanan kimse kalmıyor ve okuyan biri *"demek ki bir yerden `True` geliyor"* diye arar.

**Birleşik yolun hiçbir şeyi kalkmıyor:** `merge()`'in bindirmesi *(250)*, kodlayıcının karta
sorulması *(253, 257)*, `_stamp_for()` ve `assets/disclaimer.png`. Dördü de birleşik export'un işi,
ve 259 onları büyütecek.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Sessiz bir parça kopyalanıyor: `-i video -c copy target` | **yeşil** *(duran test; bayraksız komut değişmiyor)* |
| 2 | Sesli bir parça bugünkü ses yolunu kullanıyor, görüntü **kopya** | **yeşil** *(duran test)* |
| 3 | Ayrı export hiçbir parçada disclaimer istemiyor | **kırmızı** |
| 4 | `piece()` disclaimer diye bir şey **almıyor** — imza üç argüman | **kırmızı** |
| 5 | Birleşik export'un bindirmesi yerinde | **yeşil** *(250'nin testleri)* |

**Kalkan testler.** 249'un üç testi — `a_stamped_piece_carries_the_disclaimer_over_its_first_minute`,
`a_stamped_piece_with_a_sound_keeps_the_sound_and_the_disclaimer`,
`the_disclaimer_is_measured_from_the_video_it_goes_on` — ve 253 ile 257'nin parça üzerinden
kodlayıcıya bakan üç testi siliniyor, çünkü **anlattıkları davranış artık yok**. Kodlayıcının karta
sorulması silinmiyor; yalnız sorunun *parça üzerinden* sorulduğu testler gidiyor, ve yerine
birleştirme üzerinden soran testler zaten duruyor *(253'ün merge testi, 257'nin denemesi)*.

Silmek burada doğru olan: davranışı olmayan bir testi `skip` ile bırakmak, takımı yeşil gösterip
kaydı yalanlar.

**Kırmızı sayısı 24.** Beklenen iki değil, ve fazlası bir sürpriz değil: ikizlerin `piece`'i üç
argümana döndüğü an, üretim kodu hâlâ `disclaimer=` geçtiği için **export akışından geçen her test**
`TypeError` ile düşüyor — parçaları sayan, klasörü silen, durumu okuyan hepsi. Yirmi dördünün
tamamı bayrağın kaldırılmasıyla, tek bir yerden dönüyor. İmza bir sözleşme: ikizi değiştirmek, o
sözleşmeyi kullanan her testi aynı anda kırmızıya çeviriyor.

## Bu turda değişen

`backend/tests/test_export.py`:

- Üç bindirme testi ve parça üzerinden kodlayıcıya bakan üç test **siliniyor**.
- `a_separate_export_asks_for_the_disclaimer_on_every_piece` yerine
  `a_separate_export_copies_every_piece_untouched` *(3)*.
- `piece_takes_no_disclaimer` *(4)* — imzayı doğrudan çiviliyor.
- `FakeExporter.piece` disclaimer parametresini bırakıyor; `disclaimers` listesi kalkıyor.
- `test_photo_routes.py`'nin `RecordingExporter.piece`'i de üç argümana dönüyor.
- `STAMP` ve `NVENC` sabitleri kalıyor — birleştirme testleri onları kullanıyor.
