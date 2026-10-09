# Madde 250 · Birleşik export'ta disclaimer ilk 1 dakika — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m250-birlesik-disclaimer-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `_stamp()` ikiye:** `_stamp_for(width, height)` filtreyi kuruyor, `_stamp(video)` ffprobe'u
koşup onu çağırıyor.

**2 · `merge()`:** PNG girdisi, filtre, `-map [v] -map 0:a?`, kodlama, ses `copy`. Olgu 1 ve 2.

**3 · Modül başlığı:** ikinci kodlanan şeyi söyle.

**4 · Takım:** dört satır paralel. Beklenen: hepsi yeşil.

**5 · Commit** (yeşil). Ardından madde 251.
