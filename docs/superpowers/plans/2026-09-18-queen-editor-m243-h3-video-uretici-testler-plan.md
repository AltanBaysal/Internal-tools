# Madde 243 · queen-editor MiniMax H3 ile video üretiyor — test turunun planı

**Spec:** [test turu](../specs/2026-09-18-queen-editor-m243-h3-video-uretici-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · `test_comfy_h3_video_generator.py` (yeni):** sahte istemci ve iki küçük grafik (Director +
SeedControl). Olgu 1–5.

**2 · `test_video_prompt_writer.py`:** H3 yazarı ve talimatı. Olgu 6.

**3 · `test_workflow_asset.py`:** H3'ün iki grafiği; yapı, süre, boyut, modeller, LoRA yığını.
`config.VIDEO_MODEL`'in varsayılanı. Olgu 7–9, 11.

**4 · `test_producers.py`:** H3 grubu ve `groups_for`. Olgu 10.

**5 · `test_notebook_installs_the_producer_groups.py`:** açılır liste, listelerin anahtarları, H3
dosyaları, sürümler, damga, DaSiWa node'ları, disk, `QE_VIDEO_MODEL`, klon, form. Kutu ve baytlar
testleri güncellenir. Olgu 12–15.

**6 · `test_export.py`:** sesli parçanın beklenen satırı `-map`'lerle. Olgu 16–17.

**7 · `LayerPlayer.test.jsx`:** ses katmanı varken video susturulmuş. Olgu 18.

**8 · Takım:** CLAUDE.md'nin dört satırı paralel. Beklenen: yalnız bu testler kırmızı, sebebi
eksik modül/sabit/davranış; başka hiçbir test kırmızı değil.

**9 · Commit** (kırmızı). Ardından uygulama turu.
