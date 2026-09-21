# Madde 253 · Kodlama GPU'ya geçecek — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Araştırma:** [export hızı](../research/2026-09-21-queen-editor-export-hizi.md), kaldıraç **K1**

## Kullanıcıdan gereken

**Hiçbir şey, ve bu bilerek böyle.** Kullanıcıdan istenen üç ölçüm gelmedi; madde onu beklemek
yerine **kodlayıcıyı varsaymıyor, ffmpeg'e soruyor**. Ölçüm geldiğinde söyleyeceği tek şey kazancın
ne kadar olduğu olacak — hangi kodlayıcının kullanıldığını ffmpeg'in kendi cevabı söylüyor, ve iki
durumda da doğru çalışıyor.

## Bugün ne oluyor

Kodlanan her şey `libx264 -preset veryfast -crf 18 -pix_fmt yuv420p` ile kodlanıyor — 249'da
`_ENCODE` olarak yazıldı, 250 de onu kullanıyor. Colab'ın kutusunda **2 vCPU** var ve **T4 export
boyunca boş duruyor**.

## Seçilen yol

**Kodlayıcı sorulur, varsayılmaz.** ffmpeg'e bir kez hangi kodlayıcıları taşıdığı sorulur
*(`-encoders`)*; çıktıda `h264_nvenc` varsa o kullanılır, yoksa bugünkü `libx264` kalır. Sebep:
Colab'ın ffmpeg'inin NVENC ile derlendiği **doğrulanmadı**, ve varsaymanın bedeli her export'un
*"Unknown encoder"* ile düşmesi olurdu — FOUNDATION 1, kullanıcının işi kutsaldır.

**Bir kez sorulur.** Cevap exporter'ın ömrü boyunca aynı, ve ayrı export 22 parça yazarken 22 süreç
daha açmanın hiçbir karşılığı yok.

**Kopyalayan hiç sormaz.** Bindirmesiz bir parça kopyalanıyor; kopyalamanın kodlayıcısı yok, o yüzden
o yolda soru da yok.

**NVENC'in ayarları x264'ün ayarları değil.** `-crf` yerine `-rc vbr -cq 23`, ve `-preset fast` —
eski ve yeni ffmpeg'lerin ikisinin de kabul ettiği ad *(yeni derlemelerin `p1`–`p7`'si Colab'ın
sürümünde olmayabilir)*. `-pix_fmt yuv420p` iki yolda da duruyor.

**Bindirmenin kendisi değişmiyor:** saati, ölçüsü, duruşu, 60 saniyesi. Değişen yalnız işi yapan
donanım.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | NVENC taşıyan bir ffmpeg'de bindirmeli parça `h264_nvenc -preset fast -rc vbr -cq 23` ile kodlanıyor | **kırmızı** |
| 2 | Birleştirme de aynı kodlayıcıyı kullanıyor | **kırmızı** |
| 3 | Kodlayıcı parça başına değil **bir kez** soruluyor | **kırmızı** |
| 4 | NVENC yoksa komut bugünkü `libx264` kalıyor | **yeşil** *(249 ve 250'nin testleri; NVENC'siz ffmpeg onların dünyası)* |
| 5 | Kopyalanan bir parça kodlayıcıyı hiç sormuyor | **yeşil** *(bugün kimse sormuyor; test bunun öyle kalmasını tutuyor)* |

4 için yeni test yazılmıyor: `a_stamped_piece_carries_the_disclaimer_over_its_first_minute`,
`a_stamped_piece_with_a_sound_keeps_the_sound_and_the_disclaimer` ve
`a_merged_export_joins_and_stamps_in_one_call` zaten `libx264`'lü komutu çiviliyor, ve ikizin
varsayılanı *"NVENC yok"* olduğu için üçü de yeni imzada aynı şeyi görmeye devam ediyor. Aynısını
tekrar yazmak onların kopyası olurdu.

## Bu turda değişen

`backend/tests/test_export.py`:

- `FakeRun` artık `-encoders` sorusuna cevap veriyor — `encoders` alanı, varsayılanı **boş**
  *(NVENC'siz bir makine)*.
- `NVENC` sabiti: beklenen kodlayıcı argümanları.
- `a_stamped_piece_is_encoded_on_the_gpu_when_ffmpeg_has_nvenc` *(1)*
- `a_merged_export_is_encoded_on_the_gpu_too` *(2)*
- `the_encoder_is_asked_of_ffmpeg_once_rather_than_per_piece` *(3)*
- `a_copied_piece_never_asks_which_encoder_there_is` *(5)*
