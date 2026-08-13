# Queen Editor v8 · Görev 2 — Defterden ses hücreleri ve model notu kalksın

**Tarih:** 2026-08-13 · **Yol haritası:** [v8](../plans/2026-08-13-queen-editor-v8-roadmap.md) · Görev 2
**Önkoşul:** [Görev 1](2026-08-13-queen-editor-v8-gorev-1-ses-motoru-kurulumu-design.md) — kurulum
artık uygulamada.

## Problem

Görev 1'den sonra ses motorunun kütüphanesi iki yerden kurulabiliyor: defterden ve panelden. İki
kurulum yolu, yalnız temiz bir makinede ve kimse bakmazken birbirinden ayrılır — tam da kimsenin
fark etmediği yerde. Defterdeki hücre artık gereksiz, ve kalması bir hata değil, **ikinci bir
doğru** olurdu.

Bir de v7'de eklenen "Modeller — burada inmez" hücresi var: olmayan bir şeyi anlatıyor.

## Karar

Defter yalnız uygulamanın **koşması** için gerekli olanı kurar: ComfyUI, custom node'lar, ffmpeg.
Üreticilerin ihtiyacı olan her şey — model dosyaları ve ses motorunun kütüphanesi — uygulamanın
Üreticiler panelinden gelir.

Defterde `MMAudio` geçen tek satır kalmaz. Bunu bir test iddia eder, çünkü bu kuralı bozmak kolay:
bir hücre geri eklendiğinde ortada kırılan hiçbir şey olmaz, yalnız iki kurulum yolu geri gelir.

## Ne siliniyor

| Hücre | Ne olur |
|---|---|
| `5b33516b` — "## MMAudio (ses motoru)" başlığı | silinir |
| `6269c93f` — klon + `pip install -e .` + import denemesi | silinir |
| `3ad9cb36` — "## Modeller — burada inmez" | silinir |

## Ne yeniden yazılıyor

- **ComfyUI hücresinin notu** (`8de17e98`) bugün "kurulumu bir sonraki hücrede" diyor; o hücre
  gidiyor. Not kalır ama yeni yerini gösterir: ses ComfyUI'den geçmiyor, motoru uygulamanın
  Üreticiler panelinden kuruluyor.
- **Giriş hücresinin akış satırı** (`34c9ff58`) adım adım ne olduğunu sayıyor ve arada MMAudio
  kurulumu var; o adım çıkar. Başlığın kendisi Görev 3'ün işi.
- **Ortak yardımcılar hücresinin yorumu** (`df871d38`) "custom node ve MMAudio hücreleri kullanıyor"
  diyor; artık tek kullanıcısı var.

Silinen hücrelerin taşıdığı tek bilgi — "modeller burada inmez, panelden kurulur" — giriş
hücresinde zaten yazılı, o yüzden hiçbir şey kaybolmuyor.

## Test

`test_model_install_is_the_apps_job.py` bugün repo genelinde ölü isimleri arıyor. Yanına aynı
biçimde bir iddia daha: **defterde `MMAudio` geçmiyor.** Repo geneli değil, yalnız defter — kelime
kodda, testlerde ve bu belgelerde doğru yerde duruyor.

## Kabul edilen bedel

Görev 1'in speci'nde yazılı olanın aynısı, burada gerçekleşiyor: kurulum hatası artık Run all'da
değil, "Kur"a basınca görülüyor.
