# Madde 228 · Üretim dikeye geri dönecek — test turunun tasarımı

**Tarih:** 16 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey, kodun yazılması için. Sonucu görmek için: yeni bir projede ilk dikey üretime bakması.

## Bugün ne oluyor

218'den beri ölçüler yalnız üç grafikte duruyor ve üçü de yatay: fotoğraf `workflow_api.json`
node `1` × `11` = **1536 × 864**, video `workflow_video_api.json` node `208` ve
`workflow_video_first_last_api.json` node `328` = **848 × 480**. Arka uçta da ön yüzde de ölçü
tutan başka bir yer yok. `test_workflow_asset.py`'deki dört test bu yatay hâli çiviliyor.

## Ne olacak

Ölçüler 218'den önceki hâline döner: fotoğraf **1024 × 1536**, video **480 × 720**. İkisi de tam
2:3 — fotoğrafla video arasında fark sıfır.

**Dışa aktarmanın karışık ölçü koruması değişmiyor.** Drive'da yatay projeler var; onlara eklenen
ilk dikey video tam o korumanın durduğu yer. Onu çivileyen `test_export.py` testleri ölçüden
bağımsız — sahte ffprobe cevabı olarak iki farklı ölçü veriyorlar — ve olduğu gibi kalıyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Fotoğraf grafiği 1024 × 1536 üretiyor | **kırmızı** |
| 2 | İki video grafiği de 480 × 720 üretiyor | **kırmızı** |
| 3 | Fotoğrafla video aynı şekilde *(kural, 218'den)* | yeşil, kalır |
| 4 | Her grafik dikey kare üretiyor | **kırmızı** |

Üçüncüsünün docstring'i 218'in %0,63'lük farkını anlatıyordu; o fark artık yok, cümle de düşer.

## Bu turda değişen

Yalnız `queen-editor/backend/tests/test_workflow_asset.py`.
