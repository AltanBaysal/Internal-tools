# v14 Görev 9 — Detayda Yeni mod seçicisi: TEST döngüsü (test planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Yeniden üretimin modu taşımasını, bağlanacak kare yokken kapanmasını ve formun üç yeni
parçasını tarif eden yirmi üç testi yazmak, kırmızı bırakmak.

**Architecture:** Dört test dosyası. Ortak kural (`frame_after`) kendi evinde, kullanım durumu ve
uç kendi dosyalarında, formun üç parçası detay sayfasının testinde.

**Tech Stack:** pytest, vitest, @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-9-yeni-mod-testler-design.md)

## Global Constraints

- **Yalnız test dosyaları değişiyor.**
- **`skip` / `xfail` yok.**
- Test adları ve yorumları **İngilizce**; ekranda aranan metinler **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komutlar dört satır, birebir, boru yok.
- **`dist` bu turda derlenmiyor.**
- `production_mode.validate`'in kendi testi yok: iki kullanım durumu onu iki uçtan geçiriyor.

## Galerinin yönü

Testlerin dayandığı tek gerçek: **galerinin tepesi filmin son karesi.** `video_project((0, "a"),
(1, "a"))` galeriyi `[1_a, 0_a]` olarak veriyor, yani `1_a` tepede ve sonrası yok; `0_a`'nın filmdeki
sonrası `1_a`.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/tests/test_production_mode.py` | ortak kural | 3 test |
| `backend/tests/test_photo_usecases.py` | yeniden üretim | 6 test |
| `backend/tests/test_photo_routes.py` | uç | `regenerate_request` + 2 test |
| `frontend/src/features/photo_generation/PhotoDetail.test.jsx` | form | 12 test |

---

### Task 1: Ortak kuralın kendi nöbeti

**Files:**
- Modify: `queen-editor/backend/tests/test_production_mode.py`

**Interfaces:**
- Consumes: `production_mode.frame_after(gallery, fid)` — bu turdan sonra var olacak.

- [ ] **Step 1: Üç testi yaz**

Dosyanın sonuna:

```python
def gallery(*rows):
    """Frames as list_frames hands them over: newest first, so the film runs from the foot up."""
    return [{"id": fid, "status": status} for fid, status in rows]


def test_a_linked_video_ends_on_the_frame_above_it():
    """The film's sequence, not the gallery's reading order: the export stitches the gallery
    reversed, so the frame that plays next is the one above."""
    assert production_mode.frame_after(gallery(("1_a", "done"), ("0_a", "done")), "0_a") == "1_a"


def test_the_frame_at_the_top_of_the_gallery_has_nothing_after_it():
    # The film's last frame. Two use cases read this: the queue drops that job, the detail page
    # closes the option.
    assert production_mode.frame_after(gallery(("1_a", "done"), ("0_a", "done")), "1_a") is None


def test_a_next_frame_with_no_picture_yet_is_no_target():
    # There is nothing to end on: the same emptiness as having no next at all, seen from closer up.
    assert production_mode.frame_after(gallery(("1_a", "pending"), ("0_a", "done")), "0_a") is None
```

- [ ] **Step 2: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: üç kırmızı (`AttributeError: module ... has no attribute 'frame_after'`).

---

### Task 2: Yeniden üretim modu taşıyor

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `regenerate(..., mode=…)`, `production_mode.InvalidMode`, `regenerate.NoNextFrame`.

- [ ] **Step 1: İçe aktarımı genişlet**

Dosyanın `regenerate` içe aktarımına `NoNextFrame` ekleniyor; `InvalidMode` bugün
`queue_layer`'dan geliyor ve uygulama turunda `production_mode`'a taşınacak — test onu
`production_mode.InvalidMode` olarak okuyor, çünkü taşındıktan sonra evi orası.

- [ ] **Step 2: Altı testi yaz**

`test_a_frame_made_again_is_produced_under_its_own_name`'in altına:

```python
def make_video_again(fid, mode=None, gallery=((0, "a"), (1, "a"))):
    """One frame's video made again, with the mode the form would have sent.

    A video rather than a photo: the mode belongs to a video and nothing else, and a photo job would
    answer for a rule it does not have.
    """
    store, record, plan_store = video_project(*gallery)
    extra = {} if mode is None else {"mode": mode}
    born = regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                      {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                      "düğün", fid, layers.VIDEO, "p", **extra)
    return born, plan_store.appended[-1][0]


def test_a_video_made_again_is_planned_in_the_mode_it_was_asked_for():
    """The whole madde in one line: pressing the button without touching the box has to keep the
    video's own mode, and the form can only keep it by sending it."""
    _born, job = make_video_again("0_a", production_mode.LOOP)

    assert job["mode"] == production_mode.LOOP


def test_a_linked_video_made_again_is_planned_with_its_target():
    # Resolved here rather than sent by the screen: the gallery is already open on this side, and a
    # target coming from outside would be the same rule living in two places.
    _born, job = make_video_again("0_a", production_mode.LINKED)

    assert job["linkedTo"] == "1_a"


def test_linking_the_last_frame_of_the_film_is_refused():
    """The screen closes the button before this can be pressed. The server refuses anyway: planning
    a job with nothing to end on would send it to a render that fails on a target it cannot name."""
    with pytest.raises(NoNextFrame):
        make_video_again("1_a", production_mode.LINKED)


def test_a_mode_nobody_knows_is_refused():
    with pytest.raises(production_mode.InvalidMode):
        make_video_again("0_a", "kelebek")


def test_a_mode_on_a_layer_that_ends_nowhere_is_refused():
    # Only a video arrives at a picture. Ignoring the argument would hide the caller's mistake
    # behind a photo that came out fine.
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(production_mode.InvalidMode):
        regenerate(sync_runner(), store, record, plan_store, FakeOrderStore(),
                   {layers.PHOTO: FakeGenerator()}, lambda: 7, lambda: "t",
                   "düğün", "0_a", layers.PHOTO, "p", mode=production_mode.LOOP)


def test_a_video_made_again_with_no_mode_named_is_planned_without_one():
    # Every caller before this madde named none, and the plan has to keep reading back the same way.
    _born, job = make_video_again("0_a")

    assert "mode" not in job
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: dokuz kırmızı — Task 1'in üçü ve bunlardan altısı. Sonuncusu (`no mode named`) doğuştan
yeşil olabilir; çıktı ne diyorsa o yazılır.

---

### Task 3: Uç modu geçiriyor

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_routes.py`

- [ ] **Step 1: `regenerate_request`'i genişlet**

```python
def regenerate_request(client, frame, layer="photo", prompt="a", project="düğün", mode=None):
    body = {"frame": frame, "layer": layer, "prompt": prompt}
    if mode is not None:
        # Left out rather than sent as null: what the older screen sends is a body with no mode at
        # all, and that shape has to keep working.
        body["mode"] = mode
    return client.post(f"/api/projects/{project}/regenerate", json=body)
```

- [ ] **Step 2: İki testi yaz**

`test_a_frame_made_again_joins_the_gallery_beside_its_source`'un altına:

Modun plana geçtiği uçta **üretim üzerinden gözlenemiyor**: `make_client`'ın üretici haritasında
video yok, dolayısıyla iş kuyrukta bekliyor ve kare hiçbir mod taşımıyor. Uçta gözlenebilen şey
değerin kurala ulaşması, ve onu iki reddediş gösteriyor. Modun doğru geçtiğini Task 2 kullanım
durumu seviyesinde zaten tutuyor.

```python
def test_a_regenerate_mode_nobody_knows_is_refused(tmp_path):
    """Proof that the body's mode reaches the rule at all: an unknown one could not be refused if
    the route were dropping the field."""
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = regenerate_request(client, "P0_0", layer="video", mode="kelebek")

    assert resp.status_code == 400
    assert resp.get_json()["error"]


def test_linking_a_frame_with_nothing_after_it_is_refused_with_a_reason(tmp_path):
    """One frame in the gallery, so it is the film's last. The screen never sends this; the answer
    still has to be a refusal rather than a job that will fail later."""
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = regenerate_request(client, "P0_0", layer="video", mode="linked")

    assert resp.status_code == 400
    assert resp.get_json()["error"]
```

- [ ] **Step 3: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: ikisi de kırmızı — bugün her ikisi de 202 dönüyor, çünkü uç `mode`'u hiç okumuyor.

---

### Task 4: Formun üç parçası

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

**Interfaces:**
- Consumes: `LAYERED`, `open(fid, {frames})`, `tab(name)`, `regenButton()`, `regenerateFrame` sahtesi.

- [ ] **Step 1: Bloğu yaz**

`PhotoDetail — how the video was made` bloğunun altına:

```jsx
describe("PhotoDetail — the new mode", () => {
  // The gallery's top is the film's last frame: the export stitches it reversed. NEWER stands above
  // P0_0, so P0_0 has somewhere to link to and NEWER has not.
  const LOOPED = { ...LAYERED, modes: { video: "loop" } };
  const NEWER = { id: "P1_0", file: "P1_0.png", status: "done", prompt: "sonraki", negative: "",
                  layers: { photo: "P1_0.png" }, failed: [], owed: [], prompts: {} };
  const UNMADE = { ...NEWER, status: "pending", layers: {}, owed: ["photo"] };
  const modeBox = () => screen.getByLabelText("Yeni mod");

  async function openVideo(frames) {
    await open("P0_0", { frames });
    fireEvent.click(tab("Video"));
  }

  it("offers the new mode, opened on the one this video was made in", async () => {
    await openVideo([NEWER, LOOPED]);

    expect(modeBox().value).toBe("loop");
  });

  it("opens on the plain one when the video's line never named a mode", async () => {
    await openVideo([NEWER, LAYERED]);

    expect(modeBox().value).toBe("standard");
  });

  it("keeps the video's own mode when nobody touched the box", async () => {
    // The point of the default: a user who only edited the prompt gets the video they had.
    regenerateFrame.mockResolvedValue({ job: "running", frame: "P0_1" });
    await openVideo([NEWER, LOOPED]);

    await act(async () => { fireEvent.click(regenButton()); });

    expect(regenerateFrame).toHaveBeenCalledWith("düğün", "P0_0", "video", "kadın dönüyor", "loop");
  });

  it("sends the mode that was picked", async () => {
    regenerateFrame.mockResolvedValue({ job: "running", frame: "P0_1" });
    await openVideo([NEWER, LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "standard" } });
    await act(async () => { fireEvent.click(regenButton()); });

    expect(regenerateFrame).toHaveBeenCalledWith("düğün", "P0_0", "video", "kadın dönüyor",
                                                 "standard");
  });

  it("marks the box once the mode is no longer the video's own", async () => {
    await openVideo([NEWER, LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "standard" } });

    expect(modeBox().style.borderColor).toBe("var(--accent)");
  });

  it("closes production when the film's last frame is asked to link", async () => {
    // The gallery's top. The design refused both a disabled option and an error after the press:
    // the option is pickable, and picking it says why and shuts the button.
    await openVideo([LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "linked" } });

    expect(modeBox().style.borderColor).toBe("var(--danger)");
    expect(screen.getByText("Bu son kare — bağlanacak sonraki kare yok.")).toBeTruthy();
    expect(regenButton().disabled).toBe(true);
  });

  it("closes it too when the next frame has no picture yet", async () => {
    // The design never named this one. Letting it through would be the error-after-the-press it
    // refused, so it closes the same way and says its own reason.
    await openVideo([UNMADE, LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "linked" } });

    expect(screen.getByText("Sonraki karenin fotoğrafı henüz üretilmedi.")).toBeTruthy();
    expect(regenButton().disabled).toBe(true);
  });

  it("leaves linking alive where there is something to link to", async () => {
    await openVideo([NEWER, LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "linked" } });

    expect(regenButton().disabled).toBe(false);
    expect(screen.queryByText(/bağlanacak sonraki kare yok/)).toBeNull();
  });

  it("says what pressing would open", async () => {
    await openVideo([NEWER, LOOPED]);

    expect(screen.getByText("Yeni bir kare açılır — P0_0 kopyası, loop video.")).toBeTruthy();
  });

  it("follows the mode with that line", async () => {
    await openVideo([NEWER, LOOPED]);

    fireEvent.change(modeBox(), { target: { value: "linked" } });

    expect(screen.getByText("Yeni bir kare açılır — P0_0 kopyası, bağlı video.")).toBeTruthy();
  });

  it("puts none of it on the photo tab", async () => {
    // A photo arrives nowhere, and the design wrote no sentence for what its regenerate would open.
    await open("P0_0", { frames: [NEWER, LOOPED] });

    expect(screen.queryByLabelText("Yeni mod")).toBeNull();
    expect(screen.queryByText(/Yeni bir kare açılır/)).toBeNull();
  });

  it("puts none of it on the sound tab either", async () => {
    await open("P0_0", { frames: [NEWER, LOOPED] });

    fireEvent.click(tab("Ses"));

    expect(screen.queryByLabelText("Yeni mod")).toBeNull();
    expect(screen.queryByText(/Yeni bir kare açılır/)).toBeNull();
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

Expected: QueenAgent'ın ikisi yeşil. Ön yüzde **on kırmızı** — on ikinin ikisi (foto ve ses
sekmesinin yokluğu) doğuştan yeşil, çünkü kutu bugün hiç yok.

Python tarafı **koleksiyon hatası** veriyor:

```
ERROR queen-editor\backend\tests\test_export.py
ERROR queen-editor\backend\tests\test_photo_usecases.py
!!! Interrupted: 2 errors during collection !!!
ImportError: cannot import name 'NoNextFrame' from ...usecases.regenerate
```

`test_export.py` da düşüyor, çünkü `test_photo_usecases`'ten yardımcı içe aktarıyor.

**Bunun bedeli var ve söylenmesi gerekiyor:** pytest oturumu kesildiği için geri kalan ~650 test bu
turda hiç koşmuyor. Yani "kırmızı" burada bir sayı değil, bir durma.

**Neden kabul ediliyor:** turun tek kuralı, kaynağa dokunmadan testleri yazmak. `NoNextFrame`'i var
etmenin yolu onu `regenerate.py`'ye eklemek — yani kaynağı bu turda değiştirmek. Boş bir iskelet
sınıf da kaynağa dokunmak olurdu ve üstelik uygulama turunun işini önden yapardı.

Uygulama turunun ilk adımı bu yüzden istisnayı var etmek: koleksiyon açılır açılmaz gerçek kırmızı
sayısı görünür hâle geliyor.

---

### Task 5: Kırmızıyı commit et

- [ ] **Step 1: Sayıları oku**

Ön yüzde 10 kırmızı, 2 doğuştan yeşil. Python tarafında koleksiyon hatası — yukarıdaki iki modül,
ve oturumun kesilmesi.

- [ ] **Step 2: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): making a video again asks which mode it should be

Regenerate has never known about modes, so a loop video made again came back plain and
lost the badge it had. These tests give the form a Yeni mod box whose default is this
video's own mode: a user who edited only the prompt presses once and gets the video they
had.

The target of a linked one is worked out on the server, from the gallery it already
holds. A target sent from the screen would be the same rule living in two places.

Linking the film's last frame is refused there too. The screen shuts the button before
it can be pressed -- the design refused both a disabled option and an error after the
press -- but a job planned with nothing to end on would reach a render that fails on a
target it cannot even name.

The screen asks the server's own question rather than only the design's: a next frame
whose picture has not landed is no target either, and the design never named that case.
Letting it through would be exactly the error-after-the-press it refused, so it closes
the same way in its own words.

The rule for which frame comes next now has one home and two callers, and so does the
mode validation.

Ten red on the front. The python side does not get as far as a number: NoNextFrame does
not exist yet, so two modules will not import and pytest stops collecting -- around 650
tests never run this round. Writing an empty class to open the collection would be
touching the source, which is the one thing this round does not do. The implementation
round starts by making the exception, and the real count appears with it.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in yirmi üç testi Task 1'de üç, Task 2'de altı, Task 3'te iki, Task 4'te on
iki. 2. karar (`validate`'in taşınması) bilerek testsiz; 9. karar (kimlikle anma) 20. testin
`P0_0 kopyası` beklentisinde.

**Tip tutarlılığı:** `frame_after(gallery, fid) -> str | None` üç testte de aynı imzayla.
`regenerate(..., mode=…)` anahtar kelimeli, çünkü bugünkü çağıranların hiçbiri onu vermiyor.
`regenerateFrame` beşinci argümanı dize.

**Kontrol edilen tuzak:** 12–21 arası testler galeriye **iki** kare koyuyor (`[NEWER, LOOPED]`),
çünkü tek kareli bir galeride her kare son karedir ve bağlama testlerinin hepsi yanlış sebeple
geçerdi.

**Kontrol edilen tuzak 2:** 14. test kutuya hiç dokunmuyor ve yine de `"loop"` bekliyor. Varsayılanı
`STANDARD` yapıp kutuyu doğru gösteren bir uygulama burada düşüyor.

**Kontrol edilen tuzak 3:** 17. test üç şeyi birden ölçüyor — kenarlık, cümle, pasif buton. Üçü tek
durum; birini ölçüp ötekileri bırakmak, yarısı uygulanmış bir kapanmayı yeşil gösterirdi.

**Kontrol edilen tuzak 4:** 22. ve 23. testler hem kutuyu hem satırı arıyor. Yalnız kutuyu aramak,
satırı her sekmeye çizen bir uygulamada da geçerdi.

**Kontrol edilen tuzak 5:** `modeBox` `getByLabelText` kullanıyor, `querySelector("select")` değil —
sayfada başka bir `select` doğduğu gün ikincisi sessizce yanlış kutuyu tutardı.
