# Queen Editor v5 · Görev 18 — Galeride video · Uygulama planı

> **Uygulayıcıya:** her adım önce kırmızı test, sonra en küçük kod. Tasarım:
> [Görev 18 spec](../specs/2026-08-12-queen-editor-v5-gorev-18-galeride-video-design.md).

**Hedef:** videolu kare rozetini kazansın, videosu kuyrukta/üretilen kare fotoğrafıyla dursun ve
hâlini hapıyla söylesin, kuyruk paneli video işlerini saysın.

**Mimari:** sunucu her kare satırına `owed` ve `failed` listelerini ekler; ekran hapı ve rozeti
onlardan çizer, çalışan işin katmanı `currentLayer` olarak taşınır.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Katman sırası her yerde foto → video → ses.
- Test komutları (birebir):
  - `python -m pytest queen-editor -q`
  - `npm test --prefix queen-editor/frontend -- --run`
  - `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — Satır ne beklediğini söyler

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/domain/usecases/list_frames.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

- [ ] **Adım 1 — kırmızı testler (galeri testlerinin yanına):**

```python
def test_a_frame_says_which_layers_the_queue_still_owes_it():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store = FakePlanStore(frames=[
        frame(0),
        {"id": "0_a", "type": "video", "number": 0, "prompt": "", "negative": "", "seed": None,
         "model": ""},
        frame(1),
    ])

    rows = {row["id"]: row for row in
            list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")}

    assert rows["0_a"]["owed"] == ["video"]     # its photo landed; the video is still coming
    assert rows["1_a"]["owed"] == ["photo"]
    assert rows["0_a"]["failed"] == []


def test_a_produced_layer_leaves_the_owed_list():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    plan_store = FakePlanStore(frames=[
        frame(0),
        {"id": "0_a", "type": "video", "number": 0, "prompt": "", "negative": "", "seed": None,
         "model": ""},
    ])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert rows[0]["owed"] == []


def test_a_layer_that_blew_up_is_named_as_such():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", "failed", "t", error="node 41")
    plan_store = FakePlanStore(frames=[frame(0)])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    # A failed layer holds its slot -- it is not owed and it is not done.
    assert rows[0]["failed"] == ["video"]
    assert rows[0]["owed"] == []
```

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı.

- [ ] **Adım 3 — `list_frames.py`:** modül başlığına bir paragraf ve iki yardımcı:

```python
def _owed_layers(jobs, slots):
    """{frame: [layer, ...]} -- what the queue still owes each frame, in the engine's own order."""
    owed = {}
    for job in queue.open_jobs(jobs, slots):
        owed.setdefault(job["id"], []).append(queue.type_of(job))
    return owed


def _failed_layers(cells):
    """The frame's layers whose latest line says the render blew up, in layer order."""
    return [slot for slot in queue.ORDER
            if (cells.get(slot) or {}).get("status") == queue.FAILED]
```

`list_frames` gövdesinde, `slots` okunduktan sonra:

```python
    owed = _owed_layers(plan_store.read(project)["frames"], slots)
```

> `plan_store.read` zaten döngüde çağrılıyor; onu bir değişkene al ve ikisinde de kullan.

ve iki satır oluşumuna `"owed": owed.get(fid, []), "failed": _failed_layers(cells)` eklenir (plan
döngüsünde ve kaydın kendi döngüsünde).

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Çalışan işin katmanı ve gerçek sayılar

**Dosyalar:**
- Değişecek: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`
- Test: `queen-editor/frontend/src/features/photo_generation/useGeneration.test.jsx`

- [ ] **Adım 1 — kırmızı testler:**

```jsx
it("says which layer the worker is making, not just which frame", async () => {
  api.getStatus.mockResolvedValue({ status: "running", project: "düğün",
                                    current: { id: "P0_0", type: "video" } });
  const { result } = renderHook(() => useGeneration("düğün"));

  await waitFor(() => expect(result.current.current).toBe("P0_0.png"));
  expect(result.current.currentLayer).toBe("video");
});

it("counts the video jobs the frames say they are owed", async () => {
  api.listFrames.mockResolvedValue([
    { id: "P0_0", file: "P0_0.png", status: "done", layers: {}, owed: ["video"], failed: [] },
    { id: "P1_0", file: "P1_0.png", status: "done", layers: {}, owed: [], failed: ["video"] },
  ]);
  const { result } = renderHook(() => useGeneration("düğün"));

  await waitFor(() => expect(result.current.queue).toEqual([{ layer: "video", owed: 1 }]));
  expect(result.current.failures).toEqual([{ layer: "video", count: 1 }]);
});
```

> Dosyanın kendi `api` mock kalıbını ve `renderHook` kullanımını aynen izle.

- [ ] **Adım 2:** `npm test --prefix queen-editor/frontend -- --run` → kırmızı.

- [ ] **Adım 3 — `useGeneration.js`:**

```js
  const currentLayer = job.project === project && job.status === "running" && job.current
    ? (job.current.type || "photo")
    : null;
```

`owedByKind` ve `failedByKind` satırlardan:

```js
  // What the queue owes and what blew up, layer by layer -- read off the gallery, which is the one
  // answer about what a frame is waiting for. The frame being made has no line on disk, so it
  // would count as owed: it comes out, because it is not waiting, it is being made.
  const owedByKind = { photo: 0, video: 0, audio: 0 };
  const failedByKind = { photo: 0, video: 0, audio: 0 };
  shown.forEach((frame) => {
    (frame.owed || []).forEach((layer) => {
      if (frame.file === current && layer === currentLayer) return;
      owedByKind[layer] += 1;
    });
    (frame.failed || []).forEach((layer) => { failedByKind[layer] += 1; });
  });
```

> Eski `photo` sayımları (`status === "pending"` / `"failed"`) kalkar: satır artık ikisini de
> `owed`/`failed` ile söylüyor.

- [ ] **Adım 4:** `npm test --prefix queen-editor/frontend -- --run` → yeşil (foto sayan eski
testler de yeşil kalmalı; kalmazsa mock satırlarına `owed`/`failed` ekle).

---

## Görev 3 — Rozet ve hap

**Dosyalar:**
- Değişecek: `queen-editor/frontend/src/features/photo_generation/glyphs.jsx`,
  `Gallery.jsx`, `ProjectScreen.jsx`, `PhotoDetail.jsx`
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

- [ ] **Adım 1 — kırmızı testler (`Gallery.test.jsx`):**

```jsx
const withVideo = (file, extra = {}) => ({
  id: file.replace(".png", ""), file, status: "done",
  layers: { photo: file, video: file.replace(".png", "_V1_0.mp4") }, owed: [], failed: [], ...extra,
});

describe("Gallery — what a frame owns", () => {
  it("marks a frame that has a video", () => {
    renderGallery({ frames: [withVideo("P0_0.png")] });

    expect(screen.getByText("video")).toBeTruthy();
    expect(document.querySelector("[data-glyph=play]")).toBeTruthy();
  });

  it("leaves a frame with no video unmarked", () => {
    renderGallery({ frames: [done("P0_0.png")] });

    expect(screen.queryByText("video")).toBeNull();
  });

  it("does not call a failed render a video the frame owns", () => {
    renderGallery({ frames: [withVideo("P0_0.png", { failed: ["video"] })] });

    expect(screen.queryByText("video")).toBeNull();
    expect(screen.getByText("video hata")).toBeTruthy();
  });

  it("keeps the photo on screen while the video is queued", () => {
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })] });

    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(screen.getByText("video kuyrukta")).toBeTruthy();
  });

  it("keeps the photo on screen while the video is being made", () => {
    renderGallery({ frames: [done("P0_0.png", { owed: ["video"] })],
                    current: "P0_0.png", currentLayer: "video" });

    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(screen.getByText("video üretiliyor")).toBeTruthy();
  });

  it("still draws the loading holder while the photo itself is being made", () => {
    renderGallery({ frames: [{ id: "P0_0", file: "P0_0.png", status: "pending", layers: {},
                               owed: ["photo"], failed: [] }],
                    current: "P0_0.png", currentLayer: "photo" });

    expect(screen.queryByAltText("P0_0.png")).toBeNull();
    expect(screen.getByText("foto üretiliyor")).toBeTruthy();
  });
});
```

> `renderGallery` ve `done` yardımcıları dosyada zaten var; `done`'ın ikinci parametresiyle satıra
> alan ekleyebildiğini doğrula, gerekiyorsa yardımcıyı genişlet.

- [ ] **Adım 2:** `npm test --prefix queen-editor/frontend -- --run` → kırmızı.

- [ ] **Adım 3 — `glyphs.jsx`:**

```jsx
// The play triangle the design asks for on the ownership badge. Filled, not stroked: at 9px a
// stroked triangle reads as a smudge.
export const PlayGlyph = ({ size }) => (
  <Glyph name="play" size={size}>
    <path d="M4.4 2.9 11 7l-6.6 4.1z" fill="currentColor" />
  </Glyph>
);
```

- [ ] **Adım 4 — `Gallery.jsx`:**

Sabit:

```jsx
// Madde 57's third plane: the order badge top right, the state pill top left, what the frame owns
// bottom right.
const OWNS = { position: "absolute", bottom: 6, right: 6, display: "flex", alignItems: "center",
               gap: 3, background: "rgba(10,8,7,.75)", color: "var(--ink-2)", padding: "2px 5px",
               borderRadius: 3, zIndex: 1, pointerEvents: "none" };
```

Yardımcı:

```jsx
/** The one thing worth saying about a frame's state, or nothing.
 *
 * Running first, then what blew up, then what is still owed: a frame can be several of these at
 * once, and two pills in one corner make the card unreadable. The rest is the detail page's job.
 */
function statusOf(frame, running) {
  if (running) return { layer: running, state: "running" };
  const failed = (frame.failed || [])[0];
  if (failed) return { layer: failed, state: "failed" };
  const owed = (frame.owed || [])[0];
  if (owed) return { layer: owed, state: "pending" };
  return null;
}
```

Karo çiziminde:

```jsx
          const running = frame.file === current ? currentLayer : null;
          // Only a photo render empties the card: a frame whose video is being made still has its
          // picture, and taking it away would say the photo is gone.
          const state = running === "photo" ? "running" : frame.status;
          const owns = (frame.layers || {}).video && !(frame.failed || []).includes("video");
```

`Tile`'a `pill={<StatusPill {...(statusOf(frame, running) || {})} />}` ve rozet:

```jsx
                      owns={owns}
```

`Tile` içinde, `pill`'in yanına:

```jsx
        {owns && (
          <span style={OWNS}>
            <PlayGlyph size={9} />
            <Mono size={9}>video</Mono>
          </span>
        )}
```

- [ ] **Adım 5 — `ProjectScreen.jsx`:** `currentLayer`'ı hook'tan al ve galeriye geçir.

- [ ] **Adım 6 — `PhotoDetail.jsx`:** aynı kural:

```jsx
  const state = frame && frame.file === current && currentLayer === "photo"
    ? "running" : frame?.status;
```

- [ ] **Adım 7:** `npm test --prefix queen-editor/frontend -- --run` → yeşil.

---

## Görev 4 — Tam takım, build ve commit

- [ ] **Adım 1:** `python -m pytest queen-editor -q`
- [ ] **Adım 2:** `npm test --prefix queen-editor/frontend -- --run`
- [ ] **Adım 3:** `npm run build --prefix queen-editor/frontend`
- [ ] **Adım 4:** `dist/` ile tek commit:

```
feat(queen-editor): the gallery says which frames own a video
```
