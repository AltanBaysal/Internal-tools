# v12 Görev 1 — Tohumsuz iş: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v12](../plans/2026-08-14-queen-editor-v12-roadmap.md) · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-14-queen-editor-v12-gorev-1-testler-design.md) ·
commit `e1c3d86` (beş test kırmızı)

Kararların tamamı test döngüsünde verildi ve testler onları çoktan yazdı. Bu belge yalnız o
kararların koda nasıl indiğini söylüyor.

## Ne değişiyor

`MMAudioGenerator` bir tohum kaynağı alıyor ve işin tohumu yokken bir tane seçiyor:

- Yapıcıya `new_seed=None` eklenir; verilmezse modülün kendi rastgelesi kullanılır.
- `generate()` içinde, kaynak videonun varlığı doğrulandıktan sonra ve parçalara inmeden **önce**:
  tohum yoksa bir tane seçilir. Bir kez — böylece uzun bir videonun bütün parçaları aynı tohumu
  paylaşır.

`MMAudioSampler`'a dokunulmuyor. `rng.manual_seed(seed)` olduğu gibi kalıyor, çünkü artık ona hep
bir tam sayı geliyor — kural üreticide, patlayan satırda değil.

## Neden port varsayılanlı, `main.py` değişmiyor

`start_batch` ve `regenerate` tohumu dışarıdan alıyor çünkü ikisi de alan katmanında ve saf olmak
zorunda. `MMAudioGenerator` veri katmanında: zaten geçici dizin açıyor, dosya yazıyor, silinen bir
oda bırakıyor. Orada rastgele bir sayı üretmek katmanın doğasına aykırı değil.

Port yine de var, çünkü testin tohumu bilmesi gerekiyor — "iki iş farklı tohum alır" ancak tohumlar
bilinirse kanıtlanabilir. Yani port testin ihtiyacı; varsayılan üretimin cevabı. `main.py`'ye
üçüncü bir `lambda: random.randint(...)` eklemek aynı kararı iki yerde yazmak olurdu.

Aralık fotoğrafınkiyle aynı: `0` ile `2**31 - 1`.

## Bilerek yapılmayan

**Seçilen tohum kayda geçmiyor.** `run_loop` satıra işin tohumunu yazıyor, o da hâlâ `None`; yani
bir ses satırından yeniden üretilemiyor. Bu bir gerileme değil — video da bugün böyle, o da tohumsuz
planlanıyor. Üreticinin kullandığı tohumu geri döndürmesi üç üreticinin de port'unu değiştirirdi;
bu görevin işi kuyruğu akıtmak.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `.../data/mmaudio_generator.py` | tohum kaynağı ve tohumsuz işin cevabı |

Ön yüz değişmiyor, `dist/` yeniden derlenmiyor.

## Bitti sayılır

`python -m pytest queen-editor/backend/tests -q` → 597 geçen, 0 düşen.
