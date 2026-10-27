# Madde 291 · Disclaimer tuvalin %80'i olacak — test turunun tasarımı

**Tarih:** 2026-09-21 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

**Alındı.** Oran kullanıcının kendi sayısı *(21 Eylül — "disclaimer sağdan soldan az boşluk ver,
ekranın %80'i olsun mesela")*, alt boşluk da onun kararı *("aşağıdan verilen boşluk iyi")*.

Bedeli söylendi ve kabul edildi: PNG `1902 × 98`, yani 1920 için çizilmiş; %80'de yazı da **%20
küçülüyor**, iki satır ~49 pikselden ~39 piksele iniyor. Kullanıcı *"evet bilerek istiyorum"* dedi.

## Bugünkü durum, koddan

`_stamp()` disclaimer'ı tuvalin **tam genişliğine** ölçekliyor — `[1:v]scale=1920:-1[d]`
*([ffmpeg_video_exporter.py:119](../../../queen-editor/backend/features/photo_generation/data/ffmpeg_video_exporter.py#L119))* —
ve `DISCLAIMER_WIDTH` oranı 259'da **silinmişti**: 1.0 ile çarpan bir oran, okuyana aramaya değer
bir şey varmış gibi görünüyordu.

**Karar gerçek videoyu görünce değişti.** 259'un sözü *"yatayda dolduracak şekilde"*ydi ve ekranda
denenmemişti; deneyince iki yanın fazla dolu olduğu görüldü.

## Kural

Disclaimer **tuval genişliğinin %80'i**: 1920'de **1536 piksel**, iki yanında 192'şer piksel
boşluk. Oran geri geliyor, ve bu kez 1.0 değil — yani gerçekten bir şey söylüyor.

**Yükseklik yine `-1`:** ffmpeg oranı koruyor, biz bir yükseklik yazmıyoruz.

## Çivilenen olgular

**1 · Disclaimer tuvalin %80'i.** Filtre zincirinde `[1:v]scale=1536:-1[d]`.

**2 · Tam genişlik gitti.** `scale=1920:-1` zincirde yok.

**3 · Alt boşluk aynı.** `H-h-43` — yüksekliğin %4'ü, kullanıcının beğendiği boşluk.

**4 · Ortalama aynı.** `overlay=(W-w)/2`, yani iki yandaki boşluk eşit; ffmpeg'in kendi hesabı,
bizim yazdığımız bir sayı değil.

**5 · Tuval değişmiyor.** `scale=1920:1080:force_original_aspect_ratio=decrease` + `pad` yerinde:
kırpma yok, iki yanı bant *(259)*.

## Ayarlanan testler

`STAMP` — testlerin beklediği filtre zincirinin tamamı — disclaimer satırını içeriyor, o yüzden
ona bakan testler bu maddeyle kırmızıya dönüyor. **Ayarlanıyor, silinmiyor:** soruları zincirin
başka parçaları hakkında.

`test_the_disclaimer_fills_the_canvas_width` ise **adını ve gerekçesini kaybediyor** — artık
doldurmuyor. Yerine iki yanında boşluk bırakan hâlini soran bir test geçiyor, ve eski gerekçe
*(259'un "dolduracak şekilde"si)* metinde durmuyor: bu deponun kuralı, bir yorum yalnız bugün
doğru olanı söyler.

## Kapsam dışı

**Ayrı export.** Orada disclaimer zaten yok *(261)*.

**PNG'nin kendisi.** Okunur bir tasarım [BACKLOG](../../../queen-editor/BACKLOG.md)'da duruyor;
bu madde yalnız bugünkü dosyanın ekranda kapladığı yeri değiştiriyor.
