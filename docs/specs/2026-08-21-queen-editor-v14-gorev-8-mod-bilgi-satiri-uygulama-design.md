# v14 · Görev 8 — Detayda Üretim modu bilgi satırı · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-8-mod-bilgi-satiri-testler-design.md) —
kararlar orada verildi ve commit edilmiş on iki test onları tarif ediyor.

## Değişen dosyalar

### 1 · `domain/run_loop.py` — vardığı yer satıra yazılıyor

`_end_for`'un dönüşü bugün doğrudan `producer.generate`'e gidiyor; bir değişkende tutuluyor, çünkü
satır da onu istiyor.

`_mode_of`, `_made_with(job, end)` oluyor: satırın "nasıl yapıldı" kısmını tek elden veren yardımcı.
Modu **ve** vardığı resmin adını döndürüyor, ikisi de yalnız varsa. İki ayrı yardımcı ile iki ayrı
sözlük açmak yerine tek yer, çünkü ikisi de aynı soruyu cevaplıyor ve `append` çağrısı okunur
kalıyor.

Ad `end[0]` — üreticiye giden çiftin dosya adı. Loop'unki kendi resmi, bağlınınki hedefin resmi,
standartta çift yok.

### 2 · `data/photo_record.py` — hücreye katlanıyor

`slots()` `mode`'u nasıl katlıyorsa `endsOn`'u da öyle.

### 3 · `domain/usecases/list_frames.py` — kareye çıkıyor

`_modes` ile `_reasons` aynı şekli paylaşıyor; üçüncü bir kopya yerine **tek bir `_per_layer(cells,
field)`** doğuyor ve `_modes` onun üstüne oturuyor. `_reasons` kendi süzgecini koruyor: o yalnız
patlamış katmanlara bakıyor, ötekiler alanın kendi varlığına.

Kare `endsOn: {layer: file}` alıyor, iki `append` çağrısında da.

### 4 · `domain/copy_frame.py` — kopya götürüyor

`carry_layers` bugün `mode`'u tek tek taşıyor; artık taşınacak iki alan var, dolayısıyla döngü bir
liste üzerinden geçiyor: kareden okunan alan adları ve satıra konan karşılıkları.

### 5 · `features/photo_generation/production_modes.js` — modun adı

`labelOf(mode)` — listenin etiketini veriyor, tanımadığı bir değerde değerin kendisini. Panel
etiketi listeden okuyor, detay sayfası da: ikisi aynı şeyi adlandırıyor.

### 6 · `features/photo_generation/PhotoDetail.jsx` — satırın kendisi

Sıra ve dosya adlarının yanına, aynı sarmalayan sıraya bir `Field`. Yalnız `open === "video"` ve
karenin video modu varsa. Bağlı modda değer `${label} → ${endsOn}`.

## Bitti sayılır

Dört komutun dördü de yeşil. `dist` bu commit'te derleniyor.
