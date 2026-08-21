# v14 Görev 7 — Galeride loop rozeti: TEST döngüsü (test planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Üretilen videonun modunu satırdan karoya taşıyan zincirin on üç testini yazmak ve kırmızı
bırakmak.

**Architecture:** Üç test dosyası, zincirin dört halkası: motor satıra yazıyor, kayıt hücreye
katlıyor, `list_frames` kareye veriyor, karo kelimeyi değiştiriyor. Kaynak dosyalara bu turda
dokunulmuyor; `FakeRecord` bir sahte olduğu için değişiyor.

**Tech Stack:** pytest, vitest, @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-7-loop-rozeti-testler-design.md)

## Global Constraints

- **Yalnız test dosyaları değişiyor.** `run_loop.py`, `photo_record.py`, `list_frames.py`,
  `copy_frame.py`, `layer_words.js` bu turda el değmeden kalıyor.
- **`skip` / `xfail` yok.**
- Test adları ve yorumları **İngilizce**; ekranda aranan metinler **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komutlar dört satır, birebir, boru yok.
- **`dist` bu turda derlenmiyor** — ön yüz kaynağı değişmiyor.

## Beklenen şekiller

| Halka | Şekil |
|---|---|
| Satır | `{"file": …, "layer": "video", …, "mode": "loop"}` |
| Hücre | `{"status": "done", "file": …, "mode": "loop"}` |
| Kare | `{"id": …, "layers": {…}, "modes": {"video": "loop"}, …}` |
| Karo | sol altta `loop`, `video` değil |

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/tests/test_photo_usecases.py` | motor, galeri cevabı, kopya | `FakeRecord.slots` + 6 test |
| `backend/tests/test_photo_record.py` | gerçek kaydın katlaması | 2 test |
| `frontend/src/features/photo_generation/Gallery.test.jsx` | karonun kelimesi | 5 test |

---

### Task 1: Sahte kayıt gerçeğine yetişiyor

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Produces: `FakeRecord.slots()` hücresinde `mode`. Task 2 ve Task 4 buna dayanıyor.

- [ ] **Step 1: `slots`'a modu ekle**

`FakeRecord.slots` içinde, `error` katlamasının yanına:

```python
    def slots(self, project):
        folded = {}
        for row in self.rows:
            cell = {"status": row.get("status", "done"), "file": row["file"]}
            if isinstance(row.get("error"), str):
                cell["error"] = row["error"]
            if isinstance(row.get("mode"), str):
                cell["mode"] = row["mode"]
            folded.setdefault(self._frame_of(row), {})[self._layer_of(row)] = cell
        return folded
```

Sınıfın kendi belgesi zaten *"Folds the log the way DrivePhotoRecord does"* diyor. Sahte geride
kalsaydı motor testleri gerçekte olmayan bir dünyada koşardı.

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: 639 yeşil — kimse bu alanı henüz okumuyor, dolayısıyla hiçbir şey değişmedi.

---

### Task 2: Motor modu satıra yazıyor

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `render_one_video(mode, …)` ve `render_seedless(new_seed)` — ikisi de dosyada duruyor.

- [ ] **Step 1: Üç testi yaz**

`test_a_linked_video_whose_target_lost_its_photo_turns_that_frame_red`'in altına, `render_seedless`
tanımının üstüne:

```python
def video_row(record):
    """The produced video's own line -- the one the gallery and the detail page read back."""
    return [row for row in record.rows
            if row.get("layer") == "video" and row.get("status") == "done"][0]


def test_a_loop_video_says_on_its_row_that_it_is_one():
    """Until now the mode reached the render and stopped there. The tile has no other way of
    knowing: the file it holds is a video like any other."""
    _generator, record = render_one_video(production_mode.LOOP)

    assert video_row(record)["mode"] == production_mode.LOOP


def test_a_plain_video_says_so_on_its_row_as_well():
    # Both written, because the tile and the detail page have to tell the two apart -- an absent
    # field would mean plain and unknown at the same time.
    _generator, record = render_one_video(production_mode.STANDARD)

    assert video_row(record)["mode"] == production_mode.STANDARD


def test_a_job_that_names_no_mode_leaves_the_field_off_its_row():
    """Which jobs carry a mode is the queue's rule (queue_layer puts it on video jobs alone), and
    the loop does not write that rule a second time. A photo row saying standard would be a field
    that means nothing on nearly every line it appears on."""
    _generator, record = render_seedless(lambda: 777)

    assert "mode" not in video_row(record)
```

`render_seedless` video işini elle planlıyor ve `mode` alanı koymuyor — modu olmayan işin tam
kendisi.

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: iki kırmızı (`KeyError: 'mode'`), üçüncü yeşil — bugün hiçbir satırda alan yok, yani
"alan yok" testi doğuştan geçiyor. Nöbeti uygulama turundan sonra başlıyor.

---

### Task 3: Gerçek kayıt modu hücreye katlıyor

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_record.py`

- [ ] **Step 1: İki testi yaz**

`test_a_line_without_an_error_carries_no_error_field`'in altına:

```python
def test_a_line_that_names_a_mode_carries_it_into_the_slot(tmp_path):
    """What the gallery reads a loop badge from: the produced layer's own line, folded like every
    other field."""
    record = record_at(tmp_path)
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "mode": "loop"})

    assert record.slots("düğün")["0_a"]["video"]["mode"] == "loop"


def test_a_slot_whose_line_named_no_mode_has_no_mode_key(tmp_path):
    # Videos already on Drive were produced before modes existed. Their slots must not claim a mode
    # they never had -- absent is the honest answer, and the reader decides what to do with it.
    record = record_at(tmp_path)
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    assert "mode" not in record.slots("düğün")["0_a"]["video"]
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: birinci kırmızı (`KeyError: 'mode'`), ikinci doğuştan yeşil — aynı sebeple.

---

### Task 4: Galeri cevabı ve kopya

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: Task 1'in `FakeRecord.slots`'u, `video_project((0, "a"))` ve `gallery_of`/`list_frames`
  çağrısının dosyadaki bugünkü biçimi.

- [ ] **Step 1: `list_frames`'in iki testini yaz**

`test_a_frames_taken_layers_are_published`'in hemen altına — komşusu, çünkü ikisi de aynı hücrelerin
kareye nasıl açıldığını ölçüyor. Çağrı biçimi o testinkinin aynısı:

```python
def test_the_gallery_says_which_mode_made_each_layer():
    """The tile's loop badge and the detail page's information row both ask this one question, so
    the frame answers it once."""
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "mode": "loop"})

    frames = list_frames(record, FakeStore(), planned((0, "a", "ilk")), FakeOrderStore(), "düğün")

    assert frames[0]["modes"] == {"video": "loop"}


def test_a_layer_with_no_mode_on_its_line_is_left_out_of_the_map():
    # Shaped like errors: only the layers that have one are in it, so a missing key is the answer
    # rather than a value standing for absence.
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    frames = list_frames(record, FakeStore(), planned((0, "a", "ilk")), FakeOrderStore(), "düğün")

    assert frames[0]["modes"] == {}
```

- [ ] **Step 2: Kopyanın testini yaz**

`test_a_sound_copy_carries_the_photo_and_the_video`'nun altına:

```python
def test_a_sound_copy_carries_the_videos_mode_too():
    """One file, two frames holding it. Without the mode the twin's tile would read video while the
    original reads loop -- two answers about the same video."""
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor", "mode": "loop"})

    queue_layer(sync_runner(), store, record, plan_store, FakeOrderStore(),
                {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", layers.AUDIO, variants=2)

    assert record.slots("düğün")["P0_1"]["video"]["mode"] == "loop"
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_the_gallery_says_which_mode_made_each_layer` ve
`test_a_layer_with_no_mode_on_its_line_is_left_out_of_the_map` ikisi de kırmızı (`KeyError:
'modes'` — alan hiç yok), `test_a_sound_copy_carries_the_videos_mode_too` kırmızı.

---

### Task 5: Karonun kelimesi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: dosyanın `withVideo(file, extra)` yardımcısı — `layers` ve `modes` `extra` ile
  veriliyor.

- [ ] **Step 1: Beş testi yaz**

`Gallery — what a frame owns` bloğunun sonuna, `keeps the photo on screen while the video is
queued`'ün üstüne:

```jsx
  it("marks a loop video with its own word", () => {
    renderGallery({ frames: [withVideo("P0_0.png", { modes: { video: "loop" } })] });

    expect(screen.getByText("loop")).toBeTruthy();
  });

  it("never shows both words on one frame", () => {
    // They share the corner: the badge is one row per layer, and loop takes the video row's word
    // rather than standing beside it.
    renderGallery({ frames: [withVideo("P0_0.png", { modes: { video: "loop" } })] });

    expect(screen.queryByText("video")).toBeNull();
  });

  it("leaves a video made the plain way saying video", () => {
    renderGallery({ frames: [withVideo("P0_0.png", { modes: { video: "standard" } })] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(screen.queryByText("loop")).toBeNull();
  });

  it("adds the sound beside the loop, not instead of it", () => {
    renderGallery({ frames: [withVideo("P0_0.png", {
      layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" },
      modes: { video: "loop" } })] });

    expect(screen.getByText("loop")).toBeTruthy();
    expect(screen.getByText("ses")).toBeTruthy();
  });

  it("says nothing about a loop video that blew up", () => {
    // A failed layer holds its slot but is not owned -- that tile is the pill's to speak for, and
    // the mode must not smuggle a word past that rule.
    renderGallery({ frames: [withVideo("P0_0.png", { modes: { video: "loop" },
                                                     failed: ["video"] })] });

    expect(screen.queryByText("loop")).toBeNull();
    expect(screen.queryByText("video")).toBeNull();
  });
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: QueenAgent'ın ikisi yeşil. queen-editor'ün python tarafı **altı kırmızı** (Task 2'den iki,
Task 3'ten bir, Task 4'ten üç), ön yüzü **üç kırmızı** — `marks a loop video`, `never shows both
words`, `adds the sound beside the loop`. `leaves a video made the plain way` ve `says nothing about
a loop video that blew up` doğuştan yeşil: ikisi de bugünkü davranışı da tarif ediyor.

---

### Task 6: Kırmızıyı commit et

- [ ] **Step 1: Sayıları oku**

On üç testin dokuzu kırmızı: python tarafında 6, ön yüzde 3. Doğuştan yeşil olan dördü Task 2, 3 ve
5'te tek tek yazıldı; başka bir sayı çıkarsa durup sebebi bulunur.

- [ ] **Step 2: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): a loop video wears its own word in the gallery

The mode reaches the render and stops there. Nothing writes it down, so a finished loop
video is a video like any other and its tile says so. These tests carry it the rest of
the way: the engine writes the mode on the produced layer's row, the record folds it
into the slot, the gallery hands it out as modes per layer, and the tile swaps the word.

The map is shaped like errors -- only the layers whose line named one -- because the
detail page asks the same question of the same frame, and a field named for the video
would need renaming the day a second layer gains a mode.

A sound copy takes its source's video row, so it takes the mode with it. Otherwise the
twin's tile would read video while the original reads loop, over one file.

The word replaces, never joins: the badge is one row per layer, so the two cannot appear
together by construction rather than by a rule.

Six red on the python side, three on the front. Four more are born green -- each one
measures an absence that today is true for a different reason, and forcing them red
would mean writing them wrong on purpose.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in on üç testi Task 2'de üç, Task 3'te iki, Task 4'te üç, Task 5'te beş.
Kararlar 1–6 test edildi; 7 (silme onayı değişmiyor) ve 8 (bağlı modun rozeti yok) birer sınır, ve
bir sınırın nöbeti olmaz.

**Tip tutarlılığı:** `mode` her halkada dize; `modes` her yerde `{layer: mode}` haritası. Karo
tarafında `modes` bir `extra` alanı, `layers` gibi.

**Kontrol edilen tuzak:** Task 1 sahteyi gerçeğe eşitliyor ve bu, Task 2 ile Task 4'ün kırmızılarının
ölçtüğü şeyin gerçekten motor olmasını sağlıyor. Sahte geride kalsaydı Task 4 kırmızı kalırdı ama
sebebi kaynak değil sahte olurdu.

**Kontrol edilen tuzak 2:** 10. test `queryByText("video")` diyor. Yalnız `getByText("loop")`,
iki kelimeyi yan yana yazan bir uygulamada da geçerdi.

**Kontrol edilen tuzak 3:** 13. test hem `loop` hem `video` yokluğunu arıyor. Kelime değiştirme
işlemi `owned`'ın patlamış katman süzgecinden **sonra** gelmezse bu test düşer.

**Kontrol edilen tuzak 4:** 2. test standart videonun da satıra yazıldığını istiyor. Yalnız loop
yazılsaydı, alanın yokluğu hem "standart" hem "bilinmiyor" demek olurdu — ve 8. madde o ikisini
ayırt etmek zorunda.

**Doğuştan yeşil olan dört:** 3, 5, 11, 13. İkisi yokluk ölçüyor (`mode` alanı yok, anahtar yok),
ikisi bugünkü doğru davranışı tarif ediyor (düz video "video" der, patlamış katman hiçbir şey
demez). Nöbetleri uygulama turundan sonra başlıyor: alan var olduğunda yanlış yere yazılmadığını
tutan onlar.

7. test (`modes == {}`) doğuştan **kırmızı**, çünkü alan hiç yok — `KeyError`. Yokluk ölçüyor gibi
duruyor ama ölçtüğü şey haritanın boş olması, haritanın olmaması değil.
