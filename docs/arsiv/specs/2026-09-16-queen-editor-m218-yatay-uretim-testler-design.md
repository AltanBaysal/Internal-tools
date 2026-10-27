# Madde 218 · Üretim yatay olacak — test turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kararlar ve nereden geldikleri

**Oranı grafiğin kendi notu belirledi.** Creator'ın desteklenen ölçüler tablosunda tek yatay satır
var — `1344 × 768 → 1536 × 864` — ve 1536/864 tam **16:9**. Bugünkü `1024 × 1536` de aynı tablonun
High-Res sütununda *(832 × 1216'nın karşılığı)*, yani ölçü zaten o listeden seçiliyor. Benim ilk
önerim olan 3:2 aynası *(1536 × 1024)* listede olmadığı için elendi.

**Video 848 × 480.** 16:9'un 480 yüksekliğinde tam karşılığı yok — 854 on altıya bölünmüyor. İki
aday vardı: `848 × 480` *(1,767)* ve `768 × 432` *(tam 16:9)*. Seçilen birincisi, çünkü WAN 2.2'nin
eğitildiği **480 yüksekliğini** koruyor; fotoğrafla arasındaki **%0,63** fark, video grafiğinin
`stretch` yeniden boyutlandırması altında görünmez. *(Kullanıcı bu ölçüyü bana bıraktı.)*

**Oran sabit değişiyor, ayar olmuyor.** Ayar demek aynı projede iki oran demek, ve dışa aktarma
bunu kaldırmıyor — aşağıya bak.

| | Bugün | Bundan sonra |
|---|---|---|
| Fotoğraf | 1024 × 1536 | **1536 × 864** |
| Video *(iki graf da)* | 480 × 720 | **848 × 480** |

## Ölçü koddan gelmiyor, üç grafiğin içinde

| Dosya | Node | Bugün |
|---|---|---|
| [workflow_api.json](../../../queen-editor/workflow_api.json) | `1` *Width* → `easy int`, `11` *Height*; ikisi de `EmptyLatentImage`'a gidiyor | 1024 × 1536 |
| [workflow_video_api.json](../../../queen-editor/workflow_video_api.json) | `208` `mxSlider2D`, başlık *"VIDEO Width x Height"* — `Xi`/`Xf`, `Yi`/`Yf` | 480 × 720 |
| [workflow_video_first_last_api.json](../../../queen-editor/workflow_video_first_last_api.json) | `328`, aynısı | 480 × 720 |

Backend'de tek bir genişlik/yükseklik sabiti yok. Ön yüzde de yok: galeri karesi `1/1` ve
`objectFit: cover`, oynatıcı zaten `16/9` — yani ön yüz yön değiştirmesinden etkilenmiyor,
oynatıcıdaki siyah bantlar **ortadan kalkıyor**.

## Asıl tehlike: dışa aktarma hiç yeniden kodlamıyor

[`FfmpegVideoExporter.merge`](../../../queen-editor/backend/features/photo_generation/data/ffmpeg_video_exporter.py)
parçaları `concat` + `-c copy` ile birleştiriyor. Bu bilinçli — *"the graph already produced the
size, codec and frame rate the export wants"* — ama o cümlenin dayandığı varsayım **her parçanın
aynı ölçüde olması**. Oran değişince bu varsayım kırılıyor: eski dikey videolarla yeni yatay
videolar aynı projede birleşirse çıkan dosya bozulur, **ve bugün hiçbir yerde bir uyarı yoktur.**

Maddenin kabul cümlesi zaten bunu istiyordu. Çözüm birleştirmeyi yeniden kodlamak değil *(dakikalar
ve kalite, hem de doğru olanı hangi oran olduğunu kimse söyleyemez)*: **birleştirme, parçaların
ölçüsünü sorup uyuşmadıklarında ne bulduğunu söyleyerek duracak.** `separate` modu etkilenmiyor —
orada parçalar birleşmiyor, her dosya kendi başına duruyor.

Ölçüyü soran şey `ffprobe`: ffmpeg'le birlikte kuruluyor *(defterin `apt-get install ... ffmpeg`
satırı)*, ve dosyanın kendi başlığını okuyor.

## Çivilenecek olgular

### Grafikler

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Foto grafiği **1536 × 864** üretiyor | **kırmızı** |
| 2 | Standart video grafiği **848 × 480** üretiyor | **kırmızı** |
| 3 | İlk-son kare grafiği de aynı ölçüyü taşıyor | **kırmızı** |
| 4 | Fotoğrafın oranı ile videonun oranı **%1 içinde** uyuşuyor | yeşil *(bugün ikisi de 2:3)*, ve öyle kalmalı |
| 5 | Üçü de yatay — genişlik yükseklikten büyük | **kırmızı** |

Dördüncüsü asıl kural, ve sayılardan uzun yaşayacak olan: video grafiği kareyi hedefe
`keep_proportion: "stretch"` ile çekiyor, yani iki oran ayrışırsa görüntü **ezilir** ve hiçbir hata
çıkmaz. Beşincisi maddenin kendisi; ikisi birden olmadan "yatay" ölçülemez.

### Dışa aktarma

| # | Ne diyor | Bugün |
|---|---|---|
| 6 | Birleştirmeden önce her parçanın ölçüsü soruluyor | **kırmızı** |
| 7 | Hepsi aynıysa `concat` + `-c copy` bugünkü hâliyle koşuyor | yeşil, ve öyle kalmalı |
| 8 | Ölçüler ayrışıyorsa birleştirme **durur**, ve hangi parçanın hangi ölçüde olduğunu söyler | **kırmızı** |
| 9 | Ölçü okunamazsa hata `ffprobe`'un kendi cümlesini taşır | **kırmızı** |
| 10 | Durduğunda hiçbir şey birleştirilmemiştir | **kırmızı** |

Sekizincisi bir cümle değil bir **liste** basıyor: "farklı ölçüler var" demek kullanıcıya hangi
kareyi sileceğini söylemez. Dokuzuncusu deponun kendi kuralı — *"never invent a cause in an error
message"*.

## Bu turda değişen

Yalnız testler:

- `queen-editor/backend/tests/test_workflow_asset.py` — 1–5
- `queen-editor/backend/tests/test_export.py` — 6–10

Grafiklerin sayıları ve `merge`'in kendisi uygulama turunun işi.
