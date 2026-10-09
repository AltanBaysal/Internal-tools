# Madde 235 · Birleşik export parçalarını Drive'a bırakmaz — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-17-queen-editor-m235-birlesik-export-parcalari-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · `photo_store.py`.** `make_pieces_dir()` — `tempfile.mkdtemp` ile bir klasör açar, yolunu
döndürür. Neden Drive'da olmadığını yazan bir docstring.

**2 · `run_export.py`.** Parçaların klasörü moda göre seçilir; birleştirmeden sonra ve düşen ya da
iptal edilen koşuda kaldırılır.

**3 · Takım koşulur**, dördü de. Beklenen: hepsi yeşil.

**4 · Yol haritasında 235 işaretlenir**, Durum 21/24 olur. Commit'lenir.

Ön yüz değişmediği için build gerekmiyor.
