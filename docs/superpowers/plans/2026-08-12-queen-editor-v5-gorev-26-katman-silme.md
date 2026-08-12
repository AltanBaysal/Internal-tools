# Queen Editor v5 · Görev 26 — Sekme başına tek yıkıcı eylem · Uygulama planı

> Tasarım: [Görev 26 spec](../specs/2026-08-12-queen-editor-v5-gorev-26-katman-silme-design.md).
> Önce kırmızı test, sonra en küçük kod.

**Hedef:** açık sekme hangi katmansa yıkıcı buton onu silsin; kare galeride kalsın.

**Mimari:** yeni use case `domain/usecases/remove_layer.py`; uç nokta
`POST /api/projects/<p>/layers/<kind>/delete`; detay sayfası sekmeye göre buton ve onay seçer.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — `remove_layer`

**Dosyalar:** yeni `domain/usecases/remove_layer.py`, test: `tests/test_photo_usecases.py`

**Arayüz:**

```python
def remove_layer(record, store, plan_store, order_store, now, project, file, kind) -> dict
```

- [ ] **Adım 1 — kırmızı testler:**

```python
def layered_project(audio=True):
    """A produced frame that carries a photo, a video and (by default) a sound."""
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})
    if audio:
        record.append("düğün", {"file": "0_a_V1_0_S1_0.wav", "frame": "0_a", "layer": "audio",
                                "status": "done", "prompt": "kumaş"})
    return store, record, plan_store


def test_deleting_a_video_takes_the_sound_over_it():
    store, record, plan_store = layered_project()

    gone = remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                        "düğün", "0_a.png", layers.VIDEO)

    assert gone == {"deleted": ["0_a_V1_0.mp4", "0_a_V1_0_S1_0.wav"]}
    assert sorted(store.deleted) == ["0_a_V1_0.mp4", "0_a_V1_0_S1_0.wav"]
    # The frame keeps its place and its picture.
    assert list(record.slots("düğün")["0_a"]) == ["photo", "video", "audio"]
    assert record.slots("düğün")["0_a"]["photo"]["status"] == "done"
    assert record.slots("düğün")["0_a"]["video"]["status"] == "deleted"


def test_deleting_a_sound_leaves_the_video_alone():
    store, record, plan_store = layered_project()

    remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                 "düğün", "0_a.png", layers.AUDIO)

    assert store.deleted == ["0_a_V1_0_S1_0.wav"]
    assert record.slots("düğün")["0_a"]["video"]["status"] == "done"


def test_a_layer_the_frame_does_not_carry_costs_nothing():
    store, record, plan_store = layered_project(audio=False)

    assert remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                        "düğün", "0_a.png", layers.AUDIO) == {"deleted": []}
    assert store.deleted == []


def test_a_file_another_frame_still_holds_is_left_on_disk_when_a_layer_goes():
    store, record, plan_store = layered_project(audio=False)
    # A sound copy shares this very video (madde 102).
    record.append("düğün", {"file": "0_a.png", "frame": "P0_1", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "P0_1", "layer": "video",
                            "status": "done"})

    remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                 "düğün", "0_a.png", layers.VIDEO)

    assert store.deleted == []
    assert record.slots("düğün")["P0_1"]["video"]["status"] == "done"


def test_a_job_still_owed_above_the_deleted_layer_leaves_the_queue():
    # Its video is gone, so the sound that was coming has nothing to lie over.
    store, record, plan_store = layered_project(audio=False)
    plan_store.append("düğün", [{"id": "0_a", "type": "audio", "number": 0, "variant": 0,
                                 "prompt": "", "negative": "", "seed": None, "model": ""}])

    remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                 "düğün", "0_a.png", layers.VIDEO)

    assert record.slots("düğün")["0_a"]["audio"]["status"] == "removed"
    assert owed_files(record, plan_store) == []


def test_deleting_a_layer_of_a_frame_the_gallery_does_not_know_is_refused():
    store, record, plan_store = layered_project()

    with pytest.raises(FrameMissing):
        remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                     "düğün", "yok.png", layers.VIDEO)


def test_the_gallery_stops_reporting_a_deleted_layer():
    store, record, plan_store = layered_project()

    remove_layer(record, store, plan_store, FakeOrderStore(), lambda: "t",
                 "düğün", "0_a.png", layers.VIDEO)

    frame = list_frames(record, store, plan_store, FakeOrderStore(), "düğün")[0]
    assert frame["layers"] == {"photo": "0_a.png"}
    assert frame["status"] == "done"
```

`owed_files` var olan yardımcı; `video_project` ve `FakeOrderStore` de var.

- [ ] **Adım 2:** kırmızı (`ModuleNotFoundError`).

- [ ] **Adım 3 — `remove_layer.py`:**

```python
"""Take one layer off a frame -- the frame itself stays in the gallery.

"sil = kaldır" read at one height of the stack: what goes is the named layer and everything ABOVE
it, because a sound is mixed over a video and a sound whose video is gone lies over nothing (madde
31). What is under it is not touched.

Removing the photo is not this use case's business: the photo is the base layer, so deleting it is
deleting the frame, and remove_frames is where that lives.

Which files really go is decided the same way a frame's deletion decides it -- a file another frame
still holds stays where it is (madde 101) -- and the disk is touched before the log, so a failed
unlink leaves the record untouched.
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.photo_name import layer_file
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.retry_frame import FrameMissing  # noqa: F401


def remove_layer(record, store, plan_store, order_store, now, project, file, kind):
    """Returns what really left the disk: {"deleted": [file names]}."""
    # Raises ProjectMissing when there is no such project.
    gallery = {frame["file"]: frame
               for frame in list_frames(record, store, plan_store, order_store, project)}
    frame = gallery.get(file)
    if frame is None:
        raise FrameMissing(f"Bu kare galeride yok: {file}")

    slots = record.slots(project)
    cells = slots.get(frame["id"], {})
    over = queue.ORDER[queue.ORDER.index(kind):]      # the layer itself and everything above it
    closing = {(frame["id"], slot) for slot in over
               if layers.is_taken((cells.get(slot) or {}).get("status"))}
    deleted = sorted(layers.files_to_unlink(slots, closing))

    for name in deleted:
        store.delete(project, name)
    for fid, slot in sorted(closing):
        record.mark(project, fid, slot, slots[fid][slot]["file"], queue.DELETED, now())
    # A job the queue still owes above the closed layer never gets to be made: it would look for a
    # video that is no longer there. The name is the one it would have taken.
    for slot in over:
        if slot in frame.get("owed", []):
            record.mark(project, frame["id"], slot,
                        layer_file(slot, frame["id"], (cells.get(layers.VIDEO) or {}).get("file")),
                        queue.REMOVED, now())
    return {"deleted": deleted}
```

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Uç nokta

**Dosyalar:** `presentation/routes.py`, `main.py`, test: `tests/test_photo_routes.py`

- [ ] **Adım 1 — kırmızı testler:**

```python
def delete_layer_request(client, file, layer="video", project="düğün"):
    return client.post(f"/api/projects/{project}/layers/{layer}/delete", json={"file": file})


def give_it_a_video(drive, frame="P0_0", project="düğün"):
    """Put a produced video on a frame, the way the engine would.

    By hand because no video producer runs in these tests -- the graph is not in the repo. A second
    DrivePhotoRecord over the same folder is the same log: the record is a file, not a session.
    """
    name = f"{frame}_V1_0.mp4"
    (drive / project / name).write_bytes(b"MP4")
    DrivePhotoRecord(DriveStorage(str(drive))).append(project, {
        "file": name, "frame": frame, "layer": "video", "status": "done",
        "prompt": "kadın dönüyor"})
    return name


def test_deleting_a_video_leaves_the_frame_in_the_gallery(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    give_it_a_video(drive)

    resp = delete_layer_request(client, "P0_0.png")

    assert resp.status_code == 200
    assert resp.get_json() == {"deleted": ["P0_0_V1_0.mp4"]}
    assert not (drive / "düğün" / "P0_0_V1_0.mp4").exists()
    assert files_of(client) == ["P0_0.png"]


def test_the_photo_layer_is_not_deleted_this_way(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    assert delete_layer_request(client, "P0_0.png", layer="photo").status_code == 404


def test_deleting_a_layer_of_an_unknown_frame_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    assert delete_layer_request(client, "9_z.png").status_code == 404
```

`DrivePhotoRecord` ve `DriveStorage` bu test dosyasında zaten import edili.

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — `routes.py`:**

```python
# The layers that can be taken off a frame on their own. The photo is not among them: it is the
# base layer, so removing it is removing the frame (POST …/frames/delete).
REMOVABLE = (layers.VIDEO, layers.AUDIO)

    @bp.post("/api/projects/<project>/layers/<kind>/delete")
    def delete_layer(project, kind):
        if kind not in REMOVABLE:
            return jsonify({"error": f"Silinebilir bir katman değil: {kind}"}), 404
        body = request.get_json(silent=True) or {}
        try:
            return jsonify(remove_layer(project, body.get("file"), kind))
        except (ProjectMissing, FrameMissing) as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            # The operating system's own words -- never guess the cause.
            return jsonify({"error": str(exc)}), 500
```

`make_photo_generation_blueprint` imzasına `remove_layer` eklenir; `main.py` ve testin `make_client`'ı
bağlar.

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 3 — Ön yüz: sekmenin kendi butonu

**Dosyalar:** `shared/api.js`, `useGeneration.js`, `PhotoDetail.jsx`,
test: `PhotoDetail.test.jsx`

- [ ] **Adım 1 — kırmızı testler** (`removeLayer: vi.fn()` api mock'una eklenir ve import edilir)**:**

```jsx
describe("PhotoDetail — one destructive action per tab", () => {
  it("offers the frame on the photo tab and the layer on the others", async () => {
    await open("P0_0.png", { frames: [LAYERED] });
    expect(screen.getByText("Sil")).toBeTruthy();

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Videoyu sil — kare kalır")).toBeTruthy();
    expect(screen.queryByText("Sil")).toBeNull();

    fireEvent.click(tab("Ses"));
    expect(screen.getByText("Sesi sil — video kalır")).toBeTruthy();
  });

  it("asks with the design's own words before taking a video", async () => {
    await open("P0_0.png", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));

    expect(screen.getByText("Video silinsin mi?")).toBeTruthy();
    expect(screen.getByText(/üzerindeki ses kalıcı olarak silinir/)).toBeTruthy();
    expect(removeLayer).not.toHaveBeenCalled();
  });

  it("says what a sound costs instead", async () => {
    await open("P0_0.png", { frames: [LAYERED] });

    fireEvent.click(tab("Ses"));
    fireEvent.click(screen.getByText("Sesi sil — video kalır"));

    expect(screen.getByText("Ses silinsin mi?")).toBeTruthy();
    expect(screen.getByText(/video sessiz oynar/)).toBeTruthy();
  });

  it("deletes the open layer and comes back to the photo tab", async () => {
    removeLayer.mockResolvedValue({ deleted: ["P0_0_V1_0.mp4"] });
    await open("P0_0.png", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));
    await act(async () => { fireEvent.click(confirmButton()); });

    expect(removeLayer).toHaveBeenCalledWith("düğün", "P0_0.png", "video");
    expect(navigate).not.toHaveBeenCalled();
    expect(tab("Foto").getAttribute("aria-current")).toBe("page");
  });

  it("stays on the frame and says so when the server refuses", async () => {
    removeLayer.mockRejectedValue(new Error("Proje yok: düğün"));
    await open("P0_0.png", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByText("Videoyu sil — kare kalır"));
    await act(async () => { fireEvent.click(confirmButton()); });

    expect(screen.getByText("Video silinemedi")).toBeTruthy();
  });

  it("leaves no fill under any of the three (madde 83)", async () => {
    await open("P0_0.png", { frames: [LAYERED] });
    expect(screen.getByText("Sil").closest("button").style.background).toBe("none");

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Videoyu sil — kare kalır").closest("button").style.background)
      .toBe("none");
  });
});
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:**

`api.js`:

```js
// Take one layer off a frame. The frame stays: what goes is this layer and whatever lies over it.
export async function removeLayer(project, file, kind) {
  return request(`/api/projects/${encodeURIComponent(project)}/layers/${kind}/delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file }),
  });
}
```

`useGeneration.js`: `removeLayer(file, kind)` — cevabı döndürür, reddedilince `null` ve `setError`;
ardından `poll()` (kuyruk başlamaz, yalnız galeri tazelenir).

`PhotoDetail.jsx`:

```jsx
// The one destructive thing each tab offers (madde 80). The photo tab's is the frame itself and
// keeps its own words until Görev 31; these two take a layer and say what survives it.
const DESTRUCTIVE = {
  video: { label: "Videoyu sil — kare kalır", title: "Video silinsin mi?",
           body: "Bu video ve üzerindeki ses kalıcı olarak silinir — bu geri alınamaz. "
                 + "Kare ve fotoğrafı galeride kalır." },
  audio: { label: "Sesi sil — video kalır", title: "Ses silinsin mi?",
           body: "Bu ses kalıcı olarak silinir — bu geri alınamaz. Video ve kare kalır; "
                 + "video sessiz oynar." },
};
```

- buton: `open === "photo"` ise bugünkü buton, değilse `DESTRUCTIVE[open].label`; üçünde de
  `background: "none"` (madde 83);
- onay: foto bugünkü 320'lik pencere, katman `width={400}` ve `DESTRUCTIVE[open]` metinleri;
- `handleDeleteLayer`: `removeLayer(file, open)` → başarılıysa `setOpen("photo")`, reddedilirse
  `setRefused(true)`; kart metni `${LAYER_WORD[open]} silinemedi`;
- sahne, katmanı olmayan sekmede oynatıcı çizmez (`holds`): silme ile poll'un arasına düşen tazeleme
  oynatıcıyı olmayan dosyayla bırakmasın.

- [ ] **Adım 4:** yeşil.

---

## Görev 4 — Tam takım, build, commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): each tab takes away only what it shows
```
