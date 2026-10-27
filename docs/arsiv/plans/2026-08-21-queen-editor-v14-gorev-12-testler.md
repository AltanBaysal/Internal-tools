# v14 Görev 12 — Toplu katman silme: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Toplu katman silmenin ne yapacağını 18 yeni testle yazmak, sözleşme değiştiği için gereken
güncellemeleri yapmak, ve hepsini kırmızı commit etmek. Kaynak kodda tek satır değişmiyor.

**Architecture:** Üç dosya. Arka uçta bugünkü `remove_layer` bir kimlik **listesi** almaya başlıyor,
yani onu çağıran testler yeni imzayla konuşuyor; ekranda bar iki düğme ve iki pencere kazanıyor.

**Tech Stack:** pytest, Flask test client, React 18 + vitest + @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-12-toplu-katman-silme-testler-design.md)

## Global Constraints

- **Bu tur yalnız test yazar.** `backend/` ve `frontend/src` altındaki kaynak dosyalar değişmiyor.
- Test adları ve yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `skip` / `xfail` yok.
- Henüz olmayan adlar: `domain/frame_list.py` (`InvalidFrames`), `remove_layer`'ın çoğul imzası,
  Gallery'nin `onRemoveLayer` prop'u. İlki python dosyalarının başında içe aktarıldığı için
  `test_photo_usecases.py` ve onunla birlikte `test_export.py` **toplanamıyor** — 11. maddedeki
  kararın aynısı, dürüst kırmızı ve bedeli yazılı.
- Yeni testler **Türkçe cümleleri birebir** yazıyor: `9 karenin videosu silinsin mi?`,
  `Seçili 12 kareden videosu olmayan 3 kare atlanır.`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `backend/tests/test_photo_usecases.py` | katman silme işi | 5 yeni + 8 güncelleme |
| `backend/tests/test_photo_routes.py` | rota | 2 yeni + 3 güncelleme |
| `frontend/src/features/photo_generation/Gallery.test.jsx` | bar ve pencereler | 11 yeni |
| `frontend/src/features/photo_generation/PhotoDetail.test.jsx` | tek karenin çağrısı | 1 güncelleme |

---

### Task 1: Katman silme işi

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `remove_layer(record, store, plan_store, order_store, now, project, frames, kind)` ve
  `frame_list.InvalidFrames` — henüz yok.

- [ ] **Step 1: İçe aktarmaları düzelt**

`copy_frames` ve `remove_frames` içe aktarmaları hata sınıflarını bırakıyor, yerine ortak ev:

```python
from backend.features.photo_generation.domain.frame_list import InvalidFrames
from backend.features.photo_generation.domain.usecases.copy_frames import copy_frames
from backend.features.photo_generation.domain.usecases.remove_frames import remove_frames
```

`InvalidFiles`'ı bekleyen test ve `InvalidFrames`'i bekleyen kopyalama testi aynı adı kullanıyor
artık; iki `pytest.raises` satırı da `InvalidFrames` diyor.

- [ ] **Step 2: Bugünkü yedi çağrıyı listeye al**

`remove_layer`'ı çağıran testlerde kimlik listeye giriyor — `"0_a"` → `["0_a"]`, `"P0_1"` →
`["P0_1"]`. Davranış iddiaları aynen duruyor.

- [ ] **Step 3: `FrameMissing` bekleyen testi değiştir**

`test_deleting_a_layer_of_a_frame_the_gallery_does_not_know_is_refused` siliniyor; yerini Step 5'in
3 numaralı testi alıyor ve aynı kimliği aynı yerden sınıyor.

- [ ] **Step 4: İki kareli demirbaşı yaz**

`layered_project`'in hemen altına:

```python
def two_layered(audio=True):
    """Two produced frames, each carrying a photo and a video (and a sound by default)."""
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    for number in (0, 1):
        record.append("düğün", {"file": f"{number}_a_V1_0.mp4", "frame": f"{number}_a",
                                "layer": "video", "status": "done"})
        if audio:
            record.append("düğün", {"file": f"{number}_a_V1_0_S1_0.wav", "frame": f"{number}_a",
                                    "layer": "audio", "status": "done"})
    return store, record, plan_store
```

- [ ] **Step 5: Beş testi yaz**

`test_the_gallery_stops_reporting_a_deleted_layer`'ın hemen üstüne:

```python
def test_one_layer_comes_off_every_frame_named():
    store, record, plan_store = two_layered()

    gone = remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                        "düğün", ["0_a", "1_a"], layers.VIDEO)

    assert gone == {"deleted": ["0_a_V1_0.mp4", "0_a_V1_0_S1_0.wav",
                                "1_a_V1_0.mp4", "1_a_V1_0_S1_0.wav"]}
    # The frames keep their places and their pictures: only the layer fell.
    assert [record.slots("düğün")[fid]["photo"]["status"] for fid in ("0_a", "1_a")] == [
        "done", "done"]
    assert [record.slots("düğün")[fid]["video"]["status"] for fid in ("0_a", "1_a")] == [
        "deleted", "deleted"]


def test_a_file_two_frames_share_goes_when_both_let_go_in_one_press():
    # The whole press is worked out before a line is written, which is the only way this can be
    # right: read frame by frame, the second would still see the first holding the file.
    store, record, plan_store = layered_project(audio=False)
    with_a_copy(record)

    gone = remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                        "düğün", ["0_a", "P0_1"], layers.VIDEO)

    assert gone == {"deleted": ["0_a_V1_0.mp4"]}
    assert store.deleted == ["0_a_V1_0.mp4"]


def test_a_layer_asked_off_an_identity_the_gallery_does_not_know_is_skipped():
    # Another tab can delete a frame while the confirm sits open; refusing the whole press over one
    # name that is already gone would leave the rest undone.
    store, record, plan_store = layered_project()

    gone = remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                        "düğün", ["yok", "0_a"], layers.VIDEO)

    assert gone == {"deleted": ["0_a_V1_0.mp4", "0_a_V1_0_S1_0.wav"]}


@pytest.mark.parametrize("names", ["0_a", [7], None])
def test_taking_a_layer_off_needs_a_list_of_identities(names):
    store, record, plan_store = layered_project()

    with pytest.raises(InvalidFrames):
        remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                     "düğün", names, layers.VIDEO)


def test_a_sound_still_owed_is_dropped_on_every_frame_the_video_left():
    store, record, plan_store = two_layered(audio=False)
    plan_store.append("düğün", [{"id": fid, "type": "audio", "number": number, "variant": 0,
                                 "prompt": "", "negative": "", "seed": None, "model": ""}
                                for number, fid in ((0, "0_a"), (1, "1_a"))])

    remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                 "düğün", ["0_a", "1_a"], layers.VIDEO)

    assert [record.slots("düğün")[fid]["audio"]["status"] for fid in ("0_a", "1_a")] == [
        "removed", "removed"]
    assert owed_files(record, plan_store) == []
```

- [ ] **Step 6: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: `test_photo_usecases.py` ve `test_export.py` toplanamıyor — `frame_list` yok.

---

### Task 2: Rota

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_routes.py`

**Interfaces:**
- Consumes: `POST …/layers/<kind>/delete`, gövde `{frames: [...]}`.

- [ ] **Step 1: Yardımcıyı çoğullaştır**

```python
def delete_layer_request(client, frames, layer="video", project="düğün"):
    return client.post(f"/api/projects/{project}/layers/{layer}/delete", json={"frames": frames})
```

Bugünkü iki çağrısı listeye giriyor: `delete_layer_request(client, ["P0_0"])`, ve foto katmanını
sınayan test `delete_layer_request(client, ["P0_0"], layer="photo")`.

- [ ] **Step 2: Bilinmeyen kareyi bekleyen testi değiştir**

```python
def test_deleting_a_layer_of_an_unknown_frame_is_skipped(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = delete_layer_request(client, ["P9_9"])

    # Skipped rather than refused: one name that is already gone must not undo the rest.
    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": []}
```

- [ ] **Step 3: İki testi yaz**

Onun hemen altına:

```python
def test_deleting_one_layer_off_many_frames_in_one_press(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    give_it_a_video(drive, "P0_0")
    give_it_a_video(drive, "P1_0")

    resp = delete_layer_request(client, ["P0_0", "P1_0"])

    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": ["P0_0_V1_0.mp4", "P1_0_V1_0.mp4"]}
    # The frames and their pictures stay exactly where they were: only the layer fell.
    gallery = client.get("/api/projects/düğün/frames").get_json()["frames"]
    assert [frame["layers"] for frame in gallery] == [{"photo": "P1_0.png"},
                                                      {"photo": "P0_0.png"}]


def test_a_layer_delete_body_that_is_not_a_list_of_identities_is_refused(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = delete_layer_request(client, "P0_0")

    assert resp.status_code == 400
    assert "metin dizisi" in resp.get_json()["error"]
```

- [ ] **Step 4: Takımı koştur**

Run: `python -m pytest queen-editor -q`
Expected: hâlâ toplama hatası — `frame_list` yok.

---

### Task 3: Bar ve pencereler

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: Gallery'nin `onRemoveLayer(frames, kind) -> Promise` prop'u — henüz yok.

- [ ] **Step 1: On bir testi yaz**

`describe("Gallery — copying a card", …)` bloğunun kapanışından sonra:

```jsx
describe("Gallery — taking a layer off many frames", () => {
  // A frame that carries all three layers. withVideo's extra is spread after its own map, so this
  // replaces it rather than adding to it.
  const withSound = (file) => withVideo(file, {
    layers: { photo: file, video: file.replace(".png", "_V1_0.mp4"),
              audio: file.replace(".png", "_V1_0_S1_0.wav") },
  });
  // Three frames, three answers to "does it carry this layer": both, video only, neither.
  const MIXED = [withSound("2_a.png"), withVideo("1_a.png"), done("0_a.png")];
  const remover = () => vi.fn().mockResolvedValue({ deleted: [] });

  function pick(...names) {
    names.forEach((name) => fireEvent.click(checkOf(name)));
  }

  it("puts the two layer buttons to the right of Sil", () => {
    renderGallery({ frames: MIXED, onCopy: vi.fn(), onRemoveLayer: remover() });
    pick("2_a.png");

    const bar = screen.getByText("1 seçili").parentElement;
    const words = [...bar.querySelectorAll("button")].map((one) => one.textContent.trim());
    expect(words).toEqual(["Tümünü seç", "Kopyala", "Sil", "Videoları sil", "Sesleri sil",
                           "Vazgeç"]);
  });

  it("draws no Videoları sil when nothing selected carries a video", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("0_a.png");

    // A window asking about 0 frames is not a window, so the button is simply not there.
    expect(screen.queryByText("Videoları sil")).toBeNull();
    expect(screen.queryByText("Sesleri sil")).toBeNull();
  });

  it("draws no Sesleri sil when nothing selected carries a sound", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("1_a.png");

    expect(screen.getByText("Videoları sil")).toBeTruthy();
    expect(screen.queryByText("Sesleri sil")).toBeNull();
  });

  it("counts only the frames that carry the layer", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png", "0_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));

    expect(screen.getByText("2 karenin videosu silinsin mi?")).toBeTruthy();
    expect(screen.getByText(/Kareler ve fotoğrafları kalır/)).toBeTruthy();
  });

  it("names the frames it will skip", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png", "0_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));

    // First, because it is what explains the number in the title.
    expect(screen.getByText(
      "Seçili 3 kareden videosu olmayan 1 kare atlanır. "
      + "Kareler ve fotoğrafları kalır. Videoya bindirilen sesler de gider.")).toBeTruthy();
  });

  it("says nothing about skipping when every selected frame carries the layer", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));

    expect(screen.queryByText(/atlanır/)).toBeNull();
  });

  it("promises the video stays when the sound is the one going", () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("2_a.png");

    fireEvent.click(screen.getByText("Sesleri sil"));

    expect(screen.getByText("1 karenin sesi silinsin mi?")).toBeTruthy();
    expect(screen.getByText("Kareler, fotoğrafları ve videoları kalır.")).toBeTruthy();
  });

  it("sends only the frames that carry the layer", async () => {
    const onRemoveLayer = remover();
    renderGallery({ frames: MIXED, onRemoveLayer });
    pick("2_a.png", "1_a.png", "0_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));
    // The window's own Sil is the last one on screen; the bar's is the first.
    await act(async () => { fireEvent.click(screen.getAllByText("Sil").at(-1)); });

    expect(onRemoveLayer).toHaveBeenCalledWith(["2_a", "1_a"], "video");
  });

  it("sends nothing when the window is cancelled", () => {
    const onRemoveLayer = remover();
    renderGallery({ frames: MIXED, onRemoveLayer });
    pick("2_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));
    fireEvent.click(screen.getByText("Vazgeç"));

    expect(onRemoveLayer).not.toHaveBeenCalled();
    expect(screen.queryByText("1 karenin videosu silinsin mi?")).toBeNull();
  });

  it("closes the selection once the layer is gone", async () => {
    renderGallery({ frames: MIXED, onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));
    await act(async () => { fireEvent.click(screen.getAllByText("Sil").at(-1)); });

    expect(screen.queryByText("2 seçili")).toBeNull();
  });

  it("does not count a video that blew up", () => {
    // The tile shows no video badge for a red layer, and the window has to agree with the tile.
    renderGallery({ frames: [withVideo("2_a.png"), withVideo("1_a.png", { failed: ["video"] })],
                    onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png");

    fireEvent.click(screen.getByText("Videoları sil"));

    expect(screen.getByText("1 karenin videosu silinsin mi?")).toBeTruthy();
    expect(screen.getByText(/videosu olmayan 1 kare atlanır/)).toBeTruthy();
  });
});
```

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: on bir kırmızı.

---

### Task 4: Detay sayfasının çağrısı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

- [ ] **Step 1: İddiayı listeye al**

```jsx
    expect(removeLayer).toHaveBeenCalledWith("düğün", ["P0_0"], "video");
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: queen-agent'ın ikisi yeşil (384 / 474). queen-editor python iki toplama hatasıyla duruyor.
queen-editor frontend'de **11 kırmızı** — Gallery'nin onu ve PhotoDetail'in güncellemesi. Gallery'nin
13 numaralı testi (`atlanır` cümlesinin yokluğu) doğuştan yeşil: düğme yokken pencere de yok, yani
ölçtüğü yokluk bugün zaten doğru. Nöbeti uygulama turunda, cümle doğduktan sonra tutuyor.

---

### Task 5: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): a layer can be taken off many frames at once

Eighteen tests for the bar's two new buttons and what they promise. A window counts only
the frames that really carry the layer, and when some of the selection does not, a sentence
of its own says how many are being skipped -- it comes first, because it is what explains
the number in the title. A layer that blew up is not one the frame carries: the tile shows
no badge for it, and the window agrees with the tile.

The buttons are not drawn at all when nothing selected carries that layer, and the request
carries exactly the frames the window counted.

Behind them, remove_layer takes a list of identities rather than one. One use case for one
frame and for many, the way deleting frames already works -- the layer is still singular,
only the frames are not. The whole press is worked out before a line is written, which is
the only way a file two frames share can be right: read one frame at a time, the second
would still see the first holding it.

An identity the gallery does not know is skipped rather than refused, for the reason
deleting frames already skips one: another tab can take a frame away while the window sits
open, and one gone name must not undo the rest.

The body check is now in three places, so it moves to one: frame_list carries the rule and
the exception. remove_frames loses InvalidFiles, whose name was already stale -- the body
says frames, not files.

test_photo_usecases.py imports a module that does not exist yet, so it and test_export.py
do not collect this round. Honest red with its cost written down.

queen-agent green (384 / 474). queen-editor frontend: 12 red.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in 18 testi Task 1 (1–5), Task 2 (6–7), Task 3 (8–18). Sözleşme
güncellemeleri Task 1 Step 1–3, Task 2 Step 1–2, Task 4.

**Tip tutarlılığı:** `remove_layer` her yerde `(…, project, frames, kind)`; cevabı hep
`{"deleted": [...]}`. `onRemoveLayer(frames, kind)` — kancanın imzasıyla aynı sıra.

**Kontrol edilen tuzak:** bardaki `Sil` çöp ikonu taşıdığı için metni boşlukla başlıyor; sırayı
okuyan test kırpıyor, ve `getByText("Videoları sil")` normalleştirme sayesinde çalışıyor.

**Kontrol edilen tuzak 2:** pencerenin onay düğmesi de `Sil` diyor. `getAllByText("Sil")` yalnız iki
düğmeyi buluyor — `Videoları sil` başka bir metin, eşleşmiyor — ve pencere JSX'te bardan sonra
çizildiği için sonuncusu pencerenindir.

**Kontrol edilen tuzak 3:** `withSound`, `withVideo`'nun `layers` haritasını **değiştiriyor**,
eklemiyor; `withVideo` extra'yı kendi haritasından sonra yaydığı için bu doğru.

**Kontrol edilen tuzak 4:** 13 numaralı test `queryByText(/atlanır/)` ile bir yokluğu ölçüyor ve
bugün de doğru — düğme yokken pencere de yok. Doğuştan yeşil olması bekleniyor; nöbeti uygulama
turunda, atlama cümlesi doğduktan sonra tutuyor.

**Bilerek dışarıda:** `useGeneration` ve `api.js`, 11. maddedeki gerekçeyle.
