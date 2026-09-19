# Madde 248 · Queen Editor adının yanında V5 — uygulama turunun tasarımı

**Tarih:** 19 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Test turu:** [tasarım](2026-09-19-queen-editor-m248-surum-basligi-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey bu turda. Colab'da görülür.

## Ne değişiyor

- **`frontend/src/shared/version.js`** *(yeni)*: `export const VERSION = "V5";` ve neden elle yazıldığını
  söyleyen tek yorum — QueenAgent'ınkiyle aynı gerekçe.
- **Dört ekranın başlığı** *(`ProjectsScreen.jsx`, `ProjectScreen.jsx`, `PhotoDetail.jsx`,
  `ExportScreen.jsx`)*: `wf-hl` span'ının metni `` `Queen Editor ${VERSION}` ``. Tek metin düğümü:
  ad ve sürüm aynı boyda, aynı ağırlıkta, aynı renkte.
- **`dist`** yeniden derleniyor ve aynı commit'e giriyor.
