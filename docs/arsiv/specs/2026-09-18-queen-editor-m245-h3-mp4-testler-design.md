# Madde 245 · H3 grafikleri MP4 kaydediyor — test turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Karar 18 Eylül'de kullanıcıyla verildi *(maddenin satırında)*. `"MP4"` ve `"H.264"`
yazılışlarının doğruluğu Colab'da görülür.

## Bugün ne oluyor

İki H3 grafiğinde kaydedici düğüm 2568 (`DaSiWa_EnhancedVideoCombine`) `container: "Auto"`,
`codec: "Auto"` taşıyor, ve kullanıcının denemesinde WebM/AV1 yazdı. Üretici yalnız `.mp4`'ü alıyor;
`fetch_output` sıfır dosyayla *"grafikte Batch Size 1 mi?"* diye duruyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | İki H3 grafiğinde de 2568 `DaSiWa_EnhancedVideoCombine`, `container` `"MP4"`, `codec` `"H.264"` | **kırmızı** |
| 2 | Beklenen uzantıda çıktı yoksa hata o uzantıyı söylüyor, *"Batch Size"* demiyor | **kırmızı** |

İki çıktı gelen durumun *"Batch Size"* sorusu doğru, ve onu tutan test değişmiyor. Gelen dosyanın
adının hatada durduğunu tutan test de değişmiyor.

## Bu turda değişen

- `test_workflow_asset.py`: `test_both_h3_graphs_save_an_mp4` *(olgu 1)*.
- `test_comfy_client.py`: `test_fetch_output_names_the_wanted_extension_when_none_came` *(olgu 2)*.
