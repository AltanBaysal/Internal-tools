# Madde 320 — Sıranın kendi `Ekle` kartı, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Spec'in dokuz testi ve iki değişen ekran testi — kırmızı.

**Spec:** [m320 test turu](../specs/2026-09-24-queen-editor-m320-ekle-karti-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**; cümleler tasarımdan harfi harfine. Kaynak kod değişmiyor.

---

## Görev 1: Sunucu

`test_reference_usecases.py` — `test_a_reference_for_a_project_that_does_not_exist_is_refused`'ın
önüne:

```python
def test_a_file_of_another_kind_is_refused_by_the_row_it_was_picked_into():
    """Madde 320: a row's own Ekle card picks into that row, and that a sound is not a picture is
    the server's rule to say (FOUNDATION 4). Nothing is written."""
    store, pool = FakeStore(), FakeReferenceStore()

    with pytest.raises(UnknownReference) as exc:
        add_references(store, pool, FakeOrderStore(), FakeClips(), "düğün",
                       [("kisa-2.wav", b"WAV")], row=references.PICTURE)

    assert str(exc.value) == "kisa-2.wav fotoğraf yuvasına giremez — bu dosya ses."
    assert pool.pools == {}


def test_a_file_of_its_rows_kind_goes_into_that_row():
    store, pool = FakeStore(), FakeReferenceStore()

    answer = add_references(store, pool, FakeOrderStore(), FakeClips(), "düğün",
                            [("kedi.png", b"PNG")], row=references.PICTURE)

    assert answer == [picture()]
```

`test_reference_routes.py` — `test_the_order_is_saved_and_read_back`'in önüne:

```python
def test_the_row_a_file_was_picked_into_comes_with_the_upload(tmp_path):
    """Madde 320: the screen says which row's card the file came from, and the server holds the
    file to it."""
    client, drive, _dist = make_client(tmp_path)

    resp = client.post("/api/projects/düğün/references",
                       data={"files": [(BytesIO(b"WAV"), "kisa-2.wav")], "kind": "picture"},
                       content_type="multipart/form-data")

    assert resp.status_code == 400
    assert resp.get_json()["error"] == "kisa-2.wav fotoğraf yuvasına giremez — bu dosya ses."
    assert not (drive / "düğün" / "referans").exists()
```

## Görev 2: `api.test.js`

```js
  it("sends the row a file was picked into with the upload", async () => {
    // Madde 320: which row's card a file came from is the server's to hold the file to.
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ references: [] }));
    vi.stubGlobal("fetch", fetchMock);
    const file = new File([new Uint8Array([1])], "kedi.png", { type: "image/png" });

    await api.uploadReferences("düğün", [file], "picture");

    expect(fetchMock.mock.calls[0][1].body.get("kind")).toBe("picture");
  });
```

## Görev 3: `ReferencePanel.test.jsx`

`pick(files, card = "fotoğraf ekle")`; değişen iki test *(spec'te)*; dosyanın sonuna *"adding from a
row's card"* bloğu — beş test: seçicilerin `accept`'i ve `multiple`'ı; `uploadReferences("düğün",
[dosya], "video")`; yoldaki kartın `Yükleniyor…`'su ve üç seçicinin kapalı olması; retin sıraların
üstünde durması *(`compareDocumentPosition`)* ve sonraki seçimde gitmesi; `Ekle` adında bir seçici
olmaması. Kod test dosyasında, bu planla aynı commit'te.

## Görev 4: Koşu ve kırmızı commit

- [ ] Dört satır — pytest'te üç, vitest'te altı yeni ve iki değişen test kırmızı.
- [ ] `test(m320): …(red)`.
