# Madde 405 — Üretim süresi kaydı, test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Her katmanın üretim süresinin kaydedildiğini ve kartta okunduğunu söyleyen testleri yazmak, kırmızı koşmak, kırmızı commit'lemek.

**Architecture:** Testler üç yerde: kaydın okuyucusu (`test_photo_record.py`), döngü + galeri + kopya (`test_photo_usecases.py`, sahte saatle), uç (`test_photo_routes.py`). Üretim kodu bu turda değişmez.

**Tech Stack:** pytest, Flask test client.

**Spec:** [m405 test turu](../specs/2026-10-01-queen-editor-m405-uretim-suresi-kaydi-testler-design.md)

## Global Constraints

- Alan adı: satırda ve hücrede `renderSeconds`, kartta `renderSeconds: {katman: saniye}`.
- Saniye onda bire yuvarlanmış sayı.
- Test adları ve yorumlar İngilizce; hiçbir test gerçek bir saniye beklemez.
- Testler yalnız CLAUDE.md'nin dört satırıyla koşulur, aynen, paralel.
- `skip`, `xfail` yok.

---

### Task 1: Kayıt hücreye süreyi taşır

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_record.py` — `test_a_line_that_names_an_ending_picture_carries_it_into_the_slot`'tan sonra

- [ ] **Step 1: Testi yaz**

```python
def test_a_line_that_names_its_render_time_carries_it_into_the_slot(tmp_path):
    """What the card's production time is read from: the produced layer's own line (madde 405)."""
    record = record_at(tmp_path)
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "renderSeconds": 46.3})

    assert record.slots("düğün")["0_a"]["video"]["renderSeconds"] == 46.3
```

### Task 2: Döngü üretilen satıra modelin süresini yazar

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py` — `FakeRecord.slots`, log testlerinin arkası, `test_each_produced_photo_gets_a_record_row`

- [ ] **Step 1: `FakeRecord.slots` gerçeğinin katladığını katlasın** — `endsOn` bloğunun arkasına:

```python
            if isinstance(row.get("renderSeconds"), (int, float)):
                cell["renderSeconds"] = row["renderSeconds"]
```

- [ ] **Step 2: Sahte saat ve süren üretici** — `test_every_produced_frame_gets_its_own_line`'dan sonra:

```python
class Clock:
    """Stands still until something says time passed, so a test can name whose seconds they were."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def passes(self, seconds):
        self.now += seconds


class Takes(FakeGenerator):
    """A producer that works for the given seconds a call; `fails` attempts blow up first."""

    def __init__(self, clock, *seconds, fails=0):
        super().__init__()
        self.clock, self.seconds, self.fails = clock, list(seconds), fails

    def generate(self, prompt, negative, seed, model="", lora="", source=None, end=None,
                 references=()):
        super().generate(prompt, negative, seed, model, lora, source, end, references)
        self.clock.passes(self.seconds.pop(0) if len(self.seconds) > 1 else self.seconds[0])
        if len(self.calls) <= self.fails:
            raise FrameFault(f"node 41: {prompt}")
        return b"DATA"


def rows_of(record, layer):
    return [row for row in record.rows if row.get("layer") == layer and row.get("status") == "done"]
```

- [ ] **Step 3: Beş döngü testi**

```python
def test_a_produced_layer_carries_how_long_the_model_worked_on_it():
    clock, record, plan_store = Clock(), FakeRecord(), FakePlanStore(frames=[frame(0)])

    make_job(sync_runner(), FakeStore(), record, plan_store, {layers.PHOTO: Takes(clock, 46.34)},
             lambda: "t", "düğün", clock=clock)()

    assert rows_of(record, "photo")[0]["renderSeconds"] == 46.3


def test_waiting_in_the_queue_is_no_part_of_a_layers_time():
    # The second photo waited the whole of the first one's render; none of that is its own.
    clock, record = Clock(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0), frame(1)])

    make_job(sync_runner(), FakeStore(), record, plan_store,
             {layers.PHOTO: Takes(clock, 30.0, 50.0)}, lambda: "t", "düğün", clock=clock)()

    assert [row["renderSeconds"] for row in rows_of(record, "photo")] == [30.0, 50.0]


class SlowStore(FakeStore):
    """Drive answering slowly: every read takes the given seconds of the clock."""

    def __init__(self, clock, seconds):
        super().__init__()
        self.clock, self.seconds = clock, seconds

    def read(self, project, filename):
        self.clock.passes(self.seconds)
        return super().read(project, filename)


def test_reading_what_a_layer_is_made_from_is_no_part_of_its_time():
    clock = Clock()
    _store, record, plan_store = video_job_project(job_prompt="kamera yaklaşır")
    store = SlowStore(clock, 5.0)
    store.files["0_a.png"] = b"PNG"

    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: Takes(clock, 40.0)},
             lambda: "t", "düğün", clock=clock)()

    assert rows_of(record, "video")[0]["renderSeconds"] == 40.0


class SlowWriter(FakeWriter):
    def __init__(self, clock, seconds):
        super().__init__()
        self.clock, self.seconds = clock, seconds

    def write(self, prompts, mode="standard", source=None, end=None, scene=""):
        self.clock.passes(self.seconds)
        return super().write(prompts, mode, source, end, scene)


def test_writing_the_prompt_is_no_part_of_the_layers_time():
    # The writer is not the model that makes the layer (madde 403 gave it a turn of its own).
    clock = Clock()
    store, record, plan_store = video_job_project(prompt="kırmızı elbiseli kadın")

    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: Takes(clock, 40.0)},
             lambda: "t", "düğün", clock=clock, writers={layers.VIDEO: SlowWriter(clock, 20.0)})()

    assert rows_of(record, "video")[0]["renderSeconds"] == 40.0


def test_a_retried_layer_carries_the_time_of_the_attempt_that_made_it():
    # The attempts that fell made nothing; adding them up would count the falls, not the render.
    clock, record, plan_store = Clock(), FakeRecord(), FakePlanStore(frames=[frame(0)])

    make_job(sync_runner(), FakeStore(), record, plan_store,
             {layers.PHOTO: Takes(clock, 10.0, fails=2)}, lambda: "t", "düğün", clock=clock)()

    assert rows_of(record, "photo")[0]["renderSeconds"] == 10.0
```

- [ ] **Step 4: Satır testi süreyi karşılaştırmanın dışında tutar** — `test_each_produced_photo_gets_a_record_row`:

```python
def test_each_produced_photo_gets_a_record_row():
    record = FakeRecord()
    run_batch(sync_runner(), FakeStore(), FakeGenerator(), text='["a"]', variants=2, record=record)
    # start_batch runs on the real clock, so the time is only said to be a number; the loop's own
    # tests name it exactly.
    assert all(isinstance(row.pop("renderSeconds"), float) for row in record.rows)
    assert record.rows == [ ... bugünkü iki satır, aynen ... ]
```

### Task 3: Kart ve ikiz

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py` — `test_a_layer_that_blew_up_is_named_as_such`'tan ve `test_a_twin_carries_the_videos_mode_and_where_it_ended`'dan sonra

- [ ] **Step 1: Üç galeri testi**

```python
def test_a_card_says_how_long_each_of_its_layers_took():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done",
                            "renderSeconds": 46.3})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "renderSeconds": 212.0})
    plan_store = FakePlanStore(frames=[frame(0)])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert rows[0]["renderSeconds"] == {"photo": 46.3, "video": 212.0}


def test_a_frame_made_before_times_were_kept_has_none():
    # Nothing is filled in after the fact: an old frame says no time rather than a guessed one.
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store = FakePlanStore(frames=[frame(0)])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert rows[0]["renderSeconds"] == {}


def test_a_layer_that_blew_up_has_no_time():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done",
                            "renderSeconds": 46.3})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "renderSeconds": 212.0})
    record.mark("düğün", "0_a", "video", "0_a_V1_0.mp4", "failed", "t", error="node 41")
    plan_store = FakePlanStore(frames=[frame(0)])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert rows[0]["renderSeconds"] == {"photo": 46.3}
```

- [ ] **Step 2: İkiz testi**

```python
def test_a_twin_carries_how_long_its_layers_took():
    # One file, two frames holding it: the twin's tile must not read no time where the original
    # reads one.
    store, record, plan_store, order = twin_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "renderSeconds": 212.0})

    copy_of(record, store, plan_store, order, ["0_a"])

    assert record.slots("düğün")["C1_0_a"]["video"]["renderSeconds"] == 212.0
```

### Task 4: Uç

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_routes.py` — `test_a_listed_frame_carries_the_prompt_behind_it`'tan sonra

- [ ] **Step 1: Testi yaz**

```python
def test_a_listed_frame_carries_how_long_its_layers_took(tmp_path):
    client, drive = make_client(tmp_path)
    DrivePhotoRecord(DriveStorage(str(drive))).append(
        "düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done",
                  "renderSeconds": 46.3})

    row = client.get("/api/projects/düğün/frames").get_json()["frames"][0]

    assert row["renderSeconds"] == {"photo": 46.3}
```

### Task 5: Kırmızı koş, commit'le

- [ ] **Step 1:** Dört satır, aynen, paralel:
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
- [ ] **Step 2:** Beklenen: `queen-editor` pytest'inde yeni 11 test kırmızı (alan yok / `KeyError`);
  değişen satır testi de kırmızı (`row.pop` alan yokken `KeyError`) — doğru sebep, alan henüz
  yazılmıyor. Öteki üç satır yeşil.
- [ ] **Step 3:** Spec, plan ve testler tek commit'te; mesaj çift tırnaksız, `Co-Authored-By` satırıyla.
