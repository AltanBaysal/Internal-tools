# Madde 488 · Grafik dosyasını okuyan kodun üç kopyası tek yerde — plan

**Spec:** [2026-10-21-queen-editor-m488-graph-loader-design.md](../specs/2026-10-21-queen-editor-m488-graph-loader-design.md)
· **Dal:** `feat/queen-editor-v10` · Test önce (TDD).

1. `queen-editor/backend/tests/test_comfy_graph.py` — eksik dosya, UI formatı, eksik node'lar (hepsi
   tek mesajda), tam grafik ve taze kopya. Kırmızı (modül yok).
2. `queen-editor/backend/features/photo_generation/data/comfy_graph.py` — `load_graph(path, nodes)`,
   H3'ün `_load`'undan genelleştirilmiş. Yeşil.
3. `comfy_photo_generator.py` — `NODES`; `_load` silinir, `_graph` `load_graph` çağırır; `json`
   importu düşer.
4. `comfy_krea_photo_generator.py` — aynısı.
5. `comfy_h3_video_generator.py` — `_load` `load_graph(path, NODES)` + HMCumshot adımı.
6. `python -m pytest queen-editor -q`.
