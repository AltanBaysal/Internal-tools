# Queen Editor v5 · Görev 15 — Kapsam ve kopya kare kuralları · Uygulama planı

> **Uygulayıcıya:** her adım önce kırmızı test, sonra en küçük kod. Tasarım:
> [Görev 15 spec](../specs/2026-08-12-queen-editor-v5-gorev-15-kopya-kare-design.md).

**Hedef:** video panelinde varyant kutusu doğsun; varyantın fazlası ve videosu olan karenin bütün
varyantları, kaynağın fotoğrafını paylaşan **kopya kareler** olarak galeriye girsin.

**Mimari:** kimlik kuralı yeni bir saf modüle (`domain/copy_frame.py`) çıkar; kopyayı doğuran yer
`queue_videos` use case'i olur — kayıt satırını, plan işini ve sıra dosyasını o yazar. Ön yüzde
`VideoPanel` bir sayı kutusu kazanır ve kapsam sayımı ikiye ayrılır.

**Yığın:** Python (pytest) · React 18 + Vitest.

## Genel kısıtlar

- Kod, yorum, test adı ve commit **İngilizce**; kullanıcıya görünen metin **Türkçe**.
- Yorum **neden**i anlatır, kodu tekrar etmez; koddan sapan yorum yasak.
- Katman kuralı: `presentation → domain ← data`; domain saf kalır, port alır.
- Varyant tavanı **26** (`start_batch.MAX_VARIANTS`) — video için de aynısı.
- Test komutları (birebir, değiştirmeden):
  - `python -m pytest queen-editor -q`
  - `npm test --prefix queen-editor/frontend -- --run`
  - `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — Kimlik: bir sonraki varyant

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/domain/photo_name.py`
- Yeni: `queen-editor/backend/features/photo_generation/domain/copy_frame.py`
- Test: `queen-editor/backend/tests/test_photo_name.py`, `queen-editor/backend/tests/test_name_rules.py`

**Arayüz:**
- Üretir: `variant_of(name) -> int | None`, `copy_frame.next_id(ids, number) -> str`.

- [ ] **Adım 1 — kırmızı test (`test_photo_name.py` sonuna):**

```python
def test_a_name_says_which_variant_it_is():
    assert variant_of("P11_3.png") == 3
    assert variant_of("P11_3_V1_0.mp4") == 3
    # a=0, b=1: the letter scheme's variants are the same numbers written differently.
    assert variant_of("11_d.png") == 3
    assert variant_of("kapak.png") is None
```

`variant_of`'u dosyanın import satırına ekle.

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → ImportError.

- [ ] **Adım 3 — `photo_name.py`:** iki şemanın çözümlemesi tek yere iner, `number_of` onu okur:

```python
def _parts(name):
    """(number, variant) a name claims, as numbers; (None, None) when it fits neither scheme.

    Both schemes are read here, once: they are two spellings of the same pair, and a second copy of
    the parsing would let them drift apart.
    """
    stem = frame_id_of(name)
    if stem.startswith("P"):
        number, _, variant = stem[1:].partition("_")
        if number.isdigit() and variant.isdigit():
            return int(number), int(variant)
        return None, None
    number, _, letter = stem.partition("_")
    if number.isdigit() and len(letter) == 1 and letter.isalpha():
        return int(number), ord(letter) - ord("a")
    return None, None


def number_of(filename):
    """The prompt number a file's name claims; None when the name fits neither scheme.

    Both schemes claim numbers, because both name real files and a number may never be reused.
    """
    return _parts(filename)[0]


def variant_of(filename):
    """Which of its prompt's variants a file's name claims; None when it fits neither scheme."""
    return _parts(filename)[1]
```

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

- [ ] **Adım 5 — kırmızı test (`test_name_rules.py` sonuna):**

```python
def test_a_copy_takes_the_next_variant_of_its_source():
    assert next_id({"P11_0", "P11_1", "P4_9"}, 11) == "P11_2"


def test_a_copy_of_a_letter_named_frame_joins_the_same_family():
    # 11_d is variant 3 written the old way: the copy is the family's next, not its second.
    assert next_id({"11_a", "11_d"}, 11) == "P11_4"


def test_a_gap_left_by_a_deleted_variant_is_not_reused():
    # The deleted frame keeps its line in the record, so its name stays claimed.
    assert next_id({"P11_0", "P11_2"}, 11) == "P11_3"


def test_the_first_copy_of_an_untouched_number_is_variant_zero():
    assert next_id({"P4_0"}, 11) == "P11_0"
```

`from backend.features.photo_generation.domain.copy_frame import next_id` ekle.

- [ ] **Adım 6:** `python -m pytest queen-editor -q` → ImportError.

- [ ] **Adım 7 — `copy_frame.py`:**

```python
"""What a new frame in an existing prompt's family is called.

A copy frame keeps its source's prompt number and takes the next variant, so its name still says
what produced the picture (design v3, madde 97). Written apart from the use case that makes copies
because "yeniden üret" (Görev 25) asks the same question about a different act.
"""
from backend.features.photo_generation.domain.photo_name import frame_id, number_of, variant_of


def next_id(ids, number):
    """The identity a new frame in `number`'s family takes; `ids` is every identity in the project.

    One past the highest variant ever used, never a gap: a gap belongs to a frame that was deleted,
    and reusing its name would bind one name to two different pictures -- with browsers still
    holding the old bytes under an immutable cache header.
    """
    used = [variant_of(fid) for fid in ids if number_of(fid) == number]
    used = [variant for variant in used if variant is not None]
    return frame_id(number, max(used) + 1 if used else 0)
```

- [ ] **Adım 8:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Galeri kare başına tek satır

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/domain/usecases/list_frames.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

**Neden burada:** Görev 14'ten kalan kusur — plan artık kare başına birden çok iş tutuyor, galeri
planı satır satır okuduğu için videosu kuyruğa girmiş kare iki kez çiziliyor. Kopya kareler
gelmeden önce kapanmalı, yoksa yeni testler kusurun üstüne yazılır.

- [ ] **Adım 1 — kırmızı test (`test_photo_usecases.py`, galeri testlerinin yanına):**

```python
def test_a_frame_whose_video_is_queued_is_still_one_frame():
    # The plan holds a job per layer; the gallery holds a row per frame.
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store = FakePlanStore(frames=[
        frame(0),
        {"id": "0_a", "type": "video", "number": 0, "prompt": "", "negative": "", "seed": None,
         "model": ""},
    ])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert [row["id"] for row in rows] == ["0_a"]
    # The row comes from the photo job, so it still carries what the photo was asked for.
    assert rows[0]["prompt"] == "p"
```

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → iki satır geldiği için kırmızı.

- [ ] **Adım 3 — `list_frames.py`:** plan döngüsünün başına, `fid = frame["id"]`'den önce:

```python
        if queue.type_of(frame) != layers.PHOTO:
            # A frame's row comes from its photo job alone. The plan holds one job per layer, and a
            # video job is that frame's layer -- read as a row of its own it would draw the frame
            # twice.
            continue
```

Modül `layers` ve `queue`'yu zaten import ediyor.

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 3 — Kapsam: videolu kare seçimle girer

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/domain/usecases/queue_videos.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

**Arayüz:**
- Üretir: `frames_in_scope(gallery, files=None) -> list` (artık port değil, galerinin kendisini
  alır — `queue_videos` galeriyi bir kez okur).

- [ ] **Adım 1 — kırmızı testler:** (`frames_in_scope`'u import satırına ekle)

```python
def test_a_selected_frame_that_has_a_video_is_still_in_scope():
    # "These ones" is the user's own word: madde 25's copies have no other way in.
    gallery = [{"id": "0_a", "file": "0_a.png", "status": "done",
                "layers": {"video": "0_a_V1_0.mp4"}},
               {"id": "1_a", "file": "1_a.png", "status": "done", "layers": {}}]

    assert [f["id"] for f in frames_in_scope(gallery, ["0_a.png"])] == ["0_a"]
    # The panel's row is called "Videosu olmayanlar": with no selection it means exactly that.
    assert [f["id"] for f in frames_in_scope(gallery)] == ["1_a"]


def test_a_frame_whose_name_claims_no_number_takes_no_video():
    # Its job could not be stored: the plan keeps a number per job and reads back only jobs that
    # have one, so the video would quietly vanish instead of being made.
    gallery = [{"id": "kapak", "file": "kapak.png", "status": "done", "layers": {}}]

    assert frames_in_scope(gallery, ["kapak.png"]) == []
```

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı (imza hâlâ portları istiyor).

- [ ] **Adım 3 — `queue_videos.py`:** kapsam fonksiyonunu galeri üstünde çalışır hâle getir ve
videolu kareyi yalnız `files is None` iken ele:

```python
def frames_in_scope(gallery, files=None):
    """The frames a video job can be hung on, in gallery order.

    `files` is the gallery's own selection; None means every frame that has no video.

    A frame that already has one is out of the None scope and in a selection's: the panel's row is
    called "Videosu olmayanlar", while picking a frame by hand says "this one" -- and that is the
    only way madde 25's "every variant of a frame that already has a video" can be asked for.
    """
    chosen = None if files is None else set(files)
    scope = []
    for frame in gallery:
        if chosen is not None and frame["file"] not in chosen:
            continue
        # Only a produced photo can carry a video; a frame still waiting for its own has nothing to
        # hang one on. A name that claims no number cannot be planned at all: the plan stores a
        # number per job and reads back only the jobs that have one.
        if frame["status"] != "done" or _family(frame)[0] is None:
            continue
        if chosen is None and layers.VIDEO in frame.get("layers", {}):
            continue
        scope.append(frame)
    return scope
```

`_family` Görev 4'te yazılıyor — bu adımda onu da ekle (kodu Görev 4, Adım 3'te).

`queue_videos` içinde galeriyi bir kez oku:

```python
    gallery = list_frames(record, store, plan_store, order_store, project)
    scope = frames_in_scope(gallery, files)
```

`list_frames` importu duruyor; `store`/`plan_store` parametreleri `queue_videos`'ta hâlâ gerekli.

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 4 — Kopya kare doğar

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/domain/usecases/queue_videos.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

**Arayüz:**
- Tüketir: `copy_frame.next_id`, `photo_name.number_of/variant_of`.
- Üretir: `queue_videos(..., files=None, variants=1, log=None) -> int`.

- [ ] **Adım 1 — kırmızı testler:**

```python
def test_one_variant_hangs_the_video_on_the_frame_itself():
    store, record, plan_store = video_project((0, "a"))

    added = queue_videos(sync_runner(), store, record, plan_store, FakeOrderStore(),
                         {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", variants=1)

    assert added == 1
    assert [job["id"] for job in plan_store.appended[-1]] == ["0_a"]
    assert photo_statuses(record) == {"0_a": "done"}      # no copy was born


def test_the_variants_past_the_first_are_born_as_copy_frames():
    store, record, plan_store = video_project((0, "a"))

    added = queue_videos(sync_runner(), store, record, plan_store, FakeOrderStore(),
                         {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", variants=3)

    assert added == 3
    assert [job["id"] for job in plan_store.appended[-1]] == ["0_a", "P0_1", "P0_2"]


def test_a_copy_points_at_its_source_own_photo():
    store, record, plan_store = video_project((0, "a"))

    queue_videos(sync_runner(), store, record, plan_store, FakeOrderStore(),
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", variants=2)

    copy = record.slots("düğün")["P0_1"]
    assert copy["photo"] == {"status": "done", "file": "0_a.png"}
    # Only a photo: a video variant carries no audio (madde 102), and its own video is still owed.
    assert list(copy) == ["photo"]


def test_every_variant_of_a_frame_that_has_a_video_is_a_copy():
    store, record, plan_store = video_project((0, "a"))
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    added = queue_videos(sync_runner(), store, record, plan_store, FakeOrderStore(),
                         {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün",
                         files=["0_a.png"], variants=2)

    assert added == 2
    assert [job["id"] for job in plan_store.appended[-1]] == ["P0_1", "P0_2"]


def test_a_copy_frame_carries_its_source_prompt():
    store, record, plan_store = video_project((0, "a"))

    queue_videos(sync_runner(), store, record, plan_store, FakeOrderStore(),
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", variants=2)

    born = [row for row in record.rows if row["frame"] == "P0_1"][0]
    assert born["prompt"] == "p"                 # the source's own, from the plan's photo job
    assert born["createdAt"] == "t"


def test_a_video_job_says_which_number_and_variant_it_belongs_to():
    # The plan drops a job whose number is not a number, so a copy's job has to carry its own.
    store, record, plan_store = video_project((0, "a"))

    queue_videos(sync_runner(), store, record, plan_store, FakeOrderStore(),
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", variants=2)

    jobs = {job["id"]: job for job in plan_store.appended[-1]}
    assert (jobs["0_a"]["number"], jobs["0_a"]["variant"]) == (0, 0)
    assert (jobs["P0_1"]["number"], jobs["P0_1"]["variant"]) == (0, 1)


def test_the_variant_count_has_the_same_ceiling_as_a_photo_batch():
    store, record, plan_store = video_project((0, "a"))

    with pytest.raises(InvalidVariants):
        queue_videos(sync_runner(), store, record, plan_store, FakeOrderStore(),
                     {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", variants=27)
    assert plan_store.appended == []
```

> `video_project` karelerinin prompt'u `frame(...)` yardımcısından geliyor — `"ilk"` yerine o
> yardımcının gerçekten yazdığı metni kullan.

`InvalidVariants` zaten `test_photo_usecases.py`'ta import edili (start_batch testleri kullanıyor);
değilse import satırına ekle.

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → hepsi kırmızı.

- [ ] **Adım 3 — `queue_videos.py`:** modülün üst yorumuna kopya kuralını ekle ve gövdeyi yaz.

Import satırları:

```python
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.copy_frame import next_id
from backend.features.photo_generation.domain.photo_name import number_of, variant_of
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import (  # noqa: F401
    MAX_VARIANTS,
    InvalidVariants,
    ProjectMissing,
)
```

Yardımcılar:

```python
def _family(frame):
    """(number, variant) the frame's identity claims -- what the plan wrote down as a fallback.

    Read off the identity rather than the plan's fields, because a copy frame has no photo job in
    the plan: its row comes from the record, and the name is the only thing that says which
    prompt's family it belongs to.
    """
    number, variant = number_of(frame["id"]), variant_of(frame["id"])
    return (number if number is not None else frame.get("number"),
            variant if variant is not None else frame.get("variant"))


def _video_job(fid, number, variant):
    """The plan line for one video. Prompt is empty on purpose: a language model writes it when the
    job's turn comes (Görev 16), and a box the user never saw must not pretend otherwise."""
    return {"id": fid, "type": layers.VIDEO, "number": number, "variant": variant,
            "prompt": "", "negative": "", "seed": None, "model": ""}


def _known_ids(record, plan_store, project):
    """Every identity the project has ever used -- deleted frames included, so no name is reused."""
    return ({frame["id"] for frame in plan_store.read(project)["frames"]}
            | set(record.slots(project)))
```

Gövde:

```python
def queue_videos(runner, store, record, plan_store, order_store, producers, now, project,
                 files=None, variants=1, log=None):
    """Returns how many video jobs the queue took."""
    if files is not None and (not isinstance(files, list)
                              or any(not isinstance(name, str) for name in files)):
        raise InvalidScope("Seçim listesi metin dizisi olmalı.")
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= MAX_VARIANTS:
        raise InvalidVariants(f"Varyant sayısı 1-{MAX_VARIANTS} arası bir tam sayı olmalı.")
    gallery = list_frames(record, store, plan_store, order_store, project)
    scope = frames_in_scope(gallery, files)
    if not scope:
        # Nothing owed and nothing started: an empty scope is a result, not a failure.
        return 0

    taken = _known_ids(record, plan_store, project)
    jobs, born = [], {}
    # Oldest first, the direction the engine works in: the gallery is newest-first and its foot is
    # what gets made first, so a plan written the way it reads would run backwards wherever the
    # gallery's own order file has nothing to say.
    for frame in reversed(scope):
        fid = frame["id"]
        number, variant = _family(frame)
        owed = variants
        if layers.VIDEO not in frame.get("layers", {}):
            jobs.append(_video_job(fid, number, variant))
            owed -= 1
        for _ in range(owed):
            copy = next_id(taken, number)
            taken.add(copy)
            # A real frame, born with a photo row of its own that points at its source's picture:
            # that is the whole of "kopya kare" -- no flag, no field, and the gallery draws it,
            # deletes it and orders it by the rules it already has.
            record.append(project, {"file": frame["file"], "frame": copy, "layer": layers.PHOTO,
                                    "status": queue.DONE, "prompt": frame.get("prompt", ""),
                                    "negative": frame.get("negative", ""),
                                    "seed": frame.get("seed"), "createdAt": now()})
            born.setdefault(fid, []).append(copy)
            jobs.append(_video_job(copy, number, variant_of(copy)))

    plan_store.append(project, jobs)
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store)
    return len(jobs)
```

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → Görev 3'ün testi dahil yeşil. Sıra dosyası
testi henüz yok; kopyalar şimdilik galerinin tepesinde duruyor (Görev 5 yerine koyacak).

---

## Görev 5 — Kopya kaynağın üstüne yerleşir

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/domain/usecases/queue_videos.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

- [ ] **Adım 1 — kırmızı testler:**

```python
def test_a_copy_takes_its_place_right_above_its_source():
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    order = FakeOrderStore()

    queue_videos(sync_runner(), store, record, plan_store, order,
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün",
                 files=["0_a.png"], variants=3)

    # The whole gallery is written down, newest first, with the copies hanging above their source.
    assert order.order == ["1_a", "P0_2", "P0_1", "0_a"]


def test_the_gallery_draws_the_copy_next_to_its_source():
    store, record, plan_store = video_project((0, "a"), (1, "a"))
    order = FakeOrderStore()

    queue_videos(sync_runner(), store, record, plan_store, order,
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün",
                 files=["0_a.png"], variants=2)

    rows = list_frames(record, store, plan_store, order, "düğün")
    assert [row["id"] for row in rows] == ["1_a", "P0_1", "0_a"]
    assert [row["file"] for row in rows] == ["1_a.png", "0_a.png", "0_a.png"]


def test_nothing_is_written_to_the_order_file_when_no_copy_is_born():
    store, record, plan_store = video_project((0, "a"))
    order = FakeOrderStore()

    queue_videos(sync_runner(), store, record, plan_store, order,
                 {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", variants=1)

    assert order.order == []
```

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı (sıra dosyası boş kalıyor).

- [ ] **Adım 3 — `queue_videos.py`:** yardımcıyı ekle:

```python
def _placed(gallery, born):
    """The gallery's own sequence with each frame's new copies hanging directly above it.

    Above rather than below for two reasons: the gallery's rule is newest on top and a copy is newer
    than its source, and production reads the gallery from its foot up -- so the source's own video
    is made first and its copies follow.

    The whole sequence is written, not just the copies: a project nobody has dragged has no order
    file at all, and a file holding the copies alone would send every other frame to the top.
    """
    placed = []
    for fid in gallery:
        placed.extend(reversed(born.get(fid, [])))
        placed.append(fid)
    return placed
```

ve `plan_store.append`'ten hemen önce:

```python
    if born:
        order_store.write(project, _placed([frame["id"] for frame in gallery], born))
```

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 6 — Uç nokta varyantı taşır

**Dosyalar:**
- Değişecek: `queen-editor/backend/features/photo_generation/presentation/routes.py`
- Test: `queen-editor/backend/tests/test_photo_routes.py`

- [ ] **Adım 1 — kırmızı testler (`test_photo_routes.py` sonuna):**

```python
def test_the_videos_endpoint_carries_the_variant_count(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = client.post("/api/projects/düğün/videos", json={"variants": 2})

    assert resp.status_code == 202
    # One video on the frame itself and one on the copy it just gained.
    assert resp.get_json()["added"] == 2


def test_the_videos_endpoint_refuses_an_impossible_variant_count(tmp_path):
    client, _ = make_client(tmp_path)

    resp = client.post("/api/projects/düğün/videos", json={"variants": 0})

    assert resp.status_code == 400
    assert resp.get_json()["field"] == "variants"


def test_a_copy_frame_shares_its_source_photo_file(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    client.post("/api/projects/düğün/videos", json={"variants": 3})

    rows = client.get("/api/projects/düğün/frames").get_json()["frames"]
    assert [row["id"] for row in rows] == ["P0_2", "P0_1", "P0_0"]
    # Three frames, one picture on disk.
    assert {row["file"] for row in rows} == {"P0_0.png"}
```

> Bu dosyada gerçek `DriveStorage` ve gerçek use case'ler koşuyor; video üreticisi yok, o yüzden
> koşu "waiting"e düşüyor — testlerin baktığı şey cevabın kendisi.

- [ ] **Adım 2:** `python -m pytest queen-editor -q` → kırmızı.

- [ ] **Adım 3 — `routes.py`, `post_videos` içinde:**

```python
        # No "variants" key means one video per frame: a client that predates the box asks for what
        # it always asked for.
        try:
            added = queue_videos(project, files=files, variants=body.get("variants", 1))
        ...
        except InvalidVariants as exc:
            return jsonify({"error": str(exc), "field": "variants"}), 400
```

`InvalidVariants` bu dosyada zaten import edili.

- [ ] **Adım 4:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 7 — Panelde varyant kutusu

**Dosyalar:**
- Değişecek: `queen-editor/frontend/src/features/photo_generation/VideoPanel.jsx`
- Değişecek: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`
- Değişecek: `queen-editor/frontend/src/shared/api.js`
- Test: `queen-editor/frontend/src/features/photo_generation/VideoPanel.test.jsx`

- [ ] **Adım 1 — kırmızı testler (`VideoPanel.test.jsx`):**

```jsx
const variantBox = () => screen.getByRole("spinbutton");

describe("VideoPanel — variants", () => {
  it("multiplies the estimate by the variant count", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "3" } });

    expect(screen.getByText("6 video üretilecek — her kare kendi videosunu alır.")).toBeTruthy();
  });

  it("refuses a count the server would refuse", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "27" } });

    expect(variantBox().value).toBe("1");
  });

  it("sends the count along with the scope", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 4 });
    renderPanel({ onQueue });

    fireEvent.change(variantBox(), { target: { value: "2" } });
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 2);
  });

  it("counts a selected frame that already has a video", () => {
    // Picking it by hand is how a second video is asked for -- it becomes a copy frame.
    renderPanel({ selected: ["1_a.png"] });

    expect(screen.getByText("Seçili kareler").closest("button").textContent).toContain("1");
    expect(screen.getByText("1 video üretilecek — her kare kendi videosunu alır.")).toBeTruthy();
  });
});
```

Var olan iki gönderim testi de sayıyı taşır: `toHaveBeenCalledWith(null)` → `(null, 1)`,
`toHaveBeenCalledWith(["0_a.png"])` → `(["0_a.png"], 1)`.

- [ ] **Adım 2:** `npm test --prefix queen-editor/frontend -- --run` → kırmızı.

- [ ] **Adım 3 — `VideoPanel.jsx`:**

Sabit ve yardımcı:

```jsx
const MAX_VARIANTS = 26;

/** What the box may hold while it is being typed in -- the photo panel's rule, for the same
 *  reason: a value outside the range is simply not taken, so there is no error state to design. */
function acceptsVariants(text) {
  if (text === "") return true;
  if (!/^\d+$/.test(text)) return false;
  return Number(text) >= 1 && Number(text) <= MAX_VARIANTS;
}
```

`eligible` ikiye ayrılır:

```jsx
/** A frame can carry a video once its photo has landed. Read off the gallery, which already says
 *  what each frame holds -- the server decides the same way. */
function produced(frames) {
  return (frames || []).filter((frame) => frame.status === "done");
}
```

Gövde:

```jsx
  const [variants, setVariants] = useState("1");
  ...
  const chosen = selected || [];
  const done = produced(frames);
  // The scope row's own name decides this: "Videosu olmayanlar" leaves out the ones that have one,
  // while picking frames by hand says "these ones" -- and that is how a second video is asked for.
  const missing = done.filter((frame) => !(frame.layers || {}).video);
  const inSelection = done.filter((frame) => chosen.includes(frame.file));
  ...
  const counts = { missing: missing.length, selected: inSelection.length };
  const scoped = scope === "selected" ? inSelection : missing;
  const owed = scoped.length * (Number(variants) || 0);
```

`handleAdd` gönderimi:

```jsx
    onQueue(scope === "selected" ? inSelection.map((frame) => frame.file) : null, Number(variants))
```

Kutu, Süre bloğunun üstüne (madde 23'ün sırası: kapsam · varyant · buton):

```jsx
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <Mono size={11} style={{ ...LABEL, flex: 1 }}>Varyant</Mono>
        <input
          className="wf-input"
          type="number"
          min={1}
          max={MAX_VARIANTS}
          value={variants}
          onChange={(e) => { if (acceptsVariants(e.target.value)) setVariants(e.target.value); }}
          onBlur={() => { if (variants === "") setVariants("1"); }}
          style={{ width: 56, textAlign: "center", fontSize: 13 }}
        />
      </div>
```

- [ ] **Adım 4 — `useGeneration.js`:** `queueVideo` ikinci parametreyi taşır:

```js
  const queueVideo = useCallback((files, variants) => (
    queueVideos(project, files, variants)
```

- [ ] **Adım 5 — `api.js`:**

```js
export async function queueVideos(project, files, variants) {
  return request(`/api/projects/${encodeURIComponent(project)}/videos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...(files === null ? {} : { files }), variants }),
  });
}
```

- [ ] **Adım 6:** `npm test --prefix queen-editor/frontend -- --run` → yeşil.

---

## Görev 8 — Tam takım ve commit

- [ ] **Adım 1:** `python -m pytest queen-editor -q`
- [ ] **Adım 2:** `npm test --prefix queen-editor/frontend -- --run`
- [ ] **Adım 3:** `npm run build --prefix queen-editor/frontend`
- [ ] **Adım 4:** `dist/` ile birlikte tek commit:

```
feat(queen-editor): a second video on the same photo becomes its own frame
```
