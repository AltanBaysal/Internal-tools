# Madde 427 — Bir satırı sürüklemek öteki satırların sırasını silmesin, test turunun planı

> **Koşum:** bu oturumda, satır satır. Adımlar `- [ ]` ile işaretlenir. Bu turda kaynak kod
> değişmiyor; testler kırmızı commit'lenir.

**Hedef:** Bir satırı sürüklemenin yalnız o satırın sırasını değiştirdiğini, öteki satırların kayıtlı
sıralarında kaldığını, ve bunun yeniden başlatmadan sonra da sürdüğünü söyleyen testler — bugün
kırmızı, ve kırmızı oldukları yer sebebi kanıtlıyor.

**Yaklaşım:** Kullanıcının yolu gerçek kapıdan ve gerçek klasörden: `test_reference_routes.py`'nin
sunucusu, dosyalar ve sıra ekranın gönderdiği biçimde. Kural sahte portlarla use case'te, üç satırla.

**Araçlar:** pytest, Flask'ın test istemcisi.

**Spec:** [m427 test turu](../specs/2026-10-06-queen-editor-m427-surukleme-sirasi-testler-design.md)

## Her yere geçerli kurallar

- Test adları, docstring'ler ve yorumlar **İngilizce**.
- Testler yalnız CLAUDE.md'nin dört satırıyla, olduğu gibi, paralel koşulur; `skip` / `xfail` yok.
- Hiçbir test gerçek bir Drive'a dokunmaz: kapı testleri `tmp_path`'te.

**Arayüz — uygulama turunun vereceği:** yok. Kapı ve use case bugünkü imzalarıyla; değişen yalnız
belgede sürüklenmeyen satırların kalması.

---

## Görev 1: `backend/tests/test_reference_routes.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_reference_routes.py`

- [ ] **Adım 1: `pick` satırın tipini de alır** — varsayılan `"picture"`, bugünkü çağrılar aynı.

```python
def pick(client, name, data=b"PNG", kind="picture"):
    """One file through a row's Ekle card, the way the screen sends it: one file, and the row it was
    picked into (madde 320)."""
    return client.post("/api/projects/düğün/references",
                       data={"files": [(BytesIO(data), name)], "kind": kind},
                       content_type="multipart/form-data")
```

- [ ] **Adım 2: `test_the_same_picture_picked_again_lands_in_slot_two`'nun ardına yeni test.**

```python
def test_dragging_the_videos_leaves_the_pictures_where_they_stood(tmp_path):
    """Madde 427, the user's path: photos whose saved order is not their name order -- the second
    one sorts first -- and then a drag in the videos row. The screen sends the dragged row alone, and
    the photos stay where they stood."""
    client, drive, dist = make_client(tmp_path)
    pick(client, "zeynep.png", b"ONE")
    pick(client, "ayse.png", b"TWO")
    pick(client, "bir.mp4", b"MP4", kind="video")
    pick(client, "iki.mp4", b"MP4", kind="video")

    dragged = client.put("/api/projects/düğün/references/order",
                         json={"order": {"video": ["iki.mp4", "bir.mp4"]}})

    assert dragged.status_code == 200
    assert slots_of(dragged.get_json()) == [
        ("zeynep.png", 1), ("ayse.png", 2), ("iki.mp4", 1), ("bir.mp4", 2)]
    # The restart: the order is on the disk, not in the process.
    again = client_over(drive, dist).get("/api/projects/düğün/references")
    assert slots_of(again.get_json()) == [
        ("zeynep.png", 1), ("ayse.png", 2), ("iki.mp4", 1), ("bir.mp4", 2)]
```

## Görev 2: `backend/tests/test_reference_usecases.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_reference_usecases.py`

- [ ] **Adım 1: `test_a_sent_order_keeps_only_the_names_the_pool_holds`'un ardına yeni test.**

```python
def test_a_dragged_row_leaves_every_other_row_as_it_was_saved():
    """Madde 427: a drag sends its own row alone, and the rows it did not touch keep the order they
    were saved in. Each row is saved against its name order, so a row that fell back to reading by
    name would show."""
    orders = FakeOrderStore({"düğün": {references.PICTURE: ["zeynep.png", "ayse.png"],
                                       references.VIDEO: ["iki.mp4", "bir.mp4"],
                                       references.AUDIO: ["rüzgar.wav", "kuş.wav"]}})
    store, pool = FakeStore(), FakeReferenceStore()
    for name in ("zeynep.png", "ayse.png", "bir.mp4", "iki.mp4", "rüzgar.wav", "kuş.wav"):
        pool.save("düğün", name, b"FILE")

    left = save_reference_order(store, pool, orders,
                                "düğün", {references.VIDEO: ["bir.mp4", "iki.mp4"]})

    assert orders.read("düğün") == {references.PICTURE: ["zeynep.png", "ayse.png"],
                                    references.VIDEO: ["bir.mp4", "iki.mp4"],
                                    references.AUDIO: ["rüzgar.wav", "kuş.wav"]}
    assert [(row["name"], row["slot"]) for row in left] == [
        ("zeynep.png", 1), ("ayse.png", 2), ("bir.mp4", 1), ("iki.mp4", 2),
        ("rüzgar.wav", 1), ("kuş.wav", 2)]
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

Beklenen: `queen-editor` pytest'inde **tam iki** kırmızı — yeni iki test, ikisi de aynı yerden:
kapıda `[("ayse.png", 1), ("zeynep.png", 2), …]`, use case'te belgede yalnız `video` satırı.
Öteki üç satır yeşil. **Kırmızı başka bir yerden geliyorsa sebep kanıtlanmamıştır:** commit yok,
madde *"bulamadım"* diye döner.

- [ ] **Adım 3: commit** — spec, plan ve iki test dosyası.

```powershell
git add docs/specs/2026-10-06-queen-editor-m427-surukleme-sirasi-testler-design.md docs/plans/2026-10-06-queen-editor-m427-surukleme-sirasi-testler-plan.md queen-editor/backend/tests/test_reference_routes.py queen-editor/backend/tests/test_reference_usecases.py
git commit -m @'
test(queen-editor): Madde 427 red -- a drag in one row of the reference pool leaves every other row in its saved order, after a restart too; today the pictures fall back to name order when the videos are dragged

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
