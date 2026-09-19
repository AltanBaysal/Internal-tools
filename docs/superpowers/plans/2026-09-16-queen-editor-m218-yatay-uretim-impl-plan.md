# Madde 218 · Üretim yatay olacak — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-16-queen-editor-m218-yatay-uretim-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı: `64058f74` — 7 test, hepsi `python -m pytest queen-editor`'de.

## Adımlar

**1 · `workflow_api.json`.** Node `1` → 1536, node `11` → 864.

**2 · `workflow_video_api.json`.** Node `208`: `Xi`/`Xf` → 848, `Yi`/`Yf` → 480.

**3 · `workflow_video_first_last_api.json`.** Node `328`: aynısı.

**4 · `ffmpeg_video_exporter.py`.**

- `__init__` bir `ffprobe="ffprobe"` alır.
- `_size(path)` → `"<genişlik>x<yükseklik>"`; `ffprobe -v error -select_streams v:0
  -show_entries stream=width,height -of csv=s=x:p=0`. Sıfırdan farklı çıkışta `RuntimeError`,
  içinde `ffprobe`'un son satırı — `_ffmpeg_run`'ın bugünkü davranışının aynısı.
- `merge` en başta her parçayı ölçer. Tek ölçü varsa bugünkü akış; birden fazlaysa `RuntimeError`,
  mesajda her parça kendi ölçüsüyle. Liste dosyası bu noktadan **sonra** yazılır.

**5 · Takım koşulur**, dördü de — hepsi yeşil beklenir:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

`dist` derlenmiyor: ön yüzde tek satır değişmedi.

**6 · Yol haritası** 218'i ✅ yapar, durum 7/11 olur.

**7 · Tek commit.**

## Değişen dosyalar

`queen-editor/workflow_api.json`,
`queen-editor/workflow_video_api.json`,
`queen-editor/workflow_video_first_last_api.json`,
`queen-editor/backend/features/photo_generation/data/ffmpeg_video_exporter.py`,
`docs/superpowers/roadmaps/2026-09-11-queen-editor-v5-roadmap.md`.
