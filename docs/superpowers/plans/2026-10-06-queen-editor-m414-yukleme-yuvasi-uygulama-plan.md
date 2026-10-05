# Madde 414 — Yüklenen resim tıklanan yuvaya, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Adımlar `- [ ]` ile işaretlenir. Testlere dokunulmaz:
> kırmızı commit'lenen üç test koddan yeşile döner.

**Hedef:** Yükleme, dosyanın geldiği satırı sıra belgesine yazar — satır o an durduğu gibi, yeni
dosyalar sonunda; böylece adı önce gelen yeni dosya eskinin yuvasını alamaz.

**Yaklaşım:** `add_references` dosyaları yazdıktan sonra elindeki `held`'den ve `arriving`'den
satırları kurar ve belgeye yazar; belgenin öteki satırları olduğu gibi. Doğruluğunu yitiren dört
belge düzelir.

**Araçlar:** Python.

**Spec:** [m414 uygulama turu](../specs/2026-10-06-queen-editor-m414-yukleme-yuvasi-uygulama-design.md)

## Her yere geçerli kurallar

- Kod ve yorumlar **İngilizce**; yorum *neden*i ve yalnız bugün doğru olanı söyler.
- Testler yalnız CLAUDE.md'nin dört satırıyla, olduğu gibi, paralel; `skip` / `xfail` yok.
- `dist` kurulmaz; yol haritasına dokunulmaz.

---

## Görev 1: `domain/usecases/add_references.py`

**Dosya:** Değiştir:
`queen-editor/backend/features/photo_generation/domain/usecases/add_references.py`

- [ ] **Adım 1: modülün belgesine, *"Names are worked out…"* paragrafının ardına:**

```python
Each file goes in at the end of its own row, and that row is written into the order as it then
stands (madde 414). The order is what places a file: one it does not name waits among the others by
name (references.placed), so an upload left out of it would stand wherever its name sorts -- in
front of the reference already there whenever it sorts first. A second kedi.png, stored as
kedi-2.png, always would: "-" sorts before ".".
```

- [ ] **Adım 2: dosyalar yazıldıktan sonra, `return`'den önce.** Değişken `one`: `row` fonksiyonun
  parametresi.

```python
    for name, data in writing:
        pool.save(project, name, data)
    # After the files, so the order never names one that did not land. The row is rebuilt from what
    # the pool holds, so a name whose file was deleted by hand in Drive drops out of it here.
    order = orders.read(project)
    for kind in {one["kind"] for one in arriving}:
        order[kind] = [one["name"] for one in held + arriving if one["kind"] == kind]
    orders.write(project, order)
    return list_references(store, pool, orders, project)
```

## Görev 2: doğruluğunu yitiren belgeler

**Dosyalar:** Değiştir:
- `queen-editor/backend/features/photo_generation/domain/references.py` — `placed`
- `queen-editor/backend/features/photo_generation/data/reference_order_store.py` — modül
- `queen-editor/backend/features/photo_generation/domain/usecases/remove_reference.py` — modül
- `queen-editor/backend/features/photo_generation/domain/usecases/save_reference_order.py` — modül

- [ ] **Adım 1: `placed`'in son paragrafı.**

```python
    A file the order has never heard of waits at the end, among those by name: one put in the
    folder by hand from Drive, or any file of a row nothing has written down yet -- a pool from
    before uploads wrote their place. An upload is never one of them: it writes its row
    (add_references, madde 414).
```

- [ ] **Adım 2: `reference_order_store.py`'nin ilk iki paragrafı.**

```python
"""The order the reference pool stands in -- the only place that knows this file.

A document of its own beside the folder, because it answers what the folder cannot: which slot each
reference stands in (madde 300). A drag writes it, and so does every upload, with the new file at
the end of its row (madde 414). The folder says what exists; this says in what order. A name can
outlive its file here -- one deleted by hand in Drive -- and it then stands in no slot (madde 321).
```

- [ ] **Adım 3: `remove_reference.py` — ilk paragrafın son cümlesi.** *"A name left in the order
  would not show as a hole (the pool counts only what is there), but a file uploaded under it later
  would slip back into its old place rather than join the end of its row."* yerine:

```python
references tight and numbers them by order. The order names only references that are there, the
way a dragged one does (save_reference_order).
```

- [ ] **Adım 4: `save_reference_order.py` — modülün ikinci paragrafı.**

```python
The sequence is filtered against what the pool really holds before it is stored, the way the
gallery's own order is (save_order): the server writes only names it can see itself, so a stale tab
cannot leave ghosts in the file -- names that stand in no slot (madde 321).
```

## Görev 3: Koş, yeşili oku, commit'le

- [ ] **Adım 1: dört satır, paralel, olduğu gibi.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; `queen-editor` pytest'inde test turunun üç kırmızısı yeşil.

- [ ] **Adım 2: fork noktasından farkı oku** — FOUNDATION ve CODE-STANDARD'a göre: domain dışarıdan
  bir şey almıyor, yorumlar doğru, ölü kod yok.

- [ ] **Adım 3: commit** — kod, belgeler, spec ve plan tek commit.

```powershell
git add docs/superpowers/specs/2026-10-06-queen-editor-m414-yukleme-yuvasi-uygulama-design.md docs/superpowers/plans/2026-10-06-queen-editor-m414-yukleme-yuvasi-uygulama.md queen-editor/backend/features/photo_generation
git commit -m @'
fix(queen-editor): 414 -- an upload writes its row into the reference order, as the row stands with the new file at its end; before, nothing wrote it and the pool placed unwritten files by name, so a new picture whose name sorted first, or a same-named copy stored as -2, took slot 1 from the photo already there

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
