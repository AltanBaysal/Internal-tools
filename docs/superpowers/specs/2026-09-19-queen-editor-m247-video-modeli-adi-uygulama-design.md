# Madde 247 · Video panelinin kutusu kurulu modeli gösteriyor — uygulama turunun tasarımı

**Tarih:** 19 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Test turu:** [tasarım](2026-09-19-queen-editor-m247-video-modeli-adi-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey bu turda. Colab'da görülür.

## Ne değişiyor

- **`producers/domain/model_groups.py`:** `groups_for`'un yanına `video_model_name(video_model)` —
  `h3` → *MiniMax H3*, başka her şey → *WAN 2.2 I2V*. Kural `groups_for`'un ve `main.py`'nin
  üreticiyi seçtiği kuralla aynı, ve aynı dosyada duruyor.
- **`list_producers(groups, files, video_model="")`:** video satırına `model` alanı. Fotoğraf ve ses
  satırları değişmiyor.
- **`main.py`:** `list_producers`'a `config.VIDEO_MODEL` geçiyor.
- **`LayerPanel.jsx`:** video sözlüğünden `model` çıkıyor. Kutu `producer.model`'i gösteriyor, yoksa
  sözlüğün kendi adını *(ses: MMAudio v2)*; ikisi de yoksa boş. Yorum güncel hâline.
- **`dist`** yeniden derleniyor ve aynı commit'e giriyor.
