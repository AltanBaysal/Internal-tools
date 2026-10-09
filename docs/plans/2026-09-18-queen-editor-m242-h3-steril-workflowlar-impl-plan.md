# Madde 242 · H3'ün iki API workflow'u steril — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-18-queen-editor-m242-h3-steril-workflowlar-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · Taşı:** `workflow (1).json` → `queen-editor/workflow_video_h3_api.json`, `workflow.json` →
`queen-editor/workflow_video_h3_first_last_api.json`.

**2 · İki dosyada:** Director'ün prompt'u dört yerde `""`; `05.png` → `example.png`.

**3 · I2VA dosyasında:** timeline'ın ikinci öğesi çıkar; `"mode":"FL2VA"` → `"mode":"I2VA"`.

**4 · Oku:** `05.png`, `dynv2` ve prompt cümlesi aranır, bulunmamalı; JSON geçerli; I2VA'da tek öğe.

**5 · Takım:** CLAUDE.md'nin dört satırı paralel koşar, yeşil kalır.

**6 · Yol haritasında 242 işaretlenir**, Durum 30/32 olur. Commit'lenir.
