# Madde 286 · Parçaların ses akışı — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m286-parca-sesi-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `sound(video)`:** `size()`'ın kardeşi; boş cevap `None`, dolu cevap `(hız, düzen)`. Olgu 1.

**2 · `merge()` sesi soruyor**, ve sesi olan bir parça varsa olmayanların yanına sessizlik
yazıyor; `concat` listesine yeni dosya giriyor. Olgu 2, 3, 5.

**3 · Tek düzenli setlerde hiçbir şey olmuyor** — kodun şeklinden geliyor, ayrı bir dal yok.
Olgu 4.

**4 · Takım:** dört satır paralel. Beklenen: üç kırmızının hepsi yeşil, iki bekçi yeşil kalıyor.

**5 · Commit** (yeşil). Ardından 282.
