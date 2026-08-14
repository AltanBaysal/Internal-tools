# Rapor yenilemeyi aşmasın: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3` · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-14-queen-editor-rapor-yenilemeyi-asmasin-testler-design.md) ·
commit `e59dc4e` (3 test kırmızı)

## Ne değişiyor

`useGeneration` bir şey hatırlıyor: **bu sayfa koşan bir durum gördü mü.** Görmediyse, sunucunun
verdiği bitmiş/durmuş durum ekrana `idle` olarak veriliyor.

- Yoklama bir durum getirdiğinde, o durum bir rapor değilse (`done`/`error` dışındaysa) sayfa
  "izlemiş" sayılır.
- Sayfa bir koşuyu **kendisi başlattığında** da izlemiş sayılır. Bu şart: kuyruğa iş ekleyip ilk
  yoklamadan önce biten bir koşunun raporu, kullanıcı düğmeye kendi bastığı hâlde gizlenirdi.
- Kancanın döndürdüğü `job`, izlenmemiş bir raporun yerine `{status: "idle"}` verir. Ham durum
  içeride duruyor; değişen yalnız ekranın okuduğu.

## Neden burada

Karar tümüyle sunuma ait: sunucu doğruyu söylemeye devam ediyor, ikinci bir sekme aynı koşuyu
izliyor olabilir. `useGeneration` zaten "ekranın iş hakkında bildiği"ni türetiyor — kuyruk,
başarısızlıklar, üretilen kare — ve bu da aynı cinsten bir türetim. Tek yerde durunca her tüketici
kendiliğinden doğru okuyor.

## Dokunulmayan

`waiting` bir rapor değil, yaşayan bir hâl — kuyruk hâlâ o üreticiyi bekliyor, ve sayfa onu
izlemese de doğru. `stopping`, `current` ve `currentLayer` yalnız koşarken anlamlı, dolayısıyla ham
durumdan okunmaya devam ediyor.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `.../photo_generation/useGeneration.js` | izlenmemiş rapor `idle` olarak verilir |
| `queen-editor/frontend/dist/` | yeniden derlenir (aynı commit) |

## Bitti sayılır

`npm test --prefix queen-editor/frontend` → 337 geçen, 0 düşen; `dist/` aynı commit'te.
