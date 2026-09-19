# Madde 248 · Queen Editor adının yanında V5 — test turunun tasarımı

**Tarih:** 19 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Karar maddenin satırında: dört ekranın dördünde de.

## Bugün ne oluyor

Dört ekranın başlığında `Queen Editor` sabit metin. `frontend/src/shared/` altında bir sürüm dosyası
yok.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | `shared/version.js`'in `VERSION`'ı bir koşu numarası biçiminde: `V` ve rakamlar | **kırmızı** *(dosya yok)* |
| 2 | Proje listesinin başlığı `Queen Editor V<n>` | **kırmızı** |
| 3 | Proje ekranının başlığı aynı | **kırmızı** |
| 4 | Kare detayının başlığı aynı | **kırmızı** |
| 5 | Export ekranının başlığı aynı | **kırmızı** |

**Değerin kendisi çivilenmiyor**, QueenAgent'ın 209'daki gerekçesiyle: `V5` elle verilen bir karar,
ve testte ikinci kez yazılırsa bir karar iki yerde durur. Tutulan biçim — `v5`, `5`, `V5.1` yakalanır.
Ekran testleri de sürüm dosyasını içe aktarmıyor, biçimle bakıyor: dosya yokken dört test dosyası
toplanamayıp bütünüyle düşerdi.

## Bu turda değişen

- `shared/version.test.js` *(yeni)*: `the version reads as a run number` *(1)*.
- `ProjectsScreen.test.jsx`, `ProjectScreen.test.jsx`, `PhotoDetail.test.jsx`,
  `ExportScreen.test.jsx`: her birine `puts the version next to the name` *(2–5)*.
