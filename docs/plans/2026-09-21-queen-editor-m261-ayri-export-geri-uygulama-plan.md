# Madde 261 · Ayrı export'tan disclaimer kalkacak — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m261-ayri-export-geri-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `piece()`:** bindirme dalı ve bayrak gitti, üç argüman kaldı. Olgu 1–4.

**2 · `run_export`:** bayrağı geçen argüman gitti.

**3 · Ölü kod:** `_stamp(video)` silindi; `merge()` zaten `_stamp_for()` kullanıyor.

**4 · Yorumlar:** modül başlığı ve `_stamp_for()`'un docstring'i artık doğruyu söylüyor.

**5 · Takım:** dört satır paralel. Beklenen: 24 kırmızının hepsi yeşil.

**6 · Commit** (yeşil). Ardından 259.
