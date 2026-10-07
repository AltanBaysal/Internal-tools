# Queen Editor v5 · Görev 19 — Katman hatası davranışı · Uygulama planı

> Tasarım: [Görev 19 spec](../specs/2026-08-12-queen-editor-v5-gorev-19-katman-hatasi-design.md).
> Her adım önce kırmızı test, sonra en küçük kod.

**Hedef:** hatalı katman aynı kareye geri gönderilsin; fotosu duran karede buton imleçle inen bir
örtüde çıksın; basılan buton kuyruğa girdiğini söylesin.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — Tekrar dene kırmızı katmanı iade eder

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/domain/usecases/retry_frame.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

- [ ] **Adım 1 — kırmızı testler (retry testlerinin yanına):**

```python
def test_retry_puts_the_frames_failed_layer_back_rather_than_its_photo():
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", "failed", "t", error="node 41")
    plan_store = FakePlanStore(frames=[
        frame(0),
        {"id": "0_a", "type": "video", "number": 0, "prompt": "", "negative": "", "seed": None,
         "model": ""},
    ])

    retry_frame(sync_runner(), store, record, plan_store, {}, lambda: "t", "düğün", "0_a.png")

    cells = record.slots("düğün")["0_a"]
    assert cells["video"] == {"status": "queued", "file": "0_a_V1_0.mp4"}
    # The photo is untouched: retrying a layer does not re-render the picture under it.
    assert cells["photo"]["status"] == "done"


def test_retry_of_a_frame_with_nothing_red_still_asks_for_its_photo():
    # A deleted photo the user wants back: no layer is failed, and the photo is what is missing.
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "t")
    plan_store = FakePlanStore(frames=[frame(0)])

    retry_frame(sync_runner(), store, record, plan_store, {layers.PHOTO: FakeGenerator()},
                lambda: "t", "düğün", "0_a.png")

    assert record.slots("düğün")["0_a"]["photo"]["status"] == "done"   # produced again
```

> `retry_frame`'in var olan testleri de bu dosyada; kırmızıya dönerlerse imza değil davranış
> değişmiştir, oku ve düzelt.

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı.

- [ ] **Adım 3 — `retry_frame.py`:** modül başlığına bir cümle ve gövde:

```python
    cells = record.slots(project).get(target["id"], {})
    red = [(layer, cell) for layer, cell in cells.items() if cell["status"] == queue.FAILED]
    for layer, cell in red:
        # The layer's own file, not the frame's photo: what goes back in line is the render that
        # blew up, and it goes back onto THIS frame -- retrying a layer never makes a copy
        # (design v3, madde 68).
        record.mark(project, target["id"], layer, cell["file"], queue.QUEUED, now())
    if not red:
        # Nothing red: the frame is asking for a photo it no longer has (a deleted one), which is
        # what retry meant before layers existed.
        record.mark(project, target["id"], layers.PHOTO, file, queue.QUEUED, now())
```

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Örtü, buton ve "Kuyruğa eklendi"

**Dosyalar:**
- Değişecek: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`,
  `queen-editor/frontend/src/shared/app.css`
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

- [ ] **Adım 1 — kırmızı testler:**

```jsx
describe("Gallery — a layer that blew up", () => {
  const brokenVideo = withVideo("P0_0.png", { failed: ["video"] });

  it("offers the way back over the photo instead of covering it", () => {
    renderGallery({ frames: [brokenVideo], onRetry: () => {} });

    // The picture stays; the button rides an overlay that CSS only shows under the pointer.
    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(tileOf("P0_0.png").querySelector("[data-veil]")).toBeTruthy();
    expect(screen.getByText("Tekrar dene")).toBeTruthy();
  });

  it("keeps the middle of an empty red card for its own button", () => {
    renderGallery({ frames: [broken("P0_0.png")], onRetry: () => {} });

    expect(tileOf("P0_0.png").querySelector("[data-veil]")).toBeNull();
    expect(screen.getByText("Tekrar dene")).toBeTruthy();
  });

  it("says the job went into the queue and refuses a second press", () => {
    const onRetry = vi.fn();
    renderGallery({ frames: [brokenVideo], onRetry });

    fireEvent.click(screen.getByText("Tekrar dene"));

    expect(onRetry).toHaveBeenCalledWith("P0_0.png");
    expect(screen.getByText("Kuyruğa eklendi").closest("button").disabled).toBe(true);
    fireEvent.click(screen.getByText("Kuyruğa eklendi"));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("says the same thing on an empty red card", () => {
    const onRetry = vi.fn();
    renderGallery({ frames: [broken("P0_0.png")], onRetry });

    fireEvent.click(screen.getByText("Tekrar dene"));

    expect(screen.getByText("Kuyruğa eklendi").closest("button").disabled).toBe(true);
  });
});
```

- [ ] **Adım 2:** `npm test --prefix queen-editor/frontend -- --run` → kırmızı.

- [ ] **Adım 3 — `Gallery.jsx`:** basılan kareleri tutan durum ve tek buton bileşeni.

```jsx
  // Which frames have just been sent back. The screen's own memory: the server keeps no "asked
  // for" flag, and the next poll brings the frame back as a waiting one anyway.
  const [retried, setRetried] = useState([]);
```

```jsx
const VEIL = { position: "absolute", inset: 0, display: "flex", alignItems: "center",
               justifyContent: "center", background: "rgba(0,0,0,.55)",
               borderRadius: "var(--r-sm)", zIndex: 3 };

/** The way back from a failed render. Pressed once: the queue took it, and the card changes on the
 *  next poll -- so the button says so itself rather than sitting there ready for a second press. */
function RetryButton({ file, sent, onRetry }) {
  return (
    <Btn sm disabled={sent}
         onClick={(e) => { e.preventDefault(); e.stopPropagation(); if (!sent) onRetry(file); }}
         style={{ color: "var(--danger)", borderColor: "var(--danger)", background: "transparent" }}>
      {sent ? "Kuyruğa eklendi" : <><Icon.Regen /> Tekrar dene</>}
    </Btn>
  );
}
```

Karo çiziminde, `owns`'un yanına:

```jsx
          // A layer that blew up on a frame that still has its picture: the card stays as it is
          // and the way back comes down over it under the pointer (madde 67).
          const brokenLayer = produced && (frame.failed || []).length > 0;
```

`<Tile>`'a `veil` verilir:

```jsx
                      veil={brokenLayer && (
                        <div data-veil className="qe-veil" style={VEIL}>
                          <RetryButton file={frame.file} sent={retried.includes(frame.file)}
                                       onRetry={press} />
                        </div>
                      )}
```

> `press` değil: `onRetry`'ı saran küçük bir kapanış yaz —
> `function sendBack(file) { setRetried((names) => [...names, file]); onRetry(file); }`

`Tile` imzasına `veil` eklenir ve `{pill}`'in altına `{veil}` konur.

Kartın ortasındaki mevcut buton da aynı bileşene döner:

```jsx
                        <RetryButton file={frame.file} sent={retried.includes(frame.file)}
                                     onRetry={sendBack} />
```

- [ ] **Adım 4 — `app.css`:** örtü yalnız imleç altında görünür ve görünmezken tıklama yemez.

```css
/* A layer that failed on a frame that still has its photo: the way back rides an overlay that only
   comes down under the pointer, so the picture is never hidden for good. */
.qe-veil {
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.12s;
}
.qe-tile:hover .qe-veil {
  opacity: 1;
  pointer-events: auto;
}
```

- [ ] **Adım 5:** `npm test --prefix queen-editor/frontend -- --run` → yeşil.

---

## Görev 3 — Tam takım, build, commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): a failed layer is retried onto the frame it belongs to
```
