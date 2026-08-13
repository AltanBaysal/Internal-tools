# Queen Editor v8 · Görev 3 — Defterin ve README'nin adı bugünü anlatsın

**Tarih:** 2026-08-13 · **Yol haritası:** [v8](../plans/2026-08-13-queen-editor-v8-roadmap.md) · Görev 3
**Önkoşul:** [Görev 2](2026-08-13-queen-editor-v8-gorev-2-defterden-ses-kalksin-design.md) — aynı
metinlere dokunuyor.

## Problem

Defterin başlığı *"Queen Editor — Tek foto (Bölüm 4)"*. İkisi de yanlış: uygulama tek foto değil üç
katman üretiyor (foto → video → ses), diziyi export ediyor, üreticilerini kendi kuruyor. "Bölüm 4"
ise sekiz yol haritası önceki bir sayım.

README aynı eskimeyi taşıyor: *"two-screen web UI"*, *"one photo per prompt"*, *"Part 1…4"*, ve
Görev 2'den sonra artık yanlış olan bir cümle — defterin "ses kütüphanesini kurduğu".

Bunlar hata değil, **eskimiş doğru**lar; tehlikesi de o: defteri ilk kez açan kişi başlığa inanır.

## Karar

**Defterin başlığı: "Queen Editor — Colab kurulumu".** Kullanıcının seçimi. Defterin işini söylüyor
— kurar ve sunucuyu açar; üretim uygulamanın içinde. Bölüm numarası yok, çünkü numaranın doğru
kalması için her yol haritasında güncellenmesi gerekiyordu ve kalmadı.

**README bugünü anlatır.** Kapanmış yol haritalarının sırası zaten `docs/superpowers/plans/`
altında duruyor; README onu tekrarlamak yerine uygulamanın ne olduğunu söyler.

## Ne değişiyor

| Yer | Bugün | Sonra |
|---|---|---|
| Defter başlığı | "Tek foto (Bölüm 4)" | "Colab kurulumu" |
| Defter giriş paragrafı | akışta MMAudio adımı yok ama "tek foto" dili var | defterin işi: kur, sun, link bas |
| README girişi | "two-screen web UI… one photo per prompt" | proje → kareler → üç katman → export |
| README "Built in cumulative parts" | Part 1…4 sayımı | yol haritalarına tek işaret |
| README §3 | "installs ComfyUI, its custom nodes and the sound library" | ses kütüphanesi çıkar (Görev 2) |
| README §2 | iki secret | üçüncüsü de yazılır: video için `XAI_API_KEY` |

`XAI_API_KEY` bu görevin kapsamına giriyor çünkü aynı eskimenin parçası: defter onu istiyor,
README'de yok, ve README'yi doğru diye okuyan biri videonun neden prompt yazamadığını anlamıyor.

## Test

Yok. Değişen şey metin, ve bir başlığın doğru olup olmadığını test değil okuyan anlar. Görev 1 ve
2'nin testleri koşuyor olacak; defter bozulursa `test_the_notebook_installs_no_producer_engine`
zaten okunabilir bir JSON bekliyor.
