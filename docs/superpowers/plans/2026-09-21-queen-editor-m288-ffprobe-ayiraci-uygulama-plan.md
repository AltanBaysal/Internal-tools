# Madde 288 · `sound()`'un ffprobe ayıracı — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m288-ffprobe-ayiraci-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · Komut.** `ffmpeg_video_exporter.py`'nin `sound()`'unda `"csv=s=:p=0"` → `"csv=p=0"`.

**2 · Okuma.** Aynı işlevde `said.partition(":")` → `said.partition(",")`.

**3 · Yorum.** Docstring'e ayıracın neden yazılmadığı giriyor — `size()`'ın `s=x`'ini görüp buraya
da bir ayıraç koymak isteyecek göz için.

**4 · Takım:** dört satır paralel. Üç kırmızının da yeşile dönmesi, ve başka hiçbir şeyin
düşmemesi beklenir.

**5 · Commit** (yeşil).
