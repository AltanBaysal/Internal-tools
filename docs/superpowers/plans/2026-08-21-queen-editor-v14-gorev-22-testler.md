# v14 Görev 22 — Detayın görsel hizalaması: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detay sayfasının on altı farkını yirmi üç testle yazmak. Yirmi beşi kırmızı commit
ediliyor.

**Architecture:** İki test dosyası. Üretim kodu bu döngüde değişmiyor.

**Tech Stack:** vitest, @testing-library/react, jsdom.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-22-detay-hizalamasi-testler-design.md)

## Global Constraints

- **Üretim kodu bu döngüde değişmiyor.** Tutamaklar uygulama turunda geliyor.
- Test adları **İngilizce**, yorumlar **İngilizce**; ekran metni **Türkçe**.
- `skip` / `xfail` yok — kırmızı kırmızı commit edilir.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist` bu commit'te **derlenmiyor**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../research/2026-08-20-queen-editor-tasarim-v4-farklari.md` | kararların kaynağı | 36–39 eklenir |
| `.../photo_generation/PhotoDetail.test.jsx` | detay sayfası | 19 yeni, 3 düzeltilen |
| `.../photo_generation/LayerPlayer.test.jsx` | oynatıcı | 5 yeni |
| `backend/tests/test_photo_usecases.py` | yeniden üretme kuralı | 2 yeni |
| `backend/tests/test_photo_routes.py` | yolun çevirisi | 1 yeni |

---

### Task 1: 36–39. kararlar kaynağına yazılıyor

**Files:**
- Modify: `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md`

- [ ] **Step 1: Tarih notu**

`*(21 Ağustos 2026, 13, 15, 20 ve 21. madde uygulanırken.)*` →
`*(21 Ağustos 2026, 13, 15, 20, 21 ve 22. madde uygulanırken.)*`

- [ ] **Step 2: Tabloya dört satır**

```markdown
| 36 | **Oklar dizinin ucunda sönük kalır.** Fark okların her karede tam opak ve tıklanabilir durmasını istiyor ve kendi notu "uçta basılınca ne olacağını tasarım söylemiyor" diyor. Tasarım başka bir yerde uçların dönmediğini söylüyor; dönmüyorsa uçtaki oka basınca hiçbir şey olmaz, ve hiçbir şey yapmayan tam opak bir ok orada bir kare olduğunu söyler. Sönüklük o cümlenin dürüst karşılığı. Gözlem ortadaki bir kareyi çizen artboard'dan geliyor olmalı — orada iki ok da zaten tam opak. | 104 |
| 37 | **Kuyruktaki kopya karede şerit duruyor, etiket geliyor.** Farkın şeridi hiç çizmeme yarısı alınmıyor: aynı listenin 92. maddesi kuyrukta bekleyen katmanın sekmesi açılınca kutusunda ne yazacağını tarif ediyor (19. maddede uygulandı), 99. maddesi de düğmenin sekmede durmasını istiyor — şerit kalkarsa ikisi de ulaşılamaz olur. Etiket yarısı alınıyor: sahnedeki resmin bu kareye ait olmadığını bugün hiçbir şey söylemiyor, köşeye "kaynak foto · kopya kare" giriyor. | 112 |
| 38 | **"Kuyruktan çıkar — kare kalır" yazılmıyor.** Kuyruk kareyi çıkarıyor, katmanı değil: `remove_frames.py` kimliklerle çalışıyor ve üretilmemiş bir kareyi kuyruktan düşürüyor. Bir katmanı kuyruktan alıp kareyi bırakan bir basış yok, dolayısıyla "kare kalır" diyen bir düğme motorun yapamadığını vaat ederdi. Farkın asıl şikâyeti — düğmenin yalnız foto sekmesinde olması — düzeltiliyor. | 99 |
| 39 | **Hap fotoğrafın içine inmiyor.** Köşe sahneye göre konumlanıyor, fotoğrafa göre değil: resim sahnenin ortasında `contain` ile duruyor ve sol kenarının nerede olduğu ancak yerleşimden sonra belli. Tutturulacak bir kenar yok. Hapın nabız atan noktası alınıyor, konumu bugünkü yerinde kalıyor. | 107 |
```

---

### Task 2: Sahnenin testleri

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

**Interfaces:**
- Consumes: `data-stage`, `data-making`, `data-strip` — ilk ikisi uygulama turunda doğar.

- [ ] **Step 1: `the layer tabs` bloğunun hemen üstüne yeni blok**

```jsx
// The frame the worker is holding a layer of: its photo is on disk, its video is not yet.
const RENDERING = { ...LAYERED, layers: { photo: "P0_0.png" }, owed: ["video"],
                    prompts: { photo: "kırmızı elbise" } };

describe("PhotoDetail — the stage", () => {
  it("opens the stage from the top and drops the strip closer to it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 103: the tabs sat 16px down over a stage padded evenly on all four sides, so the strip
    // and the picture crowded the same band. The top opens, the other three stay.
    const stage = document.querySelector("[data-stage]");
    expect(stage.style.paddingTop).toBe("48px");
    expect([stage.style.paddingRight, stage.style.paddingBottom, stage.style.paddingLeft])
      .toEqual(["24px", "24px", "24px"]);
    expect(document.querySelector("[data-strip]").style.top).toBe("12px");
  });

  it("puts a step between a waiting frame's two lines", async () => {
    await open("P0_0", { frames: [{ id: "P0_0", file: "P0_0.png", status: "pending", prompt: "p",
                                    layers: {}, failed: [], owed: ["photo"], prompts: {} }] });

    // Fark 105: both lines read at the same size, so neither was the heading. The word is the
    // heading now and the sentence under it steps back.
    expect(screen.getByText("bekliyor").style.fontSize).toBe("14px");
    expect(screen.getByText("henüz üretilmedi").style.fontSize).toBe("10px");
    expect(screen.getByText("henüz üretilmedi").style.color).toBe("var(--ink-4)");
  });

  it("swaps the fonts of the failed stage's title and reason", async () => {
    await open("P0_0", { frames: [BROKEN] });

    // Fark 106: exactly the other way round from today. The two words are a heading and read as
    // one; what the renderer said is machine output and reads as machine output.
    expect(screen.getByText("Bu kare üretilemedi").className).toContain("wf-note");
    expect(screen.getByText("CUDA out of memory — 3 kez denendi").className).toContain("wf-mono");
  });

  it("keeps the picture and lays a box over it while a layer is made", async () => {
    await open("P0_0", { frames: [RENDERING],
                         status: { status: "running", project: "düğün",
                                   current: { id: "P0_0", layer: "video" } } });

    // Fark 113: the photo used to be swapped for a spinner, so the one thing the user could still
    // look at went away for the length of the render.
    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(document.querySelector("[data-making]").textContent).toContain("video üretiliyor");
    expect(document.querySelector("[data-making] .qe-dot--alive")).toBeTruthy();
  });

  it("still spins where there is no picture yet", async () => {
    await open("2_a", { frames: MIXED, status: RUNNING });

    // The exception the fark does not name: a photo being made has nothing to keep on screen, so
    // the holder stays what it was.
    expect(document.querySelector(".wf-spinner")).toBeTruthy();
    expect(document.querySelector("[data-making]")).toBeNull();
  });

  it("says whose picture a copy frame is showing", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    // Fark 112: the stage is full of the source's photo and nothing said so (karar 37).
    expect(screen.getByText("kaynak foto · kopya kare")).toBeTruthy();
  });
});
```

---

### Task 3: Hapların ve düğmelerin testleri

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

- [ ] **Step 1: `one destructive action per tab` bloğunun hemen üstüne**

```jsx
describe("PhotoDetail — what the page says it did", () => {
  it("makes the queued pill beat", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P0_2" });
    await open("P0_0", { frames: [LAYERED] });

    await act(async () => { fireEvent.click(regenButton()); });

    // Fark 107: the same live dot the gallery's own running pill carries. Its place does not
    // change -- the corner is fixed to the stage and the photo's edge is not a thing to aim at
    // (karar 39).
    expect(screen.getByText("yeniden üretilecek — kuyrukta")
      .querySelector(".qe-dot--alive")).toBeTruthy();
  });

  it("says a retry was a retry and not a new frame", async () => {
    retryFrame.mockResolvedValue({ job: "running" });
    await open("P0_0", { frames: [BROKEN] });

    await act(async () => { fireEvent.click(screen.getByText("Tekrar dene — bu kareye")); });

    // Fark 108: both presses used to leave the same sentence in the corner, and only one of them
    // opens a frame of its own.
    expect(screen.getByText("kuyrukta — tekrar denenecek")).toBeTruthy();
    expect(screen.queryByText("yeniden üretilecek — kuyrukta")).toBeNull();
  });

  it("says on the button that a retry opens no new frame", async () => {
    await open("P0_0", { frames: [BROKEN] });

    // Fark 109: retry is the one exception to uret = ekle, and the button is where that is read.
    expect(screen.getByText("Tekrar dene — bu kareye")).toBeTruthy();
  });

  it("offers a second way out of a failed layer", async () => {
    await open("P0_0", { frames: [{ ...LAYERED, layers: { photo: "P0_0.png" }, failed: ["video"],
                                    errors: { video: "ComfyUI 500 — 3 kez denendi" },
                                    prompts: { photo: "kırmızı elbise" } }] });

    fireEvent.click(tab("Video"));

    // Fark 100: a copy with no video is pointless, so the way out stands beside the way back.
    expect(screen.getByText("Tekrar dene — bu kareye")).toBeTruthy();
    expect(screen.getByText("Kareyi sil")).toBeTruthy();
  });

  it("puts the way out of the queue on the waiting layer's own tab", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    // Fark 99: the button lived on the photo tab alone, which is not the tab the user is on when
    // they are looking at what they are waiting for. The words are the photo tab's own -- the
    // queue takes frames out, not layers (karar 38).
    expect(screen.getByText("Kuyruktan çıkar")).toBeTruthy();
  });

  it("draws the regenerate button full size and the delete one small", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 110: one of the two is what the page is for and the other is the way out. They were
    // drawn at the same size, which said they weigh the same.
    expect(regenButton().className).toContain("wf-btn--hl");
    expect(regenButton().className).not.toContain("wf-btn--sm");
    expect(screen.getByText("Sil").closest("button").className).toContain("wf-btn--sm");
  });

  it("drops the red from the delete button while the frame is being made", async () => {
    await open("2_a", { frames: MIXED, status: RUNNING });

    // Fark 111: a disabled button in the destructive colour reads as a refusal rather than a wait.
    const bin = screen.getByText("Kuyruktan çıkar").closest("button");
    expect(bin.disabled).toBe(true);
    expect(bin.style.color).not.toBe("var(--danger)");
    expect(bin.style.borderColor).not.toBe("var(--danger)");
  });
});
```

- [ ] **Step 2: `one destructive action per tab` bloğuna iki test**

`asks with the design's own words before taking a video` testinin hemen altına:

```jsx
  it("names the file the layer confirm is about to take", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));

    // Fark 101: a frame can hold more than one video across its history, and the window that says
    // one of them is going should say which.
    expect(screen.getByText(/^P0_0_V1_0\.mp4 ve üzerindeki ses/)).toBeTruthy();
  });
```

`the arrows and the keyboard` bloğundaki silme testinin yanına değil, aynı yıkıcı bloğun sonuna:

```jsx
  it("counts the frame in the confirm the way the selection bar does", async () => {
    await open("1_a");

    fireEvent.click(screen.getByText("Sil"));

    // Fark 102: one window, one language. The bar says 2 kare silinsin mi and this said something
    // else about one.
    expect(screen.getByText("1 kare silinsin mi?")).toBeTruthy();
  });
```

---

### Task 4: Kutuların testleri

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

- [ ] **Step 1: `the negative prompt` bloğuna dört test**

```jsx
  it("lets the negative be edited", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 98: the prompt was the user's and the negative was not, though the two travel into the
    // same job together.
    fireEvent.change(screen.getByDisplayValue("bulanık"), { target: { value: "bulanık, gürültü" } });

    expect(screen.getByDisplayValue("bulanık, gürültü")).toBeTruthy();
  });

  it("marks the negative's box once it is no longer the frame's own", async () => {
    await open("P0_0", { frames: [LAYERED] });

    const box = screen.getByDisplayValue("bulanık");
    expect(box.style.borderColor).not.toBe("var(--accent)");

    fireEvent.change(box, { target: { value: "bulanık, gürültü" } });

    expect(screen.getByDisplayValue("bulanık, gürültü").style.borderColor).toBe("var(--accent)");
  });

  it("sends the negative that was typed", async () => {
    regenerateFrame.mockResolvedValue({ frame: "P1_0" });
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.change(screen.getByDisplayValue("bulanık"), { target: { value: "gürültü" } });
    await act(async () => { fireEvent.click(regenButton()); });

    // An accent border promising a different frame while the negative never leaves the screen
    // would be the box lying about what it did.
    expect(regenerateFrame)
      .toHaveBeenCalledWith("düğün", "P0_0", "photo", "kırmızı elbise", undefined, "gürültü");
  });

  it("reads a prompt in the same face the panel reads it in", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 117: the visual language says a prompt box is monospace wherever it stands, and the
    // production panel already obeys it. The same words read in two faces on two screens.
    expect(screen.getByDisplayValue("kırmızı elbise").className).toContain("wf-mono");
  });

  it("keeps the face when the box is only there to be read", async () => {
    await open("3_a", { frames: MIXED });

    expect(screen.getByText("dördüncü").className).toContain("wf-mono");
  });
```

---

### Task 5: Motorun testleri

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`
- Modify: `queen-editor/backend/tests/test_photo_routes.py`

**Interfaces:**
- Consumes: `regenerate(..., negative=...)` — **uygulama turunda doğar**.

- [ ] **Step 1: `test_only_the_words_count_as_a_change`'in hemen altına iki test**

```python
def test_the_new_photo_carries_the_negative_it_was_given():
    # Fark 98: the negative became the user's too, so what goes down is the box's own words and not
    # the line the source frame happened to be made from.
    store, record, plan_store = video_project((0, "a"))

    regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
               {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
               "düğün", "0_a", layers.PHOTO, "p", negative="bulanık, gürültü")

    assert plan_store.appended[-1][0]["negative"] == "bulanık, gürültü"


def test_a_layer_over_the_photo_carries_no_negative_whatever_it_is_given():
    # Only a photo is made from a prompt and a negative of its own; the layers over it are made from
    # what is under them. The editable box is the photo tab's alone and this is the rule behind it.
    store, record, plan_store = video_project((0, "a"))

    regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
               {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
               "düğün", "0_a", layers.VIDEO, "p", negative="bulanık")

    assert plan_store.appended[-1][0]["negative"] == ""
```

- [ ] **Step 2: `test_a_regenerate_mode_nobody_knows_is_refused`'un altına bir test**

```python
def test_the_body_negative_reaches_the_new_frames_line(tmp_path):
    """Proof that the box's own words travel: an unchanged prompt would otherwise keep the source's
    negative and the screen would be promising an edit that never left it."""
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    client.post("/api/projects/düğün/regenerate",
                json={"frame": "P0_0", "layer": "photo", "prompt": "a",
                      "negative": "bulanık, gürültü"})

    rows = client.get("/api/projects/düğün/frames").get_json()["frames"]
    assert rows[0]["negative"] == "bulanık, gürültü"
```

---

### Task 6: Oynatıcının testleri

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPlayer.test.jsx`

**Interfaces:**
- Consumes: `data-scene`, `data-track` — uygulama turunda doğar.

- [ ] **Step 1: Bloğun sonuna beş test**

```jsx
  it("brings the clock inside the video", () => {
    render(<LayerPlayer videoUrl="/v.mp4" />);

    // Fark 114: the times and the line sat under the video in a framed row of their own, so the
    // player read as two things stacked rather than one.
    expect(document.querySelector("[data-scene] [data-track]")).toBeTruthy();
    expect(document.querySelector("[data-track]").style.position).toBe("absolute");
  });

  it("takes the frame off the progress line", () => {
    render(<LayerPlayer videoUrl="/v.mp4" />);

    // A line over a picture needs no box around it: the picture is the contrast.
    expect(document.querySelector("[data-progress]").parentElement.className)
      .not.toContain("wf-stroke");
  });

  it("brings the waveform inside the video too", () => {
    render(<LayerPlayer videoUrl="/v.mp4" audioUrl="/s.wav" />);

    expect(document.querySelector("[data-scene] [data-bar]")).toBeTruthy();
  });

  it("draws the bars nobody has reached yet in translucent white", () => {
    render(<LayerPlayer videoUrl="/v.mp4" audioUrl="/s.wav" />);

    // Fark 115: the faintest ink was a tone for text on the panel's own ground, and these bars
    // stand on a picture.
    expect(document.querySelectorAll("[data-bar]")[45].style.background)
      .toMatch(/rgba\(255,\s*255,\s*255/);
  });

  it("gives the play button an outline and a drawn glyph", () => {
    render(<LayerPlayer videoUrl="/v.mp4" />);

    // Fark 116: the mark inside it was a text character, which is a different shape in every font
    // the browser might fall back to.
    const button = screen.getByRole("button", { name: "Oynat" });
    expect(button.style.borderStyle).toBe("solid");
    expect(button.querySelector("[data-glyph=play]")).toBeTruthy();
  });
```

---

### Task 7: Üç testin aradığı kelime

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

- [ ] **Step 1**

`puts the frame back in line without asking`:

```jsx
    await act(async () => { fireEvent.click(screen.getByText("Tekrar dene — bu kareye")); });
```

`asks before deleting, then opens the next photo`:

```jsx
    expect(screen.getByText("1 kare silinsin mi?")).toBeTruthy();
```

`takes it out of the queue without asking`:

```jsx
    expect(screen.queryByText("1 kare silinsin mi?")).toBeNull();
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: ilk ikisi yeşil (384 / 474). queen-editor Python **697 testin 3'ü kırmızı**, frontend
**519 testin 26'sı kırmızı** — 24 yeni, artı `puts the frame back in line without asking` ile
`asks before deleting, then opens the next photo`.

`still spins where there is no picture yet` **yeşil doğuyor**: farkın adlandırmadığı istisnayı
ölçüyor ve o istisna bugün de doğru. Yazılmasının sebebi, farkın *"resmi koru"* diye okunması
hâlinde olmayan bir resmin korunmaya çalışılması.

---

### Task 8: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the detail page comes into line

Twenty differences meet on one page. Sixteen are written as twenty five tests; four are
closed with a reason, in the source, because each one contradicts something the design says
elsewhere or something the engine can do.

The arrows keep dimming at the ends: the design rules out wrapping, and a fully lit arrow
that does nothing when pressed says there is a frame there when there is not. The tab strip
stays on a queued copy frame, because the same list describes what the waiting layer's tab
shows and asks for the button to stand on it -- take the strip away and neither is
reachable. Its label is taken though: nothing on that page said whose picture was on the
stage. A button promising to take a layer out of the queue and leave the frame is not
written, because the queue removes frames and not layers. And the pill stays where it is:
the corner is fixed to the stage, and a photo drawn to fit has no edge to aim at until the
browser has laid it out.

What is written: the stage opens from the top, a waiting frame's two lines step apart, the
failed stage's two lines trade faces, a layer being made keeps its picture under a dark box,
the queued pill beats, a retry says on both the button and the pill that it opens no new
frame, the failed layer gets its second way out, the button that leaves the queue comes to
the tab the user is actually on, the two buttons stop weighing the same, a disabled delete
drops its red, the confirms name what they are about to take, the negative becomes the
user's, the prompt reads in the same face it reads in on the panel, and the player's clock,
line and waveform move inside the video.

One of the sixteen reaches the engine. The regenerate route carries a frame, a layer, a
prompt and a mode, and the use case writes the source frame's negative onto the new frame's
line. Making the box writable and leaving that would give the user an accent border
promising a different frame while the words never left the screen. Three red tests on that
side say the box's own words travel, and that a layer over the photo still carries none.

One of the twenty five is green from birth. A layer being made keeps its picture, but a
photo being made has no picture to keep, and the difference does not say so -- read as keep
the picture it would have something reaching for one that is not there. The test is what
stops that reading.

Frontend source untouched, so no dist in this commit.

Four suites run; 3 red in queen-editor python and 26 in its frontend.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in on altı farkı Task 2 (103, 105, 106, 113, 112), Task 3 (107, 108, 109,
100, 99, 110, 111, 101, 102), Task 4 (98, 117), Task 5 (114, 115, 116). Dört karar Task 1.

**Tip tutarlılığı:** `data-stage`, `data-making`, `data-scene`, `data-track` uygulama turunun
planında birebir aynı yazılıyor.

**Kontrol edilen tuzak:** 4. test `current: { id: "P0_0", layer: "video" }` veriyor — `useGeneration`
çalışan katmanı oradan okuyor, `currentLayer` yoksa "photo" varsayılıyor ve o zaman resim değil
gösterge çıkardı.

**Kontrol edilen tuzak 2:** `border` kısayolu okunmuyor. 23. testte `borderStyle`, 13. testte
`borderColor` — ikisi de uzun ad.

**Kontrol edilen tuzak 3:** 22. test `rgba` değerini gevşek eşliyor: cssstyle boşlukları
normalleştiriyor ve birebir karşılaştırma yanıltıcı biçimde kırılır.

**Kontrol edilen tuzak 4:** 13. test `not.toBe` kullanıyor, `toBe("")` değil. Düğme nötr çerçeve
alacak, çerçevesiz kalmayacak.

**Kontrol edilen tuzak 5:** 16–18. testler `MIXED`'in `3_a` karesini açıyor — o karenin negatifi
var ("bulanık") ve fotoğrafı üretilmemiş. Negatif kutusu üretilmiş olsun olmasın yazılabilir:
düzenlenen şey karenin sözleri, dosyası değil.

**Değişmeyen:** öteki üç takım, `dist`, üretim kodu.
