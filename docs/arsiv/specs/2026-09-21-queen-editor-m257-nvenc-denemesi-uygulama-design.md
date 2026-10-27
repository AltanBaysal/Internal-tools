# Madde 257 · NVENC'in derlenmiş olması kullanılabilir olması değil — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m257-nvenc-denemesi-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

`_encoder()`'ın tek sorusu değişiyor. `-encoders` listesini okumak yerine **deneme kodlaması**
yapılıyor:

```
ffmpeg -hide_banner -f lavfi -i nullsrc -t 0.1 -c:v h264_nvenc -f null -
```

Dönen kod sıfırsa `_GPU_ENCODE`, değilse `_CPU_ENCODE`. Önbellek, çağrı sayısı ve çağıranlar
değişmiyor; `piece()` ile `merge()` aynı yerden aynı cevabı alıyor.

Onbir kırmızının tamamı bu tek değişiklikle yeşile döndü — testlerin istediği şey tek bir şeydi.

## Neden liste yetmiyor

`-encoders` **derleme zamanının** cevabı. Üç hâl onu geçip kodlamada düşüyor: kart yok, sürücü
uyuşmuyor, kartın NVENC oturumları dolu. Üçünde de bugünkü kod GPU'yu seçer ve export ortasında
ffmpeg'in *"No capable devices found"*u ile kaybolur. Deneme bu üçünü de baştan ayırıyor, çünkü
sorduğu şey tam olarak *"bu makine bu kodlayıcıyla kodlayabiliyor mu"*.

**Defterin GPU kontrolü yerinde duruyor** ve bu maddenin yerine geçmiyor: o, kartsız bir oturumda
uygulamanın hiç açılmamasını sağlıyor; bu ise kart varken de düşebilecek üç hâli karşılıyor. İkisi
farklı sorular.

## Bedeli

Export başına bir ffmpeg süreci daha — onda bir saniyelik, diske hiçbir şey yazmayan bir kodlama.
Cevap saklandığı için parça başına değil, süreç ömrü boyunca bir kez.

## Bu turda değişen

- `backend/features/photo_generation/data/ffmpeg_video_exporter.py`: `_encoder()`'ın sorusu ve
  onun gerekçesini söyleyen docstring.
