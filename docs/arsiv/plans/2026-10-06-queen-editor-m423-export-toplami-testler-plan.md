# Madde 423 — Export'un toplamı her videonun kendi uzunluğundan, test turunun planı

> **Koşum:** bu oturumda, satır satır, 423'ün worktree'sinde (dalı `feat/queen-editor-v9`'un
> ucundan). Testler yazılır, dört satır koşulur, yeni testlerin kırmızısı görülür, ve suite kırmızı
> commit'lenir.

**Hedef:** Kaydın katlanışının videonun uzunluğunu taşıdığını, galeri kartının onu söylediğini,
özetin her videonun kendi uzunluğunu topladığını — satırı söylemeyeni grafiğin uzunluğuyla —, kopya
karenin kaynağının uzunluğuyla sayıldığını ve ekranın tasarımın *karışık uzunluklar* cümlesini
yazdığını anlatan testler.

**Yaklaşım:** Yeni bir dosya, `test_export_total.py`; kayıt gerçek `DrivePhotoRecord`, geçici
klasörde; mağaza, plan ve sıra `test_photo_usecases.py`'nin sahteleri; grafiğin uzunluğu bir
`lambda`. Ekranın testi `ExportScreen.test.jsx`'te, sahte özetle.

**Araçlar:** pytest (`tmp_path`), vitest + Testing Library.

**Spec:** [m423 test turu](../specs/2026-10-06-queen-editor-m423-export-toplami-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**; ekrandaki cümle Türkçe ve birebir:
  `24 video export edilecek · 3:08 dk`.
- Testler dört satırla koşulur; `skip` / `xfail` / `.skip` / `.todo` yok. Bu turda kaynak kod
  değişmiyor; `dist` değişmiyor.
- Öteki ajanların dosyalarına dokunulmaz: `test_photo_usecases.py`'den yalnız içe aktarılır.

**Arayüz — uygulama turunun vereceği:**
- `DrivePhotoRecord.slots(project)` — video hücresinde, satırı söylüyorsa `"seconds"` (sayı).
- `list_frames(...)` — her kartta `"lengths"`: `{katman: saniye}`, yalnız satırı söyleyen katmanlar.
- `copy_frame.CARRIED` — `("lengths", "seconds")` da taşınır.
- `export_summary(record, store, plan_store, order_store, seconds, project)` — imzası aynı;
  `"seconds"` her videonun `lengths["video"]`'ı, yoksa `seconds()`.

---

## Görev 1: Arka uçtaki testler

**Dosyalar:** Oluştur: `queen-editor/backend/tests/test_export_total.py`

- [ ] **Adım 1: Dosyayı yaz**

```python
"""Madde 423: the export's total is added up from each video's own length.

Since madde 422 an H3 video's line in the photo record says how long it was made ("seconds"). A video
whose line says nothing -- every one made before 422, and every WAN video -- runs as long as its
graph says, which the summary asks of the session's video producer, as it always did.

The record is the real one over a folder: what is proved is the whole road from a line on Drive to
the number on the export screen, the fold included.
"""
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.usecases.copy_frames import copy_frames
from backend.features.photo_generation.domain.usecases.export_summary import export_summary
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.services.drive.storage import DriveStorage
from backend.tests.test_photo_usecases import (
    FakeGenerator,
    FakeOrderStore,
    FakePlanStore,
    FakeStore,
    frame,
    sync_runner,
)


def project(tmp_path, *videos):
    """Frames 0_a, 1_a, … each with its photo and a produced video. `videos` is the length each
    video's line says, None for a line that says none -- what every line before madde 422 is."""
    record = DrivePhotoRecord(DriveStorage(str(tmp_path)))
    plan_store = FakePlanStore(frames=[frame(number) for number in range(len(videos))])
    for number, seconds in enumerate(videos):
        fid = f"{number}_a"
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        record.append("düğün", {"file": f"{fid}_V1_0.mp4", "frame": fid, "layer": "video",
                                "status": "done",
                                **({} if seconds is None else {"seconds": seconds})})
    return FakeStore(), record, plan_store


def summary(store, record, plan_store, graph):
    """The export summary, `graph` standing for how long the session's video graph runs."""
    return export_summary(record, store, plan_store, FakeOrderStore(), lambda: graph, "düğün")


# --- The record's fold ---------------------------------------------------------------------------

def test_a_videos_line_that_says_its_length_carries_it_into_the_slot(tmp_path):
    _store, record, _plan = project(tmp_path, 12)

    assert record.slots("düğün")["0_a"]["video"]["seconds"] == 12


def test_a_line_written_before_lengths_carries_none_into_the_slot(tmp_path):
    # Every video on Drive before madde 422. Absent is the honest answer; the summary decides what
    # to do with it.
    _store, record, _plan = project(tmp_path, None)

    assert "seconds" not in record.slots("düğün")["0_a"]["video"]


# --- The gallery ---------------------------------------------------------------------------------

def test_a_card_says_how_long_its_video_runs(tmp_path):
    store, record, plan_store = project(tmp_path, 12)

    card = list_frames(record, store, plan_store, FakeOrderStore(), "düğün")[0]

    assert card["lengths"] == {"video": 12}


def test_a_card_whose_video_says_no_length_has_none(tmp_path):
    # Nothing filled in after the fact: an old video's card says no length rather than a guessed
    # one.
    store, record, plan_store = project(tmp_path, None)

    card = list_frames(record, store, plan_store, FakeOrderStore(), "düğün")[0]

    assert card["lengths"] == {}


# --- The export summary --------------------------------------------------------------------------

def test_the_total_adds_up_each_videos_own_length(tmp_path):
    """H3 videos of different lengths total what each of them runs (madde 423)."""
    store, record, plan_store = project(tmp_path, 4, 8, 12)

    answer = summary(store, record, plan_store, graph=4)

    assert (answer["videos"], answer["seconds"]) == (3, 24)


def test_a_video_whose_line_says_no_length_counts_at_the_graphs_own(tmp_path):
    """Every video made before madde 422, and every WAN video: its graph said how long it runs."""
    store, record, plan_store = project(tmp_path, 12, None)

    assert summary(store, record, plan_store, graph=5)["seconds"] == 17


def test_videos_all_of_one_length_total_what_they_did(tmp_path):
    """"Tek uzunlukta videoları olan projede toplam bugünküyle aynı" -- the projects already on
    Drive."""
    store, record, plan_store = project(tmp_path, None, None)

    assert summary(store, record, plan_store, graph=4)["seconds"] == 8


def test_a_twin_holding_a_video_counts_at_that_videos_length(tmp_path):
    """A copy frame shares its source's video file (madde 102), so it runs exactly as long."""
    store, record, plan_store = project(tmp_path, 12)
    copy_frames(record, store, plan_store, FakeOrderStore(), lambda: "t", "düğün", ["0_a"])

    answer = summary(store, record, plan_store, graph=4)

    assert (answer["videos"], answer["seconds"]) == (2, 24)


def test_a_video_made_at_a_chosen_length_counts_at_it(tmp_path):
    """Madde 422's line, the fold and the summary together: a video put in the queue at 12 seconds
    is counted at 12, whatever the graph says."""
    record = DrivePhotoRecord(DriveStorage(str(tmp_path)))
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store = FakePlanStore(frames=[frame(0)])
    plan_store.frames.append({"id": "0_a", "type": "video", "number": 0, "variant": 0,
                              "prompt": "kadın dönüyor", "negative": "", "seed": 5, "model": "",
                              "seconds": 12})
    store = FakeStore()

    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: FakeGenerator()},
             lambda: "t", "düğün")()

    assert summary(store, record, plan_store, graph=4)["seconds"] == 12
```

## Görev 2: Ekranın testi

**Dosyalar:** Değiştir: `queen-editor/frontend/src/features/photo_generation/ExportScreen.test.jsx`

- [ ] **Adım 1:** `describe("ExportScreen", …)`'in ilk testinin
  (`says how many videos there are and how long they run`) hemen altına:

```jsx
  it("writes a total of mixed lengths the way the design does", async () => {
    // Designer's 206, karışık uzunluklar: 6 × 4 + 4 × 5 + 6 × 8 + 8 × 12 = 188 seconds. The total
    // is the server's; the screen only writes it, its seconds always padded.
    await open({ ...SUMMARY, videos: 24, seconds: 188 });

    expect(screen.getByText("24 video export edilecek · 3:08 dk")).toBeTruthy();
  });
```

## Görev 3: Dört satır, kırmızı

- [ ] **Adım 1:** CLAUDE.md'nin dört satırı, yazıldığı gibi, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
- [ ] **Adım 2:** Beklenen — `queen-editor`'ün pytest'inde **7 kırmızı**, hepsi
  `test_export_total.py`'de: `…carries_it_into_the_slot` (`KeyError: 'seconds'`),
  `test_a_card_says…` ve `test_a_card_whose…` (`KeyError: 'lengths'`), `…each_videos_own_length`
  (12 ≠ 24), `…counts_at_the_graphs_own` (10 ≠ 17), `…twin…` (8 ≠ 24), `…chosen_length…` (4 ≠ 12).
  `…carries_none_into_the_slot`, `…all_of_one_length…` ve ekranın yeni testi yeşil. Öteki her şey
  yeşil.

## Görev 4: Kırmızı commit

- [ ] **Adım 1:**

```powershell
git add docs/specs/2026-10-06-queen-editor-m423-export-toplami-testler-design.md docs/plans/2026-10-06-queen-editor-m423-export-toplami-testler-plan.md queen-editor/backend/tests/test_export_total.py queen-editor/frontend/src/features/photo_generation/ExportScreen.test.jsx
git commit -m 'test(queen-editor): Madde 423 red -- the export total adds up each video own length' -m 'Seven new tests red in test_export_total.py; the old-lines, one-length and screen tests green, and every other test green.' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
```

---

# İnceleme turu — satır üretilen videonun uzunluğunu söyler

**Hedef:** Gerçek üreticilerin gerçek döngüde yazdığı video satırının, yapılan videonun uzunluğunu
söylediğini anlatan testler; ve döngü video üreticisine soru sormaya başlayınca sahtelerin cevap
vermesi.

**Arayüz — uygulama turunun vereceği:**
- Her video üreticisi: `seconds(asked=None) -> sayı` — H3 `asked` ya da grafiğinin 4'ü; WAN her
  zaman grafiğinin 5'i.
- Döngü her üretilen video satırına `"seconds": producer.seconds(job.get("seconds"))` yazar.

## Görev 5: Sahteler cevap verir

**Dosyalar:** Değiştir: `queen-editor/backend/tests/test_photo_usecases.py`,
`queen-editor/backend/tests/test_variant_batch.py`, `queen-editor/backend/tests/test_reference_routes.py`

- [ ] **Adım 1:** `test_photo_usecases.py`'nin `FakeGenerator`'ına, `generate`'in altına:

```python
    def seconds(self, asked=None):
        """How long a video asked at `asked` comes out -- the loop asks every video producer and
        writes the answer on the row (madde 423). This one makes what it is asked, and its graph's 4
        when asked none, the way H3 does."""
        return 4 if asked is None else asked
```

- [ ] **Adım 2:** Aynı dosyada `FakeVideoGenerator`, `FailsTwice` ve `test_a_layer_type_is_made…`'deki
  `Records`'a aynı cevap (belgesiz):

```python
    def seconds(self, asked=None):
        return 4 if asked is None else asked
```

- [ ] **Adım 3:** `Takes` saniyelerini `self.works`'te tutar — `self.seconds` yöntemi örtüyordu:
  `self.clock, self.works, self.fails = clock, list(seconds), fails` ve
  `self.clock.passes(self.works.pop(0) if len(self.works) > 1 else self.works[0])`.
- [ ] **Adım 4:** `test_variant_batch.py`'nin `BatchGenerator`'ı aynı sebeple:
  `self.fits, self.clock, self.works, self.stop = fits, clock, seconds, stop` ve
  `self.clock.passes(self.works)`. Kurucunun `seconds=` argümanı aynı.
- [ ] **Adım 5:** `test_reference_routes.py`'nin `FakeGenerator`'ına:

```python
    def seconds(self, asked=None):
        return 4 if asked is None else asked
```

## Görev 6: Gerçek üreticiler gerçek döngüde

**Dosyalar:** Değiştir: `queen-editor/backend/tests/test_producer_contract.py`

- [ ] **Adım 1:** İçe aktarmalar: `import pytest`, ve
  `from backend.features.photo_generation.data.comfy_h3_video_generator import ComfyH3VideoGenerator`.
- [ ] **Adım 2:** Dosyanın sonuna:

```python
# --- Madde 423: a video's row says how long the video that was made runs ---------------------------

def wan():
    return ComfyVideoGenerator(VideoComfy(), VIDEO_GRAPH, FIRST_LAST_GRAPH, timeout=60)


def h3():
    return ComfyH3VideoGenerator(VideoComfy(), config.H3_VIDEO_WORKFLOW_PATH,
                                 config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH, timeout=60)


def video_row(video, asked, tmp_path):
    """One frame's three layers under the real loop, its video made by `video` and its job asked at
    `asked` seconds (None: asked none) -- the row the video left."""
    record = Record()
    jobs = [{**job, "seconds": asked} if job["type"] == "video" and asked is not None else job
            for job in FRAMES]
    producers = {**producers_over(VideoComfy(), Ffmpeg(), tmp_path), layers.VIDEO: video}
    make_job(Runner(), Store(), record, Plan(jobs), producers,
             lambda: "2026-10-06T00:00:00+00:00", "düğün")()
    return next(row for row in record.rows if row["layer"] == layers.VIDEO)


def test_a_video_queued_for_h3_and_made_by_wan_says_wans_length(tmp_path):
    """An H3 session queued it at 12 seconds; a later session installed WAN, which makes its graph's
    5 whatever it is asked. The row says what was made -- the export adds these up (madde 423)."""
    assert video_row(wan(), 12, tmp_path)["seconds"] == 5


def test_a_wan_video_says_its_graphs_length(tmp_path):
    assert video_row(wan(), None, tmp_path)["seconds"] == 5


@pytest.mark.parametrize("asked", [4, 8, 12])
def test_an_h3_video_says_the_length_it_was_asked(tmp_path, asked):
    assert video_row(h3(), asked, tmp_path)["seconds"] == asked


def test_an_h3_video_asked_no_length_says_its_graphs_own(tmp_path):
    """Every H3 job queued before madde 422: the Director keeps the graph's 4."""
    assert video_row(h3(), None, tmp_path)["seconds"] == 4
```

## Görev 7: 422'nin testi satırın yeni cevabını söyler

**Dosyalar:** Değiştir: `queen-editor/backend/tests/test_video_length.py`

- [ ] **Adım 1:** `test_a_job_that_carries_no_length_is_made_at_the_graphs_own`:

```python
def test_a_job_that_carries_no_length_is_made_at_the_graphs_own():
    """Every video queued before madde 422, and every one a WAN session queued: the producer is told
    nothing, and its graph says how long the video runs. The row says what was made -- the
    producer's answer, this fake's graph 4 (madde 423)."""
    generator, row = made({})

    assert generator.lengths == [None]
    assert row["seconds"] == 4
```

- [ ] **Adım 2:** `test_export_total.py`'nin belgeleri: modülün ikinci paragrafı ve
  `…counts_at_the_graphs_own`'un belgesi "uzunluk söylemeyen satır = bu değişiklikten önce yapılan
  video" der.

## Görev 8: Dört satır, kırmızı, commit

- [ ] **Adım 1:** Dört satır, paralel. Beklenen: `queen-editor`'ün pytest'inde **4 kırmızı** —
  `…made_by_wan_says_wans_length` (12 ≠ 5), `…wan_video_says_its_graphs_length`,
  `…asked_no_length_says_its_graphs_own` ve 422'nin `…made_at_the_graphs_own`'u
  (`KeyError: 'seconds'`). `…says_the_length_it_was_asked` (3 durum) yeşil. Öteki her şey yeşil.
- [ ] **Adım 2:**

```powershell
git add docs/specs/2026-10-06-queen-editor-m423-export-toplami-testler-design.md docs/plans/2026-10-06-queen-editor-m423-export-toplami-testler-plan.md queen-editor/backend/tests/test_photo_usecases.py queen-editor/backend/tests/test_variant_batch.py queen-editor/backend/tests/test_reference_routes.py queen-editor/backend/tests/test_producer_contract.py queen-editor/backend/tests/test_video_length.py queen-editor/backend/tests/test_export_total.py
git commit -m 'test(queen-editor): Madde 423 red -- a video row says how long the made video runs' -m 'Four red: WAN-made rows say the job length or none, an H3 row asked none says none, and 422 test now expects the producer answer. The H3 asked-length cases green; every other test green.' -m 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>'
```
