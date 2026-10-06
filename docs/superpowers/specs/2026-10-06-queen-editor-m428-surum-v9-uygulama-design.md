# Madde 428 · Başlıkta sürüm V9 yazar — uygulama turunun tasarımı

**Tarih:** 6 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
428 · **Dal:** `feat/queen-editor-v9` · **Tur:** 2/2 ·
**Test turu:** [tasarımı](2026-10-06-queen-editor-m428-surum-v9-testler-design.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Testlerin istediği kod

**Tek satır:** `frontend/src/shared/version.js`'te `VERSION = "V9"`. Sayıyı tutan tek yer o, ve
412'den beri dört ekranın dördü de — proje listesi, proje ekranı, karenin sayfası, export ekranı —
tam onu çizmeye testle bağlı. Başka hiçbir dosya değişmiyor: `dist/` dışında `queen-editor/` altında
`V8` yazan başka yer yok (test turunun taraması).

Dosyanın yorumu değişmiyor — sayının neden elle yazıldığını ve dört ekranın onu çizdiğini söylüyor,
ikisi de bugün doğru.

**Hiçbir test değişmiyor.** Testler sayıyı değil bağı tutuyor *(248, 285, 412)*.

## `dist/`

FOUNDATION'ın 3. kararı `dist/`'in kaynakla aynı commit'te build'lenmesini istiyor: defter depoyu
klonluyor ve hiçbir şey build etmiyor, build'siz bir dal Colab'da hâlâ `V8` gösterir. Bu madde
dalga 6'yla paralel bir şeritte koşuyor, ve şeritlerin `dist/`'i birleştirmede bir kez, koşuyu
yürüten tarafından build'lenip commit'leniyor; bu şerit `dist/`'e dokunmuyor. Colab'da `V9`, o build
itildikten sonra görünür.

## Bu turda değişen

- `frontend/src/shared/version.js`: `"V8"` → `"V9"`.

## Beklenen sonuç

Dört satır yeşil.
