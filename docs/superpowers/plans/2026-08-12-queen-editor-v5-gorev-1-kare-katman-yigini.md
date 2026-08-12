# Görev 1 — Kare katman yığını olur · Uygulama planı

> **Ajan için:** bu plan **superpowers:executing-plans** ile görev görev uygulanır. Adımlar
> `- [ ]` kutularıyla izlenir.

**Amaç:** Kare, fotoğrafının dosya adı olmaktan çıkıp kendi kimliği ve üç katman yuvası (foto ·
video · ses) olan bir yığına dönüşür; hiçbir üretim var olan katmanı ezemez ve kareyi silmek bütün
katman dosyalarını götürür — paylaşılan dosya son sahibi gidene kadar diskte kalır.

**Mimari:** Günlük satırı `frame` + `layer` alanı kazanır ve katlama "dosya başına"dan "(kare,
katman) başına"ya geçer. Yuva kuralı saf bir alan modülünde (`domain/layers.py`) durur; kuyruk,
galeri, sıra ve silme onu okur. Yeni proje dosyası, yeni uç nokta ve arayüz değişikliği yok.

**Yığın:** Python 3 · Flask (sync) · pytest. Ön yüze dokunulmadığı için `npm` yok, `dist/`
üretilmez.

**Spec:** [Görev 1 — Kare katman yığını](../specs/2026-08-12-queen-editor-v5-gorev-1-kare-katman-yigini-design.md)
**Yol haritası:** [v5 Görev 1](2026-08-12-queen-editor-v5-roadmap.md)

## Genel kısıtlar

- **Full TDD.** Hiçbir üretim kodu satırı, önce kırmızı bir test yokken yazılmaz. Sıra hep aynı:
  başarısız test → koş, düştüğünü gör → en küçük kod → koş, geçtiğini gör.
- **Test komutu her yerde aynı, tam takım:** `python -m pytest queen-editor -q`
  (`queen-editor/pytest.ini` rootdir'i ve `pythonpath`'i veriyor).
- **Bağımlılık yönü:** `presentation → domain ← data → services`. `domain/layers.py` yalnız
  `domain/queue.py`'yi okur; `data/` domain'i okur, tersi olmaz.
- **Dil ayrımı:** yorum, docstring, **test adı** ve commit mesajı İngilizce; kullanıcının gördüğü
  metin Türkçe. Bu görevde kullanıcıya giden yeni metin yok.
- **Geriye uyum, migrasyon yok.** `frame`/`layer` alanı olmayan eski satır foto katmanı sayılır ve
  kimliği dosya adının uzantısız hâlidir; `.png` ile biten eski sıra girdisi kimliğe çevrilir.
- **Commit mesajlarında çift tırnak yok** (PowerShell here-string'i bölüyor).
- **v4'ün nöbetçi kuralı korunur:** silinen fotoğrafın karesi kuyruğa geri dönmez. Yuva kuralı
  kuyruk borcuna sızarsa bu test kırmızıya döner — sızmanın alarmı odur.

## Dosya haritası

| Dosya | Sorumluluğu | Durum |
|---|---|---|
| `domain/layers.py` | Katman sözlüğü, yuva doluluğu, "üret = ekle" kısıtı, paylaşılan dosya kuralı | **yeni** |
| `tests/test_layers.py` | Yukarıdakinin testleri | **yeni** |
| `domain/photo_name.py` | Kare kimliği ↔ dosya adı | değişir |
| `data/photo_record.py` | Satırın kare ve katman taşıması, `slots()` katlaması | değişir |
| `domain/queue.py` | Kuyruk borcunun kare kimliğiyle anahtarlanması | değişir |
| `domain/run_loop.py` · `usecases/retry_frame.py` · `usecases/cancel_generation.py` | Yazma çağrılarının yeni imzaya geçmesi | değişir |
| `usecases/list_frames.py` | `id` ve `layers` alanlarını yayınlaması | değişir |
| `domain/gallery_order.py` · `data/order_store.py` · `usecases/save_order.py` | Sıranın kare kimliği tutması | değişir |
| `usecases/remove_frames.py` | Bütün katmanları kapatması, paylaşılan dosyayı bırakması | değişir |
| `domain/ports.py` | `PhotoRecord` sözleşmesi | değişir |
| `tests/test_photo_record.py` · `test_frame_queue.py` · `test_gallery_order.py` · `test_order_store.py` · `test_photo_usecases.py` | Kimliğe geçen beklentiler ve yeni davranışlar | değişir |

Yollar `queen-editor/backend/features/photo_generation/` ve `queen-editor/backend/tests/` altında.

**Neden üç görev.** 1.1 ve 1.2 tek başlarına yeşile boyanabilen bağımsız birimler. 1.3 ise tek
parça: kayıt kimliğe geçtiği an kuyruk, galeri, sıra ve silme aynı anda geçmek zorunda — arada
yeşil bir nokta yok, dolayısıyla bölmek sahte bir sınır olurdu. 1.4 kabul kriterinin nöbetçisi.

---

## Görev 1.1 — Katman sözlüğü ve yuva kuralı

Saf alan modülü; hiçbir şeye bağlı değil, her şey ona bağlanacak.

**Dosyalar:**
- Oluştur: `queen-editor/backend/features/photo_generation/domain/layers.py`
- Test: `queen-editor/backend/tests/test_layers.py`

**Arayüz:**
- Üretir: `PHOTO` `VIDEO` `AUDIO` sabitleri · `is_taken(status) -> bool` ·
  `can_produce(slots, slot) -> bool` · `files_to_unlink(slots, closing) -> set`
- `slots` biçimi: `can_produce` için `{slot: status}` (tek kare), `files_to_unlink` için
  `{frame: {slot: {"status", "file"}}}` (bütün proje).
- Tüketir: `domain/queue.py`'nin durum sabitleri.

- [ ] **Adım 1: Başarısız testi yaz**

`queen-editor/backend/tests/test_layers.py`:

```python
from backend.features.photo_generation.domain import layers, queue


def test_an_empty_slot_can_be_produced_into():
    assert layers.can_produce({}, layers.VIDEO) is True


def test_a_produced_layer_cannot_be_overwritten():
    assert layers.can_produce({layers.VIDEO: queue.DONE}, layers.VIDEO) is False


def test_a_failed_layer_counts_as_present():
    # The user's call: a red layer stays out of the panel's scope and is rescued by Tekrar dene.
    assert layers.can_produce({layers.VIDEO: queue.FAILED}, layers.VIDEO) is False


def test_a_deleted_layer_frees_the_slot():
    assert layers.can_produce({layers.VIDEO: queue.DELETED}, layers.VIDEO) is True


def test_a_requeued_layer_frees_the_slot():
    assert layers.can_produce({layers.VIDEO: queue.QUEUED}, layers.VIDEO) is True


def test_audio_needs_a_video_under_it():
    assert layers.can_produce({}, layers.AUDIO) is False
    assert layers.can_produce({layers.VIDEO: queue.DONE}, layers.AUDIO) is True


def test_a_taken_audio_slot_is_refused_like_any_other():
    assert layers.can_produce({layers.VIDEO: queue.DONE,
                               layers.AUDIO: queue.DONE}, layers.AUDIO) is False


def test_a_photo_slot_needs_nothing_under_it():
    assert layers.can_produce({}, layers.PHOTO) is True
```

- [ ] **Adım 2: Testi koş, düştüğünü gör**

Koş: `python -m pytest queen-editor -q`
Beklenen: `ModuleNotFoundError: No module named 'backend.features.photo_generation.domain.layers'`

- [ ] **Adım 3: En küçük kodu yaz**

`queen-editor/backend/features/photo_generation/domain/layers.py`:

```python
"""A frame is a stack of layers: a photo, at most one video, at most one audio.

The unit is the slot, not the file. Two frames can point at one file -- a copy frame shares its
source's photo -- so "what happened to this layer" is a question about a (frame, slot) pair, and a
fold per file would answer it wrong the moment sharing starts.

Which slot may be produced into is the whole of "üret = ekle, sil = kaldır": production writes only
into a free slot, so nothing can ever be overwritten. Retry needs no rule of its own -- it writes a
"queued" line, and that frees the slot.

This is not the queue's question. Whether a slot is free says what MAY be asked for; what the queue
still owes is queue.is_open's answer and it did not change. A deleted photo frees its slot without
putting the frame back in line.
"""
from backend.features.photo_generation.domain import queue

PHOTO = "photo"
VIDEO = "video"
AUDIO = "audio"

# A slot is taken while its latest line says a layer is there -- produced or blown up. A failed
# layer counts as present deliberately: the frame stays out of the production panel's scope and is
# rescued by Tekrar dene alone, so one frame never gets two ways to be produced at once.
TAKEN = (queue.DONE, queue.FAILED)


def is_taken(status):
    """True while a layer occupies the slot."""
    return status in TAKEN


def can_produce(slots, slot):
    """slots: {slot name: status} for ONE frame. May a new layer be written into `slot`?"""
    if is_taken(slots.get(slot)):
        return False
    if slot == AUDIO:
        # Audio is mixed over a video, so a frame without one has nowhere to put it.
        return is_taken(slots.get(VIDEO))
    return True


def files_to_unlink(slots, closing):
    """Which files stop being pointed at once `closing` is closed.

    slots: {frame: {slot: {"status", "file"}}} for the whole project.
    closing: {(frame, slot)} -- the slots a deletion is about to close.

    Answered before a single line is written: the disk is touched first, so a failed unlink leaves
    the record untouched. A file another frame still holds is left where it is.
    """
    going, staying = set(), set()
    for frame, frame_slots in slots.items():
        for slot, cell in frame_slots.items():
            if not is_taken(cell["status"]):
                continue
            if (frame, slot) in closing:
                going.add(cell["file"])
            else:
                staying.add(cell["file"])
    return going - staying
```

- [ ] **Adım 4: Testi koş, geçtiğini gör**

Koş: `python -m pytest queen-editor -q` → hepsi yeşil.

- [ ] **Adım 5: Paylaşılan dosya testlerini yaz**

`test_layers.py`'ye ekle:

```python
def cell(file, status=queue.DONE):
    return {"status": status, "file": file}


def test_a_closed_slots_file_is_unlinked():
    slots = {"12_a": {layers.PHOTO: cell("12_a.png")}}
    assert layers.files_to_unlink(slots, {("12_a", layers.PHOTO)}) == {"12_a.png"}


def test_a_file_another_frame_still_holds_stays():
    # An audio variant shares its source's video (design v3, madde 102).
    slots = {"12_a": {layers.PHOTO: cell("12_a.png"), layers.VIDEO: cell("shared.mp4")},
             "13_a": {layers.PHOTO: cell("13_a.png"), layers.VIDEO: cell("shared.mp4")}}
    closing = {("12_a", layers.PHOTO), ("12_a", layers.VIDEO)}
    assert layers.files_to_unlink(slots, closing) == {"12_a.png"}


def test_the_last_holder_takes_the_shared_file_with_it():
    slots = {"12_a": {layers.VIDEO: cell("shared.mp4")},
             "13_a": {layers.VIDEO: cell("shared.mp4")}}
    closing = {("12_a", layers.VIDEO), ("13_a", layers.VIDEO)}
    assert layers.files_to_unlink(slots, closing) == {"shared.mp4"}


def test_an_empty_slot_unlinks_nothing():
    # A frame pulled out of the queue never had a file, so closing it deletes nothing.
    slots = {"12_a": {layers.PHOTO: cell("12_a.png", queue.REMOVED)}}
    assert layers.files_to_unlink(slots, {("12_a", layers.PHOTO)}) == set()


def test_closing_nothing_unlinks_nothing():
    slots = {"12_a": {layers.PHOTO: cell("12_a.png")}}
    assert layers.files_to_unlink(slots, set()) == set()
```

- [ ] **Adım 6: Koş ve commit**

Koş: `python -m pytest queen-editor -q` → yeşil.

```bash
git add queen-editor/backend/features/photo_generation/domain/layers.py queen-editor/backend/tests/test_layers.py
git commit -m 'feat(queen-editor): layer slots decide what may be produced'
```

---

## Görev 1.2 — Kare kimliği

Dosya adı ile kimliği ayıran iki küçük işlev. Ayrı görev, çünkü bundan sonraki her şey ikisini de
çağırıyor.

**Dosyalar:**
- Değiştir: `queen-editor/backend/features/photo_generation/domain/photo_name.py`
- Test: `queen-editor/backend/tests/test_photo_name.py`

**Arayüz:**
- Üretir: `frame_id(number, letter) -> str` · `frame_id_of(name) -> str`; `file_name` ve
  `number_of` davranışları aynen kalır.

- [ ] **Adım 1: Başarısız testi yaz**

`test_photo_name.py`'nin import satırını genişlet ve testleri ekle:

```python
from backend.features.photo_generation.domain.photo_name import (
    file_name,
    frame_id,
    frame_id_of,
    number_of,
)
```

```python
def test_a_frames_identity_is_its_number_and_letter():
    assert frame_id(12, "a") == "12_a"


def test_a_photo_file_name_yields_its_frames_identity():
    assert frame_id_of("12_a.png") == "12_a"


def test_a_name_that_is_already_an_identity_comes_back_unchanged():
    # Order files written after this change store identities; both shapes have to read.
    assert frame_id_of("12_a") == "12_a"


def test_a_file_name_is_its_identity_plus_the_extension():
    assert file_name(12, "a") == f"{frame_id(12, 'a')}.png"
```

- [ ] **Adım 2: Testi koş, düştüğünü gör**

Koş: `python -m pytest queen-editor -q`
Beklenen: `ImportError: cannot import name 'frame_id'`

- [ ] **Adım 3: Kodu yaz**

`photo_name.py`'yi bütünüyle şu hâle getir:

```python
"""How a frame is identified and how its photo file is named.

The two are not the same thing, and this is the file that keeps them apart. The identity says which
frame; the name says which file. A photo file can belong to more than one frame -- a copy frame
shares its source's picture -- and one frame can own three files, so a name can never stand in for
an identity.

The identity is given at birth and never rewritten: gallery order, the detail page's address and
the selection all point at it, and an identity that grew as layers arrived would break every one of
them the first time a video landed.
"""


def frame_id(number, letter):
    """The frame's identity: number = prompt, letter = variant."""
    return f"{number}_{letter}"


def frame_id_of(name):
    """"12_a.png" -> "12_a"; a name that already is an identity comes back unchanged."""
    return name[: -len(".png")] if name.endswith(".png") else name


def file_name(number, letter):
    """The name a frame's photo is stored under."""
    return f"{frame_id(number, letter)}.png"


def number_of(filename):
    """"12_a.png" -> 12; anything that does not fit the scheme -> None."""
    if not filename.endswith(".png"):
        return None
    number, _, letter = filename[: -len(".png")].partition("_")
    if not number.isdigit() or len(letter) != 1 or not letter.isalpha():
        return None
    return int(number)
```

- [ ] **Adım 4: Koş ve commit**

Koş: `python -m pytest queen-editor -q` → yeşil.

```bash
git add queen-editor/backend/features/photo_generation/domain/photo_name.py queen-editor/backend/tests/test_photo_name.py
git commit -m 'feat(queen-editor): a frame identity is not a file name'
```

---

## Görev 1.3 — Kayıt, kuyruk, galeri, sıra ve silme kimliğe geçer

Tek atomik geçiş: kayıt kimliğe geçtiği an onu okuyan her yer aynı anda geçmek zorunda. Adımlar
alan alan ilerler ama yeşil nokta yalnız sonda.

**Dosyalar:**
- Değiştir: `data/photo_record.py` · `domain/ports.py` · `domain/queue.py` · `domain/run_loop.py` ·
  `usecases/retry_frame.py` · `usecases/cancel_generation.py` · `usecases/list_frames.py` ·
  `domain/gallery_order.py` · `data/order_store.py` · `usecases/save_order.py` ·
  `usecases/remove_frames.py`
- Test: `tests/test_photo_record.py` · `test_frame_queue.py` · `test_gallery_order.py` ·
  `test_order_store.py` · `test_photo_usecases.py`

**Arayüz:**
- Üretir: `record.slots(project) -> {frame: {slot: {"status", "file"}}}` ·
  `record.mark(project, frame, layer, file, status, at, error=None)` ·
  `record.statuses(project) -> {frame: photo slot status}` ·
  `list_frames` çıktısında `id` ve `layers` alanları · `order_store.read` kimlik listesi.
- Tüketir: `layers.*`, `photo_name.frame_id`, `photo_name.frame_id_of`.
- Değişmeyen: `queue.counts()["failures"]` **dosya adı** döndürür; `list_frames` çıktısındaki
  `file` alanı durur; `remove_frames` isteği ve cevabı dosya adı taşır. Arayüz dokunulmadan çalışır.

### Kayıt

- [ ] **Adım 1: Kayıt testlerini yaz**

`test_photo_record.py`'de var olan `mark` çağrılarını yeni imzaya çevir —
`record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "t3")` biçiminde — ve `statuses`
beklentilerini kimliğe çevir (`{"0_a": "deleted", "1_a": "failed"}`). Sonra ekle:

```python
def test_a_video_line_does_not_answer_for_its_frames_photo(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {**entry("0_a.png"), "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "failed"})

    # The photo is still there; only the video blew up.
    assert record.statuses("düğün") == {"0_a": "done"}


def test_slots_fold_the_latest_line_per_frame_and_layer(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {**entry("0_a.png"), "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_v0.mp4", "deleted", "t3")

    assert record.slots("düğün") == {
        "0_a": {"photo": {"status": "done", "file": "0_a.png"},
                "video": {"status": "deleted", "file": "0_a_v0.mp4"}}}


def test_two_frames_over_one_file_close_independently(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo",
                            "status": "done"})
    record.append("düğün", {"file": "0_a.png", "frame": "0_a_c1", "layer": "photo",
                            "status": "done"})
    record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "t3")

    slots = record.slots("düğün")
    assert slots["0_a"]["photo"]["status"] == "deleted"
    assert slots["0_a_c1"]["photo"]["status"] == "done"


def test_lines_without_a_frame_or_layer_are_photos_of_their_own_frame(tmp_path):
    # What the projects already on Drive look like: no frame field, no layer field.
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))

    assert record.slots("düğün") == {"0_a": {"photo": {"status": "done", "file": "0_a.png"}}}


def test_the_photo_list_follows_the_frame_not_the_file(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo",
                            "status": "done"})
    record.append("düğün", {"file": "0_a.png", "frame": "0_a_c1", "layer": "photo",
                            "status": "done"})
    record.mark("düğün", "0_a", "photo", "0_a.png", "deleted", "t3")

    # One frame let go of the picture; the other still shows it.
    assert [row["frame"] for row in record.list("düğün")] == ["0_a_c1"]


def test_a_video_line_is_not_a_photo(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", {**entry("0_a.png"), "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    assert [row["file"] for row in record.list("düğün")] == ["0_a.png"]
```

- [ ] **Adım 2: Koş, düştüğünü gör**

Koş: `python -m pytest queen-editor -q`
Beklenen: `AttributeError: 'DrivePhotoRecord' object has no attribute 'slots'` ve `mark`
çağrılarında `TypeError`.

- [ ] **Adım 3: Kaydı yaz**

`data/photo_record.py`'nin başını şu hâle getir:

```python
"""PhotoRecord over DriveStorage -- the only place that knows the record file's name and shape.

This is the log of what happened to every layer of every planned frame: one JSON object per line,
appended right after the event itself, never rewritten. Append-only is the point -- a session that
dies mid-write loses at most the line it was adding, where rewriting the whole file could lose every
earlier one. So a photo landing, a video landing, a deletion, a failed render and a frame pulled out
of the queue are all lines; reading folds them per (frame, layer) and the latest line wins.

Folded per pair rather than per file because a file can be shared: closing one frame's photo must
not close the copy frame that points at the same picture.
"""
import json

from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.photo_name import frame_id_of, number_of

FILE = "photos.jsonl"


def _status_of(row):
    """A row's status, including rows written before the field existed.

    Those older rows are exactly two kinds: a photo landing (prompt + createdAt) and a deletion
    (deletedAt). Nothing needs migrating -- the projects already on Drive keep reading.
    """
    status = row.get("status")
    if isinstance(status, str):
        return status
    return queue.DELETED if row.get("deletedAt") else queue.DONE


def _frame_of(row):
    """Which frame the row is about.

    Rows written before frames had identities are one photo each, so the file name without its
    extension is the frame they belong to -- exactly the shape frame_id gives new frames.
    """
    frame = row.get("frame")
    if isinstance(frame, str):
        return frame
    return frame_id_of(row["file"])


def _layer_of(row):
    """Which slot the row is about; a row from before layers existed can only be a photo."""
    layer = row.get("layer")
    return layer if isinstance(layer, str) else layers.PHOTO
```

Sınıfta `mark`, `statuses` ve `list`'i değiştir, `slots`'u ekle; `append`, `_rows` ve `max_number`
dokunulmadan kalır:

```python
    def mark(self, project, frame, layer, file, status, at, error=None):
        """Write down an event that produced no layer: a failure, a deletion, a frame pulled out of
        the queue, or a slot put back in line."""
        entry = {"frame": frame, "layer": layer, "file": file, "status": status, "at": at}
        if error is not None:
            # The server's own words, verbatim -- never a guessed cause.
            entry["error"] = error
        self.append(project, entry)

    def slots(self, project):
        """{frame: {slot: {"status", "file"}}} -- the latest line per (frame, slot) wins."""
        folded = {}
        for row in self._rows(project):
            folded.setdefault(_frame_of(row), {})[_layer_of(row)] = {
                "status": _status_of(row), "file": row["file"]}
        return folded

    def statuses(self, project):
        """{frame: photo slot status} -- what the queue reads.

        Only the photo slot: the queue owes photos, and a video line must never answer for the frame
        it hangs on.
        """
        return {frame: cells[layers.PHOTO]["status"]
                for frame, cells in self.slots(project).items() if layers.PHOTO in cells}

    def list(self, project):
        """Every photo that still exists, newest first -- one row per frame, not per file."""
        live = {}
        for row in self._rows(project):
            if _layer_of(row) != layers.PHOTO:
                continue
            frame = _frame_of(row)
            if _status_of(row) == queue.DONE:
                live[frame] = {**row, "frame": frame}
            else:
                live.pop(frame, None)
        return list(reversed(list(live.values())))
```

`domain/ports.py`'de `PhotoRecord`'u eşle:

```python
class PhotoRecord(Protocol):
    def append(self, project: str, entry: dict) -> None:
        """Add one produced layer's row."""
        ...

    def list(self, project: str) -> list:
        """Every photo that still exists, newest first."""
        ...

    def mark(self, project: str, frame: str, layer: str, file: str, status: str, at: str,
             error: str | None = None) -> None:
        """Append a line for an event that produced no layer."""
        ...

    def slots(self, project: str) -> dict:
        """{frame: {slot: {"status", "file"}}} -- the latest line per (frame, slot)."""
        ...

    def statuses(self, project: str) -> dict:
        """{frame: photo slot status} for every frame the log has seen."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the record has ever seen, whatever became of the frame."""
        ...
```

`tests/test_photo_usecases.py`'deki `FakeRecord`'u gerçeğiyle aynı katlamaya geçir (var olan
`append` çağrıları geriye uyum sayesinde olduğu gibi çalışmaya devam eder):

```python
class FakeRecord:
    """Folds the log the way DrivePhotoRecord does: the latest line per (frame, layer) wins."""

    def __init__(self):
        self.rows = []

    def append(self, project, entry):
        self.rows.append(entry)

    def mark(self, project, frame, layer, file, status, at, error=None):
        entry = {"frame": frame, "layer": layer, "file": file, "status": status, "at": at}
        if error is not None:
            entry["error"] = error
        self.rows.append(entry)

    def _frame_of(self, row):
        return row.get("frame") or frame_id_of(row["file"])

    def _layer_of(self, row):
        return row.get("layer", "photo")

    def slots(self, project):
        folded = {}
        for row in self.rows:
            folded.setdefault(self._frame_of(row), {})[self._layer_of(row)] = {
                "status": row.get("status", "done"), "file": row["file"]}
        return folded

    def statuses(self, project):
        return {frame: cells["photo"]["status"]
                for frame, cells in self.slots(project).items() if "photo" in cells}

    def list(self, project):
        live = {}
        for row in self.rows:
            if self._layer_of(row) != "photo":
                continue
            frame = self._frame_of(row)
            if row.get("status", "done") == "done":
                live[frame] = {**row, "frame": frame}
            else:
                live.pop(frame, None)
        return list(reversed(list(live.values())))
```

`FakeRecord`'un `max_number` gibi var olan öteki üyeleri dokunulmadan kalır; dosyanın import
satırına `frame_id_of` eklenir.

Aynı dosyadaki `FakeOrderStore` de gerçeğinin geriye uyumunu taşımalı, yoksa `.png` yazılmış eski
sıralarla kurulan testler kimlik filtresinden geçemez:

```python
class FakeOrderStore:
    """Mirrors DriveOrderStore: what is stored reads back as frame identities."""

    def __init__(self, order=()):
        self.order = list(order)

    def read(self, project):
        return [frame_id_of(name) for name in self.order]

    def write(self, project, order):
        self.order = list(order)
```

### Kuyruk

- [ ] **Adım 4: Kuyruk testlerini yaz**

`test_frame_queue.py`'deki `statuses` sözlüklerinin anahtarlarını `"0_a.png"` → `"0_a"` çevir ve
ekle:

```python
def test_the_queue_reads_statuses_by_frame_identity():
    frames = [{"number": 0, "letter": "a"}, {"number": 1, "letter": "a"}]
    assert [f["number"] for f in queue.open_frames(frames, {"0_a": queue.DONE})] == [1]


def test_failures_are_reported_as_file_names():
    # The screen marks red tiles by file name; the fold is keyed by identity.
    frames = [{"number": 3, "letter": "b"}]
    assert queue.counts(frames, {"3_b": queue.FAILED})["failures"] == ["3_b.png"]
```

- [ ] **Adım 5: Kuyruğu yaz**

`domain/queue.py`: import satırını `from ...photo_name import file_name, frame_id` yap, `_name`
yerine `_key` koy ve üç işlevde onu kullan:

```python
def _key(frame):
    """A frame is looked up by identity, never by file name: a file can belong to two frames."""
    return frame_id(frame["number"], frame["letter"])


def open_frames(frames, statuses):
    """The plan frames still owed: the untouched ones in plan order, then the ones put back in line.

    Tekrar dene must not jump the queue (design v2, G10). A frame the user sent back has already had
    its turn, so it waits behind everything that has not had one; among themselves the re-queued
    frames keep plan order, which is all the design asks for. Where a frame sits in the GALLERY does
    not change -- that is Madde 5's rule, and this is only the order it is rendered in.
    """
    fresh = [f for f in frames if statuses.get(_key(f)) is None]
    requeued = [f for f in frames if statuses.get(_key(f)) == QUEUED]
    return fresh + requeued


def counts(frames, statuses):
    """The numbers the status endpoint publishes -- read from disk rather than from a run's memory,
    so they are still right after the server restarts.

    Looked up by identity, published as file names: the screen marks its red tiles by file.
    """
    failures = [file_name(f["number"], f["letter"]) for f in frames
                if statuses.get(_key(f)) == FAILED]
    return {"total": len(frames),
            "done": sum(1 for f in frames if statuses.get(_key(f)) == DONE),
            "failed": len(failures),
            "failures": failures}
```

`next_frame` değişmez (zaten `open_frames`'i çağırıyor).

`domain/run_loop.py`: import satırına `layers` ve `frame_id` ekle; döngüde kimliği hesapla ve iki
yazma çağrısını çevir:

```python
            frame = owed[0]
            fid = frame_id(frame["number"], frame["letter"])
            name = file_name(frame["number"], frame["letter"])
```

```python
                    record.mark(project, fid, layers.PHOTO, name, queue.FAILED, now(),
                                error=str(exc))
```

```python
            record.append(project, {"file": filename, "frame": fid, "layer": layers.PHOTO,
                                    "status": queue.DONE,
                                    "prompt": frame["prompt"], "negative": frame["negative"],
                                    "seed": frame["seed"], "createdAt": now()})
```

`usecases/cancel_generation.py`: döngüyü kimlikle yaz (import'a `layers`, `frame_id` eklenir):

```python
    for frame in queue.open_frames(frames, record.statuses(project)):
        record.mark(project, frame_id(frame["number"], frame["letter"]), layers.PHOTO,
                    file_name(frame["number"], frame["letter"]), queue.REMOVED, now())
```

`usecases/retry_frame.py`: planda kareyi bul, kimliğiyle işaretle (import'a `layers`, `frame_id`):

```python
    frames = plan_store.read(project)["frames"]
    target = next((f for f in frames if file_name(f["number"], f["letter"]) == file), None)
    if target is None:
        raise FrameMissing(f"Bu kare planda yok: {file}")
    record.mark(project, frame_id(target["number"], target["letter"]), layers.PHOTO, file,
                queue.QUEUED, now())
```

### Galeri

- [ ] **Adım 6: Galeri testlerini yaz**

`test_photo_usecases.py`'ye ekle:

```python
def test_every_frame_carries_its_identity():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done", "prompt": "ilk"})
    plan_store = planned((0, "a", "ilk"), (1, "a", "ikinci"))

    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert [f["id"] for f in frames] == ["1_a", "0_a"]


def test_a_frames_taken_layers_are_published():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    plan_store = planned((0, "a", "ilk"))

    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert frames[0]["layers"] == {"photo": "0_a.png", "video": "0_a_v0.mp4"}


def test_an_emptied_slot_names_no_file_and_keeps_the_frame():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_v0.mp4", "deleted", "t3")
    plan_store = planned((0, "a", "ilk"))

    frames = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    # Video and audio change how a frame looks, never whether it is here.
    assert [f["id"] for f in frames] == ["0_a"]
    assert frames[0]["layers"] == {"photo": "0_a.png"}


def test_a_pending_frame_has_no_layers_yet():
    frames = list_frames(FakeRecord(), FakeStore(), planned((0, "a", "ilk")),
                         FakeOrderStore(), "düğün")

    assert frames[0]["layers"] == {} and frames[0]["status"] == "pending"
```

- [ ] **Adım 7: Galeriyi yaz**

`usecases/list_frames.py`'yi şu hâle getir:

```python
"""The gallery: every frame that has a place in it, in the order it is shown, top first.

One answer, not two. The plan says what was asked for and the record says what became of it; putting
those together here is what lets the gallery be a single sequence instead of four buckets, and it is
why a frame turns into a photo without moving.

"running" is not among the statuses: a frame being rendered has no line on disk (a dead process must
not leave one behind), so the screen learns it from the live worker and draws the pending frame it
already has in place.

Only the photo slot decides whether a frame is here at all. Nothing deletes a photo on its own --
the photo is the base layer, so deleting it is deleting the frame -- while video and audio change
how a frame looks, never whether it exists.
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.gallery_order import apply_order
from backend.features.photo_generation.domain.photo_name import file_name, frame_id
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing

# What the gallery draws. A removed or deleted frame is gone from it entirely.
SHOWN = (queue.DONE, queue.FAILED)


def _taken_files(cells):
    """The files a frame really has right now -- an emptied slot names nothing."""
    return {slot: cell["file"] for slot, cell in cells.items()
            if layers.is_taken(cell["status"])}


def list_frames(record, store, plan_store, order_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    slots = record.slots(project)
    photos = {row["frame"]: row for row in record.list(project)}

    frames = []
    seen = set()
    # Newest first, the same direction the record answers in, so an unordered gallery already reads
    # the way the design wants it.
    for frame in reversed(plan_store.read(project)["frames"]):
        fid = frame_id(frame["number"], frame["letter"])
        cells = slots.get(fid, {})
        photo = cells.get(layers.PHOTO)
        status = photo["status"] if photo else None
        if status is not None and status not in SHOWN and not queue.is_open(status):
            continue                    # removed or deleted: it has no place in the gallery
        seen.add(fid)
        # The photo slot's own file when it has one -- a copy frame's picture is its source's, not
        # the name its own number would give. A frame with nothing produced yet is drawn under the
        # name it is planned to take.
        frames.append({**frame, "id": fid,
                       "file": photo["file"] if photo else file_name(frame["number"],
                                                                     frame["letter"]),
                       "layers": _taken_files(cells),
                       "status": status if status in SHOWN else "pending"})

    # Photos the plan no longer knows about: projects generated before the plan became permanent
    # kept only their last batch, and those photos are still the gallery's.
    for fid, row in photos.items():
        if fid not in seen:
            frames.append({**row, "id": fid, "layers": _taken_files(slots.get(fid, {})),
                           "status": queue.DONE})

    return apply_order(frames, order_store.read(project))
```

### Sıra

- [ ] **Adım 8: Sıra testlerini yaz**

`test_gallery_order.py`'yi kimliğe çevir — yardımcılar ve beklentiler:

```python
def rows(*ids):
    return [{"id": i, "prompt": "p"} for i in ids]


def ids(result):
    return [row["id"] for row in result]


def test_an_unordered_record_keeps_its_own_sequence():
    assert ids(apply_order(rows("2_a", "1_a"), [])) == ["2_a", "1_a"]


def test_a_stored_order_is_applied():
    assert ids(apply_order(rows("2_a", "1_a", "0_a"), ["0_a", "2_a", "1_a"])) == \
        ["0_a", "2_a", "1_a"]


def test_frames_the_order_never_heard_of_go_on_top():
    # The record is newest-first, so 4_a is newer than 3_a and stays above it.
    assert ids(apply_order(rows("4_a", "3_a", "1_a", "0_a"), ["0_a", "1_a"])) == \
        ["4_a", "3_a", "0_a", "1_a"]


def test_a_name_the_record_does_not_know_is_ignored():
    assert ids(apply_order(rows("1_a"), ["silinmis", "1_a"])) == ["1_a"]


def test_a_repeated_name_is_placed_once():
    assert ids(apply_order(rows("1_a", "0_a"), ["1_a", "1_a", "0_a"])) == ["1_a", "0_a"]


def test_an_empty_record_returns_empty():
    assert apply_order([], ["1_a"]) == []
```

`test_order_store.py`'de var olan `test_yazilan_sira_geri_okunur`'u kimlikle yaz
(`store.write("düğün", ["1_a", "0_a"])` → aynısı geri okunur) ve ekle:

```python
def test_an_order_written_before_identities_reads_as_identities():
    # Every project on Drive holds photo names in this file.
    store = DriveOrderStore(FakeStorage({("düğün", FILE): '{"order": ["1_a.png", "0_a.png"]}'}))

    assert store.read("düğün") == ["1_a", "0_a"]
```

`save_order`'ın var olan testleri de kimliğe çevrilir: istek dosya adı göndermeye devam eder ama
kaydedilen ve geri dönen liste kimliktir (`["1_a.png", "0_a.png"]` gönder → `["1_a", "0_a"]` dön).

- [ ] **Adım 9: Sırayı yaz**

`domain/gallery_order.py`:

```python
"""The gallery's order: the record says what exists, the order file says in what sequence.

Kept as a pure function so the rule is testable without Drive: it can neither invent a frame nor
hide one -- whatever the order file says, the result is always exactly the record's own set.

Keyed by frame identity, not by file name: two frames can share one picture, and a list of file
names could not say which of them it meant.
"""


def apply_order(rows, order):
    """rows: frames, newest first. order: stored frame identities. Returns them in gallery order."""
    by_id = {row["id"]: row for row in rows}
    ordered = []
    seen = set()
    for fid in order:
        row = by_id.get(fid)
        if row is not None and fid not in seen:
            seen.add(fid)
            ordered.append(row)
    # A frame the order file has never heard of is new: it belongs on top, and among themselves
    # those keep the record's own newest-first sequence.
    fresh = [row for row in rows if row["id"] not in seen]
    return fresh + ordered
```

`data/order_store.py`: import ekle ve `read`'in son satırını çevir.

```python
from backend.features.photo_generation.domain.photo_name import frame_id_of
```

```python
        # Files written before frames had identities hold photo names; both shapes read.
        return [frame_id_of(name) for name in order if isinstance(name, str)]
```

`usecases/save_order.py`: bilinen kümeyi kimlikten oku, **gelen adları kimliğe çevir** — arayüz
hâlâ dosya adı gönderiyor, spec gereği ona dokunulmuyor — ve docstring'ine bunu yaz.

```python
from backend.features.photo_generation.domain.photo_name import frame_id_of
```

```python
    known = {frame["id"] for frame in list_frames(record, store, plan_store, order_store, project)}
    cleaned = []
    seen = set()
    for name in order:
        # The screen still drags file names around; what is stored is the frame's identity.
        fid = frame_id_of(name)
        if fid in known and fid not in seen:
            seen.add(fid)
            cleaned.append(fid)
    order_store.write(project, cleaned)
    return cleaned
```

### Silme

- [ ] **Adım 10: Silme testlerini yaz**

`test_photo_usecases.py`'ye ekle; var olan silme testleri (`test_a_photo_leaves_the_disk_and_the_log_says_so`,
`test_a_frame_that_was_never_produced_only_leaves_the_queue`,
`test_a_failed_frame_leaves_the_gallery_the_same_way`, `test_a_frame_pulled_out_never_gets_its_number_back`)
**dokunulmadan geçmeye devam etmeli** — sıra dosyası beklentisi kimliğe çevrilir
(`assert order.order == ["1_a"]`).

```python
def test_deleting_a_frame_takes_all_of_its_layer_files():
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    record.append("düğün", {"file": "0_a_v0_s0.wav", "frame": "0_a", "layer": "audio",
                            "status": "done"})
    plan_store = planned((0, "a", "a"))

    result = remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün",
                           ["0_a.png"])

    assert result == {"deleted": ["0_a.png"], "removed": []}
    assert sorted(store.deleted) == ["0_a.png", "0_a_v0.mp4", "0_a_v0_s0.wav"]
    assert list_frames(record, store, plan_store, FakeOrderStore(), "düğün") == []


def test_a_file_another_frame_still_holds_is_left_on_disk():
    store, record = FakeStore(), FakeRecord()
    # An audio variant shares its source's video (design v3, madde 102).
    for fid in ("0_a", "1_a"):
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        record.append("düğün", {"file": "0_a_v0.mp4", "frame": fid, "layer": "video",
                                "status": "done"})
    plan_store = planned((0, "a", "a"), (1, "a", "b"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a.png"])

    # Its own picture goes; the video the other frame still plays stays.
    assert store.deleted == ["0_a.png"]


def test_the_last_holder_takes_the_shared_file_with_it():
    store, record = FakeStore(), FakeRecord()
    for fid in ("0_a", "1_a"):
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        record.append("düğün", {"file": "0_a_v0.mp4", "frame": fid, "layer": "video",
                                "status": "done"})
    plan_store = planned((0, "a", "a"), (1, "a", "b"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün",
                  ["0_a.png", "1_a.png"])

    assert sorted(store.deleted) == ["0_a.png", "0_a_v0.mp4", "1_a.png"]


def test_deleting_a_frame_whose_video_failed_unlinks_what_is_there():
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.mark("düğün", "0_a", "video", "0_a_v0.mp4", "failed", "t2", error="ComfyUI 500")
    plan_store = planned((0, "a", "a"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a.png"])

    # A failed layer holds its planned name; unlinking a file that never landed is not an error.
    assert sorted(store.deleted) == ["0_a.png", "0_a_v0.mp4"]
```

- [ ] **Adım 11: Silmeyi yaz**

`usecases/remove_frames.py`'yi şu hâle getir:

```python
"""Take frames out of the gallery -- whatever they are.

One use case for one frame and for many, and for photos and pending frames alike: the confirm box
is a single window over a mixed selection, so the request behind it is a single call. What each name
costs is decided here, from its own state:

  produced  -> every layer it owns leaves the disk and the log says deleted
  not yet   -> nothing to delete; the log says removed and the queue skips it

Which files really go is decided before a single line is written: a picture two frames share stays
where it is until the last of them lets go (design v3, madde 101). The disk is touched first, so a
failed unlink leaves the record untouched and the error is the whole truth; then the log is appended
to (never rewritten -- see data/photo_record.py). The order file is written once at the end rather
than per frame: it is a single small document, and one write is one chance to be interrupted
instead of N.

A name the gallery does not know is skipped, not refused. The confirm box can sit open while another
tab removes the same frame, and refusing the whole batch over one that is already gone would leave
the rest standing against the user's own decision. The answer says what really happened.

The frame being rendered needs no guard: it writes its own line when it lands, and the latest line
about a slot wins, so a removal that raced it is undone by the photo itself.
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


class InvalidFiles(Exception):
    """The body was not a list of file names."""


def remove_frames(record, store, plan_store, order_store, now, project, files):
    if not isinstance(files, list) or any(not isinstance(name, str) for name in files):
        raise InvalidFiles("Silinecek dosya listesi metin dizisi olmalı.")
    # Raises ProjectMissing when there is no such project.
    gallery = {frame["file"]: frame
               for frame in list_frames(record, store, plan_store, order_store, project)}
    slots = record.slots(project)

    # The whole deletion is decided first: which slots close, and which files that leaves unheld.
    deleted, removed, closing = [], [], set()
    for name in files:
        frame = gallery.get(name)
        if frame is None:
            continue
        if frame["status"] == queue.DONE:
            cells = slots.get(frame["id"], {})
            closing |= {(frame["id"], slot) for slot, cell in cells.items()
                        if layers.is_taken(cell["status"])}
            deleted.append(name)
        else:
            removed.append(name)

    for file in sorted(layers.files_to_unlink(slots, closing)):
        store.delete(project, file)
    for fid, slot in sorted(closing):
        record.mark(project, fid, slot, slots[fid][slot]["file"], queue.DELETED, now())
    for name in removed:
        record.mark(project, gallery[name]["id"], layers.PHOTO, name, queue.REMOVED, now())

    gone = {gallery[name]["id"] for name in deleted + removed}
    if gone:
        order_store.write(project, [fid for fid in order_store.read(project) if fid not in gone])
    return {"deleted": deleted, "removed": removed}
```

- [ ] **Adım 12: Tam takımı koş**

Koş: `python -m pytest queen-editor -q`
Beklenen: **hepsi yeşil.** Kırmızı kalan varsa kaynağı bul ve düzelt; testi gevşetme.

- [ ] **Adım 13: Commit**

```bash
git add queen-editor/backend
git commit -m 'feat(queen-editor): a frame is a stack of layers, not a photo'
```

---

## Görev 1.4 — Kabul kriterinin nöbetçileri

Spec'in iki cümlesini doğrudan kanıtlayan testler; adları cümlenin kendisi olsun ki bir daha
bozulduklarında ne kaybedildiği okunsun.

**Dosyalar:**
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

- [ ] **Adım 1: Testleri yaz**

```python
def test_a_frame_that_has_a_video_cannot_take_a_second_one():
    # Acceptance 1: production writes into a free slot or not at all.
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    cells = record.slots("düğün")["0_a"]
    assert layers.can_produce({slot: cell["status"] for slot, cell in cells.items()},
                              layers.VIDEO) is False


def test_deleting_a_frame_leaves_none_of_its_layer_files_behind():
    # Acceptance 2, first half.
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    record.append("düğün", {"file": "0_a_v0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    plan_store = planned((0, "a", "a"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a.png"])

    assert record.slots("düğün")["0_a"] == {
        "photo": {"status": "deleted", "file": "0_a.png"},
        "video": {"status": "deleted", "file": "0_a_v0.mp4"}}
    assert sorted(store.deleted) == ["0_a.png", "0_a_v0.mp4"]


def test_a_deleted_photo_still_never_returns_to_the_queue():
    # v4's guard: a free slot is not a debt. If the layer rule leaks into the queue, this goes red.
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png", "status": "done"})
    plan_store = planned((0, "a", "a"))

    remove_frames(record, store, plan_store, FakeOrderStore(), stamped, "düğün", ["0_a.png"])

    assert owed_files(record, plan_store) == []
```

`test_photo_usecases.py`'nin import satırına `layers` eklenir.

- [ ] **Adım 2: Koş**

Koş: `python -m pytest queen-editor -q` → yeşil (kod yerinde; bu testler nöbetçi).

- [ ] **Adım 3: Commit**

```bash
git add queen-editor/backend/tests/test_photo_usecases.py
git commit -m 'test(queen-editor): guard the layer stack acceptance criteria'
```

---

## Kapanış

- [ ] `python -m pytest queen-editor -q` yeşil.
- [ ] Ön yüze dokunulmadı → `npm run build` **koşulmaz**, `dist/` değişmez.
- [ ] Dal push edilir.

**Spec kapsaması:**

| Spec bölümü | Görev |
|---|---|
| 1 · Kare ile dosya ayrılıyor | 1.2 |
| 2 · Günlük kareyi ve katmanı söylüyor | 1.3 (Kayıt) |
| 3 · Yuva kuralı, kuyruk borcundan ayrı | 1.1, 1.3 (Kuyruk), 1.4 |
| 4 · Silme ve paylaşılan dosya | 1.1 (kural), 1.3 (Silme) |
| 5 · Galeri sırası kare kimliği tutar | 1.3 (Sıra) |
| 6 · Uç noktalar | 1.3 (Galeri, Silme) |
| 7 · Testler | hepsi |
| 8 · Kabul kriteri | 1.4 |
