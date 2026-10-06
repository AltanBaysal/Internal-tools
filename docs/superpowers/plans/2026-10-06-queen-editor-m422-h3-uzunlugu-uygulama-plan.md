# Madde 422 — H3 videosu projenin uzunluğunda, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır, ana klasörde (`feat/queen-editor-v9`). Kod yazılır, dört satır
> koşulur, yeşil görülür. **Commit yok:** 421'le birlikte kullanıcının Changes'inde okunur.

**Hedef:** Projenin uzunluk ayarı ve kapısı; kuyruğa giren H3 videosunun o anki uzunluğu taşıması;
Tekrar dene'nin o anki uzunluğu kullanması; uzunluğun Director'a üç yerde gitmesi; WAN'ın, fotoğrafın
ve sesin onu alıp görmezden gelmesi; `main.py`'nin bağlaması.

**Yaklaşım:** Uzunluk işin plan satırında; döngü onu her üreticiye verir; kural, mağaza ve kapı
`photo_generation`'da; `main.py` kuyruğa okuyucuyu yalnız H3 oturumunda verir.

**Spec:** [m422 uygulama turu](../specs/2026-10-06-queen-editor-m422-h3-uzunlugu-uygulama-design.md),
[m422 test turu](../specs/2026-10-06-queen-editor-m422-h3-uzunlugu-testler-design.md)

## Her yere geçerli kurallar

- Kod ve yorum İngilizce; kullanıcının gördüğü cümle Türkçe:
  `Video uzunluğu 4, 8 ya da 12 saniye olmalı.`, `Proje yok: <proje>`.
- Domain dışarıdan hiçbir şey içe aktarmaz; özellik özelliği içe aktarmaz; somut sınıflar yalnız
  `main.py`'de bağlanır.
- Testlere dokunulmaz.

---

## Görev 1: Kural — `domain/video_length.py` (yeni)

```python
"""How long an H3 video runs (madde 422): the project's one choice, and what the queue does with it.

The user's words (v9-1, 5 Ekim): "videoları veya 4 8 12 arasında seçebilmek video uzunlupunu",
"varsalın 8 olsun", "h3e özel". Only H3's length is chosen -- a WAN video runs as long as its graph
says, and in a WAN session nothing here is handed a length at all (main.py).

A video carries the length it was put in the queue with, and comes out at it however the project
changes while it waits ("Eklendiği uzunlukta"): the length is written on the job's plan line, never
read again when its turn comes.
"""
from backend.features.photo_generation.domain import layers, queue

LENGTHS = (4, 8, 12)
DEFAULT = 8


class InvalidLength(Exception):
    """A length the project cannot be set to (message is user-facing)."""


def check(seconds):
    """Refuse anything but 4, 8 or 12 whole seconds. bool is an int in Python, and True would
    silently mean a one-second video."""
    if isinstance(seconds, bool) or not isinstance(seconds, int) or seconds not in LENGTHS:
        raise InvalidLength("Video uzunluğu 4, 8 ya da 12 saniye olmalı.")


def carried(length, project):
    """What a video job put in the queue now carries about its length: the project's length at this
    moment. `length` answers it; None -- a session whose video model takes no length -- carries
    nothing."""
    return {"seconds": length(project)} if length else {}


def at_length_now(plan_store, project, fids, length):
    """Put these frames' red videos back in the queue at the project's length now.

    Tekrar dene puts a video in the queue again, and it goes at the length of that moment
    ("Tekrar dene — bu kareye" -- "Evet"). Each frame's latest video line is written again with the
    new length and everything else as it was: the plan only grows, and the engine makes a frame's
    layer from its latest line (queue._latest_per_frame). A video already at that length is left
    alone, so then a retry re-plans nothing, as it always did. One append for all of them, because
    the plan file is written whole every time.
    """
    if not length or not fids:
        return
    seconds = length(project)
    latest = {}
    for job in plan_store.read(project)["frames"]:
        if queue.type_of(job) == layers.VIDEO:
            latest[job["id"]] = job
    again = [{**latest[fid], "seconds": seconds} for fid in fids
             if fid in latest and latest[fid].get("seconds") != seconds]
    if again:
        plan_store.append(project, again)
```

## Görev 2: Mağaza — `data/video_length_store.py` (yeni)

```python
"""VideoLengthStore over DriveStorage -- the only place that knows the length file's name and shape.

A file of its own (CODE-STANDARD, Separation of concerns): it is written the moment the length is
chosen and read whenever a video is put in the queue, where settings.json is overwritten by every
photo batch. Anything unreadable reads as nothing saved, so a file half-written or edited by hand
never keeps a project from opening.
"""
import json

FILE = "video_length.json"


class DriveVideoLengthStore:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def read(self, project):
        """The saved length as a whole number, or None when there is none to read."""
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return None
        try:
            data = json.loads(raw)
        except ValueError:
            return None
        seconds = data.get("seconds") if isinstance(data, dict) else None
        # bool is an int in Python, and true would read as a one-second video.
        return seconds if isinstance(seconds, int) and not isinstance(seconds, bool) else None

    def write(self, project, seconds):
        self._storage.write_text(project, FILE, json.dumps({"seconds": seconds}))
```

## Görev 3: Kullanım — `domain/usecases/video_length.py` (yeni)

```python
"""Read and save how long the project's H3 videos run (madde 422).

The messages are user-facing Turkish; presentation forwards them untouched.
"""
from backend.features.photo_generation.domain import video_length
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def get_video_length(lengths, project):
    """The project's length in seconds: what was saved, or 8 when nothing usable was."""
    if not lengths.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    saved = lengths.read(project)
    return saved if saved in video_length.LENGTHS else video_length.DEFAULT


def save_video_length(lengths, project, seconds):
    """The value is refused before the project is looked for: the cheap refusal comes first. The
    project must already exist -- writing would otherwise create one, and every folder under the root
    counts as a project."""
    video_length.check(seconds)
    if not lengths.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    lengths.write(project, seconds)
```

## Görev 4: Kapı — `presentation/video_length_routes.py` (yeni)

```python
"""/api/projects/<project>/video-length -- how long the project's H3 videos run (madde 422).

A blueprint of its own, the way Referanstan's record has one: the cards' factory, and everything
wired to it, stays as it was. Translation only; the use case's sentences go out verbatim.
"""
from flask import Blueprint, jsonify, request

from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing
from backend.features.photo_generation.domain.video_length import InvalidLength


def make_video_length_blueprint(get_video_length, save_video_length):
    """Both arguments are use cases already bound to a store (see main.py)."""
    bp = Blueprint("video_length", __name__)

    @bp.get("/api/projects/<project>/video-length")
    def get_length(project):
        try:
            return jsonify({"seconds": get_video_length(project)})
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.put("/api/projects/<project>/video-length")
    def put_length(project):
        body = request.get_json(silent=True) or {}
        try:
            save_video_length(project, body.get("seconds"))
        except InvalidLength as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        # 204: the client already has what it sent; there is nothing to send back.
        return "", 204

    return bp
```

## Görev 5: Port — `domain/ports.py`

- [ ] `PhotoGenerator.generate`'in imzası `references: tuple = (), seconds: int | None = None)`, ve
  belgesinin sonuna:

```
        `seconds` is how long a video should run, from its job (madde 422). Only an H3 video job
        carries one, and only H3's producer uses it; the others take it and ignore it, like `end`.
        None is a job that carries none, and its graph's own length stands.
```

- [ ] `OrderStore`'dan sonra:

```python
class VideoLengthStore(Protocol):
    def project_exists(self, project: str) -> bool:
        ...

    def read(self, project: str) -> int | None:
        """How long the project's H3 videos run, in seconds; None when nothing usable is saved."""
        ...

    def write(self, project: str, seconds: int) -> None:
        """Replace the saved length."""
        ...
```

## Görev 6: Kuyruğun kapıları

- [ ] **`queue_layer.py`** — içe aktarma `video_length`; imzaya `length=None`; `taken = …`'dan önce:

```python
    # Asked once per press, and only of a video: every job this press puts in the queue carries the
    # length of this moment (madde 422).
    timed = video_length.carried(length, project) if kind == layers.VIDEO else {}
```

  ve döngüde `_mark`'ın `None` denetiminden sonra:

```python
        mark = {**mark, **timed}
```

- [ ] **`queue_references.py`** — içe aktarma `video_length`; imzaya `length=None`; kartlar:

```python
    # Every card is an H3 video, made at the project's length of this moment (madde 422).
    timed = video_length.carried(length, project)
    cards = [{**card, **timed}
             for card in plan_reference_cards(next_number(store, plan_store, record, project),
                                              written, variants, new_seed)]
```

- [ ] **`regenerate.py`** — içe aktarma `video_length`; imzaya `length=None`; plan satırında
  `**mark,`'tan sonra:

```python
        # A new video goes at the project's length of this moment (madde 422).
        **(video_length.carried(length, project) if kind == layers.VIDEO else {}),
```

- [ ] **`retry_frame.py`** — içe aktarma `video_length`; imzaya `length=None`; `red`'den sonra,
  satırlar yazılmadan önce:

```python
    # Before the red lines are put back, so a loop already running never takes the video at the
    # length it is leaving (madde 422).
    if any(layer == layers.VIDEO for layer, _cell in red):
        video_length.at_length_now(plan_store, project, [fid], length)
```

- [ ] **`retry_failed.py`** — içe aktarma `layers`, `video_length`; imzaya `length=None`; gövde:

```python
    red = [(fid, layer, cell) for fid, cells in record.slots(project).items()
           for layer, cell in cells.items() if cell["status"] == queue.FAILED]
    # Before the red lines are put back, like one frame's Tekrar dene (madde 422).
    video_length.at_length_now(plan_store, project,
                               [fid for fid, layer, _cell in red if layer == layers.VIDEO], length)
    for fid, layer, cell in red:
        record.mark(project, fid, layer, cell["file"], queue.QUEUED, now())
    run_queue(…)
    return len(red)
```

## Görev 7: Döngü — `run_loop.py`

- [ ] `producer.generate(…, references=pool, seconds=current.get("seconds"))`.
- [ ] `_made_with`'in sonunda, `return made`'den önce:

```python
    if job.get("seconds"):
        # How long the video was made, so the export can add up each one's own (madde 422).
        made["seconds"] = job["seconds"]
```

  ve belgesinin ilk paragrafı: *"The mode, the name of the picture the video arrived at, and how
  long it was made -- each only when there is one."*

## Görev 8: Üreticiler

- [ ] **H3** — `generate(…, references=(), seconds=None)`; `_from_pool(prompt, seed, references,
  seconds)`; ikisinde de Director okunurken:

```python
        director = _director(workflow, seconds)
```

  modül düzeyinde:

```python
def _director(workflow, seconds):
    """The Director's inputs, set to run `seconds` -- the graph's own note says to set the length
    there ("set duration (s)"), and nothing else in the graph counts frames. A job with no length
    leaves the graph's own: every one queued before madde 422."""
    director = workflow[DIRECTOR_NODE]["inputs"]
    if seconds is not None:
        director["duration"] = seconds
    return director
```

  `_render`'da, iki `builder_state` de Director'ın süresini taşır:

```python
        timeline["builder_state"]["duration"] = director["duration"]
        …
        state["duration"] = director["duration"]
```

  Modül belgesi: `"2730"  MiniMaxH3Director   -> the pictures, the prompt and the length`, ve
  uzunluğun üç yerini söyleyen paragraf. `seconds()`'ın belgesi: grafiğin kendi süresi — uzunluk
  taşımayan işin yapıldığı süre; export özeti onu her video için söylüyor.

- [ ] **WAN, fotoğraf, ses** — `generate(…, references=(), seconds=None)`; belgelerinde neden alıp
  görmezden geldikleri.

## Görev 9: `main.py`

- [ ] İçe aktarmalar: `DriveVideoLengthStore`, `get_video_length`, `save_video_length`,
  `make_video_length_blueprint`.
- [ ] `_photo_bp`'den önce:

```python
# How long the project's H3 videos run (madde 422): a file of its own in the project, behind a door of
# its own. Only H3's length is chosen ("h3e özel"), so only an H3 session's queue reads it -- a WAN
# video runs as long as its graph says, and its job carries no length at all.
_video_lengths = DriveVideoLengthStore(_storage)
_video_length = (partial(get_video_length, _video_lengths) if config.VIDEO_MODEL == "h3"
                 else None)
```

- [ ] `retry_frame`, `retry_failed`, `queue_layer`, `regenerate` ve `queue_references`'in
  partial'larına `length=_video_length`.
- [ ] Kapı:

```python
_video_length_bp = make_video_length_blueprint(
    get_video_length=partial(get_video_length, _video_lengths),
    save_video_length=partial(save_video_length, _video_lengths))
```

  ve `create_app`'in listesine `_video_length_bp`.

## Görev 10: Koşu — yeşil

- [ ] **Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; test turunun 44 kırmızısı yeşile döndü.

- [ ] **Commit yok.**
