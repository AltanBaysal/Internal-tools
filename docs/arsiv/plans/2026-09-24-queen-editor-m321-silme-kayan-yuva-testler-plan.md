# Madde 321 — × hemen siliyor, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*. Takımı ve commit'i
> orkestratör koşuyor *(yol haritası, Kol A)*.

**Hedef:** Spec'in beş sunucu, üç ekran testi — kırmızı; giden üç test ve bir bekçi yeniden yazımı.

**Spec:** [m321 test turu](../specs/2026-09-24-queen-editor-m321-silme-kayan-yuva-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**; cümleler tasarımdan harfi harfine. Kaynak kod değişmiyor.
- Bayt değişmezinde ASCII dışı harf olmaz: `test_photo_usecases`'teki adlar ASCII.

---

## Görev 1: `test_references.py`

`test_a_slot_whose_file_is_gone_stays_empty` yerinde yeniden yazılır; `test_a_missing_slot_in_the_middle_is_a_gap`
ve `test_the_last_one_leaving_is_not_a_gap` silinir *(spec, Giden)*.

```python
def test_a_file_gone_from_the_folder_leaves_no_hole():
    """Madde 321: a name the order still holds with no file behind it -- one deleted by hand in
    Drive -- stands in no slot. The ones after it move up, so <Picture 2> is the second picture that
    is really there, which is the one H3 will be handed."""
    order = {references.PICTURE: ["bir.png", "iki.png", "üç.png"]}

    placed = references.placed(order, [item("bir.png", references.PICTURE),
                                       item("üç.png", references.PICTURE)])

    assert [(row["name"], row["slot"]) for row in placed] == [("bir.png", 1), ("üç.png", 2)]
```

## Görev 2: `test_reference_usecases.py`

`test_removing_the_middle_one_leaves_its_slot_empty` yerinde, ardına yeni test:

```python
def test_removing_the_middle_one_moves_the_ones_after_it_up():
    """Madde 321: the slot numbers change, and that is what a prompt's <Picture N> points at from
    now on -- H3 packs the references tight and numbers them by order."""
    orders = FakeOrderStore({"düğün": {references.PICTURE: ["bir.png", "iki.png", "üç.png"]}})
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [(f"{name}.png", b"PNG") for name in ("bir", "iki", "üç")], orders=orders)

    left = remove_reference(store, pool, orders, "düğün", "iki.png")

    assert [(row["name"], row["slot"]) for row in left] == [("bir.png", 1), ("üç.png", 2)]


def test_a_removed_name_uploaded_again_goes_to_the_end():
    """The deleted name keeps no place in the order: a file uploaded under it later is a new
    reference, and a new one goes in at the end of its row (madde 320)."""
    orders = FakeOrderStore({"düğün": {references.PICTURE: ["bir.png", "iki.png", "üç.png"]}})
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [(f"{name}.png", b"PNG") for name in ("bir", "iki", "üç")], orders=orders)
    remove_reference(store, pool, orders, "düğün", "iki.png")

    again = added(store, pool, [("iki.png", b"NEW")], orders=orders)

    assert [(row["name"], row["slot"]) for row in again] == [
        ("bir.png", 1), ("üç.png", 2), ("iki.png", 3)]
```

`test_a_dragged_order_drops_the_names_it_left_out` yerinde:

```python
def test_a_sent_order_keeps_only_the_names_the_pool_holds():
    """A tab left open from before a delete sends a name whose file is gone. The server writes only
    what it can see: a dead name left in the order would pull a later file of that name back into
    the middle of its row."""
    orders = FakeOrderStore()
    store, pool = FakeStore(), FakeReferenceStore()
    added(store, pool, [("bir.png", b"ONE"), ("üç.png", b"THREE")], orders=orders)

    save_reference_order(store, pool, orders,
                         "düğün", {references.PICTURE: ["bir.png", "iki.png", "üç.png"]})

    assert orders.read("düğün") == {references.PICTURE: ["bir.png", "üç.png"]}
```

`ready_pool`'un docstring'i: `"""A pool with one picture in it -- everything a reference run
needs."""`. `test_a_reference_run_with_a_gap_in_the_pool_is_refused` silinir *(Görev 4'e taşınıyor)*.

## Görev 3: `test_reference_routes.py`

`test_a_deleted_reference_leaves_its_slot_where_it_was` yerinde:

```python
def test_a_deleted_reference_leaves_no_hole_after_a_restart(tmp_path):
    """Madde 321: the ones after it move up, and a reload reads the same row."""
    client, drive, dist = make_client(tmp_path)
    upload(client, ("bir.png", b"1"), ("iki.png", b"2"), ("üç.png", b"3"))
    client.put("/api/projects/düğün/references/order",
               json={"order": {"picture": ["bir.png", "iki.png", "üç.png"]}})

    left = client.post("/api/projects/düğün/references/iki.png/delete")

    assert [(row["name"], row["slot"]) for row in left.get_json()["references"]] == [
        ("bir.png", 1), ("üç.png", 2)]
    again = client_over(drive, dist).get("/api/projects/düğün/references")
    assert [(row["name"], row["slot"]) for row in again.get_json()["references"]] == [
        ("bir.png", 1), ("üç.png", 2)]
```

## Görev 4: `test_photo_usecases.py`

`FakeReferenceOrders` bir sıra alıyor; `run_references` `orders=None` alıp geçiriyor
*(`orders or FakeReferenceOrders()`)*. `test_a_reference_job_is_rendered_with_the_pools_own_files`'ın
ardına:

```python
def test_a_file_gone_from_the_pool_by_hand_does_not_stop_a_reference_run():
    """Madde 321: the order still names a file deleted in Drive, and that is no hole -- the run goes
    ahead, and H3 is handed what is really there, in order."""
    store, record, plan_store = FakeStore(), FakeRecord(), FakePlanStore()
    generator = FakeGenerator()

    added = run_references(store, record, plan_store, generator=generator,
                           pool=FakePool(["kedi.png", "kus.png"]),
                           orders=FakeReferenceOrders(
                               {"picture": ["kedi.png", "at.png", "kus.png"]}))

    assert added == 1
    assert generator.references == [[("kedi.png", b"kedi.png bytes", "picture"),
                                     ("kus.png", b"kus.png bytes", "picture")]]
```

## Görev 5: `ReferencePanel.test.jsx`

İlk bloktan `draws the slot a deleted reference left empty` ve `asks before taking a reference out`
çıkar; dosyanın sonuna:

```js
describe("ReferencePanel — deleting at once (madde 321)", () => {
  const tile = (container, name) => container.querySelector(`[data-reference="${name}"]`);
  const picture = (name, slot) => ({ name, kind: "picture", seconds: null, slot });
  const bin = (name) => screen.getByLabelText(`${name} referansını sil`);

  it("deletes at once, with no window", async () => {
    await open();
    removeReference.mockResolvedValue(pool([]));

    await act(async () => { fireEvent.click(bin("kedi.png")); });

    expect(removeReference).toHaveBeenCalledWith("düğün", "kedi.png");
    expect(screen.queryByText("kedi.png silinsin mi?")).toBeNull();
    expect(screen.getByText("Fotoğraflar 0/9")).toBeTruthy();
  });

  it("numbers the row the way the server answers after a delete", async () => {
    const { container } = await open(pool([picture("bir.png", 1), picture("iki.png", 2),
                                            picture("üç.png", 3)]));
    removeReference.mockResolvedValue(pool([picture("bir.png", 1), picture("üç.png", 2)]));

    await act(async () => { fireEvent.click(bin("iki.png")); });

    // The ones after it move up. The server packs the row, so the N of <Picture N> is its to say.
    expect(within(tile(container, "üç.png")).getByText("2")).toBeTruthy();
    expect(tile(container, "iki.png")).toBeNull();
  });

  it("clears the refusal at the top of the pool", async () => {
    await open();
    uploadReferences.mockRejectedValueOnce(
      new Error("kisa-2.wav fotoğraf yuvasına giremez — bu dosya ses."));
    await act(async () => { pick([new File([new Uint8Array([1])], "kisa-2.wav")]); });
    removeReference.mockResolvedValue(pool([]));

    await act(async () => { fireEvent.click(bin("kedi.png")); });

    // Madde 320's rule: the next pick or delete clears it.
    expect(screen.queryByText(/yuvasına giremez/)).toBeNull();
  });
});
```

## Görev 6: Koşu ve kırmızı commit *(orkestratör)*

- [ ] Dört satır — pytest'te beş, vitest'te üç test kırmızı; `test_a_sent_order_keeps_only_the_names_the_pool_holds`
      yeşil; `queen-agent` satırları yeşil.
- [ ] `test(m321): …(red)`.
