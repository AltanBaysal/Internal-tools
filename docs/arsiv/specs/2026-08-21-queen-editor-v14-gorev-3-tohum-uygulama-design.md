# v14 · Görev 3 — Video ve sesin tohumunun kayda geçmesi · **uygulama turu**

**Kaynak:** [test turu](2026-08-21-queen-editor-v14-gorev-3-tohum-testler-design.md) — kararlar
orada verildi ve commit edilmiş sekiz test onları tarif ediyor. Bu belge kodun nereye yazılacağını
söyler.

## Değişen dosyalar

**`domain/seed.py`** (yeni) — `MAX` ve `random_seed()`. Bugün aynı aralık üç yerde ayrı yazılı;
üçü buraya iniyor.

**`domain/run_loop.py`** — `new_seed` parametresi (varsayılanı `seed.random_seed`) ve `chosen`
değişkeni. `chosen`, denemelerin sayacıyla **aynı satırda** sıfırlanıyor: iş değiştiğinde yeni
tohum, aynı iş tekrar denendiğinde aynı tohum. Seçilen sayı hem `producer.generate`'e hem
`record.append`'e gidiyor.

Varsayılanın olması, çağıranın tohum vermeyi unutamaması demek: `resume_batch`, `retry_frame`,
`retry_failed`, `queue_layer` hepsi `make_job`'a uğruyor ve hiçbiri tohumdan haberdar olmak zorunda
değil.

**`data/mmaudio_generator.py`** — `_random_seed` ve `new_seed` düşüyor; kurucu
`(sampler, ffmpeg, tmp_dir=None)`. Docstring, tohumun neden burada seçilmediğini söylüyor: seçilse
kayda ulaşamazdı.

**`backend/main.py`** — iki `lambda: random.randint(0, 2**31 - 1)` yerine `seed.random_seed`;
`import random` düşüyor.

## Bitti sayılır

Dört komutun dördü de yeşil. Ayrıca üç var olan test, üreticinin tohum olarak `None` aldığını
iddia ediyordu; bu madde onu değiştirdiği için o iddiaları taşımayan hâllerine geliyorlar —
değişen şey iddianın kendisi değil, artık doğru olmayan bir yan bilgi.
