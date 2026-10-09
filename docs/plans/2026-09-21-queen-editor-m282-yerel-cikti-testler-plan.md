# Madde 282 · Birleşmiş dosya yerel diskte bitecek — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m282-yerel-cikti-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `ExportStore` ikizi `copy_export`'u yazıyor** — ne kopyalandığını not eden bir liste,
`copy_photo`'nun yaptığı gibi.

**2 · Olgu 1 ve 2'nin testi:** birleştirmenin hedefi `/tmp`'deki yol, ve Drive'a kopyalanan şey
`<proje>.mp4`.

**3 · Olgu 3'ün testi:** kopyalama birleştirmeden sonra — ikizin sırası okunuyor.

**4 · Olgu 4'ün testi:** düşen birleştirmede Drive'a hiçbir şey kopyalanmıyor.

**5 · Olgu 5'in testi:** ayrı export'ta kopyalama adımı hiç yok.

**6 · Olgu 6, store'un kendi testinde** *(`test_photo_store.py`)*: gerçek klasöre kopyalanıyor ve
hedef yarım görünmüyor.

**7 · Takım:** dört satır paralel. Kırmızı yalnız queen-editor arka ucunda.

**8 · Commit** (kırmızı).
