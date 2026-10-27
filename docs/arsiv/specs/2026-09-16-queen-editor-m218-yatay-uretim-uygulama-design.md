# Madde 218 · Üretim yatay olacak — uygulama turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Test turu:**
[tasarım](2026-09-16-queen-editor-m218-yatay-uretim-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Testler `64058f74`'te kırmızı: 7 tanesi, hepsi queen-editor'ün Python takımında.

## Grafiklerdeki altı sayı

| Dosya | Node | → |
|---|---|---|
| `workflow_api.json` | `1` *Width* | **1536** |
| `workflow_api.json` | `11` *Height* | **864** |
| `workflow_video_api.json` | `208` `Xi`, `Xf` | **848** |
| `workflow_video_api.json` | `208` `Yi`, `Yf` | **480** |
| `workflow_video_first_last_api.json` | `328` `Xi`, `Xf` | **848** |
| `workflow_video_first_last_api.json` | `328` `Yi`, `Yf` | **480** |

Başka hiçbir şeye dokunulmuyor. `mxSlider2D` her ölçüyü çift taşıyor *(`Xi` sürgünün değeri, `Xf`
gösterdiği)*; ikisi birden yazılıyor, çünkü hangisinin okunduğu node'un kendi işi ve ayrışmış bir
çift sessizce yanlış ölçü verir.

## Birleştirme ölçü soruyor

[`FfmpegVideoExporter`](../../../queen-editor/backend/features/photo_generation/data/ffmpeg_video_exporter.py)
bir `ffprobe` yolu daha alıyor *(`ffmpeg` gibi, varsayılanı `"ffprobe"`)* ve `merge` listeyi
yazmadan önce her parçaya soruyor:

```
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 <dosya>
```

Cevap `848x480` gibi tek satır. Üç sonuç:

- **Hepsi aynı** → bugünkü `concat` + `-c copy`, hiç değişmeden.
- **Ayrışıyor** → `RuntimeError`, ve mesaj parçaları **tek tek** sayıyor: hangi dosya hangi ölçüde.
  Liste, çünkü *"parçalar farklı ölçüde"* kullanıcıya hangi kareyi yeniden üreteceğini söylemez.
- **Okunamıyor** → `ffprobe`'un kendi son satırı, `piece`'in bugün ffmpeg için yaptığının aynısı.

Sıra önemli: yoklama **liste dosyası yazılmadan** önce koşuyor, yani durduğunda diskte ne
`pieces.txt` kalıyor ne yarım bir mp4. Dışarıda da temiz duruyor — `run_export` zaten hatayı
yakalayıp klasörü siliyor, ve `ExportRunner` cümleyi olduğu gibi ekrana veriyor.

`separate` modu etkilenmiyor: orada parçalar birleşmiyor.

## Neden yeniden kodlamıyoruz

Karışık ölçüyü `-vf scale` ile çözmek mümkün ama yanlış: hangi oranın doğru olduğunu kimse
söyleyemez *(dikey olanı mı yataya, yatayı mı dikeye?)*, ve her iki durumda da kullanıcının
görmediği bir kırpma ya da bant eklenir. Üstelik dışa aktarma dakikalar sürmeye başlar. Doğru olan,
karışıklığı **söylemek**.

## Bu turda değişmeyen

Ön yüz. Galeri karesi `1/1` + `objectFit: cover`, oynatıcı `16/9` — yön değişiminden etkilenmiyor,
üstelik oynatıcıdaki siyah bantlar kendiliğinden gidiyor. `dist` de bu yüzden yeniden derlenmiyor.
