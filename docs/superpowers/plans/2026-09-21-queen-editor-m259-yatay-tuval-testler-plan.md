# Madde 259 · Birleşik export yatay tuvale geçiyor — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m259-yatay-tuval-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `STAMP` yeniden yazılıyor** — `test_export.py`'de tek yerde duruyor, ve iki test onu tam
çağrıyla karşılaştırıyor. Yeni hâli: sığdırma + bant, sonra tam genişlikte bindirme. Olgu 1, 2, 3,
5, 6.

**2 · Olgu 4'ün testi** *(`..._canvas_is_the_same_whatever_the_pieces_measure`)*: aynı birleştirme
bir kez `480x720` parçalarla, bir kez `848x480` parçalarla koşuluyor, iki filtre zinciri birebir
karşılaştırılıyor.

**3 · Olgu 1-2'nin testi** *(`..._stands_on_a_landscape_canvas`)*: zincirde `decrease` ve `pad`
var, kırpan hiçbir şey yok.

**4 · Olgu 3'ün testi** *(`..._disclaimer_fills_the_canvas_width`)*: `scale=1920:-1`, ve %80'in
verdiği sayı zincirde yok.

**5 · Düşen test siliniyor:** `test_the_merged_disclaimer_is_measured_from_the_pieces_it_joins`.

**6 · Takım:** dört satır paralel, verbatim. Kırmızı beklenen yerde, geri kalanı yeşil.

**7 · Commit** (kırmızı).
