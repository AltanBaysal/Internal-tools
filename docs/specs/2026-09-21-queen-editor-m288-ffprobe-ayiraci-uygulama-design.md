# Madde 288 · `sound()`'un ffprobe ayıracı — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m288-ffprobe-ayiraci-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

**İki satır**, ve ikisi de `sound()`'un içinde:

- **Komut:** `-of csv=s=:p=0` → `-of csv=p=0`. Ayıraç yazılmıyor, csv kendi varsayılanını kullanıyor.
- **Okuma:** `said.partition(":")` → `said.partition(",")`. Cevabı ayıran şey ne ise, bölen de o.

**Yorum da düzeliyor.** `sound()`'un docstring'i bugün *"boş cevap bir cevaptır"* diyor ve bu
doğru kalıyor; yanına **ayıracın neden csv'nin kendisi olduğu** giriyor — çünkü koda bakan bir
sonraki göz, `size()`'ın `s=x` yazdığını görüp buraya da bir `s=` koymak isteyecek. Bu deponun
kuralı: yorum NEDEN'i söyler.

## Değişmeyen

- **`size()`.** `csv=s=x:p=0` çalışıyor, ve `848x480` o sorunun alışıldık cevabı.
- **m286'nın kuralı.** Parçalardan birinin sesi varsa hepsinin olmalı; sessizlik sesi olan
  parçanın hızına ve kanal düzenine uyuyor. Değişen yalnız o iki sayının hangi karakterden
  okunduğu.
- **Hata yolu.** Sıfırdan farklı çıkışta ffprobe'un kendi son satırı fırlatılıyor — uydurulmuş bir
  sebep değil.
- **`piece()`, `merge()`, `_with_sound()`, `_evened_out()`.** Hiçbiri bu maddeyi görmüyor.

## Bunun getirdiği

**Birleşik export Colab'da ilk adımında düşmüyor.** Ve bu maddenin asıl kazancı düzeltmenin kendisi
değil: bozuk bir ffprobe argümanı bundan sonra Colab'da değil **takımda** düşüyor, çünkü iki komut
da birebir okunuyor.

**Ölçülmeyen şey yine ölçülmedi:** düzeltilmiş komutun gerçek ffprobe'da ne yazdığı bu makinede
görülemiyor — burada ffmpeg yok. Görülen şey komutun ne olduğu, ve kullanıcının bir sonraki
export'u gerisini söyleyecek.

## Bu turda değişen

- `data/ffmpeg_video_exporter.py`: `sound()`'un komutu ve cevabı böldüğü karakter.
