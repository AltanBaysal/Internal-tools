# Madde 298 — Sınırlar, test turunun planı

**Spec:** [m298 test turu](../specs/2026-09-21-queen-editor-m298-sinirlar-testler-design.md)

Dört test dosyası: `test_references.py`, `test_reference_usecases.py`, `test_reference_routes.py`,
ve yeni `test_ffmpeg_clips.py`. Kaynak koda dokunulmuyor.

## Adımlar

1. **Kural testleri** — `references.check(pool, incoming)` çağrısıyla; havuz ve gelenler aynı
   şekilde `(ad, tip, süre)` taşıyor, çünkü kuralın ikisini ayırması için bir sebep yok.

2. **Kullanım senaryosu testleri** — 297'nin sahtelerine bir `FakeClips` ekleniyor: sorulduğu her
   baytı sayıyor, böylece *"fotoğraf hiç sorulmuyor"* söylenebiliyor. `FakeReferenceStore` artık
   süre de tutuyor, çünkü gerçek depo süreyi yolundan okuyor.

3. **Araç testleri** — `test_ffmpeg_stills.py`'ın `FakeRun`'ı gibi, bu dosyanın kendi sahtesiyle.

4. **Kapı testi** — 297'nin istemcisi artık bir de klip aracı kuruyor.

5. **Dört test satırı koşulur.**

## Beklenen kırmızı

`test_ffmpeg_clips.py` toplamada düşer; ötekiler `check` ve `seconds` olmadığı için. Var olan
referans testlerinden ikisi de düşer — havuzun listesi artık `seconds` taşıyor ve sahteler değişti.
Bu beklenen: liste satırının şekli bu maddenin değiştirdiği şey.
