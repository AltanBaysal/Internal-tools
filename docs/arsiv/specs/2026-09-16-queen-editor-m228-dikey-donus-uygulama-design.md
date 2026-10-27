# Madde 228 · Üretim dikeye geri dönecek — uygulama turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-16-queen-editor-m228-dikey-donus-testler-design.md)

## Ne değişiyor

Üç grafikte altı sayı — 218'in değiştirdiklerinin tam tersi:

| Dosya | Node | Bugün | Olacağı |
|---|---|---|---|
| `workflow_api.json` | `1` *(Width)* | 1536 | **1024** |
| `workflow_api.json` | `11` *(Height)* | 864 | **1536** |
| `workflow_video_api.json` | `208` *(Xi, Xf / Yi, Yf)* | 848 / 480 | **480 / 720** |
| `workflow_video_first_last_api.json` | `328` *(Xi, Xf / Yi, Yf)* | 848 / 480 | **480 / 720** |

## Ne değişmiyor

- **Dışa aktarmanın karışık ölçü koruması** (`ffmpeg_video_exporter.merge`). Yatay projelere eklenen
  ilk dikey video onun durduğu yer; kaldırmak o projelerde sessizce bozuk dosya demek olurdu.
- **Ön yüz.** Ölçü tutmuyor: galeri karesi kare, oynatıcı gelen videoyu kendi kutusuna sığdırıyor —
  218'den önce de dikey videoyu böyle gösteriyordu.
- **Defter.** Yön bugün defterden seçilmiyor; o, sonraya kalan iş.

`ffmpeg_video_exporter.py`'deki docstring örneği (`"848x480"`) ffprobe'un yazım biçimini gösteriyor,
hangi ölçünün üretildiğini değil — o da kalıyor.
