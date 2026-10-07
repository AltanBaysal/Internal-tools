# Madde 250 · Birleşik export'ta disclaimer ilk 1 dakika — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m250-birlesik-disclaimer-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `test_export.py`:** olgu 1 — birleştirme komutunun tamamı, `concat` girdisi ve bindirme bir
arada.

**2 · `test_export.py`:** olgu 2 — sayılar parçaların ölçüsünden.

**3 · Takım:** dört satır paralel. Beklenen: yalnız bu iki test kırmızı; `concat` listesini ve
ölçü uyuşmazlığını tutan üç test yeşil kalıyor.

**4 · Commit** (kırmızı). Ardından uygulama turu.
