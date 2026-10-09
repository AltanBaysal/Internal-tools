# Madde 283 · Tekli çıktılar kendi klasörüne — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m283-klasorler-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `photo_store`:** `make_videos_dir(folder)` geldi, `PHOTOS_DIR` `"foto"` oldu. Olgu 1, 2.

**2 · `run_export`:** tekli mod `make_videos_dir(folder)`'a kesiyor. Olgu 1.

**3 · Silme koşulu moda bağlanıyor** — iki yerde: koşu sonu ve `_clean`. Olgu 5, 6, 7.

**4 · Takım:** dört satır paralel. Beklenen: sekiz kırmızının hepsi yeşil, bekçi yeşil kalıyor.

**5 · Commit** (yeşil). Ardından 284.
