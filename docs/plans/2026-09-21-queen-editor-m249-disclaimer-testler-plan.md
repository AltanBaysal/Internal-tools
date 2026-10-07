# Madde 249 · Tekli export'ta disclaimer — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m249-disclaimer-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `FakeExporter.piece` disclaimer bayrağını kaydeder:** olgu 5 ve 6'nın bakacağı yer.

**2 · `test_export.py`, exporter testleri:** olgu 1, 2, 3 — üç test, komutun kendisine bakıyor.

**3 · `test_export.py`, `run_export` testleri:** olgu 5 ve 6, birer test.

**4 · `test_export.py`, depo testi:** olgu 7 — `config.DISCLAIMER_PATH` bir dosya gösteriyor.

**5 · Takım:** dört satır paralel. Beklenen: yalnız 1, 2, 3, 5 ve 7 kırmızı; 4 ve 6 yeşil, ve
`a_silent_piece_is_copied_rather_than_re_encoded` de dahil geri kalan her şey yeşil kalıyor.

**6 · Commit** (kırmızı). Ardından uygulama turu.
