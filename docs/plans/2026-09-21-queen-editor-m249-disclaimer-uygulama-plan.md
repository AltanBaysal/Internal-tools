# Madde 249 · Tekli export'ta disclaimer — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m249-disclaimer-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `config.py`:** `DISCLAIMER_PATH`, grafiklerin yanına.

**2 · `ffmpeg_video_exporter.py`:** üç sabit, kurucuya PNG yolu, `piece()`'e bayrak ve bindirme.
Olgu 1, 2, 3.

**3 · `run_export.py`:** bayrağı modda geçir. Olgu 5; 6 yeşil kalıyor.

**4 · `main.py`:** wiring.

**5 · `disclaimer.png`:** kullanıcının dosyası depo köküne. Olgu 7 — bu dosya gelmeden takım
yeşile dönmüyor.

**6 · Takım:** dört satır paralel. Beklenen: hepsi yeşil.

**7 · Commit** (yeşil). Ardından madde 250.
