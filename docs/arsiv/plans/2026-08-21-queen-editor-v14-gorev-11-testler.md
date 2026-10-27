# v14 Görev 11 — Kart kopyalama: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kart kopyalamanın ne yapacağını 29 testle yazmak ve kırmızı commit etmek. Kaynak kodda tek
satır değişmiyor.

**Architecture:** Dört dosya, dört katman: ad kuralı, iş kuralı, rota, ekran. Her katman kendi test
dosyasında, çünkü hepsi bugün de orada.

**Tech Stack:** pytest, Flask test client, React 18 + vitest + @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-11-kart-kopyalama-testler-design.md)

## Global Constraints

- **Bu tur yalnız test yazar.** `backend/` ve `frontend/src` altındaki kaynak dosyalar
  değişmiyor — testler kırmızı gidiyor.
- Test adları ve yorumlar **İngilizce**; ekran metni ve doküman **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `skip` / `xfail` yok.
- Henüz olmayan adlar: `photo_name.copy_id`, `photo_name.copy_parts`, `copy_frame.next_copy_id`,
  `usecases.copy_frames.copy_frames`, `usecases.copy_frames.InvalidFrames`, Gallery'nin `onCopy`
  prop'u. İlk dördü python dosyalarının başında içe aktarılıyor, yani üç dosya **toplanamıyor** ve
  `test_export.py` de onlarla düşüyor — bu turda queen-editor'ın python takımı hiç koşmuyor ve bu
  bilinerek kabul ediliyor (spec, "Kabuk hattı").

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/tests/test_photo_name.py` | kopyanın adı | 4 test |
| `backend/tests/test_photo_usecases.py` | kopyalama işi | 14 test |
| `backend/tests/test_photo_routes.py` | rota ve gerçek dosyalar | 3 test |
| `frontend/src/features/photo_generation/Gallery.test.jsx` | bar ve kısayol | 8 test |

---

### Task 1: Kopyanın adı

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_name.py`

**Interfaces:**
- Consumes: `photo_name.copy_id(base, index) -> str`, `photo_name.copy_parts(name) -> (int|None, str)`,
  `copy_frame.next_copy_id(ids, source) -> str` — henüz yok, uygulama turunda doğacak.

- [ ] **Step 1: İçe aktarmaları büyüt**

`copy_frame` satırına `next_copy_id`, `photo_name` listesine `copy_id` ve `copy_parts` ekle,
alfabetik yerlerine.

- [ ] **Step 2: Dört testi yaz**

Dosyanın sonuna:

```python
def test_a_twin_is_named_after_its_source_with_the_prefix_in_front():
    # At the front, because a suffix would read as another layer round (madde 78).
    assert copy_id("P11_1", 1) == "C1_P11_1"
    assert copy_id("P11_1", 2) == "C2_P11_1"


def test_a_twin_still_claims_its_sources_prompt_number_and_variant():
    # It is holding the source's picture, and that picture was made by prompt 11.
    assert (number_of("C1_P11_1"), variant_of("C1_P11_1")) == (11, 1)
    # The legacy scheme reads the same way through the prefix.
    assert (number_of("C2_11_b"), variant_of("C2_11_b")) == (11, 1)


def test_a_name_with_no_prefix_is_its_own_base():
    assert copy_parts("P11_1") == (None, "P11_1")
    assert copy_parts("C1_P11_1") == (1, "P11_1")
    # A copy of a copy is another copy of the same base -- the prefix never nests.
    assert copy_parts("C2_P11_1") == (2, "P11_1")


def test_a_twin_takes_the_next_copy_index_its_base_has_ever_carried():
    # Counting from one, never reusing a gap: a deleted twin keeps its line in the record, so its
    # name stays claimed -- next_id's rule, for the same reason.
    assert next_copy_id({"P11_1"}, "P11_1") == "C1_P11_1"
    assert next_copy_id({"P11_1", "C1_P11_1", "C3_P11_1"}, "P11_1") == "C4_P11_1"
    # Copying the copy counts against the same base rather than nesting the prefix.
    assert next_copy_id({"P11_1", "C1_P11_1"}, "C1_P11_1") == "C2_P11_1"
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_photo_name.py` toplanamıyor — `ImportError: cannot import name 'next_copy_id'`.

---

### Task 2: Kopyalama işi

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `copy_frames(record, store, plan_store, order_store, now, project, frames)` →
  `{"copies": [identity, ...]}`, ve `InvalidFrames` — henüz yok.

- [ ] **Step 1: İçe aktarmayı ekle**

`remove_frames` içe aktarmasının hemen üstüne:

```python
from backend.features.photo_generation.domain.usecases.copy_frames import (
    InvalidFrames,
    copy_frames,
)
```

- [ ] **Step 2: Yardımcıyı ve on dört testi yaz**

`test_nothing_is_written_to_the_order_file_when_no_copy_is_born` testinin hemen altına, kopya
karelerin bölümünün sonuna:

```python
def twin_project(*frames):
    """A project whose named frames are produced photos, with a store and an order file.

    The order file is written here rather than left empty: what a copy has to prove is where it
    lands, and a gallery nobody has dragged has no sequence of its own to land in.
    """
    store, record, plan_store = video_project(*frames)
    order = FakeOrderStore([f"{number}_a" for number, _letter in reversed(frames)])
    return store, record, plan_store, order


def copy_of(record, store, plan_store, order, names, project="düğün"):
    return copy_frames(record, store, plan_store, order, lambda: "t", project, names)


def test_a_twin_carries_every_layer_its_source_holds():
    store, record, plan_store, order = twin_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    record.append("düğün", {"file": "0_a_V1_0_S1_0.wav", "frame": "0_a", "layer": "audio",
                            "status": "done"})

    copy_of(record, store, plan_store, order, ["0_a"])

    # Everything, not everything below something: the twin has nothing left to produce.
    assert list(record.slots("düğün")["C1_0_a"]) == ["photo", "video", "audio"]


def test_a_twins_rows_point_at_its_sources_own_files():
    store, record, plan_store, order = twin_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    copy_of(record, store, plan_store, order, ["0_a"])

    twin = record.slots("düğün")["C1_0_a"]
    assert twin["photo"]["file"] == "0_a.png"
    assert twin["video"]["file"] == "0_a_V1_0.mp4"
    assert store.saved == []                     # one picture on disk, two frames holding it


def test_a_twin_carries_the_words_each_layer_was_made_from():
    store, record, plan_store, order = twin_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})

    copy_of(record, store, plan_store, order, ["0_a"])

    assert record.prompts("düğün")["C1_0_a"] == {"photo": "p", "video": "kadın dönüyor"}


def test_a_twin_carries_the_videos_mode_and_where_it_ended():
    store, record, plan_store, order = twin_project((0, "a"), (1, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "mode": "linked", "endsOn": "1_a.png"})

    copy_of(record, store, plan_store, order, ["0_a"])

    twin = record.slots("düğün")["C1_0_a"]["video"]
    assert (twin["mode"], twin["endsOn"]) == ("linked", "1_a.png")


def test_nothing_is_owed_on_a_twin():
    store, record, plan_store, order = twin_project((0, "a"))

    copy_of(record, store, plan_store, order, ["0_a"])

    # No plan line at all: an exact twin has nothing left to make, so the queue never hears of it.
    assert plan_store.appended == []
    twin = [f for f in list_frames(record, store, plan_store, order, "düğün")
            if f["id"] == "C1_0_a"][0]
    assert (twin["owed"], twin["status"]) == ([], "done")


def test_a_twin_lands_directly_above_its_source():
    store, record, plan_store, order = twin_project((0, "a"), (1, "a"))

    copy_of(record, store, plan_store, order, ["0_a"])

    assert order.order == ["1_a", "C1_0_a", "0_a"]
    assert [f["id"] for f in list_frames(record, store, plan_store, order, "düğün")] == [
        "1_a", "C1_0_a", "0_a"]


def test_the_answer_names_the_twins_that_were_born():
    store, record, plan_store, order = twin_project((0, "a"), (1, "a"))

    answer = copy_of(record, store, plan_store, order, ["0_a", "1_a"])

    # The screen moves the selection onto them, so it has to be told their names.
    assert answer == {"copies": ["C1_0_a", "C1_1_a"]}


def test_a_second_copy_is_a_copy_of_the_copy_rather_than_a_nested_name():
    store, record, plan_store, order = twin_project((0, "a"))

    copy_of(record, store, plan_store, order, ["0_a"])
    answer = copy_of(record, store, plan_store, order, ["C1_0_a"])

    assert answer == {"copies": ["C2_0_a"]}
    # And it sits above the one it was made from, not above the original.
    assert order.order == ["C2_0_a", "C1_0_a", "0_a"]


def test_a_frame_that_is_not_produced_yet_is_skipped():
    # There is nothing to twin: a pending frame owns no layer at all (Fark 79). The plan's own
    # naming gives this frame the identity 0_a -- FakePlanStore reads a letter-scheme frame back
    # the way the projects already on Drive carry it.
    store, record = FakeStore(), FakeRecord()
    plan_store, order = FakePlanStore(frames=[frame(0)]), FakeOrderStore()

    answer = copy_of(record, store, plan_store, order, ["0_a"])

    assert answer == {"copies": []}
    assert record.rows == []


def test_an_identity_the_gallery_does_not_know_is_skipped_rather_than_refused():
    # Another tab can delete a frame while this selection sits open; refusing the whole press over
    # one name that is already gone would leave the rest undone.
    store, record, plan_store, order = twin_project((0, "a"))

    answer = copy_of(record, store, plan_store, order, ["7_z", "0_a"])

    assert answer == {"copies": ["C1_0_a"]}


def test_a_layer_that_blew_up_is_not_carried_into_the_twin():
    # The red video names a file that is not on disk; a done row about it would claim it is.
    store, record, plan_store, order = twin_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "failed", "error": "node 41"})

    copy_of(record, store, plan_store, order, ["0_a"])

    assert list(record.slots("düğün")["C1_0_a"]) == ["photo"]


def test_nothing_is_written_to_the_order_file_when_nothing_was_copied():
    store, record = FakeStore(), FakeRecord()
    plan_store, order = FakePlanStore(frames=[frame(0)]), FakeOrderStore()

    copy_of(record, store, plan_store, order, ["0_a"])

    assert order.order == []


@pytest.mark.parametrize("names", ["0_a", [7], None])
def test_copying_needs_a_list_of_identities(names):
    store, record, plan_store, order = twin_project((0, "a"))

    with pytest.raises(InvalidFrames):
        copy_of(record, store, plan_store, order, names)


def test_copying_in_a_project_that_is_not_there_is_refused():
    store, record, plan_store, order = twin_project((0, "a"))

    with pytest.raises(ProjectMissing):
        copy_of(record, store, plan_store, order, ["0_a"], project="yok")
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: bu dosya da toplanamıyor — `ModuleNotFoundError: ... usecases.copy_frames`.

---

### Task 3: Rota ve gerçek dosyalar

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_routes.py`

**Interfaces:**
- Consumes: `POST /api/projects/<project>/frames/copy`, gövde `{frames: [...]}`, cevap
  `{copies: [...], frames: [...]}`.

- [ ] **Step 1: İçe aktarmayı ve bağlamayı ekle**

`remove_frames` içe aktarmasının üstüne:

```python
from backend.features.photo_generation.domain.usecases.copy_frames import copy_frames
```

`make_client` içindeki `remove_frames=partial(...)` satırının hemen üstüne:

```python
        copy_frames=partial(copy_frames, record, store, plan_store, order_store,
                            lambda: "2026-08-05T10:00:00+00:00"),
```

- [ ] **Step 2: Üç testi yaz**

`copy_frames_request` `delete_photos_request`'in hemen üstüne giriyor — iki yardımcı yan yana
duruyor, üç test ikisinin de altında, çünkü ikizi silen test her ikisini de çağırıyor:

```python
def copy_frames_request(client, frames, project="düğün"):
    return client.post(f"/api/projects/{project}/frames/copy", json={"frames": frames})


def test_the_copy_route_answers_with_the_twins_and_the_gallery_they_landed_in(tmp_path):
    client, _drive = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)

    answer = copy_frames_request(client, ["P0_0"])

    assert answer.status_code == 200
    body = answer.get_json()
    assert body["copies"] == ["C1_P0_0"]
    # The gallery comes back with it: the screen would ask for exactly this in a second round-trip.
    assert [f["id"] for f in body["frames"]] == ["P1_0", "C1_P0_0", "P0_0"]


def test_deleting_one_twin_leaves_the_others_picture_on_the_disk(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    copy_frames_request(client, ["P0_0"])

    delete_photos_request(client, ["C1_P0_0"])

    # One picture, two frames holding it: the last of them to let go is what unlinks it.
    assert (drive / "düğün" / "P0_0.png").exists()
    gallery = client.get("/api/projects/düğün/frames").get_json()["frames"]
    assert [f["id"] for f in gallery] == ["P0_0"]


def test_a_copy_body_that_is_not_a_list_of_identities_is_refused(tmp_path):
    client, _drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    answer = copy_frames_request(client, "P0_0")

    assert answer.status_code == 400
    assert "metin dizisi" in answer.get_json()["error"]
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: üçüncü dosya da toplanamıyor. Bu turda python takımı toplama hatasıyla duruyor.

---

### Task 4: Bar ve kısayol

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: Gallery'nin `onCopy(frames) -> Promise<string[]>` prop'u — henüz yok.

- [ ] **Step 1: Sekiz testi yaz**

`describe("Gallery selection mode", ...)` bloğunun **kapanışından sonra**, yeni bir blok olarak:

```jsx
describe("Gallery — copying a card", () => {
  const twins = (copies) => vi.fn().mockResolvedValue(copies);

  it("puts Kopyala in the bar, to the left of Sil", () => {
    renderGallery({ onCopy: twins(["C1_1_a"]) });
    fireEvent.click(checkOf("1_a.png"));

    const bar = screen.getByText("1 seçili").parentElement;
    const words = [...bar.querySelectorAll("button")].map((one) => one.textContent);
    expect(words).toEqual(["Tümünü seç", "Kopyala", "Sil", "Vazgeç"]);
  });

  it("draws no Kopyala when only frames that are not produced are selected", () => {
    renderGallery({ frames: [pending("2_a.png"), done("1_a.png")], onCopy: twins([]) });
    fireEvent.click(checkOf("2_a.png"));

    // Nothing in the selection owns a layer, so there is nothing to press (Fark 79).
    expect(screen.queryByText("Kopyala")).toBeNull();
    expect(screen.getByText("Sil")).toBeTruthy();
  });

  it("copies only the produced frames of a mixed selection", async () => {
    const onCopy = twins(["C1_1_a"]);
    renderGallery({ frames: [pending("2_a.png"), done("1_a.png")], onCopy });
    fireEvent.click(checkOf("2_a.png"));
    fireEvent.click(checkOf("1_a.png"));

    await act(async () => { fireEvent.click(screen.getByText("Kopyala")); });

    expect(onCopy).toHaveBeenCalledWith(["1_a"]);
  });

  it("moves the selection onto the twins", async () => {
    const onCopy = twins(["C1_1_a"]);
    // The gallery the server would answer with: the twin already sits above its source.
    renderGallery({ frames: [done("2_a.png"), done("C1_1_a.png"), done("1_a.png")], onCopy });
    fireEvent.click(checkOf("1_a.png"));

    await act(async () => { fireEvent.click(screen.getByText("Kopyala")); });

    // How the copy is noticed: no notification of its own (Fark 77).
    expect(screen.getByText("1 seçili")).toBeTruthy();
    expect(checkOf("C1_1_a.png").className).toContain("qe-check--on");
    expect(checkOf("1_a.png").className).not.toContain("qe-check--on");
  });

  it("copies with Ctrl + D as well as with the button", async () => {
    const onCopy = twins(["C1_1_a"]);
    renderGallery({ onCopy });
    fireEvent.click(checkOf("1_a.png"));

    await act(async () => { fireEvent.keyDown(window, { key: "d", ctrlKey: true }); });

    expect(onCopy).toHaveBeenCalledWith(["1_a"]);
  });

  it("takes Ctrl + D away from the browser", () => {
    renderGallery({ onCopy: twins(["C1_1_a"]) });
    fireEvent.click(checkOf("1_a.png"));

    // Left alone it opens the bookmark window, which is never what was meant over a selection.
    const taken = !fireEvent.keyDown(window, { key: "d", ctrlKey: true, cancelable: true });

    expect(taken).toBe(true);
  });

  it("leaves Ctrl + D alone while the confirm window is open", () => {
    const onCopy = twins(["C1_1_a"]);
    renderGallery({ onCopy });
    fireEvent.click(checkOf("1_a.png"));
    fireEvent.click(screen.getByText("Sil"));

    fireEvent.keyDown(window, { key: "d", ctrlKey: true });

    // The window owns the keyboard while it is up -- the same rule Esc follows.
    expect(onCopy).not.toHaveBeenCalled();
  });

  it("presses nothing when the shortcut is used on a selection with nothing to copy", () => {
    const onCopy = twins([]);
    renderGallery({ frames: [pending("2_a.png"), done("1_a.png")], onCopy });
    fireEvent.click(checkOf("2_a.png"));

    fireEvent.keyDown(window, { key: "d", ctrlKey: true });

    expect(onCopy).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: queen-agent'ın ikisi yeşil (384 / 474). queen-editor python dört toplama hatasıyla
duruyor. queen-editor frontend'de **5 kırmızı**, ve üç test doğuştan yeşil:

| Test | Neden bugün de yeşil |
|---|---|
| Kopyala doğmuyor | Düğme hiç yok, yokluğu her seçimde doğru |
| Onay penceresi açıkken çalışmıyor | Kısayolu dinleyen kimse yok |
| Kopyalanacak kare yokken göndermiyor | Aynısı |

Üçü de bir yokluğu ölçüyor ve o yokluk bugün zaten doğru. Kırmızıya zorlamak, testi değil kaynağı
test turunda değiştirmek olurdu; nöbeti uygulama turunda tutuyorlar.

---

### Task 5: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): a card can be copied, and the copy is an exact twin

Twenty-nine tests for what copying a card means. The twin carries every layer its source
really holds -- picture, video and sound, with the words, the mode and the frame the video
ended on -- and its rows point at the source's own files, so one picture is held by two
frames. Nothing is owed on it: an exact twin has nothing left to make, so the queue never
hears of it and no plan line is written.

Its name is its source's with a prefix in front: P11_1 copied is C1_P11_1. At the front
because a suffix would read as another layer round. Copying the copy gives C2_P11_1 rather
than a nested name, and the number and variant are still read through the prefix -- the
twin is holding prompt 11's picture, so it belongs to prompt 11's family.

It lands directly above its source and the selection moves onto it. That is how the copy
is noticed; there is no notification of its own.

In the bar Kopyala stands to the left of Sil, and it is not drawn at all when the selection
holds nothing that has been produced. Ctrl + D does the same thing and is taken from the
browser, which owns it for bookmarks. The confirm window keeps the keyboard while it is up.

A layer that blew up is not carried: it names a file that is not on disk, and a done row
about it would claim it is.

The route mirrors the delete one -- POST frames/copy -- and answers with the twins and the
gallery they landed in. Deleting one twin leaves the other's picture where it is; that is
proved end to end, with real files.

Three python test files import names that do not exist yet, so queen-editor's python suite
does not collect at all this round -- test_export.py comes down with them, since it borrows
their helpers. Honest red with its cost written down: the alternative was a skeleton class,
which is touching the source in a test-only tour.

Three of the eight screen tests are born green: they measure an absence that is already
true, because there is no button and nothing listening for the key. Forcing them red would
mean changing the source in a test-only tour. They take up their watch in the next one.

queen-agent green (384 / 474). queen-editor frontend: 5 red.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in 29 testi Task 1 (1–4), Task 2 (5–18), Task 3 (19–21), Task 4 (22–29).

**Tip tutarlılığı:** `copy_frames` her yerde `{"copies": [...]}` döndürüyor; rota bunun üstüne
`frames` ekliyor, yani iş kuralı galeriyi tanımıyor. `copy_parts` her yerde `(int|None, str)`.

**Kontrol edilen tuzak:** 23. test seçime **bekleyen** bir kare koyuyor ama galeride üretilmiş bir
kare de var — düğmenin yokluğu galerinin boşluğundan değil, seçimin kendisinden geliyor.

**Kontrol edilen tuzak 2:** 25. test galeriye ikizi baştan koyuyor. Gerçekte ikiz sunucudan gelen
yeni listeyle doğar; Gallery'nin işi yalnız seçimi ona taşımak, ve testin ölçtüğü tam olarak bu.

**Kontrol edilen tuzak 3:** 27. test `fireEvent.keyDown`'ın dönüş değerini okuyor —
`dispatchEvent` `preventDefault` çağrıldığında `false` veriyor. `cancelable: true` şart, yoksa olay
zaten iptal edilemez ve test her hâlde yeşil görünür.

**Kontrol edilen tuzak 4:** 9. test hem plan satırının hiç yazılmadığını hem de galerideki kaydın
borçsuz olduğunu ölçüyor — ikisi ayrı gerçek: plan sessiz kalsa bile `owed` başka bir yerden
dolabilirdi.

**Kontrol edilen tuzak 5:** `frame(0)` planda `0_a` kimliğiyle okunuyor, `P0_0` ile değil —
`FakePlanStore` harf şemasını Drive'daki projelerin taşıdığı gibi geri veriyor. Bekleyen kareyi
atlayan iki test bu adı kullanıyor.

**Bilerek dışarıda:** `useGeneration` ve `api.js`. Bugün `removeFrames`/`removePhotos` da o
dosyalarda sınanmıyor; rota testi sunucu tarafını, Gallery testleri ekran tarafını tutuyor.
