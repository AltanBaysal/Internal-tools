# v14 · Görev 2 — Kuyruk işinin üretim modunu taşıması · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-2-uretim-modu-testler-design.md) —
kararlar orada verildi ve commit edilmiş on beş test onları tarif ediyor. Bu belge kodun nereye
yazılacağını söyler.

## Değişen dosyalar

**`domain/production_mode.py`** (yeni) — üç kimlik, hepsini sayan `ALL`, ve bir işin modunu okuyan
`of`. Türkçe etiket yok: onu ön yüz taşıyor, ve kimliği etiketiyle aynı dosyada tutmak ikisinin
birbirine yapışması demek.

**`domain/usecases/queue_layer.py`** — `InvalidMode`, bir `mode` parametresi, iki doğrulama, ve
plan satırına ne yazılacağını söyleyen iki küçük fonksiyon:

- `_frame_after(gallery, fid)` — galeride bir sonraki kare, fotoğrafı varsa. Yoksa `None`.
- `_mark(kind, mode, gallery, fid)` — bu karenin satırına eklenecek anahtarlar. Video değilse boş
  sözlük (ses satırında `mode` **hiç doğmuyor**). Bağlı modda hedef yoksa `None`, ki döngü o kareyi
  atlasın.

`None` ile `{}` arasındaki fark taşıyıcı: biri "yazacak bir şey yok", öteki "bu kare kuyruğa hiç
girmesin". Tek bir dönüş tipiyle ikisini ayırmak, çağıranın sözlüğün boşluğuna bakmasını ve iki ayrı
sebebi bir koşulda toplamasını gerektirirdi.

**`domain/run_loop.py`** — `MissingEndFrame` (`frame_level = True`), ve modu okuyup bitiş karesini
seçen `_end_for`. Standart `None`, loop karenin kendi kaynağı, bağlı hedefin fotoğrafı — hedefin
fotoğrafı yoksa `MissingEndFrame`.

Motor `end`'i `_source_for` ile aynı anda, işin sırası geldiğinde okuyor: dosya Drive'da ve koşu
saatler önce başlamış olabilir.

## Sıra

`production_mode.py` önce doğar: `queue_layer` da `run_loop` da ondan okuyor. `queue_layer` ile
`run_loop` birbirinden bağımsız — biri yazıyor, öteki okuyor — ama ikisi de aynı anahtar adlarına
(`mode`, `linkedTo`) dayanıyor, ve o adlar `production_mode.py`'nin değil plan satırının sözlüğü.
Bu yüzden ikisi tek turda bitiyor: aradaki sözleşme bir modülde değil, iki dosyanın anlaşmasında.

## Bitti sayılır

Dört komutun dördü de yeşil, hiçbiri `skip` ya da `xfail` taşımıyor. Uç noktanın `mode` anahtarını
okuması bu turda **yok** — 4. maddenin işi, ve o gelene kadar modu yalnız testler verebiliyor.
