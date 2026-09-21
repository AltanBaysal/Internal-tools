# Madde 249 · Tekli export'ta disclaimer — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m249-disclaimer-testler-design.md)

## Kullanıcıdan gereken

**Disclaimer PNG'si, bu turda** — geldi, ve **kullanıcı 21 Eylül'de yeniden kesilmeyeceğine karar
verdi** *("abi dosya zaten group 5 png, o yani")*. Dosya aynı `1902 × 98`, ve 480 genişlikte satır
başına ~10 piksel bırakıyor: yazı alt ortada ince bir şerit olarak duruyor, okunmuyor. Aynı gün
konuşulan 4-5 satırlık, `960 × 300` versiyon geçerliliğini koruyor — ve onu beklemek gerekmiyor,
çünkü **resim koda girmiyor, yolla veriliyor**: yenisi geldiğinde tek dosya değişiyor ve hiçbir
satır değişmiyor.

**Yeri kullanıcının seçimi:** `queen-editor/assets/disclaimer.png` *(21 Eylül — "queen editor
altında asset diye klasör açıp koyabilirsin")*.

## Çivilenmiş olguların istediği kod

Beş dosya, hiçbirinde yeni bir katman yok.

**`backend/config.py` — `DISCLAIMER_PATH`.** Grafiklerle aynı kalıp, `_BACKEND_DIR`'ın üstünden
`assets/disclaimer.png`. Ortam değişkeni yok — grafikler gibi, bu da depoyla gelen bir dosya,
defterin seçeceği bir şey değil.

**`data/ffmpeg_video_exporter.py` — `piece()` bindirmeyi kuruyor.** Kurucu PNG'nin yolunu alıyor
*(`run` ve `ffmpeg` gibi enjekte, testler kendi yolunu veriyor)*. `piece()` bir `disclaimer` bayrağı
alıyor; bayrak yokken komut bugünkü kalıyor — kopyalama, ve export'un bugünkü hızı.

Bayrak varken tek ffmpeg çağrısı:

```
ffmpeg -y -i VIDEO -i PNG [-i SES] \
  -filter_complex [1:v]scale=<G>:-1[d];[0:v][d]overlay=(W-w)/2:H-h-<B>:enable='lt(t,60)'[v] \
  -map [v] [-map 2:a:0] -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
  [-c:a aac -shortest] TARGET
```

`<G>` videonun genişliğinin %80'i, `<B>` yüksekliğinin %4'ü — ikisi de `size()`'ın ffprobe'dan
aldığı ölçüden, yuvarlanarak. Ortalama ffmpeg'in kendi ifadesiyle *(`(W-w)/2`)*: ölçeklenmiş PNG'nin
genişliğini Python bilmiyor, ffmpeg biliyor. `enable`'ın tek tırnağı ffmpeg'in kendi kaçışı —
`lt(t,60)`'ın virgülü tırnaksız kalsa filtre zinciri orada ikiye bölünürdü.

Üç sayı modülün başında adlarıyla duruyor *(oran, oran, saniye)*; komutun içine gömülü sayı yok.

**`domain/usecases/run_export.py` — hangi modun istediği.** `exporter.piece(..., disclaimer=mode !=
MERGED)`. Kural domain'de, çünkü *"ayrı export'un parçaları export'un kendisidir"* bu dosyanın zaten
söylediği şey — `cutting` satırı aynı ayrımdan doğuyor.

**`backend/main.py` — wiring.** `FfmpegVideoExporter(disclaimer=config.DISCLAIMER_PATH)`.

**`queen-editor/assets/disclaimer.png` — dosyanın kendisi**, kullanıcının açtırdığı klasörde.

## Bunun getirdiği ve götürdüğü

**Götürdüğü hız, ve ölçülmedi.** Ayrı export artık her kareyi `libx264` ile yeniden kodluyor. Bir
kare ~5 saniye, 480 × 720; `veryfast` ile bunun bir CPU'da saniyeler sürmesi beklenir, ama **bu
depoda ölçülmüş bir sayı yok** ve buraya bir tahmin yazılmıyor. Kullanıcı koşunun sonunda test
ederken görecek; rahatsız ederse ayar `preset`'te, tek satırda.

**Getirdiği, 250'ye hazır bir zemin.** Birleşik modun parçaları temiz kopya kalıyor, yani 250
disclaimer'ı birleşmiş dosyanın kendi saatine — `concat` girdisinin üstüne, aynı tek çağrıda —
koyabilecek. Yol haritasının 250 satırında *"spec'e kalıyor"* denen risk böylece kapanıyor:
yeniden kodlanmış parçalarla kopyalananlar hiç yan yana gelmiyor.

## Bu turda değişen

- `backend/config.py`: `DISCLAIMER_PATH`.
- `backend/features/photo_generation/data/ffmpeg_video_exporter.py`: kurucuya PNG yolu, `piece()`'e
  bayrak ve bindirme, modül başına üç sabit.
- `backend/features/photo_generation/domain/usecases/run_export.py`: bayrağı geçen tek argüman.
- `backend/main.py`: bir satır wiring.
- `queen-editor/assets/disclaimer.png`: yeni dosya *(kullanıcıdan)*, yeni klasörde.
- `backend/tests/test_photo_routes.py`: `RecordingExporter.piece` de bayrağı alıyor. Test turunda
  görünmesi mümkün değildi — ikinci bir exporter ikizi, ve eski imzası yalnız üretim kodu yeni
  argümanı geçmeye başlayınca kırıldı.

Ön yüz ve `dist` bu maddede hiç değişmiyor.
