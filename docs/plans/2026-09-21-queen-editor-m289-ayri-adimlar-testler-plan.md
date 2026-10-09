# Madde 289 · Videolar, fotoğraflar, disclaimer — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m289-ayri-adimlar-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · İkizlere zaman çizgisi.** `ExportStore.copy_photo` yazdığını `self.order`'a da işliyor, ve
`FakeExporter.piece` — bir store verildiyse — `piece` yazıyor. `merge` ve `copy_export` zaten
yazıyor. Yeni kural yok, yalnız sıra.

**2 · Ayrı export'un sırası.** İki kareli proje, `order` listesi `piece, piece, copy_photo,
copy_photo` olmalı. Olgu 1 — kırmızı.

**3 · Birleşik export'un sırası.** Aynı proje, `order` listesi `piece, piece, copy_photo,
copy_photo, merge, copy_export` olmalı. Olgu 2 — kırmızı.

**4 · Son parçadan sonra iptal.** Son parçayı kestiği anda koşuyu iptal eden bir ikiz exporter;
`export(...)` `None` dönmeli, `store.photos` boş kalmalı, ve klasör silinmiş olmalı. Olgu 3 —
kırmızı.

**5 · Takım:** dört satır paralel. Kırmızı yalnız queen-editor arka ucunda, ve **üç** tane.

**6 · Commit** (kırmızı).
