# Madde 245 · H3 grafikleri MP4 kaydediyor — uygulama turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Test turu:** [tasarım](2026-09-18-queen-editor-m245-h3-mp4-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey bu turda. Değerlerin yazılışı Colab'da görülür.

## Ne değişiyor

- **İki H3 grafiği** *(`workflow_video_h3_api.json`, `workflow_video_h3_first_last_api.json`)*: düğüm
  2568'de `container` `"Auto"` → `"MP4"`, `codec` `"Auto"` → `"H.264"`. Başka hiçbir değer değişmiyor.
- **`services/comfy/client.py`, `fetch_output`:** hiçbir çıktı eşleşmezse hata ne beklendiğini
  söylüyor — verilen uzantılar, uzantı verilmediyse görsel — ve gelenlerin dökümünü taşımaya devam
  ediyor. Birden çok çıktıda bugünkü *"Batch Size"* sorusu kalıyor.

Uygulamanın geri kalanı değişmiyor: üretici zaten `.mp4` arıyor.
