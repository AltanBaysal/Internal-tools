# Madde 261 · Ayrı export'tan disclaimer kalkacak — test turunun planı

**Spec:** [test turu](../specs/2026-09-21-queen-editor-m261-ayri-export-geri-testler-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · Silinenler:** 249'un üç bindirme testi, ve 253 ile 257'nin parça üzerinden kodlayıcıya bakan
üç testi.

**2 · `FakeExporter` ve `RecordingExporter`:** `piece` üç argümana dönüyor.

**3 · İki yeni test:** olgu 3 ve 4.

**4 · Takım:** dört satır paralel. Beklenen: yalnız iki yeni test kırmızı; birleştirmenin
bindirmesi ve kart denemesi yeşil kalıyor.

**5 · Commit** (kırmızı). Ardından uygulama turu.
