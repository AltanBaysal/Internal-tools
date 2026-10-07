# Madde 291 · Disclaimer tuvalin %80'i olacak — uygulama turunun tasarımı

**Tarih:** 2026-09-21 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m291-disclaimer-genisligi-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey; oran ve alt boşluk test turunda karara bağlandı.

## Çivilenmiş olguların istediği kod

**Bir sabit geri geliyor:**

```
DISCLAIMER_WIDTH = 0.8   # of the canvas width
```

ve `_stamp()`'teki `scale={MERGED_WIDTH}:-1` yerine
`scale={round(MERGED_WIDTH * DISCLAIMER_WIDTH)}:-1` geçiyor.

**Sabit neden geri geliyor:** 259 onu 1.0 olduğu için sildi — bir şey söylemeyen bir çarpan. 0.8
bir karar, ve kararın adı olur. Hesap kodda: tuval bir gün değişirse disclaimer onunla birlikte
değişir, elle bir sayı güncellenmez.

**Yorum da düzeliyor.** Bugün *"genişliğin tamamını kaplıyor, o yüzden geriye adlandırılacak bir
oran kalmıyor"* diyor; artık kalıyor, ve sebebi kullanıcının gerçek bir export'u görmesi.

## Değişmeyen

- **Tuval** *(259)*, **alt boşluk** *(%4)*, **ortalama** *(`(W-w)/2`)*, **süre** *(60 saniye)*.
- **Ayrı export** *(261: disclaimer yok)*.
- **PNG'nin kendisi.**

## Bunun getirdiği

Birleşik videoda disclaimer'ın iki yanında 192'şer piksel boşluk kalıyor. **Yazı da %20
küçülüyor** — söylendi, kabul edildi, ve okunur bir tasarım geldiğinde tek dosya değişecek.

## Bu turda değişen

- `data/ffmpeg_video_exporter.py`: `DISCLAIMER_WIDTH` ve `_stamp()`'in disclaimer satırı.
