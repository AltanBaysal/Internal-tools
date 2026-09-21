# Madde 282 · Birleşmiş dosya yerel diskte bitecek — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Bugün ne var

235 parçaları Drive'dan kaldırıp makinenin kendi diskine aldı, **ama çıktıyı Drive'da bıraktı:**
`run_export` birleştirmeye hedef olarak Drive'ın export klasörünü veriyor, yani **ffmpeg kodladığı
akışı FUSE mount'una parça parça yazıyor**.

**Dayanak ölçüm değil belge:** Drive'ın FUSE mount'una akış yazmak Colab'da bilinen bir yavaşlık,
ve bilinen çözümü yerel diske yazıp sonunda kopyalamak
*([colabtools #1096](https://github.com/googlecolab/colabtools/issues/1096))*. Ağustos'ta ölçülen
soğuk hız **3,34 MB/s** *([export hızı araştırması](../research/2026-09-21-queen-editor-export-hizi.md))*,
ve 259'dan sonra dosya `1920 × 1080`. **Kazanç ölçülmedi**, ve buraya sayı yazılmıyor.

## Katman kararı

**Drive'ı bilen tek yer store**, ve kopyalama onun işi *(CODE-STANDARD: `data/` dosya şemasını
bilen tek katman)*. `run_export` yalnız sırayı kuruyor: birleştir, sonra kopyala. Exporter Drive
diye bir şey bilmiyor ve bilmeyecek — ona verilen hedef bir yol.

## Çivilenen olgular

**1 · Birleştirmenin hedefi parçaların yanında.** `run_export` exporter'a `/tmp`'deki yolu veriyor,
Drive'ın export klasörünü değil.

**2 · İş bitince dosya Drive'a kopyalanıyor**, projenin adıyla: `<proje>.mp4`.

**3 · Sıra bu:** kopyalama birleştirme döndükten sonra. Yani Drive'daki klasör iş sürerken
**boş** — yarım mp4 orada hiç görünmüyor.

**4 · Düşen bir birleştirme Drive'a hiçbir şey kopyalamıyor**, ve klasörler bugünkü gibi gidiyor
*(madde 94)*.

**5 · Ayrı export'a dokunulmuyor:** orada kopyalama diye bir adım yok, parçalar zaten Drive'a
yazılıyor çünkü **onlar teslim edilen dosyalar** *(235'in kararı)*.

**6 · Kopyalama tek hamlede oturuyor** — geçici bir ada kopyalanıp üstüne taşınıyor, `copy_photo`
ile aynı usul. Drive yavaş olduğu için yarı yazılmış bir hedefin görülme penceresi gerçek, ve
FOUNDATION 1 tam bunu yasaklıyor.

## Beklenen kırmızı

Birleşik export'un hedefini ve kopyalamayı soran testler — **üç civarı**, ve ayrı export'un
testleri yeşil kalmalı. Sayı takımdan okunacak.
