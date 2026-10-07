# Madde 243 · queen-editor MiniMax H3 ile video üretiyor — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-18-queen-editor-m243-h3-video-uretici-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · config + üretici:** `config.py`'ye üç sabit; `comfy_h3_video_generator.py`.

**2 · Yazar:** `H3_VIDEO_INSTRUCTION`, `H3VideoPromptWriter`.

**3 · Gruplar:** `H3_VIDEO`, `groups_for`.

**4 · Dışa aktarma:** `-map`'ler.

**5 · main.py:** seçim ve panel.

**6 · Oynatıcı:** `muted`; `npm run build`.

**7 · Defter:** CONFIG, node listesi, modeller hücresi, klon, Flask ortamı, markdown.

**8 · Takım:** dört satır paralel, yeşil.

**9 · Yol haritasında 243 işaretlenir**, Durum 31/32 olur. Kaynak ve `dist/` aynı commit'te.
