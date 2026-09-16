# Madde 228 · Üretim dikeye geri dönecek — test turunun planı

**Spec:** [test turu](../specs/2026-09-16-queen-editor-m228-dikey-donus-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** değiştirir.

## Adımlar

**1 · `test_workflow_asset.py` — olgu 1–4.**

| Bugünkü test | Olacağı |
|---|---|
| `test_the_photo_graph_renders_the_landscape_size` | `..._portrait_size` → 1024 × 1536 |
| `test_both_video_graphs_render_the_same_landscape_size` | `..._portrait_size` → (480, 720) |
| `test_the_photo_and_the_video_agree_on_the_shape_of_the_frame` | kalır; docstring'deki %0,63 cümlesi düşer |
| `test_every_graph_makes_a_landscape_frame` | `..._portrait_frame` → yükseklik > genişlik |

**2 · Takım koşulur**, dördü de:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: yalnız **queen-editor'ün arka ucu kırmızı**, üç testle; öteki üçü yeşil.

**3 · Kırmızı commit'lenir.**

## Değişen dosyalar

`queen-editor/backend/tests/test_workflow_asset.py`.
