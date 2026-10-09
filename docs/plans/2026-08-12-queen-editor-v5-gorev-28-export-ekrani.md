# Queen Editor v5 · Görev 28 — Export ekranı iskeleti · Uygulama planı

> Tasarım: [Görev 28 spec](../specs/2026-08-12-queen-editor-v5-gorev-28-export-ekrani-design.md).
> Önce kırmızı test, sonra en küçük kod.

**Hedef:** Export dosya indirmesin, kendi ekranını açsın; ekran özeti sunucudan okusun.

**Mimari:** yeni use case `domain/usecases/export_summary.py`; uç nokta
`GET /api/projects/<p>/export/summary`; yeni ekran `ExportScreen.jsx` ve üçüncü yol.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — `export_summary`, JSON export'un yerine

**Dosyalar:** yeni `domain/usecases/export_summary.py`, silinen
`domain/usecases/export_project.py`, `presentation/routes.py`, `main.py`,
testler: `tests/test_photo_usecases.py`, `tests/test_photo_routes.py`

- [ ] **Adım 1 — kırmızı testler** (eski `export_*` testleri silinir):

```python
def test_the_summary_counts_the_frames_that_have_a_video():
    store, record, plan_store = layered_project(audio=False)
    record.append("düğün", {"file": "1_a.png", "frame": "1_a", "layer": "photo", "status": "done"})

    summary = export_summary(record, store, plan_store, FakeOrderStore(), "düğün")

    assert summary == {"videos": 1, "seconds": VIDEO_SECONDS, "folder": "/fake/düğün/export"}


def test_a_project_with_no_video_exports_nothing():
    store, record, plan_store = video_project((0, "a"))

    assert export_summary(record, store, plan_store, FakeOrderStore(),
                          "düğün")["videos"] == 0


def test_a_video_that_blew_up_is_not_counted():
    store, record, plan_store = video_project((0, "a"))
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", "failed", "t")

    assert export_summary(record, store, plan_store, FakeOrderStore(),
                          "düğün")["videos"] == 0


def test_the_summary_rejects_a_missing_project():
    with pytest.raises(ProjectMissing):
        export_summary(FakeRecord(), FakeStore(projects=()), FakePlanStore(), FakeOrderStore(),
                       "yok")
```

Yol testi:

```python
def test_the_export_summary_is_json_not_a_download(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    give_it_a_video(drive)

    resp = client.get("/api/projects/düğün/export/summary")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["videos"] == 1
    assert body["seconds"] == 5
    assert body["folder"].endswith("export")


def test_the_old_export_download_is_gone(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/düğün/export").status_code == 404
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — `export_summary.py`:**

```python
"""What an export would write: how many videos, how long they run, and where they would land.

Read from the gallery rather than from disk, so "which frames have a video" has the same answer
here as everywhere else -- a second count would be a second truth, and the video is stitched in
exactly the gallery's order.

The length is not measured. Video duration cannot be chosen in this version: the graph produces a
fixed length, so the total is the count times that length (design v3, madde 86's own example --
22 videos, 1:50).
"""
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.usecases.list_frames import list_frames

# How long one produced video runs. A number rather than a measurement: every video is the same
# length until the graph's length becomes a setting.
VIDEO_SECONDS = 5


def exportable(frames):
    """The frames a video export would take, in the gallery's own order."""
    return [frame for frame in frames
            if frame.get("layers", {}).get(layers.VIDEO)
            and layers.VIDEO not in frame.get("failed", [])]


def export_summary(record, store, plan_store, order_store, project):
    # Raises ProjectMissing when there is no such project.
    frames = list_frames(record, store, plan_store, order_store, project)
    videos = exportable(frames)
    return {"videos": len(videos), "seconds": len(videos) * VIDEO_SECONDS,
            # Where an export lands is the store's answer: building a path is not the domain's job.
            "folder": store.export_dir(project)}
```

`PhotoStore` port'una ve `DrivePhotoStore`'a `export_dir(project)` eklenir (proje klasörünün
altındaki `export`; klasörü açmak Görev 30'un işi), `FakeStore`'a da testler için.

`routes.py`: `export` ucu silinir, yerine

```python
    @bp.get("/api/projects/<project>/export/summary")
    def export_summary_route(project):
        try:
            return jsonify(export_summary(project))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
```

`io`/`json` import'ları ve `send_file` kullanımı gerekmiyorsa kalkar; `main.py` ve testin
`make_client`'ı `export_project` yerine `export_summary` bağlar.

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Ekran ve yol

**Dosyalar:** `shared/router.js`, `shared/api.js`, `App.jsx`, `ProjectScreen.jsx`,
yeni `features/photo_generation/ExportScreen.jsx`,
testler: yeni `ExportScreen.test.jsx`, `ProjectScreen.test.jsx`, `shared/router.test.js`

- [ ] **Adım 1 — kırmızı testler:**

```js
// router.test.js
it("reads the export screen's path", () => {
  expect(routeFromPath("/projects/d%C3%BC%C4%9F%C3%BCn/export"))
    .toEqual({ project: "düğün", photo: null, exporting: true });
});
```

```jsx
// ProjectScreen.test.jsx
it("opens the export screen instead of downloading a file", async () => {
  await openScreen();

  fireEvent.click(screen.getByText("Export"));

  expect(navigate).toHaveBeenCalledWith("/projects/düğün/export");
});
```

```jsx
// ExportScreen.test.jsx
const SUMMARY = { videos: 22, seconds: 110, folder: "/drive/düğün/export" };

it("says how many videos and how long they run", async () => {
  await open(SUMMARY);

  expect(screen.getByText("22 video export edilecek · 1:50 dk")).toBeTruthy();
  expect(screen.getByText("/drive/düğün/export")).toBeTruthy();
});

it("offers the two exports side by side", async () => {
  await open(SUMMARY);

  expect(screen.getByText("Birleşik videoyu export et").closest("button").className)
    .toContain("wf-btn--hl");
  expect(screen.getByText("Videoları ayrı export et")).toBeTruthy();
});

it("turns into guidance when there is no video", async () => {
  await open({ videos: 0, seconds: 0, folder: "/drive/düğün/export" });

  expect(screen.getByText("Export edilecek video yok")).toBeTruthy();
  expect(screen.getByText(/önce Video üret panelinden/)).toBeTruthy();
  expect(screen.getByText("Birleşik videoyu export et").closest("button").disabled).toBe(true);
});

it("goes back to the gallery", async () => {
  await open(SUMMARY);

  fireEvent.click(screen.getByText("Galeriye dön"));

  expect(navigate).toHaveBeenCalledWith("/projects/düğün");
});

it("says so when the summary cannot be read", async () => {
  getExportSummary.mockRejectedValue(new Error("Proje yok: düğün"));
  render(<ExportScreen project="düğün" />);
  await act(async () => {});

  expect(screen.getByText("Export özeti yüklenemedi")).toBeTruthy();
});
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:**

- `router.js`: `routeFromPath` üçüncü şekli tanır (`/projects/<p>/export` → `exporting: true`);
  `exportPath(project)`.
- `api.js`: `exportUrl` gider, `getExportSummary(project)` gelir.
- `App.jsx`: `exporting` ise `<ExportScreen project={project} />`.
- `ProjectScreen.jsx`: `<a download>` yerine `<Btn ghost onClick={() => navigate(exportPath(project))}>`.
- `ExportScreen.jsx`: kendi app bar'ı (ortada `{project} · Export`), 560px ortalanmış sütun, 30
  puntoluk proje adı, çerçeveli kart (26/14/12 tip ölçeği, sola dayalı), 1 piksellik ayraç,
  "Şuraya yazılacak:" + tek aralıklı yol, altında iki eşit `Btn hl`.

```jsx
// m:ss -- the design's own "1:50 dk". Seconds are always two digits; minutes never padded.
function clock(seconds) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
}
```

- [ ] **Adım 4:** `npm test --prefix queen-editor/frontend -- --run` → yeşil.

---

## Görev 3 — Tam takım, build, commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): Export opens a screen instead of dropping a file
```
