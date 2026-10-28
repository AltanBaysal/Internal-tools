# v14 · Görev 1 — Motorun bitiş karesi alabilmesi · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-1-bitis-karesi-testler-design.md) —
kararlar orada verildi ve commit edilmiş on iki test onları tarif ediyor. Bu belge kodun nereye
yazılacağını söyler.

## Değişen dosyalar

**`backend/config.py`** — `VIDEO_FIRST_LAST_WORKFLOW_PATH`, öbür grafiğin yanına.

**`data/comfy_video_generator.py`** — iki yol tutar, iki node kümesi bilir. `generate` bir `end`
alır; verildiyse bitiş kareli grafik, verilmediyse bugünkü grafik yüklenir. İki kare de
`upload_image` ile gider, önce başlangıç sonra bitiş. `_load` artık hangi dosyayı ve hangi node'ları
istediğini argüman olarak alıyor — hata cümlesindeki dosya adı da yoldan çıkıyor, elle yazılmıyor.

**`domain/ports.py`** — `PhotoGenerator.generate` imzasına `end`. Kuyruğun tek çağrı biçimi var:
bitiş karesi olmayan üretici de argümanı alır, yok sayar.

**`data/comfy_photo_generator.py`, `data/mmaudio_generator.py`** — `end` alır, kullanmaz;
docstring'leri neden almadıklarını söyler.

**`features/producers/domain/model_groups.py`** — video grubuna `clip_vision_h.safetensors`.
Panelin "video üreticisi kurulu" cevabı bu listeden çıkıyor, ve yeni grafik o dosyayı okuyor.

**`backend/main.py`** — ikinci yolu üreticiye verir.

**`app.ipynb`** — `clip_vision` klasörü, `OPEN_VIDEO`'ya yeni satır, klon hücresinin grafik
denetimine üçüncü dosya. Video grubunun tahmini ~37 → ~39 GiB: disk ölçümü bu sayıdan besleniyor,
eski sayı yeni dosyayı saymıyor.

## Bitti sayılır

Dört komutun dördü de yeşil, hiçbiri `skip` ya da `xfail` taşımıyor.
