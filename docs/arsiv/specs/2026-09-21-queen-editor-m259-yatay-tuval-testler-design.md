# Madde 259 · Birleşik export yatay tuvale geçiyor — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

**Hiçbir şey.** Tuval bu maddede **açıkça yazılıyor** — `1920 × 1080`, kullanıcının kararı
*("yatay olsun çünkü yatay olarak biz çıktı alıyoruz", "1080 otomatik olsun")* — ve sığdırma
kaynağın kendi ölçüsünden hesaplanıyor. Yani bugün çıkan dosyanın dikey mi yatay mı olduğu
sorusunun cevabı bu maddeyi değiştirmiyor: iki durumda da aynı çerçeve çıkıyor. Ölçüm de
beklenmiyor.

## Bugün ne var

`merge()` tuvalini **kurmuyor, devralıyor:** her parçanın ölçüsünü `ffprobe`'a soruyor, hepsi aynı
ölçüdeyse ilkinin ölçüsünü alıyor, ve bindirmeyi o sayıdan hesaplıyor —
`_stamp_for(width, height)`. WAN'da parçalar `480 × 720`, yani bugün çıkan birleşik dosya
**dikey**, ve disclaimer o genişliğin %80'ine ölçekleniyor: `scale=384:-1`. Kullanıcının verdiği PNG
`1902 × 98`, yani 384 pikselde iki satır yazı **okunmuyor** — 249'un ayrı export'tan kalkmasının
sebebi de buydu *(261)*.

## Çivilenen olgular

Hepsi `merge()`'in tek ffmpeg çağrısının üzerinden okunuyor: testler komutu okuyor, bu makinede
ffmpeg yok *(mevcut `FakeRun` düzeni)*.

**1 · Birleşik dosya yatay bir tuvalde çıkıyor.** Filtre zinciri birleşmiş görüntüyü
`1920 × 1080`'e ölçekliyor ve artan yeri **bantla** dolduruyor:
`scale=1920:1080:force_original_aspect_ratio=decrease` ardından
`pad=1920:1080:(ow-iw)/2:(oh-ih)/2`.

**2 · Kırpma yok, sığdırma var.** `force_original_aspect_ratio=decrease` kaynağın oranını
koruyarak tuvale **sığan** en büyük ölçüyü seçiyor; `pad` ortalıyor. `480 × 720` bir kaynak
`720 × 1080` oluyor ve iki yanında 600 piksel bant kalıyor — kullanıcı bunu bilerek kabul etti.
Kırpan hiçbir filtre *(`crop`, `increase`)* zincirde yok.

**3 · Disclaimer tuvalin tam genişliğini kaplıyor.** `scale=1920:-1` — %80 oranı **kalkıyor**.
Kullanıcının sözü iki parçalı: *"disclaimer'ı da ona göre büyüt, asıl videodan büyük olabilir"* ve
*"yatayda dolduracak şekilde"*. PNG `1902 × 98` olduğu için 1920'de neredeyse hiç ölçeklenmiyor:
iki satır yazı ~99 piksel yükseklikte, ve ilk kez okunuyor.

**4 · Ölçü artık parçalardan gelmiyor.** Aynı proje dikey `480 × 720` parçalarla da yatay
`848 × 480` parçalarla da **birebir aynı** filtre zincirini veriyor. Bu olgu maddenin kendisi:
tuval devralınan bir sayı değil, yazılmış bir karar.

**5 · Alt kenar payı tuvalden ölçülüyor.** Yüksekliğin %4'ü, artık 1080'in %4'ü: `H-h-43`.
Kural oranını koruyor *(dibe yapışan yazı oynatıcı çubuğunun altında kalıyor)*, ölçtüğü şey
değişiyor.

**6 · Saat değişmiyor.** `enable='lt(t,60)'` yerinde: bindirme yine birleşmiş videonun ilk 60
saniyesinde *(250)*.

**7 · Kodlayıcı değişmiyor.** Karta sorulan soru ve dönen argümanlar aynı *(253, 257)*; tuval
kodlamayı gerektiren şeyi değiştirmiyor — bindirme onu zaten gerektiriyordu.

**8 · Ayrı export'a dokunulmuyor.** Parçalar yine `-c copy`, yine kaynağın kendi ölçüsünde, yine
dikey *(261)*. Tuval yalnız birleştirmenin işi.

**9 · Farklı ölçüler birleştirmeyi yine durduruyor** — ve **sebebi değişiyor.** Bugünkü cümle
*"ikisini birden sığdırmak da kırpmak ya da bant koymak olurdu"* diyor; bu maddeyle bant koymak
tam olarak yaptığımız şey oluyor, yani cümle yanlışa düşüyor. Duran gerçek sebep: **`concat`
parçaları olduğu gibi okuyor, ölçü değiştirmiyor** — iki farklı ölçüyü tek akış olarak okuyamaz,
ve okumadan da filtreye bir şey vermez. Kural aynı yerde kalıyor, gerekçesi doğruya dönüyor
*(CLAUDE.md — "bir hata mesajında sebep icat edilmez")*.

## Düşen test

`test_the_merged_disclaimer_is_measured_from_the_pieces_it_joins` **silinecek, atlanmayacak.**
Adı bu maddeyle kalkan kuralı söylüyor — bindirme parçaların ölçüsünden hesaplanıyordu — ve yerine
**4. olgunun** testi geliyor: ölçü parçalardan gelmiyor. Kalkan bir kuralın testi borç değil,
yanlış kayıttır *(261'in kararı)*.

## Beklenen kırmızı

Tam çağrıyı karşılaştıran iki test *(`..._joins_and_stamps_in_one_call`,
`..._is_encoded_on_the_gpu_too`)* yeni `STAMP`'e düşüyor, ve üç yeni test *(olgu 1-2, 3, 4)* daha.
**Beş civarı**, ve sayı spec'ten değil takımdan okunacak: bu koşuda üç kez tahminin üstüne çıktı.

## Değişmeyen

Parça başına `ffprobe` *(9. olgu onu tutuyor)*, `concat` liste dosyası ve silinmesi, sesin
`-map 0:a?` ile kopyalanması, `piece()`, `_encoder()`, ve `assets/disclaimer.png`.
