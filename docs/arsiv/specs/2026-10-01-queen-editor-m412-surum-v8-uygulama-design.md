# Madde 412 · Uygulama V8 diyecek — uygulama turunun tasarımı

**Tarih:** 1 Ekim 2026 · **Madde:** [v8 yol haritası](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) ·
**Test turu:** [tasarımı](2026-10-01-queen-editor-m412-surum-v8-testler-design.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olgunun istediği kod

**Tek satır:** `frontend/src/shared/version.js`'te `VERSION = "V8"`. Sayıyı tutan tek yer o, ve
test turundan sonra dört ekranın dördü de tam onu çizmeye bağlı. Başka hiçbir dosya değişmiyor:
`dist/` dışında `queen-editor/` altında `V6` yazan başka yer yok (test turunun taraması).

Dosyanın yorumu değişmiyor — sayının neden elle yazıldığını ve dört ekranın onu çizdiğini söylüyor,
ikisi de bugün doğru.

**Hiçbir test değişmiyor.** Testler sayıyı değil bağı tutuyor, ve sayı değişince onunla birlikte
değişiyorlar *(248, 285)*.

## `dist/`

FOUNDATION'ın 3. kararı `dist/`'in kaynakla aynı commit'te build'lenmesini istiyor: defter depoyu
klonluyor ve hiçbir şey build etmiyor, build'siz bir dal Colab'da hâlâ `V6` gösterir. Bu madde
paralel bir şeritte koşuyor, ve şeritlerin `dist/`'i birleştirmede bir kez, koşuyu yürüten tarafından
build'lenip commit'leniyor; bu şerit `dist/`'e dokunmuyor. Colab'da `V8`, o build itildikten sonra
görünür.

## Bu turda değişen

- `frontend/src/shared/version.js`: `"V6"` → `"V8"`.

## Beklenen sonuç

Dört satır yeşil.
