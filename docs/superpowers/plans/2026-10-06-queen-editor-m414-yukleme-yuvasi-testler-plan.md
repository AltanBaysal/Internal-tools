# Madde 414 — Yüklenen resim tıklanan yuvaya, test turunun planı

> **Koşum:** bu oturumda, satır satır. Adımlar `- [ ]` ile işaretlenir. Bu turda kaynak kod
> değişmiyor; testler kırmızı commit'lenir.

**Hedef:** Fotoğraflar satırında bir fotoğraf varken Ekle kartından yüklenen resmin satırın sonuna
indiğini, eskinin yerinde kaldığını, ve bunun yeniden başlatmadan sonra da sürdüğünü söyleyen
testler — bugün kırmızı, ve kırmızı oldukları yer sebebi kanıtlıyor.

**Yaklaşım:** Kullanıcının yolu gerçek kapıdan ve gerçek klasörden: `test_reference_routes.py`'nin
sunucusu. Kural sahte portlarla use case'te. Var olan üç testin kurulumu ya da yorumu, kural 1'den
sonra da doğru kalsın diye.

**Araçlar:** pytest, Flask'ın test istemcisi.

**Spec:** [m414 test turu](../specs/2026-10-06-queen-editor-m414-yukleme-yuvasi-testler-design.md)

## Her yere geçerli kurallar

- Test adları, docstring'ler ve yorumlar **İngilizce**.
- Testler yalnız CLAUDE.md'nin dört satırıyla, olduğu gibi, paralel koşulur; `skip` / `xfail` yok.
- Hiçbir test gerçek bir Drive'a dokunmaz: kapı testleri `tmp_path`'te.

**Arayüz — uygulama turunun vereceği:** yok. Kapı ve use case bugünkü imzalarıyla; değişen yalnız
yüklenen dosyanın yuvası.

---

## Görev 1: `backend/tests/test_reference_routes.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_reference_routes.py`

- [ ] **Adım 1: `names_of`'un altına iki yardımcı.**

```python
def slots_of(body):
    return [(row["name"], row["slot"]) for row in body["references"]]


def pick(client, name, data=b"PNG"):
    """One file through the Fotoğraflar row's Ekle card, the way the screen sends it: one file, and
    the row it was picked into (madde 320)."""
    return client.post("/api/projects/düğün/references",
                       data={"files": [(BytesIO(data), name)], "kind": "picture"},
                       content_type="multipart/form-data")
```

- [ ] **Adım 2: `test_two_references_are_uploaded_listed_and_one_is_deleted`'ın yorumu** — üç satır
  bire iniyor:

```python
    # A row at a time: a slot is a place inside one kind's row (madde 300).
```

- [ ] **Adım 3: `test_a_deleted_reference_leaves_no_hole_after_a_restart`'ın ardına iki test.**

```python
def test_a_picture_picked_after_the_first_lands_in_slot_two(tmp_path):
    """Madde 414, the user's own steps: one photo in the row, and a second one picked through the
    Ekle card after it. The new one sorts first by name, and still goes where it was picked."""
    client, drive, dist = make_client(tmp_path)
    pick(client, "zeynep.png", b"ONE")

    added = pick(client, "ayse.png", b"TWO")

    assert added.status_code == 200
    assert slots_of(added.get_json()) == [("zeynep.png", 1), ("ayse.png", 2)]
    # The restart: the place is on the disk, not in the process.
    again = client_over(drive, dist).get("/api/projects/düğün/references")
    assert slots_of(again.get_json()) == [("zeynep.png", 1), ("ayse.png", 2)]


def test_the_same_picture_picked_again_lands_in_slot_two(tmp_path):
    """The second kadin.png is stored as kadin-2.png, and "-" sorts before ".": read by name, the
    copy would stand in front of the first every time."""
    client, _drive, _dist = make_client(tmp_path)
    pick(client, "kadin.png", b"ONE")

    added = pick(client, "kadin.png", b"TWO")

    assert slots_of(added.get_json()) == [("kadin.png", 1), ("kadin-2.png", 2)]
```

## Görev 2: `backend/tests/test_reference_usecases.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_reference_usecases.py`

- [ ] **Adım 1: `test_the_pool_lists_in_one_stable_order`'ın belgesi.**

```python
    """Kind by kind: a slot is a place inside a row, so the pool is read a row at a time
    (madde 300)."""
```

- [ ] **Adım 2: `test_the_pool_carries_the_slot_each_reference_stands_in` sırayı dosyalardan sonra
  kurar.**

```python
def test_the_pool_carries_the_slot_each_reference_stands_in():
    orders = FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("kedi.png", b"ONE"), ("kuş.png", b"TWO")], orders=orders)
    orders.write("düğün", {references.PICTURE: ["kuş.png", "kedi.png"]})

    assert [(row["name"], row["slot"]) for row in pool_of(store, pool, orders)] == [
        ("kuş.png", 1), ("kedi.png", 2)]
```

- [ ] **Adım 3: `test_a_removed_name_uploaded_again_goes_to_the_end`'in ardına yeni test.**

```python
def test_an_upload_joins_the_end_of_its_row():
    """Madde 414: what is in the row keeps its slot, whatever the new file is called -- the Ekle card
    stands after the row's last reference, and that is where the file was picked (madde 320)."""
    orders = FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("zeynep.png", b"ONE")], orders=orders)

    answer = add_references(store, pool, orders, FakeClips(), "düğün", [("ayse.png", b"TWO")],
                            row=references.PICTURE)

    assert [(row["name"], row["slot"]) for row in answer] == [("zeynep.png", 1), ("ayse.png", 2)]
    assert [(row["name"], row["slot"]) for row in pool_of(store, pool, orders)] == [
        ("zeynep.png", 1), ("ayse.png", 2)]
```

## Görev 3: Koş, kırmızıyı oku, commit'le

- [ ] **Adım 1: junction'lar** — çalışma ağacında `node_modules` yoksa, bir kez, ana klasörünkine.
- [ ] **Adım 2: dört satır, paralel, olduğu gibi.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'inde **tam üç** kırmızı — yeni üç test, hepsi aynı yerden:
`[("ayse.png", 1), ("zeynep.png", 2)]` ve `[("kadin-2.png", 1), ("kadin.png", 2)]`. Değişen üç test
yeşil. Öteki üç satır yeşil. **Kırmızı başka bir yerden geliyorsa sebep kanıtlanmamıştır:** commit
yok, madde *"bulamadım"* diye döner.

- [ ] **Adım 3: commit** — spec, plan ve iki test dosyası.

```powershell
git add docs/superpowers/specs/2026-10-06-queen-editor-m414-yukleme-yuvasi-testler-design.md docs/superpowers/plans/2026-10-06-queen-editor-m414-yukleme-yuvasi-testler.md queen-editor/backend/tests/test_reference_routes.py queen-editor/backend/tests/test_reference_usecases.py
git commit -m @'
test(queen-editor): Madde 414 red -- a picture picked through the Ekle card lands at the end of its row and the photo before it keeps slot 1, after a restart too and for a same-named copy; one test now sets its order after its files

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
