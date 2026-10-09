# Madde 257 · NVENC'in derlenmiş olması kullanılabilir olması değil — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Düzelttiği madde:** [253'ün uygulaması](2026-09-21-queen-editor-m253-gpu-kodlama-uygulama-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Bugün ne oluyor

`_encoder()` ffmpeg'e `-hide_banner -encoders` soruyor ve çıktıda `h264_nvenc` arıyor. O çıktı
**derleme zamanının** cevabı: ffmpeg'in NVENC desteğiyle kurulduğunu söylüyor, makinede kart
olduğunu söylemiyor.

Sonucu: `h264_nvenc`'i listeleyen ama kodlayamayan bir makinede *(kart yok, sürücü uyuşmuyor, NVENC
oturumu alınamıyor)* komut koşarken düşüyor, ve o anda **tüm export gidiyor** — yarım export
bırakılmadığı için klasör de siliniyor.

Defterin CONFIG hücresi kartsız oturumu zaten durduruyor, yani bu hâle bugün düşülmüyor. Madde o
korumaya güvenmek yerine **soruyu düzeltiyor**: koruma defterin, soru ise exporter'ın işi, ve kart
dışında da düşme sebepleri var.

## Seçilen yol

**Yetenek varsayılmaz, denenir.** ffmpeg'e hiçbir şey yazmayan minik bir kodlama yaptırılır:

```
ffmpeg -hide_banner -f lavfi -i nullsrc -t 0.1 -c:v h264_nvenc -f null -
```

`nullsrc` üretilmiş bir görüntü, `-t 0.1` onun onda bir saniyesi, `-f null -` de çıktıyı hiçbir yere
yazmıyor. Dönen kod sıfırsa bu makine NVENC'le **gerçekten** kodluyor; değilse CPU'ya düşülür.

Bu, `-encoders`'ın yerini alıyor — yanına eklenmiyor. İki soru sormanın anlamı yok: denemenin cevabı
listenin cevabını da içeriyor *(derlenmemiş bir ffmpeg denemeyi de geçemez)*.

Çağrı yine **bir kez** yapılıyor ve cevabı saklanıyor; kopyalayan yol yine hiç sormuyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Sorulan şey bir **deneme kodlaması**: `-f lavfi -i nullsrc -t 0.1 -c:v h264_nvenc -f null -` | **kırmızı** *(bugün `-encoders` soruluyor)* |
| 2 | Deneme dönerse bindirmeli parça `h264_nvenc` ile kodlanıyor | **kırmızı** |
| 3 | Deneme düşerse `libx264` kullanılıyor, **ve export düşmüyor** | **kırmızı** |
| 4 | Deneme parça başına değil bir kez yapılıyor | **kırmızı** |

Dördü de kırmızı, çünkü ikizin cevap verdiği soru değişiyor: bugünün ikizi `-encoders`'a cevap
veriyor, yarınınki denemeye.

**Kırmızı sayısı 11, ve bu beklenenden fazla değil — beklenenin ölçüsü yanlıştı.** Çağrıları süzen
yardımcı artık *"nullsrc"* arıyor; üretim kodu hâlâ `-encoders` sorduğu için o çağrı **yazma çağrısı
sayılıyor**, ve bindirmeli yolun her testi `ffmpeg_calls[0]`'da gerçek komut yerine o eski sondayı
görüyor. Yani 249 ile 250'nin yedi testi de bu turda kırmızıya düşüyor, ve hepsi tek satırla —
sondanın deneme kodlaması olmasıyla — geri dönüyor. Kalıcı kırmızı yok; düşen her test yeni sondayı
istiyor.

## Bu turda değişen

`backend/tests/test_export.py`:

- `FakeRun`'ın `encoders` alanı **`nvenc`** oluyor — deneme kodlamasının dönüp dönmediği, varsayılanı
  `False` *(NVENC'i kullanamayan bir makine, yani bugünün dünyası)*.
- `encoder_calls()` artık deneme çağrısını süzüyor.
- 253'ün dört testi yeni ikize göre yazılıyor; `HAS_NVENC` sabiti yerine `nvenc=True`.
- `the_gpu_is_tried_rather_than_looked_up_in_a_list` *(1)* yeni test.
- `an_unusable_gpu_leaves_the_export_running_on_the_cpu` *(3)* yeni test.
