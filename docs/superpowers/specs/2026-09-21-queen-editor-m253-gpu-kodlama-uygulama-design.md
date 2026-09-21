# Madde 253 · Kodlama GPU'ya geçecek — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m253-gpu-kodlama-testler-design.md) ·
**Araştırma:** [export hızı](../research/2026-09-21-queen-editor-export-hizi.md), **K1**

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

Tek dosya: `data/ffmpeg_video_exporter.py`.

**`_ENCODE` ikiye ayrılıyor** — `_GPU_ENCODE` ve `_CPU_ENCODE`. GPU tarafı
`h264_nvenc -preset fast -rc vbr -cq 23`: NVENC `-crf` almıyor, ve `p1`–`p7` seviyelerini Colab'ın
ffmpeg'i tanımayabilir. CPU tarafı bugünkünün aynısı.

**`_encoder()` bir kez soruyor.** `ffmpeg -hide_banner -encoders` çıktısında `h264_nvenc` varsa GPU,
yoksa CPU. Cevap örnekte saklanıyor; ayrı export 22 parça yazarken cevabı değişmeyecek bir soruyu 22
kez sormanın karşılığı yok.

**Soramamak export'u düşürmüyor.** Çağrı sıfırdan farklı dönerse makine *"NVENC'siz"* sayılıyor,
yani kod 253'ten önceki yerinde kalıyor. Sebep FOUNDATION 1: bir varsayım yüzünden bütün bir
export'u kaybetmek, yavaş bir export'tan kötüdür.

**Kopyalayan yol hiç sormuyor.** Soru `_encoder()` çağrıldığında oluyor, ve onu yalnız bindirmeli
parça ile birleştirme çağırıyor.

## Bunun değiştirmediği şeyler

Bindirmenin saati, ölçüsü, duruşu ve 60 saniyesi; birleştirmenin tek geçiş olması; parçaların temiz
kopya kalması; ölçü uyuşmazlığının birleştirmeyi durdurması. Değişen yalnız **işi yapan donanım**.

## Hâlâ ölçülmedi

Kazancın ne olduğu. NVENC'in bu ölçüde gerçek zamanın kat kat üstünde çalışması *beklenir*, ama
buraya bir sayı yazılmıyor — araştırmanın 3. bölümündeki iki satır o sayıyı verecek. Bu maddenin
söylediği şey daha küçük ve kesin: **kart varsa iş karta gidiyor.**

## Bu turda değişen

- `backend/features/photo_generation/data/ffmpeg_video_exporter.py`: iki kodlama sabiti,
  `_encoder()`, ve onu kullanan iki çağrı *(`piece`, `merge`)*. Modül başlığı kartı anıyor.
