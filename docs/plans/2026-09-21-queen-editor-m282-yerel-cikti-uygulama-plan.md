# Madde 282 · Birleşmiş dosya yerel diskte bitecek — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m282-yerel-cikti-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `photo_store.copy_export`:** geçici ada kopyala, `os.replace` ile üstüne taşı. Olgu 6.

**2 · `run_export`'un birleşik dalı:** hedef `cutting`'te, ardından `copy_export`. Olgu 1, 2, 3.

**3 · Düşen koşu:** kopyalama `merge()`'ten sonra olduğu için düşen birleştirmede hiç
koşmuyor — ayrı bir dal gerekmiyor. Olgu 4.

**4 · Takım:** dört satır paralel. Beklenen: beş kırmızının hepsi yeşil.

**5 · Commit** (yeşil). Ardından 283.
