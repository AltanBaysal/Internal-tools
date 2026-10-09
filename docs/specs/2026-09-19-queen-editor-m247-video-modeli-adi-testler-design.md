# Madde 247 · Video panelinin kutusu kurulu modeli gösteriyor — test turunun tasarımı

**Tarih:** 19 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Görülen ve istenen maddenin satırında.

## Bugün ne oluyor

`LayerPanel.jsx`'in video sözlüğü `model: "WAN 2.2 I2V"` diyor ve kutu onu gösteriyor. `/api/producers`
satırları yalnız `id`, `name`, `installed` taşıyor; hangi video modelinin kurulu olduğu arayüze hiç
gitmiyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | `list_producers`'ın video satırı kurulu modelin adını taşıyor: `h3` → *MiniMax H3*, `wan` ve boş → *WAN 2.2 I2V* | **kırmızı** |
| 2 | Fotoğraf satırı bugünkü üç alanı taşımaya devam ediyor | yeşil *(bekçi, mevcut test)* |
| 3 | Video paneli, satır *MiniMax H3* diyorsa kutuda yalnız onu gösteriyor | **kırmızı** |
| 4 | Satır *WAN 2.2 I2V* diyorsa kutu onu gösteriyor | yeşil *(bekçi)* |
| 5 | Sunucu cevap vermeden kutu *WAN 2.2 I2V* demiyor | **kırmızı** |
| 6 | Ses paneli *MMAudio v2* demeye devam ediyor | yeşil *(bekçi, mevcut testler)* |

## Bu turda değişen

- `test_producers.py`: `test_the_video_row_names_the_model_the_notebook_installed` *(1)*.
- `LayerPanel.test.jsx`: `offers the model in the same box the photo panel uses` satırla çiziliyor ve
  *MiniMax H3* bekliyor *(3)*; yanına `offers WAN when the server says WAN` *(4)* ve `names no model
  before the server has said which` *(5)*.
