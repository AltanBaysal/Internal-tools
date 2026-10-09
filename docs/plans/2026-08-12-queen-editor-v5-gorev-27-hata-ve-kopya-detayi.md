# Queen Editor v5 · Görev 27 — Hata ve kopya kare detayı · Uygulama planı

> Tasarım: [Görev 27 spec](../specs/2026-08-12-queen-editor-v5-gorev-27-hata-ve-kopya-detayi-design.md).
> Önce kırmızı test, sonra en küçük kod.

**Hedef:** hatalı katmanın sebebi ve "Tekrar dene" detayda dursun; kuyruktaki kopya kare kendi
sayfasını açsın.

**Mimari:** kare her yerde kimliğiyle adreslenir (adres, karo, sıra, tekrar dene, silme); hata
sebebi kayıttan galeri satırına, oradan detaya taşınır.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — Hatanın sebebi galeri satırına çıkar

**Dosyalar:** `domain/policy.py`, `domain/run_loop.py`, `data/photo_record.py`,
`domain/usecases/list_frames.py`, `domain/ports.py`,
testler: `tests/test_photo_usecases.py`, `tests/test_photo_data.py`

- [ ] **Adım 1 — kırmızı testler:**

```python
def test_a_failed_render_says_how_many_times_it_was_tried():
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0)])
    generator = FakeGenerator(fail_on=["p"])

    run_batch(sync_runner(), store, generator, record=record, plan_store=plan_store,
              text='["p"]', variants=1)

    row = [r for r in record.rows if r.get("status") == "failed"][0]
    assert row["error"] == "node 41: p — 3 kez denendi"


def test_a_frame_carries_the_reason_each_layer_failed():
    record = FakeRecord()
    record.mark("düğün", "0_a", "photo", "0_a.png", "failed", "t", error="CUDA — 3 kez denendi")
    frames = list_frames(record, FakeStore(), FakePlanStore(frames=[frame(0)]),
                         FakeOrderStore(), "düğün")

    assert frames[0]["errors"] == {"photo": "CUDA — 3 kez denendi"}


def test_a_frame_that_did_not_fail_carries_no_reason():
    store, record, plan_store = video_project((0, "a"))
    frames = list_frames(record, store, plan_store, FakeOrderStore(), "düğün")

    assert frames[0]["errors"] == {}
```

`FakeRecord.slots` gerçek kaydı taklit ettiği için oraya da `error` eklenir (satırda varsa).

Veri testi (`tests/test_photo_record.py`):

```python
def test_a_failure_line_keeps_its_reason(tmp_path):
    record = DrivePhotoRecord(DriveStorage(str(tmp_path)))
    record.mark("düğün", "P0_0", "photo", "P0_0.png", "failed", "t", error="CUDA")

    assert record.slots("düğün")["P0_0"]["photo"]["error"] == "CUDA"
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:**

`policy.py`:

```python
def frame_reason(exc, attempts):
    """A failed render's own words plus how many times it was tried -- the line the detail page
    prints under the red frame. The cause is never guessed: only the renderer's text and a count."""
    return f"{exc} — {attempts} kez denendi"
```

`run_loop.py`: `record.mark(..., error=policy.frame_reason(exc, attempts))`.

`photo_record.py` — `slots()` hücresine satırda varsa `error` eklenir:

```python
            cell = {"status": _status_of(row), "file": row["file"]}
            if isinstance(row.get("error"), str):
                # Why the slot is red, in the renderer's own words. Only a failure line carries one.
                cell["error"] = row["error"]
```

`list_frames.py` — satıra `errors` alanı:

```python
def _reasons(cells):
    """{layer: why it failed} -- what the record wrote when the render blew up."""
    return {slot: cell["error"] for slot, cell in cells.items()
            if cell.get("status") == queue.FAILED and cell.get("error")}
```

`ports.py`: `PhotoRecord.slots` docstring'i hücrenin `error` taşıyabildiğini söyler.

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Arka uç kimliğe geçer

**Dosyalar:** `domain/usecases/remove_frames.py`, `retry_frame.py`, `save_order.py`,
`presentation/routes.py`, testler: `tests/test_photo_usecases.py`, `tests/test_photo_routes.py`

- [ ] **Adım 1 — kırmızı testler:**

```python
def test_removing_takes_the_named_frame_not_the_one_sharing_its_picture():
    store, record, plan_store = layered_project(audio=False)
    with_a_copy(record)

    gone = remove_frames(record, store, plan_store, FakeOrderStore(), lambda: "t",
                         "düğün", ["P0_1"])

    assert gone == {"deleted": ["P0_1"], "removed": []}
    # Nothing left the disk: every file the copy held is its source's too.
    assert store.deleted == []
    assert record.slots("düğün")["0_a"]["photo"]["status"] == "done"


def test_retry_puts_back_the_frame_whose_identity_was_given():
    store, record, plan_store = video_project((0, "a"))
    record.mark("düğün", "0_a", "photo", "0_a.png", "failed", "t")

    retry_frame(sync_runner(), store, record, plan_store, {layers.PHOTO: FakeGenerator()},
                lambda: "t", "düğün", "0_a")

    assert photo_statuses(record) == {"0_a": "done"}


def test_save_order_stores_the_identities_it_is_given():
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    order = FakeOrderStore()

    assert save_order(record, store, plan_store, order, "düğün", ["1_a", "0_a"]) == ["1_a", "0_a"]
```

Yol testleri: `{"files": [...]}` → `{"frames": [...]}`, `{"file": …}` → `{"frame": …}`; cevaplar
kimlik listesi döner.

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — üç imza, üç gövde:**

```python
# remove_frames.py -- the gallery is looked up by identity and the answer speaks identities.
def remove_frames(record, store, plan_store, order_store, now, project, frames):
    if not isinstance(frames, list) or any(not isinstance(fid, str) for fid in frames):
        raise InvalidFiles("Silinecek kare listesi metin dizisi olmalı.")
    gallery = {frame["id"]: frame
               for frame in list_frames(record, store, plan_store, order_store, project)}
    ...
    for fid in frames:
        frame = gallery.get(fid)
        if frame is None:
            continue
        ...deleted.append(fid) / removed.append(fid)...
    for fid in removed:
        record.mark(project, fid, layers.PHOTO, gallery[fid]["file"], queue.REMOVED, now())


# retry_frame.py -- no photo_file() detour: the plan already keeps identities.
def retry_frame(runner, store, record, plan_store, producers, now, project, fid, log=None,
                order_store=None, writers=None):
    ...
    target = next((f for f in frames if f["id"] == fid), None)
    if target is None:
        raise FrameMissing(f"Bu kare planda yok: {fid}")
    ...
    record.mark(project, fid, layers.PHOTO, photo_file(fid), queue.QUEUED, now())


# save_order.py -- what comes in is what is stored; frame_id_of is gone.
def save_order(record, store, plan_store, order_store, project, order):
    if not isinstance(order, list) or any(not isinstance(fid, str) for fid in order):
        raise InvalidOrder("Sıra listesi metin dizisi olmalı.")
    known = {frame["id"] for frame in list_frames(...)}
    cleaned = [fid for fid in dict.fromkeys(order) if fid in known]
```

Uç noktalar gövde alanlarını yeni adlarıyla okur (`frames`, `frame`); hata mesajları ve durum
kodları aynı kalır.

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 3 — Ön yüz kimliğe geçer

**Dosyalar:** `shared/router.js`, `shared/api.js`, `useGeneration.js`, `Gallery.jsx`,
`ProjectScreen.jsx`, `PhotoDetail.jsx`, testleri

- [ ] **Adım 1 — kırmızı testler:** (var olan testlerin fixture'ları kimlik alır)

```jsx
// Gallery.test.jsx
const done = (file, extra = {}) => ({ id: file.replace(".png", ""), file, status: "done", ...extra });

it("opens the frame by its identity, not by the picture it shows", () => {
  renderGallery({ frames: [{ id: "P0_1", file: "P0_0.png", status: "done", owed: ["video"] }] });

  fireEvent.click(screen.getByAltText("P0_0.png"));

  expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/P0_1");
});
```

```jsx
// PhotoDetail.test.jsx — sayfa artık kimlikle açılıyor
async function open(frame, { frames = PHOTOS, status = IDLE } = {}) {
  ...
  render(<PhotoDetail project="düğün" frame={frame} />);
}
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:**

- `router.js`: `photoPath(project, frame)` — segment karenin kimliği (yol adı `photos` kalır, dosya
  yolunun adıyla aynı sebeple).
- `api.js`: `removeFrames(project, frames)`, `retryFrame(project, frame)`, `saveOrder(project,
  order)` gövdeleri yeni adlarla.
- `useGeneration.js`: `current` artık `job.current.id` (dosya adı değil); `removePhotos` cevabın
  kimliklerine göre süzer.
- `Gallery.jsx`: karo anahtarı, seçim, sürükleme, "Tümünü seç", `sendBack` ve açma `frame.id` ile;
  karonun üstünde yazan ad `frame.file` kalır.
- `ProjectScreen.jsx`: `App.jsx`'ten gelen `photo` propu `frame` olur.
- `PhotoDetail.jsx`: `frames.find(f => f.id === frame)`, oklar diziyi kimlikle gezer,
  `current` karşılaştırması kimlikle.

- [ ] **Adım 4:** `npm test --prefix queen-editor/frontend -- --run` → yeşil.

---

## Görev 4 — Hata ve bekleyen katman detayı

**Dosyalar:** `PhotoDetail.jsx`, test: `PhotoDetail.test.jsx`

- [ ] **Adım 1 — kırmızı testler:**

```jsx
const BROKEN = { id: "P0_0", file: "P0_0.png", status: "failed", prompt: "kırmızı elbise",
                 negative: "", layers: {}, failed: ["photo"], owed: [],
                 prompts: { photo: "kırmızı elbise" },
                 errors: { photo: "CUDA out of memory — 3 kez denendi" } };

const QUEUED_COPY = { id: "P0_1", file: "P0_0.png", status: "done", prompt: "kırmızı elbise",
                      negative: "", layers: { photo: "P0_0.png" }, failed: [], owed: ["video"],
                      prompts: { photo: "kırmızı elbise" }, errors: {} };

describe("PhotoDetail — a frame that blew up", () => {
  it("says what the renderer said, once", async () => {
    await open("P0_0", { frames: [BROKEN] });

    expect(screen.getByText("Bu kare üretilemedi")).toBeTruthy();
    expect(screen.getByText("CUDA out of memory — 3 kez denendi")).toBeTruthy();
  });

  it("puts the frame back in line without asking", async () => {
    await open("P0_0", { frames: [BROKEN] });

    await act(async () => { fireEvent.click(screen.getByText("Tekrar dene")); });

    expect(retryFrame).toHaveBeenCalledWith("düğün", "P0_0");
    expect(screen.getByText("Kuyruğa eklendi").closest("button").disabled).toBe(true);
  });

  it("offers Kareyi sil rather than pretending it is queued", async () => {
    await open("P0_0", { frames: [BROKEN] });

    expect(screen.getByText("Kareyi sil")).toBeTruthy();
  });

  it("leaves the prompt read-only there", async () => {
    await open("P0_0", { frames: [BROKEN] });

    expect(screen.queryByDisplayValue("kırmızı elbise")).toBeNull();
    expect(screen.queryByText("Yeniden üret — yeni kare")).toBeNull();
  });
});

describe("PhotoDetail — a copy frame waiting in the queue", () => {
  it("shows the picture it holds and says what is coming", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
    expect(screen.getByText("video kuyrukta")).toBeTruthy();
  });

  it("opens the tab of the layer it is waiting for, with an empty box", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("üretim sırası gelince LLM yazacak")).toBeTruthy();
  });

  it("takes it out of the queue without asking", async () => {
    removeFrames.mockResolvedValue({ deleted: [], removed: ["P0_1"] });
    await open("P0_1", { frames: [QUEUED_COPY] });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruktan çıkar")); });

    expect(removeFrames).toHaveBeenCalledWith("düğün", ["P0_1"]);
  });
});
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:**

```jsx
// What may be opened, and what the tab shows when it is. A layer the plan never heard of has no
// tab; the rest open in whatever state they are in (madde 79, 81).
const stateOf = (frame, layer, running) => {
  if (running === layer) return "running";
  if ((frame.failed || []).includes(layer)) return "failed";
  if ((frame.owed || []).includes(layer)) return "pending";
  return (frame.layers || {})[layer] ? "done" : null;
};
```

- sahne: `done` → bugünkü (oynatıcı/fotoğraf), `failed` → kırmızı alan (uyarı ikonu, "Bu kare
  üretilemedi", `frame.errors[layer]`), `pending` → karenin taşıdığı fotoğraf ya da tutucu,
  `running` → dönen gösterge; `pending`/`running` üstünde `StatusPill`;
- sütun: `done` → Görev 25'in düzenlenebilir kutusu + "Yeniden üret", `failed` → salt okunur kutu +
  mor "Tekrar dene" (basınca "Kuyruğa eklendi"), `pending` → boş kutu, ipucu metni;
- yıkıcı buton üç hâle ayrılır (spec karar 6): kendi fotoğrafı varsa "Sil" + onay, yoksa ve bekleyen
  varsa "Kuyruktan çıkar", yoksa "Kareyi sil" — ikisi de onaysız.

- [ ] **Adım 4:** yeşil.

---

## Görev 5 — Tam takım, build, commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): a frame answers for itself, red or waiting
```
