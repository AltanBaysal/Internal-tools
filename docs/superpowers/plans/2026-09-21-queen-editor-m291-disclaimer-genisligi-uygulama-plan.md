# Madde 291 · Disclaimer tuvalin %80'i olacak — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m291-disclaimer-genisligi-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · Sabit.** `ffmpeg_video_exporter.py`'ye `DISCLAIMER_WIDTH = 0.8`, `DISCLAIMER_MARGIN`'in
yanına, ve üstündeki yorum bugünkü kararı söylüyor.

**2 · Filtre.** `_stamp()`'te `scale={MERGED_WIDTH}:-1` →
`scale={round(MERGED_WIDTH * DISCLAIMER_WIDTH)}:-1`.

**3 · Takım:** dört satır paralel. Dört kırmızının yeşile dönmesi beklenir.

**4 · Commit** (yeşil). Ön yüz değişmediği için `dist` build'lenmiyor.
