# v14 Görev 8 — Detayda Üretim modu bilgi satırı: TEST döngüsü (test planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Videonun vardığı fotoğrafı kayda geçiren zincirin ve detay sayfasındaki bilgi satırının on
iki testini yazmak, kırmızı bırakmak.

**Architecture:** Üç test dosyası. Motor–kayıt–galeri–kopya halkası 7. maddedekiyle aynı yol, bu kez
`endsOn` alanı için; ön yüzde satırın kendisi.

**Tech Stack:** pytest, vitest, @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-8-mod-bilgi-satiri-testler-design.md)

## Global Constraints

- **Yalnız test dosyaları değişiyor.**
- **`skip` / `xfail` yok.**
- Test adları ve yorumları **İngilizce**; ekranda aranan metinler **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komutlar dört satır, birebir, boru yok.
- **`dist` bu turda derlenmiyor.**
- `FakeRecord.slots` 7. maddede `mode`'u katlamayı öğrendi; şimdi `endsOn`'u da öğreniyor.

## Beklenen şekiller

| Halka | Şekil |
|---|---|
| Satır | `{…, "layer": "video", "mode": "linked", "endsOn": "1_a.png"}` |
| Hücre | `{"status": "done", "file": …, "mode": "linked", "endsOn": "1_a.png"}` |
| Kare | `{…, "modes": {"video": "linked"}, "endsOn": {"video": "1_a.png"}}` |
| Satır (ekran) | `Üretim modu` · `Sonrakine bağla → 1_a.png` |

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/tests/test_photo_usecases.py` | motor, galeri cevabı, kopya | `FakeRecord.slots` + 5 test |
| `backend/tests/test_photo_record.py` | gerçek kaydın katlaması | 1 test |
| `frontend/src/features/photo_generation/PhotoDetail.test.jsx` | bilgi satırı | 6 test |

---

### Task 1: Sahte kayıt ikinci alanı da katlıyor

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Produces: `FakeRecord.slots()` hücresinde `endsOn`. Task 3 ve Task 4 buna dayanıyor.

- [ ] **Step 1: `slots`'a ekle**

```python
            if isinstance(row.get("mode"), str):
                cell["mode"] = row["mode"]
            if isinstance(row.get("endsOn"), str):
                cell["endsOn"] = row["endsOn"]
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: 647 yeşil — kimse bu alanı henüz okumuyor.

---

### Task 2: Motor vardığı yeri satıra yazıyor

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `render_one_video(mode, linked_to=…)` ve Task 1'den bağımsız olarak `video_row(record)`.

- [ ] **Step 1: Üç testi yaz**

`test_a_job_that_names_no_mode_leaves_the_field_off_its_row`'un altına:

```python
def test_a_linked_video_names_the_picture_it_ended_on():
    """The detail page prints this name. Recorded rather than resolved later from the target's
    identity: the frame it points at can be deleted while the video it made stays, and then there
    would be no name to print for a video that really did arrive somewhere."""
    _generator, record = render_one_video(production_mode.LINKED, linked_to="1_a")

    assert video_row(record)["endsOn"] == "1_a.png"


def test_a_loop_video_names_its_own_picture():
    # One rule rather than one per mode: whatever the render was handed as an ending picture is what
    # the row names. Teaching the engine which modes have an ending would be the modes' own rule
    # written a second time.
    _generator, record = render_one_video(production_mode.LOOP)

    assert video_row(record)["endsOn"] == "0_a.png"


def test_a_plain_video_names_no_ending_picture():
    _generator, record = render_one_video(production_mode.STANDARD)

    assert "endsOn" not in video_row(record)
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: iki kırmızı (`KeyError: 'endsOn'`); üçüncü doğuştan yeşil — alan bugün hiç yazılmıyor.

---

### Task 3: Kayıt ve galeri cevabı

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_record.py`
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

- [ ] **Step 1: Kaydın testini yaz**

`test_a_slot_whose_line_named_no_mode_has_no_mode_key`'in altına:

```python
def test_a_line_that_names_an_ending_picture_carries_it_into_the_slot(tmp_path):
    """The detail page's Uretim modu row prints this file for a linked video."""
    record = record_at(tmp_path)
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "mode": "linked", "endsOn": "1_a.png"})

    assert record.slots("düğün")["0_a"]["video"]["endsOn"] == "1_a.png"
```

- [ ] **Step 2: `list_frames`'in testini yaz**

`test_a_layer_with_no_mode_on_its_line_is_left_out_of_the_map`'in altına:

```python
def test_the_gallery_says_where_a_linked_video_ended():
    """Keyed by layer like modes and errors: the frame answers per layer, so the page asking about
    one never has to know which layers the others are."""
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "mode": "linked", "endsOn": "1_a.png"})

    frames = list_frames(record, FakeStore(), planned((0, "a", "ilk")), FakeOrderStore(), "düğün")

    assert frames[0]["endsOn"] == {"video": "1_a.png"}
```

- [ ] **Step 3: Kopyanın testini yaz**

`test_a_sound_copy_carries_the_videos_mode_too`'nun altına:

```python
def test_a_sound_copy_carries_where_the_video_ended_too():
    # The twin holds the same video file, so its detail page has to be able to say the same thing
    # about it.
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor", "mode": "linked",
                            "endsOn": "1_a.png"})

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.AUDIO, variants=2)

    assert record.slots("düğün")["P0_1"]["video"]["endsOn"] == "1_a.png"
```

- [ ] **Step 4: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: beş kırmızı — Task 2'nin ikisi ve bu üç.

---

### Task 4: Detaydaki bilgi satırı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

**Interfaces:**
- Consumes: dosyanın `LAYERED` sabiti, `open(fid, {frames})`, `tab(name)`.

- [ ] **Step 1: Bloğu yaz**

`PhotoDetail — the layer tabs` bloğunun sonrasına, kendi bloğu olarak:

```jsx
describe("PhotoDetail — how the video was made", () => {
  const LOOPED = { ...LAYERED, modes: { video: "loop" } };
  const LINKED = { ...LAYERED, modes: { video: "linked" }, endsOn: { video: "P1_0.png" } };

  it("says which mode made this video", async () => {
    await open("P0_0", { frames: [LOOPED] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Üretim modu")).toBeTruthy();
    expect(screen.getByText("Loop")).toBeTruthy();
  });

  it("names the picture a linked video ended on", async () => {
    // The file rather than the frame's number: the sequence can be dragged, and then the number
    // would be a lie about a video nobody touched.
    await open("P0_0", { frames: [LINKED] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Sonrakine bağla → P1_0.png")).toBeTruthy();
  });

  it("says it and nothing more -- there is nothing here to press", async () => {
    // Changing the mode is making the video again, and that is the form below.
    await open("P0_0", { frames: [LOOPED] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Loop").closest("button")).toBeNull();
  });

  it("never draws the row on the sound tab", async () => {
    // The sound tab shows the video's file name, because the sound was laid over it -- but the
    // video's mode is not a fact about the sound.
    await open("P0_0", { frames: [LOOPED] });

    fireEvent.click(tab("Ses"));

    expect(screen.queryByText("Üretim modu")).toBeNull();
  });

  it("never draws it on the photo tab either", async () => {
    await open("P0_0", { frames: [LOOPED] });

    expect(screen.queryByText("Üretim modu")).toBeNull();
  });

  it("stays quiet about a video whose line never named a mode", async () => {
    // Videos already on Drive were produced before modes existed. An empty row would be a question
    // rather than an answer.
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));

    expect(screen.queryByText("Üretim modu")).toBeNull();
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

Expected: QueenAgent'ın ikisi yeşil. queen-editor'ün python tarafı **beş kırmızı**, ön yüzü
**üç kırmızı** — `says which mode`, `names the picture`, `says it and nothing more`. Öteki üçü
doğuştan yeşil: satır bugün hiçbir sekmede yok, dolayısıyla "yok" diyen her test geçiyor.

---

### Task 5: Kırmızıyı commit et

- [ ] **Step 1: Sayıları oku**

On iki testin sekizi kırmızı: python tarafında 5, ön yüzde 3. Başka bir sayı çıkarsa durup sebebi
bulunur.

- [ ] **Step 2: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the detail page says how this video was made

The mode is on the row since the loop badge, but where a linked video arrives is not.
The job carried the target, the render read it, and when the job was done that was the
end of it. These tests write the ending picture down as a file name -- the one the
render was actually handed.

A name rather than the target's identity, resolved later: the frame a video points at
can be deleted while the video stays, and then there would be nothing to print for a
video that really did arrive somewhere. The design asks for the file over the number for
the same kind of reason -- the sequence can be dragged and a number becomes a lie.

Whatever the render was given as an ending picture is what the row names, mode or no
mode. A loop's own picture is recorded too. Teaching the engine which modes end
somewhere would be the modes' rule written a second time.

The row on the page is information: it is a Field beside the sequence number and the
file name, with nothing to press. It is born on the video tab alone and only for a video
whose line named a mode.

Five red on the python side, three on the front. Four are born green -- the row does not
exist yet, so every test that asks for its absence already passes.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in on iki testi Task 2'de üç, Task 3'te üç, Task 4'te altı. 6. karar
(modun adı `production_modes.js`'ten) 7. ve 8. testlerin içinde: "Loop" ve "Sonrakine bağla" o
listenin kendi etiketleri.

**Tip tutarlılığı:** `endsOn` satırda ve hücrede dize, karede `{layer: file}` haritası — `modes`
ile birebir aynı ayrım.

**Kontrol edilen tuzak:** 2. test (`loop kendi fotoğrafını söyler`) `0_a.png` bekliyor, çünkü
`render_one_video` işi `0_a` üstüne kuruyor ve loop kendi resmine varıyor. Bu test, "yalnız bağlı
modda yaz" diye yazılmış bir uygulamayı düşürüyor.

**Kontrol edilen tuzak 2:** 9. test `closest("button")` diyor. Satırın metnini aramak, onu bir
düğmenin içine koyan bir uygulamada da geçerdi.

**Kontrol edilen tuzak 3:** 12. test `LAYERED`'ı olduğu gibi kullanıyor — modu olmayan videolu bir
kare. Satırı `open === "video"` koşuluna bağlayıp modu sormayan bir uygulama burada düşüyor.

**Kontrol edilen tuzak 4:** 10. test ses sekmesini açıyor, ve o sekmede videonun dosya adı **var**.
Satırı "video katmanı görünüyorsa çiz" diye yazan bir uygulama burada düşüyor.

**Doğuştan yeşil olan dört:** 3, 10, 11, 12. Üçü satırın yokluğunu ölçüyor ve satır bugün hiç yok;
biri (`3`) alanın yokluğunu ölçüyor. Nöbetleri uygulama turundan sonra başlıyor.
