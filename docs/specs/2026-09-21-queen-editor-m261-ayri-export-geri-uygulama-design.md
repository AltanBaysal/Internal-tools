# Madde 261 · Ayrı export'tan disclaimer kalkacak — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m261-ayri-export-geri-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

**`piece()` 249'dan önceki hâline döndü** — üç argüman, iki dal: sesli parça bugünkü ses yolunu
kullanıyor, sessiz parça `-c copy`. Bindirme dalı, PNG girdisi ve kodlama argümanları buradan
gitti.

**`run_export` bayrağı geçmiyor**, ve `MERGED` ayrımı orada yine yalnız **parçaların nereye
kesildiği** için duruyor — 235'in kararı, 249'dan önce de öyleydi.

**Ölü kod silindi:** `_stamp(video)` yalnız parça yolundan çağrılıyordu; `merge()` ölçüyü kendisi
tuttuğu için `_stamp_for(width, height)` kullanıyor. Kalan tek çağıran o, ve docstring artık bunu
söylüyor.

**Modül başlığı düzeltildi.** *"Bir parça disclaimer taşıdığı için kodlanıyor"* cümlesi yanlış hâle
geldi; yerine kodlanan şeyin **birleşik export** olduğu yazıldı. Yanlış olmuş bir yorum, kodun
kendisinden daha uzun yaşar.

## Kalkmayanlar

`merge()`'in bindirmesi, `_stamp_for()`, kodlayıcının karta sorulması *(253, 257)*, `_encoder()` ve
`assets/disclaimer.png`. Beşi de birleşik yolun işi, ve **259** onları büyütecek: yatay tuval, tam
genişlik.

## Bunun getirdiği

**Ayrı export yine hiçbir kareyi kodlamıyor** — akışlar kopyalanıyor, yani saniyeler. 249 ile 250'nin
getirdiği yavaşlığın ayrı export'a düşen yarısı tamamen kalktı; kalan yarısı birleşik export'ta, ve
o karta gidiyor.

## Bu turda değişen

- `data/ffmpeg_video_exporter.py`: `piece()` üç argümana döndü, bindirme dalı ve `_stamp()` silindi,
  modül başlığı ile `_stamp_for()`'un docstring'i düzeltildi.
- `domain/usecases/run_export.py`: bayrağı geçen argüman ve onu anlatan yorum gitti.
