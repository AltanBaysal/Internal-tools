# Queen Editor v5 · Görev 29 — Export uyarıları ve pasiflik · Uygulama planı

> Tasarım: [Görev 29 spec](../specs/2026-08-12-queen-editor-v5-gorev-29-export-uyarilari-design.md).
> Önce kırmızı test, sonra en küçük kod.

**Hedef:** özet kartı koşullu kırmızı satırlar taşısın; kuyruk akarken export engellensin.

**Mimari:** `export_summary` iki sayı daha döner; `ExportScreen` kuyruğun hâlini
`useGeneration`'dan okur.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — Özet iki sayı daha söyler

**Dosyalar:** `domain/usecases/export_summary.py`, test: `tests/test_photo_usecases.py`

- [ ] **Adım 1 — kırmızı testler:**

```python
def test_the_summary_counts_the_videos_with_no_sound():
    store, record, plan_store = layered_project(audio=False)

    assert export_summary(record, store, plan_store, FakeOrderStore(),
                          "düğün")["silent"] == 1


def test_a_video_with_a_sound_is_not_silent():
    store, record, plan_store = layered_project()

    assert export_summary(record, store, plan_store, FakeOrderStore(),
                          "düğün")["silent"] == 0


def test_a_sound_that_blew_up_leaves_the_video_silent():
    store, record, plan_store = layered_project(audio=False)
    record.mark("düğün", "0_a", "audio", "0_a_V1_0_S1_0.wav", "failed", "t")

    assert export_summary(record, store, plan_store, FakeOrderStore(),
                          "düğün")["silent"] == 1


def test_the_summary_counts_the_frames_that_have_no_video():
    # A produced photo without a video and a frame that is not even a photo yet: neither is in the
    # sequence, and both are worth saying.
    store, record, plan_store = layered_project(audio=False)
    record.append("düğün", {"file": "1_a.png", "frame": "1_a", "layer": "photo", "status": "done"})
    plan_store.append("düğün", [{"id": "2_a", "type": "photo", "number": 2, "variant": 0,
                                 "prompt": "p", "negative": "", "seed": 1, "model": ""}])

    assert export_summary(record, store, plan_store, FakeOrderStore(),
                          "düğün")["withoutVideo"] == 2
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:** `export_summary` galeriyi bir kez okur ve dört sayı döndürür:

```python
def export_summary(record, store, plan_store, order_store, project):
    frames = list_frames(record, store, plan_store, order_store, project)
    videos = exportable(frames)
    # A video whose sound blew up is silent too: what is not there is not laid over it.
    silent = [frame for frame in videos
              if not frame.get("layers", {}).get(layers.AUDIO)
              or layers.AUDIO in frame.get("failed", [])]
    return {"videos": len(videos), "seconds": len(videos) * VIDEO_SECONDS,
            "silent": len(silent),
            # Frames the sequence will not hold: no video yet, produced or not.
            "withoutVideo": len(frames) - len(videos),
            "folder": store.export_dir(project)}
```

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Ekran: uyarılar ve pasiflik

**Dosyalar:** `ExportScreen.jsx`, test: `ExportScreen.test.jsx`

- [ ] **Adım 1 — kırmızı testler:** (mock'a `useGeneration` eklenir)

```jsx
vi.mock("./useGeneration.js", () => ({ useGeneration: vi.fn() }));

const idle = { job: { status: "idle" }, frames: [], queue: [] };
const flowing = { job: { status: "running", project: "düğün" }, frames: [],
                  queue: [{ layer: "video", owed: 5 }] };
const paused = { job: { status: "paused", project: "düğün" }, frames: [],
                 queue: [{ layer: "video", owed: 5 }] };

it("says how many videos have no sound", async () => {
  await open({ ...SUMMARY, silent: 16 });

  expect(screen.getByText("⚠ 16 videonun sesi yok")).toBeTruthy();
});

it("draws no row for a condition that is not there", async () => {
  await open({ ...SUMMARY, silent: 0, withoutVideo: 0 });

  expect(screen.queryByText(/sesi yok/)).toBeNull();
  expect(screen.queryByText(/diziye girmeyecek/)).toBeNull();
});

it("says which frames the sequence will not hold", async () => {
  await open({ ...SUMMARY, withoutVideo: 3 });

  expect(screen.getByText("⚠ 3 videosuz kare diziye girmeyecek")).toBeTruthy();
});

it("blocks the export while the queue flows, and says why", async () => {
  await open(SUMMARY, flowing);

  expect(screen.getByText(/Üretim sürüyor — 5 video kuyrukta/)).toBeTruthy();
  expect(button("Birleşik videoyu export et").disabled).toBe(true);
});

it("lets the export run once the queue is paused", async () => {
  await open(SUMMARY, paused);

  expect(button("Birleşik videoyu export et").disabled).toBe(false);
  expect(screen.queryByText(/Üretim sürüyor/)).toBeNull();
  expect(screen.getByText("⚠ 5 karenin videosu kuyrukta bekliyor — diziye girmeyecek"))
    .toBeTruthy();
});
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:** `ExportScreen`:

```jsx
const { job, frames, queue } = useGeneration(project);
// The queue's own answer, not a second count: the panel reads these very numbers.
const flowing = job.status === "running";
const queuedVideos = (queue.find((card) => card.layer === "video") || {}).owed || 0;
// Every condition that has one, in the design's own words. A count of zero writes no row.
const warnings = [
  summary.silent && `⚠ ${summary.silent} videonun sesi yok`,
  summary.withoutVideo && `⚠ ${summary.withoutVideo} videosuz kare diziye girmeyecek`,
  !flowing && queuedVideos
    && `⚠ ${queuedVideos} karenin videosu kuyrukta bekliyor — diziye girmeyecek`,
].filter(Boolean);
```

- kırmızı satırlar kartın içinde, ana satırın altında;
- akan kuyrukta butonların hemen üstünde kendi kırmızı kartı:
  `⚠ Üretim sürüyor — ${queuedVideos} video kuyrukta. Kuyruğun bitmesini bekle veya duraklat.`;
- `disabled={empty || flowing}` iki butonda da; pasiflik `%40` opaklık (kit'in kendi kuralı).
- galeri tazelendikçe özet yeniden okunur: `useEffect(..., [project, frames])`.

- [ ] **Adım 4:** yeşil.

---

## Görev 3 — Tam takım, build, commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): the export screen says what it would leave out
```
