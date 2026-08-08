# Queen Editor v4 · Madde 1 — Canlı kuyruk (arka uç) Uygulama Planı

> **Ajan işçiler için:** bu plan bu oturumda **inline** koşulur (kullanıcı kararı). Adımlar
> `- [ ]` kutucuklarıyla takip edilir.

**Hedef:** Kuyruk, bir koşuya ait dondurulmuş listeden çıkıp sürekli açık bir sıraya döner; hatalı
kare kalıcı olur.

**Mimari:** Bir karenin durumu günlüğe satır olarak yazılır (`done · failed · removed · deleted ·
queued`), satırsız kare bekliyordur. Kuyruk = plan eksi kapanmış kareler; bu kural tek bir saf
modülde (`domain/queue.py`) durur. Döngü kare listesi taşımaz, her turda plan ve günlüğü diskten
okur — canlı kuyruğun tek mekanizması budur. Üretimi başlatan üç yol (yeni parti, devam, tekrar
dene) "kuyruğu değiştir + işçi boştaysa çalıştır" ikilisine iner.

**Yığın:** Python 3, Flask, `pytest`. Domain saf: `flask`, `requests` ya da dosya şeması bilgisi
içermez; testler sahte port'larla koşar, `spawn` senkron verilir.

**Tasarım dokümanı:**
[Madde 1 — Canlı kuyruk](../specs/2026-08-08-queen-editor-v4-madde-1-canli-kuyruk-design.md)

## Global kısıtlar

- Bağımlılık yönü: `presentation → domain ← data → services`. `feature ↛ feature`,
  `service ↛ feature`, `service ↛ service` — istisnasız.
- Yorum, docstring, **test adı** ve commit mesajı **İngilizce**; kullanıcıya giden metin **Türkçe**.
- Bir dosya başkasının cevabını bayrak olarak tekrarlamaz. `pending` ve `running` diske yazılmaz.
- Dosya önce diske yazılır, **sonra** günlük satırı eklenir. Satır "bu fotoğraf burada" demektir.
- Günlük hiç yeniden yazılmaz, yalnız satır eklenir. Plan yalnız sonuna eklenir; kare çıkarılmaz.
- Numara asla yeniden kullanılmaz: disk, plan ve günlük üçü birden talep sahibidir.
- Arayüz bu maddede hiç değişmez. `frontend/` altına dokunulmaz, `npm run build` koşulmaz.
- Testler `queen-editor/` klasöründen `pytest` ile koşar.

---

## Dosya haritası

| Dosya | Sorumluluk | Durum |
|---|---|---|
| `backend/features/photo_generation/domain/queue.py` | Kuyruk sözlüğü (`done`…`queued`) ve saf kuralı: açık kareler, sıradaki kare, sayılar | **yeni** |
| `backend/features/photo_generation/data/photo_record.py` | Günlük dosyasının şeması: satır yazma, durum katlama, geriye uyum | değişir |
| `backend/features/photo_generation/data/plan_store.py` | Plan dosyasının şeması: sonuna ekleme, kare başına negatif | değişir |
| `backend/features/photo_generation/domain/run_loop.py` | Her turda diskten okuyan döngü | yeniden yazılır |
| `backend/features/photo_generation/domain/usecases/run_queue.py` | "İşçi boştaysa bu projenin kuyruğuna koş" + `Busy` | **yeni** |
| `…/usecases/start_batch.py` | Doğrula, kareleri planla, plana ekle, kuyruğu koştur | değişir |
| `…/usecases/resume_batch.py` | Açık kare varsa kuyruğu koştur | değişir |
| `…/usecases/retry_frame.py` | `queued` satırı yaz, kuyruğu koştur | değişir |
| `…/usecases/cancel_generation.py` | Açık her kareye `removed` satırı yaz | değişir |
| `…/usecases/get_queue.py` | `{pending, failed, total}` | değişir |
| `…/usecases/delete_photos.py` | `mark(..., "deleted", ...)` | değişir |
| `…/domain/ports.py` | Port imzaları | değişir |
| `backend/main.py` | Bağlama | değişir |
| `backend/tests/test_frame_queue.py` | Kuyruk kuralının testleri | **yeni** |
| `backend/tests/test_photo_record.py` · `test_plan_store.py` · `test_photo_usecases.py` | Mevcut testler | değişir |

---

## Görev 1 — Kuyruk kuralı (`domain/queue.py`)

Saf modül; hiçbir şey ona bağlı değil, o hiçbir şeye bağlı değil (yalnız `photo_name`).

**Dosyalar:**
- Oluştur: `queen-editor/backend/features/photo_generation/domain/queue.py`
- Test: `queen-editor/backend/tests/test_frame_queue.py`

**Ürettiği arayüz (sonraki görevler buna dayanıyor):**
`DONE` `FAILED` `REMOVED` `DELETED` `QUEUED` sabitleri ·
`is_open(status) -> bool` · `open_frames(frames, statuses) -> list` ·
`next_frame(frames, statuses) -> dict | None` ·
`counts(frames, statuses) -> {"total", "done", "failed", "failures"}`.
`frames`: `[{"number", "letter", "prompt", "negative", "seed"}]` · `statuses`: `{dosya adı: durum}`.

- [ ] **Adım 1: Başarısız testi yaz**

`queen-editor/backend/tests/test_frame_queue.py`:

```python
"""The queue rule: the plan minus the frames that already settled."""
from backend.features.photo_generation.domain import queue


def frame(number, letter="a"):
    return {"number": number, "letter": letter, "prompt": "p", "negative": "", "seed": 1}


def test_a_frame_with_no_line_is_still_owed():
    assert queue.open_frames([frame(0), frame(1)], {}) == [frame(0), frame(1)]


def test_a_produced_frame_is_not_owed_again():
    assert queue.open_frames([frame(0), frame(1)], {"0_a.png": queue.DONE}) == [frame(1)]


def test_a_failed_frame_is_not_retried_on_its_own():
    assert queue.open_frames([frame(0)], {"0_a.png": queue.FAILED}) == []


def test_a_frame_pulled_out_of_the_queue_is_not_owed():
    assert queue.open_frames([frame(0)], {"0_a.png": queue.REMOVED}) == []


def test_a_deleted_photo_does_not_fall_back_into_the_queue():
    assert queue.open_frames([frame(0)], {"0_a.png": queue.DELETED}) == []


def test_queued_reopens_a_settled_frame():
    assert queue.open_frames([frame(0)], {"0_a.png": queue.QUEUED}) == [frame(0)]


def test_next_frame_is_the_first_one_still_owed():
    statuses = {"0_a.png": queue.DONE, "1_a.png": queue.FAILED}
    assert queue.next_frame([frame(0), frame(1), frame(2)], statuses) == frame(2)


def test_next_frame_is_none_when_the_queue_is_empty():
    assert queue.next_frame([frame(0)], {"0_a.png": queue.DONE}) is None


def test_counts_are_read_from_the_statuses():
    frames = [frame(0), frame(1), frame(2)]
    statuses = {"0_a.png": queue.DONE, "1_a.png": queue.FAILED}
    assert queue.counts(frames, statuses) == {"total": 3, "done": 1, "failed": 1,
                                              "failures": ["1_a.png"]}
```

- [ ] **Adım 2: Testi koş, düştüğünü gör**

`cd queen-editor && pytest backend/tests/test_frame_queue.py -v`
Beklenen: `ModuleNotFoundError: backend.features.photo_generation.domain.queue`

- [ ] **Adım 3: Modülü yaz**

`queen-editor/backend/features/photo_generation/domain/queue.py`:

```python
"""What the queue still owes: the plan minus the frames that already settled.

One pure rule, so "is this frame still coming?" has a single answer that the worker, the queue
endpoint and the gallery all read the same way.

A frame's state lives in the photo record as one line per event, latest line wins. Two states are
deliberately absent from disk: a frame with no line at all is pending -- the plan already says it
was asked for, and repeating that as a flag would give one truth two writers -- and a running frame
belongs to the live worker, because a dead process must never leave "running" behind.
"""
from backend.features.photo_generation.domain.photo_name import file_name

DONE = "done"           # the photo landed and its file is on disk
FAILED = "failed"       # the render blew up; the tile is red until Tekrar dene
REMOVED = "removed"     # a pending frame pulled out of the queue; never produced
DELETED = "deleted"     # a produced photo the user deleted
QUEUED = "queued"       # a settled frame put back in line

# QUEUED is the only written status that reopens a frame; the rest settle it for good.


def is_open(status):
    """True while the frame is still owed: never written about, or put back in line."""
    return status is None or status == QUEUED


def _name(frame):
    return file_name(frame["number"], frame["letter"])


def open_frames(frames, statuses):
    """The plan frames still owed, in the plan's own order."""
    return [f for f in frames if is_open(statuses.get(_name(f)))]


def next_frame(frames, statuses):
    """The frame the worker should render now, or None when nothing is owed."""
    owed = open_frames(frames, statuses)
    return owed[0] if owed else None


def counts(frames, statuses):
    """The numbers the status endpoint publishes -- read from disk, not from a run's memory, so
    they are still right after the server restarts."""
    names = [_name(f) for f in frames]
    failures = [name for name in names if statuses.get(name) == FAILED]
    return {"total": len(frames),
            "done": sum(1 for name in names if statuses.get(name) == DONE),
            "failed": len(failures),
            "failures": failures}
```

- [ ] **Adım 4: Testleri koş, geçtiğini gör**

`cd queen-editor && pytest backend/tests/test_frame_queue.py -v` → 9 geçti

- [ ] **Adım 5: Commit**

```bash
git add queen-editor/backend/features/photo_generation/domain/queue.py \
        queen-editor/backend/tests/test_frame_queue.py
git commit -m "feat(queen-editor): frame status vocabulary and the queue rule"
```

---

## Görev 2 — Günlük durumları tutar (`data/photo_record.py`)

**Dosyalar:**
- Değiştir: `…/data/photo_record.py`
- Değiştir: `…/domain/usecases/delete_photos.py:34`
- Değiştir: `…/domain/ports.py` (PhotoRecord)
- Test: `queen-editor/backend/tests/test_photo_record.py`, `…/test_photo_usecases.py` (sahte kayıt)

**Tükettiği:** Görev 1'in `queue.DONE` / `queue.DELETED` sabitleri.
**Ürettiği:** `record.statuses(project) -> {dosya adı: durum}` ·
`record.mark(project, file, status, at, error=None) -> None`.
`mark_deleted` **kalkar**.

- [ ] **Adım 1: Başarısız testleri yaz**

`test_photo_record.py` sonuna:

```python
def test_statuses_reads_the_latest_line_per_file():
    storage, record = fake_storage(), None
    record = DrivePhotoRecord(storage)
    record.append("düğün", {"file": "0_a.png", "status": "done", "createdAt": "t1"})
    record.mark("düğün", "1_a.png", "failed", "t2", error="ComfyUI 500")
    record.mark("düğün", "0_a.png", "deleted", "t3")
    assert record.statuses("düğün") == {"0_a.png": "deleted", "1_a.png": "failed"}


def test_a_failure_line_carries_the_servers_own_words():
    storage = fake_storage()
    record = DrivePhotoRecord(storage)
    record.mark("düğün", "1_a.png", "failed", "t2", error="ComfyUI 500: out of memory")
    assert json.loads(storage.read_lines("düğün", "photos.jsonl")[0])["error"] == \
        "ComfyUI 500: out of memory"


def test_lines_written_before_the_status_field_still_read():
    storage = fake_storage()
    record = DrivePhotoRecord(storage)
    record.append("düğün", {"file": "0_a.png", "prompt": "p", "createdAt": "t1"})
    record.append("düğün", {"file": "1_a.png", "prompt": "p", "createdAt": "t2"})
    record.append("düğün", {"file": "1_a.png", "deletedAt": "t3"})
    assert record.statuses("düğün") == {"0_a.png": "done", "1_a.png": "deleted"}
    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]


def test_only_done_frames_are_photos():
    storage = fake_storage()
    record = DrivePhotoRecord(storage)
    record.append("düğün", {"file": "0_a.png", "status": "done", "createdAt": "t1"})
    record.mark("düğün", "1_a.png", "removed", "t2")
    record.mark("düğün", "2_a.png", "failed", "t3")
    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]


def test_a_removed_frame_still_claims_its_number():
    storage = fake_storage()
    record = DrivePhotoRecord(storage)
    record.mark("düğün", "7_a.png", "removed", "t1")
    assert record.max_number("düğün") == 7
```

> `fake_storage()` ve `json` importu bu dosyada zaten var; yoksa dosyanın kendi yardımcı
> kurulumunu (`DriveStorage(tmp_path)` ya da mevcut sahte) aynen kullan — testin ilk satırında
> hangi kurulum kullanılıyorsa o.

- [ ] **Adım 2: Testleri koş, düştüğünü gör**

`cd queen-editor && pytest backend/tests/test_photo_record.py -v`
Beklenen: `AttributeError: 'DrivePhotoRecord' object has no attribute 'mark'`

- [ ] **Adım 3: Kaydı yaz**

`data/photo_record.py` — dosya başlığına ekle ve gövdeyi değiştir:

```python
"""PhotoRecord over DriveStorage -- the only place that knows the record file's name and shape.

This is the log of what happened to every planned frame: one JSON object per line, appended right
after the event itself, never rewritten. Append-only is the point -- a session that dies mid-write
loses at most the line it was adding, where rewriting the whole file could lose every earlier one.
So a photo landing, a deletion, a failed render and a frame pulled out of the queue are all lines;
reading folds them and the latest line about a file wins.
"""
import json

from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import number_of

FILE = "photos.jsonl"


def _status_of(row):
    """A row's status, including rows written before the field existed.

    Those old rows are exactly two kinds: a photo landing (prompt + createdAt) and a deletion
    (deletedAt). Nothing needs migrating -- the projects already on Drive keep reading."""
    status = row.get("status")
    if isinstance(status, str):
        return status
    return queue.DELETED if row.get("deletedAt") else queue.DONE


class DrivePhotoRecord:
    def __init__(self, storage):
        self._storage = storage

    def append(self, project, entry):
        """entry: {"file", "status", …} -- a produced photo also carries prompt, negative, seed."""
        self._storage.append_line(project, FILE, json.dumps(entry, ensure_ascii=False))

    def mark(self, project, file, status, at, error=None):
        """Write down an event that produced no photo: a failure, a deletion, a frame pulled out
        of the queue, or a frame put back in line."""
        entry = {"file": file, "status": status, "at": at}
        if error is not None:
            # The server's own words, verbatim -- never a guessed cause.
            entry["error"] = error
        self.append(project, entry)

    def _rows(self, project):
        """Every readable row, in the order it was written.

        A line that will not parse is skipped rather than raised on: the last one can be
        half-written after a session death, and one bad line must not hide the photos before it.
        """
        rows = []
        for line in self._storage.read_lines(project, FILE):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict) and isinstance(row.get("file"), str):
                rows.append(row)
        return rows

    def statuses(self, project):
        """{file name: latest status} -- the fold every "what happened to this frame" question
        reads, the queue rule included."""
        return {row["file"]: _status_of(row) for row in self._rows(project)}

    def list(self, project):
        """Every photo that still exists, newest first."""
        live = {}
        for row in self._rows(project):
            if _status_of(row) == queue.DONE:
                live[row["file"]] = row
            else:
                live.pop(row["file"], None)
        return list(reversed(list(live.values())))

    def max_number(self, project):
        """Highest number the record has ever seen, whatever became of the frame; None when empty.

        Every line counts -- deleted, failed and removed included. Their numbers have to stay
        claimed, or a new photo would take the name of an old one: same name, a different prompt,
        and browsers still holding the old bytes under an immutable cache header.
        """
        numbers = [n for n in (number_of(row["file"]) for row in self._rows(project))
                   if n is not None]
        return max(numbers) if numbers else None
```

- [ ] **Adım 4: `delete_photos` yeni yazıcıyı kullansın**

`domain/usecases/delete_photos.py` — importa ekle ve satır 34'ü değiştir:

```python
from backend.features.photo_generation.domain import queue
```
```python
        record.mark(project, file, queue.DELETED, now())
```

- [ ] **Adım 5: Port imzasını güncelle**

`domain/ports.py` içinde `PhotoRecord` gövdesini değiştir:

```python
class PhotoRecord(Protocol):
    def append(self, project: str, entry: dict) -> None:
        """Add one produced photo's row."""
        ...

    def list(self, project: str) -> list:
        """Every photo that still exists, newest first."""
        ...

    def mark(self, project: str, file: str, status: str, at: str, error: str | None = None) -> None:
        """Append a line for an event that produced no photo."""
        ...

    def statuses(self, project: str) -> dict:
        """{file name: latest status} for every frame the log has seen."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the record has ever seen, whatever became of the frame."""
        ...
```

- [ ] **Adım 6: Sahte kaydı güncelle**

`tests/test_photo_usecases.py` içindeki `FakeRecord` (satır ~87): `mark_deleted` yerine:

```python
    def mark(self, project, file, status, at, error=None):
        entry = {"file": file, "status": status, "at": at}
        if error is not None:
            entry["error"] = error
        self.rows.setdefault(project, []).append(entry)

    def statuses(self, project):
        latest = {}
        for row in self.rows.get(project, []):
            latest[row["file"]] = row.get("status", "done")
        return latest
```

> `FakeRecord`'un iç alanı bugün hangi adı taşıyorsa (`rows`, `_rows` vb.) o kullanılır; `list` ve
> `max_number` zaten var, `list` yalnız `status == "done"` satırlarını döndürecek şekilde
> düzeltilir. `test_a_deleted_number_is_never_used_again` testindeki
> `record.mark_deleted("düğün", "0_a.png", …)` çağrısı
> `record.mark("düğün", "0_a.png", "deleted", …)` olur.

- [ ] **Adım 7: Tüm testleri koş**

`cd queen-editor && pytest -q` → yeşil

- [ ] **Adım 8: Commit**

```bash
git add queen-editor/backend/features/photo_generation/data/photo_record.py \
        queen-editor/backend/features/photo_generation/domain/usecases/delete_photos.py \
        queen-editor/backend/features/photo_generation/domain/ports.py \
        queen-editor/backend/tests/test_photo_record.py \
        queen-editor/backend/tests/test_photo_usecases.py
git commit -m "feat(queen-editor): the photo log records a status per frame"
```

---

## Görev 3 — Plan sonuna eklenir, negatif kareye taşınır (`data/plan_store.py`)

**Dosyalar:**
- Değiştir: `…/data/plan_store.py`
- Değiştir: `…/domain/ports.py` (PlanStore)
- Test: `queen-editor/backend/tests/test_plan_store.py`

**Ürettiği:** `plan_store.read(project) -> {"negative": <eski üst alan>, "frames": [...]}` — her kare
`negative` taşır · `plan_store.append(project, frames) -> None` · `max_number` aynı.
`write` ve `clear` **kalkar**.

- [ ] **Adım 1: Başarısız testleri yaz**

`test_plan_store.py` sonuna:

```python
def test_append_puts_frames_at_the_end_of_the_queue():
    store = DrivePlanStore(fake_storage())
    store.append("düğün", [{"number": 0, "letter": "a", "prompt": "ilk", "negative": "n1",
                            "seed": 1}])
    store.append("düğün", [{"number": 1, "letter": "a", "prompt": "ikinci", "negative": "n2",
                            "seed": 2}])
    assert [f["prompt"] for f in store.read("düğün")["frames"]] == ["ilk", "ikinci"]


def test_each_frame_keeps_its_own_negative():
    store = DrivePlanStore(fake_storage())
    store.append("düğün", [{"number": 0, "letter": "a", "prompt": "p", "negative": "n1",
                            "seed": 1}])
    store.append("düğün", [{"number": 1, "letter": "a", "prompt": "p", "negative": "n2",
                            "seed": 2}])
    assert [f["negative"] for f in store.read("düğün")["frames"]] == ["n1", "n2"]


def test_a_plan_written_before_per_frame_negatives_falls_back_to_the_old_field(tmp_path):
    storage = fake_storage()
    storage.write_text("düğün", "plan.json", json.dumps(
        {"negative": "eski", "frames": [{"number": 0, "letter": "a", "prompt": "p", "seed": 1}]}))
    store = DrivePlanStore(storage)
    assert store.read("düğün")["frames"][0]["negative"] == "eski"


def test_max_number_counts_everything_the_plan_ever_reserved():
    store = DrivePlanStore(fake_storage())
    store.append("düğün", [{"number": 4, "letter": "a", "prompt": "p", "negative": "",
                            "seed": 1}])
    store.append("düğün", [{"number": 9, "letter": "a", "prompt": "p", "negative": "",
                            "seed": 2}])
    assert store.max_number("düğün") == 9
```

> `fake_storage()` / `tmp_path` kurulumu bu dosyada hangi biçimdeyse o kullanılır. `clear` ve
> `write` için var olan testler **silinir** — o iki metot kalkıyor.

- [ ] **Adım 2: Testleri koş, düştüğünü gör**

`cd queen-editor && pytest backend/tests/test_plan_store.py -v`
Beklenen: `AttributeError: 'DrivePlanStore' object has no attribute 'append'`

- [ ] **Adım 3: Plan deposunu yaz**

`data/plan_store.py` tamamı:

```python
"""PlanStore over DriveStorage -- the only place that knows the plan file's name and shape.

The plan is the queue: what was asked for, in the order it was asked for. It is only ever appended
to. A frame is never taken out of it and never marked -- what became of a frame is the photo
record's answer, and a plan that repeated it would give one truth two writers. That is also why a
whole-file rewrite happens once per submitted batch rather than once per frame: a Colab machine
that dies mid-write would otherwise take the entire queue with it.

A frame carries its number and letter, not a file name: the "<number>_<letter>.png" scheme is
photo_store's to know, and repeating it here would give it a second owner.
"""
import json

FILE = "plan.json"


class DrivePlanStore:
    def __init__(self, storage):
        self._storage = storage

    def read(self, project):
        """{"negative": <legacy field>, "frames": [...]} -- every frame carrying its own negative.

        negative used to be one field for the whole plan, because a plan was one run. A live queue
        holds batches submitted with different negatives, so it belongs to the frame now; the old
        top-level field is still read and handed to frames that predate the change.
        """
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return {"negative": "", "frames": []}
        try:
            data = json.loads(raw)
        except ValueError:
            # A half-written or hand-edited plan must not make the project unopenable.
            return {"negative": "", "frames": []}
        if not isinstance(data, dict) or not isinstance(data.get("frames"), list):
            return {"negative": "", "frames": []}
        legacy = data.get("negative")
        legacy = legacy if isinstance(legacy, str) else ""
        frames = []
        for frame in data["frames"]:
            if not isinstance(frame, dict) or not isinstance(frame.get("number"), int):
                continue
            negative = frame.get("negative")
            frames.append({**frame,
                           "negative": negative if isinstance(negative, str) else legacy})
        return {"negative": legacy, "frames": frames}

    def append(self, project, frames):
        """Put frames at the end of the queue.

        frames: [{"number", "letter", "prompt", "negative", "seed"}] in render order.
        """
        self._write(project, self.read(project)["frames"] + frames)

    def max_number(self, project):
        """Highest number this plan reserved, or None when there is no plan to honour."""
        numbers = [frame["number"] for frame in self.read(project)["frames"]]
        return max(numbers) if numbers else None

    def _write(self, project, frames):
        self._storage.write_text(project, FILE, json.dumps({"frames": frames},
                                                           ensure_ascii=False, indent=2))
```

- [ ] **Adım 4: Port imzasını güncelle**

`domain/ports.py` içinde `PlanStore` gövdesi:

```python
class PlanStore(Protocol):
    def read(self, project: str) -> dict:
        """{"negative", "frames"} -- the queue as stored, every frame carrying its negative."""
        ...

    def append(self, project: str, frames: list) -> None:
        """Put frames at the end of the queue."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the stored plan reserved; None when there is no plan."""
        ...
```

- [ ] **Adım 5: Sahte planı güncelle**

`tests/test_photo_usecases.py` içindeki `FakePlanStore` (satır ~65): `write`/`clear` yerine
`append` tutar, `read` `{"negative": self.negative, "frames": self.frames}` döndürür,
`written` alanı **appended** listesine dönüşür:

```python
class FakePlanStore:
    def __init__(self, frames=None, negative="", reserved=None):
        self.frames = list(frames or [])
        self.negative = negative
        self.reserved = reserved
        self.appended = []          # each append call's frames, in order

    def read(self, project):
        return {"negative": self.negative, "frames": self.frames}

    def append(self, project, frames):
        self.appended.append(frames)
        self.frames = self.frames + frames

    def max_number(self, project):
        if self.reserved is not None:
            return self.reserved
        return max((f["number"] for f in self.frames), default=None)
```

- [ ] **Adım 6: Testleri koş**

`cd queen-editor && pytest backend/tests/test_plan_store.py -v` → geçti.
`pytest -q` bu adımda **kırmızı olabilir** (kullanım noktaları hâlâ `write` çağırıyor) — Görev 4
onları düzeltiyor; bu görev tek başına commit edilmez.

---

## Görev 4 — Döngü diskten okur, üç yol tek ikiliye iner

Tek atomik değişiklik: döngü artık liste taşımadığı için üç kullanım noktası aynı anda değişmek
zorunda. Görev 3'ün commit'i de bununla birlikte atılır.

**Dosyalar:**
- Yeniden yaz: `…/domain/run_loop.py`
- Oluştur: `…/domain/usecases/run_queue.py`
- Değiştir: `…/domain/usecases/start_batch.py` · `resume_batch.py` · `retry_frame.py` ·
  `cancel_generation.py` · `get_queue.py`
- Değiştir: `backend/main.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

**Tükettiği:** Görev 1'in `queue.*`, Görev 2'nin `record.statuses/mark`, Görev 3'ün
`plan_store.read/append`.

- [ ] **Adım 1: Başarısız testleri yaz**

`tests/test_photo_usecases.py` sonuna:

```python
def test_frames_added_while_the_loop_runs_are_produced_in_the_same_run():
    runner, plan_store, record = sync_runner(), FakePlanStore(), FakeRecord()
    store, generator = FakeStore(), FakeGenerator()
    seen = []

    def generate(prompt, negative, seed):
        seen.append(prompt)
        if prompt == "ilk":
            plan_store.append("düğün", [{"number": 9, "letter": "a", "prompt": "sonradan",
                                         "negative": "", "seed": 7}])
        return b"png"

    generator.generate = generate
    run_batch(runner, store, generator, text="ilk", variants=1, record=record,
              plan_store=plan_store)
    assert seen == ["ilk", "sonradan"]


def test_the_loop_stops_by_itself_when_the_queue_empties():
    runner = sync_runner()
    run_batch(runner, FakeStore(), FakeGenerator(), text="tek", variants=1)
    assert runner.status()["status"] == "done"


def test_adding_to_the_queue_of_the_running_project_is_not_busy():
    runner = PhotoRunner(spawn=lambda fn: None)      # claims the worker, never runs the job
    runner.start("düğün", lambda: None)
    run_batch(runner, FakeStore(), FakeGenerator(), text="ikinci parti")


def test_adding_while_another_project_runs_is_busy():
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("başka", lambda: None)
    with pytest.raises(Busy):
        run_batch(runner, FakeStore(), FakeGenerator(), text="ilk")


def test_a_failed_frame_is_written_to_the_log():
    record, generator = FakeRecord(), FakeGenerator(fail_on=["patlak"])
    run_batch(sync_runner(), FakeStore(), generator, text="patlak", variants=1, record=record)
    assert record.statuses("düğün") == {"0_a.png": "failed"}


def test_the_queue_endpoint_reports_failures_after_a_restart():
    record, plan_store = FakeRecord(), FakePlanStore()
    generator = FakeGenerator(fail_on=["patlak"])
    run_batch(sync_runner(), FakeStore(), generator, text="patlak\ntutan", variants=1,
              record=record, plan_store=plan_store)
    # a fresh runner is what a restarted server has: nothing in memory
    assert get_queue(record, FakeStore(), plan_store, "düğün") == {
        "pending": [], "failed": ["0_a.png"], "total": 2}


def test_a_deleted_photo_does_not_come_back_as_pending():
    record, plan_store = FakeRecord(), FakePlanStore()
    run_batch(sync_runner(), FakeStore(), FakeGenerator(), text="tek", variants=1,
              record=record, plan_store=plan_store)
    record.mark("düğün", "0_a.png", "deleted", "t9")
    assert get_queue(record, FakeStore(), plan_store, "düğün")["pending"] == []


def test_retry_puts_the_frame_back_in_line():
    record, plan_store = FakeRecord(), FakePlanStore()
    generator = FakeGenerator(fail_on=["patlak"])
    run_batch(sync_runner(), FakeStore(), generator, text="patlak", variants=1, record=record,
              plan_store=plan_store)
    generator.fail_on = []
    retry_frame(sync_runner(), FakeStore(), record, plan_store, generator,
                lambda: "t2", "düğün", "0_a.png")
    assert record.statuses("düğün") == {"0_a.png": "done"}


def test_clearing_the_queue_keeps_the_numbers_dead():
    store, record, plan_store = FakeStore(next_no=0), FakeRecord(), FakePlanStore()
    plan_store.append("düğün", [{"number": 0, "letter": "a", "prompt": "p", "negative": "",
                                 "seed": 1}])
    cancel_generation(sync_runner(), store, record, plan_store, lambda: "t1", "düğün")
    assert record.statuses("düğün") == {"0_a.png": "removed"}
    assert next_number(store, plan_store, record, "düğün") == 1


def test_a_second_batch_renders_with_its_own_negative():
    plan_store, record = FakePlanStore(), FakeRecord()
    seen = []
    generator = FakeGenerator()
    generator.generate = lambda prompt, negative, seed: (seen.append(negative), b"png")[1]
    run_batch(sync_runner(), FakeStore(), generator, text="ilk", negative="n1", variants=1,
              record=record, plan_store=plan_store)
    run_batch(sync_runner(), FakeStore(), generator, text="ikinci", negative="n2", variants=1,
              record=record, plan_store=plan_store)
    assert seen == ["n1", "n2"]
```

> `run_batch` yardımcısı (satır ~134) `negative` parametresi alacak şekilde genişletilir ve
> `Busy` artık `run_queue`'dan import edilir. `FakeGenerator`'a `fail_on` alanı zaten varsa
> kullanılır, yoksa eklenir: `generate` çağrısında prompt `fail_on` içindeyse `RuntimeError`.

- [ ] **Adım 2: Testleri koş, düştüğünü gör**

`cd queen-editor && pytest backend/tests/test_photo_usecases.py -q`
Beklenen: `ImportError` / `TypeError: make_job() missing 1 required positional argument`

- [ ] **Adım 3: Döngüyü yeniden yaz**

`domain/run_loop.py` tamamı:

```python
"""The loop the worker runs: take the next frame the queue owes, render it, write its line, repeat.

It holds no list of its own. Every turn asks the plan and the record again, and that is the whole
mechanism behind a live queue: frames appended while the loop runs are picked up on the next turn,
and a frame that settled meanwhile is simply never reached. One loop, so the rules about failures,
pauses and what "done" means exist in exactly one place.
"""
from backend.features.photo_generation.domain import policy, queue
from backend.features.photo_generation.domain.photo_name import file_name


def make_job(runner, store, record, plan_store, generator, now, project):
    """Returns the callable PhotoRunner.start expects: it drains this project's queue."""

    def snapshot():
        return plan_store.read(project)["frames"], record.statuses(project)

    def summary(status, **extra):
        frames, statuses = snapshot()
        return {"status": status, **queue.counts(frames, statuses), **extra}

    def job():
        consecutive = 0
        while True:
            if runner.stop_requested():
                return summary("paused")
            frames, statuses = snapshot()
            owed = queue.open_frames(frames, statuses)
            if not owed:
                return summary("done")
            frame = owed[0]
            name = file_name(frame["number"], frame["letter"])
            # pending is what the gallery draws as "bekliyor": the queue behind the frame being
            # rendered. failures names the tiles it draws red, each with its own Tekrar dene.
            runner.report({**queue.counts(frames, statuses), "current": frame,
                           "pending": [file_name(f["number"], f["letter"]) for f in owed[1:]]})
            try:
                data = generator.generate(frame["prompt"], frame["negative"], frame["seed"])
            except Exception as exc:
                if runner.stop_requested():
                    # The user's own pause killed this render -- that is not a failure. The frame
                    # writes no line, so it stays owed and is produced again on resume.
                    return summary("paused")
                record.mark(project, name, queue.FAILED, now(), error=str(exc))
                consecutive += 1
                # getattr, not isinstance: domain must not import the ComfyUI service.
                reason = policy.stop_reason(consecutive, getattr(exc, "infra", False))
                if reason:
                    return summary("error", error=f"{reason}\n{exc}")
                continue
            filename = store.save(project, frame["number"], frame["letter"], data)
            # Only after the photo exists: the line is what "this photo is here" means.
            record.append(project, {"file": filename, "status": queue.DONE,
                                    "prompt": frame["prompt"], "negative": frame["negative"],
                                    "seed": frame["seed"], "createdAt": now()})
            consecutive = 0

    return job
```

- [ ] **Adım 4: `run_queue`'yu yaz**

`domain/usecases/run_queue.py` (yeni):

```python
"""Put the worker on this project's queue, if it is free.

Changing the queue and running it are two separate acts, which is what lets a batch be submitted
while another one renders: the loop reads the plan again every turn, so "already running THIS
project" is not an error -- it is the normal case. Only another project's run is a refusal, because
there is one worker.
"""
from backend.features.photo_generation.domain.run_loop import make_job


class Busy(Exception):
    """Another project's generation holds the worker (message is user-facing)."""


def run_queue(runner, store, record, plan_store, generator, now, project):
    state = runner.status()
    if state.get("status") == "running":
        if state.get("project") == project:
            return                          # the live loop will reach the new frames by itself
        raise Busy("Zaten bir üretim sürüyor.")
    if not runner.start(project, make_job(runner, store, record, plan_store, generator, now,
                                          project)):
        # Lost the race against another request between status() and start().
        raise Busy("Zaten bir üretim sürüyor.")
```

- [ ] **Adım 5: `start_batch`'i güncelle**

`domain/usecases/start_batch.py` — `Busy` sınıfını **sil**, importları ve gövdeyi değiştir:

```python
from backend.features.photo_generation.domain.prompt_list import parse_prompts
from backend.features.photo_generation.domain.usecases.run_queue import Busy, run_queue  # noqa: F401

LETTERS = "abcdefghijklmnopqrstuvwxyz"
```

> `Busy` burada yeniden dışa veriliyor: bugün onu `start_batch`'ten import eden dört yer var
> (`resume_batch`, `retry_frame`, `cancel_generation`, `presentation/routes.py`) ve tek satırlık
> bu yeniden dışa verme, o dört dosyada gereksiz bir düzenleme turunu ortadan kaldırıyor.

`plan_frames` ve `start_batch` gövdeleri:

```python
def plan_frames(start, prompts, negative, variants, new_seed):
    """[{"number", "letter", "prompt", "negative", "seed"}] in prompt-major order: 0_a 0_b … 1_a.

    Number = prompt, letter = variant -- nova-3dcg's meaning, kept so a photo's name still says
    which prompt produced it.

    The negative rides on the frame rather than on the plan: a live queue holds batches submitted
    with different negatives, and a frame has to render with the one it was submitted under.

    Seeds are drawn here, when the frames are planned, rather than when a frame renders: the plan is
    what a resumed run reads back, so a frame has to produce the image it was planned to produce.
    """
    return [{"number": start + index, "letter": LETTERS[variant], "prompt": prompt,
             "negative": negative, "seed": new_seed()}
            for index, prompt in enumerate(prompts)
            for variant in range(variants)]


def start_batch(runner, store, record, plan_store, generator, new_seed, now,
                project, text, negative, variants):
    prompts = parse_prompts(text)          # raises InvalidPrompts
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= len(LETTERS):
        raise InvalidVariants(f"Varyant sayısı 1-{len(LETTERS)} arası bir tam sayı olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    frames = plan_frames(next_number(store, plan_store, record, project), prompts, negative,
                         variants, new_seed)
    # Appended before the worker is asked to run: a run that dies leaves behind what it meant to
    # make, and a loop already in flight finds the frames on its next turn.
    plan_store.append(project, frames)
    run_queue(runner, store, record, plan_store, generator, now, project)
```

`next_number` aynen kalır.

- [ ] **Adım 6: `resume_batch`'i güncelle**

`domain/usecases/resume_batch.py` tamamı:

```python
"""Put the worker back on a queue that still owes frames.

What is left is not kept anywhere of its own: it is the plan minus the frames the record has
settled. Two places holding "what remains" would be two chances to disagree, and both of these are
on Drive, so a resumed run needs nothing the dead session had to remember.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class NothingToResume(Exception):
    """The queue has no frame left to produce."""


def resume_batch(runner, store, record, plan_store, generator, now, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    frames = plan_store.read(project)["frames"]
    if not queue.open_frames(frames, record.statuses(project)):
        raise NothingToResume("Devam edilecek kare yok.")
    run_queue(runner, store, record, plan_store, generator, now, project)
```

- [ ] **Adım 7: `retry_frame`'i güncelle**

`domain/usecases/retry_frame.py` tamamı:

```python
"""Put a frame back in line -- the one whose tile is red.

Retrying does not re-plan anything: the frame is already in the plan with its prompt, negative and
seed, so putting it back in line is one line in the record. It renders in the plan's own order.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import file_name
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class FrameMissing(Exception):
    """The plan has no frame under that name."""


def retry_frame(runner, store, record, plan_store, generator, now, project, file):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    frames = plan_store.read(project)["frames"]
    if not any(file_name(f["number"], f["letter"]) == file for f in frames):
        raise FrameMissing(f"Bu kare planda yok: {file}")
    record.mark(project, file, queue.QUEUED, now())
    run_queue(runner, store, record, plan_store, generator, now, project)
```

- [ ] **Adım 8: `cancel_generation`'ı güncelle**

`domain/usecases/cancel_generation.py` tamamı:

```python
"""Throw away what is left of a paused queue.

The photos already produced are untouched -- clearing the queue ends what is owed, it does not undo
work. Every frame still owed gets a "removed" line, which is also what keeps its number dead: the
record counts every name it has ever seen, and a reused name would hand a browser holding the old
bytes under an immutable cache header the wrong image.

Refused while the queue flows, so the frame being rendered right now -- which has no line yet, and
therefore still reads as owed -- can never be marked removed underneath the worker.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import file_name
from backend.features.photo_generation.domain.usecases.start_batch import Busy, ProjectMissing


def cancel_generation(runner, store, record, plan_store, now, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    if runner.status().get("status") == "running":
        raise Busy("Üretim sürüyor — önce durdur.")
    frames = plan_store.read(project)["frames"]
    for frame in queue.open_frames(frames, record.statuses(project)):
        record.mark(project, file_name(frame["number"], frame["letter"]), queue.REMOVED, now())
    runner.reset()
```

- [ ] **Adım 9: `get_queue`'yu güncelle**

`domain/usecases/get_queue.py` tamamı:

```python
"""What the queue still owes and what blew up, read from Drive rather than from memory.

This is how a half-finished run survives a dead session: the plan and the record are both on Drive
and the queue is one minus the other -- the same rule the worker runs on, so the screen and the
worker can never disagree. Failures come from the same place, which is why a red frame is still red
after the server restarts.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import file_name
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def get_queue(record, store, plan_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    frames = plan_store.read(project)["frames"]
    statuses = record.statuses(project)
    return {"pending": [file_name(f["number"], f["letter"])
                        for f in queue.open_frames(frames, statuses)],
            "failed": queue.counts(frames, statuses)["failures"],
            "total": len(frames)}
```

- [ ] **Adım 10: Bağlamayı güncelle**

`backend/main.py` — `cancel_generation` artık kayıt ve saat alıyor:

```python
    cancel_generation=partial(cancel_generation, _photo_runner, _photo_store, _photo_record,
                              _plan_store,
                              lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
```

`start_batch`, `resume_batch` ve `retry_frame` bağlamaları **değişmiyor** (imzaları aynı kaldı).

- [ ] **Adım 11: Testleri koş**

`cd queen-editor && pytest -q` → yeşil.
Düşen eski testler şunlar ve şöyle güncellenir:
- `test_the_plan_is_written_before_the_first_frame_renders` → `plan_store.written` yerine
  `plan_store.appended` kontrolü.
- `test_busy_runner_is_rejected` → aynı proje artık reddedilmiyor; test **başka** proje çalışıyorken
  reddedildiğini doğrulayacak şekilde yeniden yazılır.
- `test_cancel_empties_the_queue_and_returns_to_idle` → plan boşalmıyor; açık karelerin `removed`
  satırı aldığı doğrulanır.
- `test_resume_only_produces_the_frames_the_record_is_missing` → `record` sahtesi artık
  `statuses` üzerinden konuşuyor.
- `test_a_rejected_batch_writes_no_plan` → `plan_store.appended == []`.

- [ ] **Adım 12: Commit (Görev 3 + Görev 4 birlikte)**

```bash
git add queen-editor/backend/features/photo_generation queen-editor/backend/main.py \
        queen-editor/backend/tests
git commit -m "feat(queen-editor): the queue stays open while a batch renders"
```

- [ ] **Adım 13: Push**

```bash
git push
```

---

## Kabul

`cd queen-editor && pytest -q` yeşil ve şu üç cümle testlerle kanıtlanmış:

1. Üretim sürerken atılan ikinci parti kesinti olmadan kuyruğun sonuna diziliyor
   (`test_frames_added_while_the_loop_runs_are_produced_in_the_same_run`).
2. Sunucu yeniden başladıktan sonra da kuyruk uç noktası patlamış kareyi bildiriyor
   (`test_the_queue_endpoint_reports_failures_after_a_restart`).
3. Silinen bir fotoğrafın karesi kuyruğa geri dönmüyor
   (`test_a_deleted_photo_does_not_come_back_as_pending`).

Arayüz değişmediği için `npm run build` **koşulmaz** ve `dist/` commit edilmez.

## Madde 8'e not

Bu madde "üretim sürerken Tekrar dene çalışmıyor" sapmasını yan etki olarak kapatıyor: `run_queue`
aynı projenin akan kuyruğunu reddetmediği için tekrar denenen kare artık 409 yemiyor. Madde 8'e
kalan tek parça, o karenin planın kendi sırasında değil **kuyruğun sonunda** üretilmesi.
