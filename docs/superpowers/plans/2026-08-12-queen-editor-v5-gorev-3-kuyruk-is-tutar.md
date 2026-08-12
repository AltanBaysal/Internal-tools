# Görev 3 — Kuyruk kare değil iş tutar · Uygulama planı

**Amaç:** Plan kaydı iş türü taşır; borç (kare, tür) çiftine sorulur; motor türleri sırayla bitirir
(foto → video → ses) ve işi türünün üreticisine verir.

**Spec:** [Görev 3](../specs/2026-08-12-queen-editor-v5-gorev-3-kuyruk-is-tutar-design.md)

## Genel kısıtlar

Full TDD · `python -m pytest queen-editor -q` · tek commit · dil ve katman kuralları önceki
görevlerdekiyle aynı.

## Dosya haritası

| Dosya | Değişen |
|---|---|
| `domain/queue.py` | `open_jobs` / `next_job` / `counts` slots okur, tür sırasına göre diziler |
| `domain/usecases/start_batch.py` | Planlanan iş `type: photo` taşır |
| `data/plan_store.py` | `type` geriye uyumu |
| `domain/run_loop.py` | Üretici eşlemesi, işi türüne göre verme |
| `domain/usecases/resume_batch.py` · `cancel_generation.py` | `slots` okuma |
| `data/photo_record.py` · `domain/ports.py` | `statuses` kalkar (slots yeter) |
| `main.py` | Döngüye üretici eşlemesi verilmesi |
| testler | Beklentiler + tür sırası testleri |

---

## Adım 1 — Kuyruk testleri (kırmızı)

`tests/test_frame_queue.py`'yi işe göre yeniden yaz:

```python
"""The queue rule: the plan minus the jobs that already settled, type by type."""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.photo_name import frame_id


def job(number, kind=layers.PHOTO, variant=0):
    return {"id": frame_id(number, variant), "type": kind, "number": number, "variant": variant,
            "prompt": "p", "negative": "", "seed": 1}


def slots(**pairs):
    """{"P0_0__photo": "done"} -> the record's own shape."""
    folded = {}
    for key, status in pairs.items():
        frame, _, kind = key.rpartition("__")
        folded.setdefault(frame, {})[kind] = {"status": status, "file": f"{frame}.x"}
    return folded


def test_a_job_with_no_line_is_still_owed():
    assert queue.open_jobs([job(0), job(1)], {}) == [job(0), job(1)]


def test_a_finished_job_is_not_owed_again():
    assert queue.open_jobs([job(0), job(1)], slots(P0_0__photo="done")) == [job(1)]


def test_photos_come_before_videos():
    jobs = [job(0, layers.VIDEO), job(1, layers.PHOTO)]
    assert [j["type"] for j in queue.open_jobs(jobs, {})] == ["photo", "video"]


def test_videos_come_before_audio():
    jobs = [job(0, layers.AUDIO), job(1, layers.VIDEO)]
    assert [j["type"] for j in queue.open_jobs(jobs, {})] == ["video", "audio"]


def test_a_type_is_finished_before_the_next_one_starts():
    jobs = [job(0, layers.PHOTO), job(1, layers.VIDEO), job(2, layers.PHOTO)]
    assert queue.next_job(jobs, {})["id"] == "P0_0"
    assert queue.next_job(jobs, slots(P0_0__photo="done"))["id"] == "P2_0"
    assert queue.next_job(jobs, slots(P0_0__photo="done", P2_0__photo="done"))["id"] == "P1_0"


def test_plan_order_is_kept_inside_a_type():
    assert [j["id"] for j in queue.open_jobs([job(1), job(0)], {})] == ["P1_0", "P0_0"]


def test_a_requeued_job_waits_behind_the_ones_that_never_ran():
    jobs = [job(0), job(1)]
    assert [j["id"] for j in queue.open_jobs(jobs, slots(P0_0__photo="queued"))] == \
        ["P1_0", "P0_0"]


def test_one_frames_slots_are_owed_separately():
    # The photo landed; the video that hangs on it is still owed.
    jobs = [{"id": "P0_0", "type": "photo"}, {"id": "P0_0", "type": "video"}]
    assert [j["type"] for j in queue.open_jobs(jobs, slots(P0_0__photo="done"))] == ["video"]


def test_a_deleted_photo_does_not_fall_back_into_the_queue():
    assert queue.open_jobs([job(0)], slots(P0_0__photo="deleted")) == []


def test_counts_are_read_from_the_slots():
    jobs = [job(0), job(1), job(2)]
    taken = slots(P0_0__photo="done", P1_0__photo="failed")
    assert queue.counts(jobs, taken) == {"total": 3, "done": 1, "failed": 1,
                                         "failures": ["P1_0.png"]}
```

## Adım 2 — `queue.py`

```python
"""What the queue still owes: the plan minus the jobs that already settled, type by type.

One pure rule, so "is this job still coming?" has a single answer that the worker, the queue
endpoint and the gallery all read the same way.

A job's state lives in the photo record as one line per event, latest line wins, folded per
(frame, layer). Two states are deliberately absent from disk: a job with no line at all is pending
-- the plan already says it was asked for, and repeating that as a flag would give one truth two
writers -- and a running job belongs to the live worker, because a dead process must never leave
"running" behind.

The engine finishes one type before it starts the next: photos, then videos, then audio. That is the
design's rule (madde 36) and it pays for itself twice -- each type loads its own producer, so
hopping between them would reload a model every turn, and a video needs the photo it hangs on to
exist first.
"""
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.photo_name import photo_file

DONE = "done"           # the layer landed and its file is on disk
FAILED = "failed"       # the render blew up; the tile stays red until Tekrar dene
REMOVED = "removed"     # a pending job pulled out of the queue; never produced
DELETED = "deleted"     # a produced layer the user deleted
QUEUED = "queued"       # a settled job put back in line

# QUEUED is the only written status that reopens a job; the rest settle it for good.

# The order the engine works in.
ORDER = (layers.PHOTO, layers.VIDEO, layers.AUDIO)


def is_open(status):
    """True while the job is still owed: never written about, or put back in line."""
    return status is None or status == QUEUED


def _status(slots, job):
    cell = slots.get(job["id"], {}).get(job.get("type", layers.PHOTO))
    return cell["status"] if cell else None


def open_jobs(jobs, slots):
    """The jobs still owed, in the order the engine will do them.

    Type first, then the plan's own order. Inside a type, a job the user sent back with Tekrar dene
    waits behind everything that has never had a turn (design v2, G10) -- among themselves the
    re-queued ones keep plan order. Where a frame sits in the GALLERY does not change; this is only
    the order work is done in.
    """
    owed = []
    for kind in ORDER:
        same = [j for j in jobs if j.get("type", layers.PHOTO) == kind]
        fresh = [j for j in same if _status(slots, j) is None]
        requeued = [j for j in same if _status(slots, j) == QUEUED]
        owed += fresh + requeued
    return owed


def next_job(jobs, slots):
    """The job the worker should do now, or None when nothing is owed."""
    owed = open_jobs(jobs, slots)
    return owed[0] if owed else None


def counts(jobs, slots):
    """The numbers the status endpoint publishes -- read from disk rather than from a run's memory,
    so they are still right after the server restarts.

    Looked up by identity, published as file names: the screen marks its red tiles by file.
    """
    failures = [photo_file(j["id"]) for j in jobs if _status(slots, j) == FAILED]
    return {"total": len(jobs),
            "done": sum(1 for j in jobs if _status(slots, j) == DONE),
            "failed": len(failures),
            "failures": failures}
```

**Döngüsel import, ve çözümü.** `open_frames` / `next_frame` adları `open_jobs` / `next_job` olur.
Ama `layers.py` bugün `queue`'yu import ediyor (`TAKEN = (queue.DONE, queue.FAILED)`); `queue` da
katman adlarını isteyince ikisi birbirini import eder.

Çözüm: **durum sözlüğü `layers.py`'ye taşınır.** Bir satırın durumu zaten bir katmanın başına geleni
anlatıyor, dolayısıyla yeri orası. `queue.py` onları kendi adıyla yeniden yayınlar
(`DONE = layers.DONE` …) ki bugünkü `queue.DONE` çağrıları olduğu gibi çalışsın, ve import tek yöne
akar: `queue → layers`.

## Adım 3 — Plan ve start_batch

`plan_frames` her işe `"type": queue.PHOTO` yazar. `plan_store.read` geriye uyumu ekler:

```python
                           "type": frame.get("type") if isinstance(frame.get("type"), str)
                           else queue.PHOTO,
```

## Adım 4 — Döngü üreticiyi türüne göre seçer

`make_job(runner, store, record, plan_store, producers, now, project, …)` — `generator` yerine
`producers`, bir eşleme: `{queue.PHOTO: <PhotoGenerator>}`.

```python
            job = owed[0]
            produce = producers.get(job.get("type", queue.PHOTO))
            if produce is None:
                # Never silently skipped: skipping would lose work the user asked for.
                return summary("error", error=f"Bu iş türü için üretici yok: {job.get('type')}")
```

`main.py` eşlemeyi `{queue.PHOTO: generator}` diye verir.

## Adım 5 — `statuses` kalkar

`record.statuses` artık kimsenin okumadığı bir katlama; `slots` onu kapsıyor. Kayıttan ve
`ports.py`'den çıkar. Testlerdeki `record.statuses(...)` iddiaları `test_photo_usecases.py`'ye
konan küçük bir yardımcıya döner:

```python
def photo_statuses(record, project="düğün"):
    """{frame: photo slot status} -- what the tests used to read off the record."""
    return {frame: cells["photo"]["status"]
            for frame, cells in record.slots(project).items() if "photo" in cells}
```

## Adım 6 — Tam takım ve commit

```bash
git add -A
git commit -m 'feat(queen-editor): the queue holds jobs with a type, finished type by type'
```

## Kabul kriteri

- Karışık türde işlerde motor türleri sırayla bitiriyor.
- Yalnız foto işi olan kuyruk bugünküyle aynı akıyor; v4 nöbetçisi yeşil.
- `python -m pytest queen-editor -q` yeşil.
