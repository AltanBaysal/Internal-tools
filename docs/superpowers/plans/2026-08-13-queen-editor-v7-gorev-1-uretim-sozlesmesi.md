# Görev 1 — Üretim sözleşmesi tek olsun (uygulama planı)

**Spec:** [Görev 1](../specs/2026-08-13-queen-editor-v7-gorev-1-uretim-sozlesmesi-design.md) ·
**Roadmap:** [v7](2026-08-13-queen-editor-v7-roadmap.md) · Blok 1

**Amaç:** Üç üretici de kuyruğun beklediği tek sözleşmeyi karşılasın
(`generate(prompt, negative, seed, model="", source=None) -> bytes`), ve bu sözleşmeyi kuyrukla
birlikte koşan bir test korusun.

**Yaklaşım:** Önce sözleşmeyi kıran testi yaz (kırmızı), sonra iki üreticiyi ve portu düzelt.
Test, gerçek üretici sınıflarını gerçek döngünün altında koşturur; sahte olan yalnız ComfyUI
istemcisi, MMAudio örnekleyicisi ve ffmpeg.

## Global kısıtlar

- Kod, yorum, docstring ve test adları **İngilizce**; kullanıcıya görünen metin Türkçe.
- Katmanlar: `presentation → domain ← data → services`. Bu görev yalnız `domain/ports.py` ve iki
  `data/` üreticisine dokunur; somut bağlama (`main.py`) değişmez.
- Ön yüz değişmiyor → `npm run build` gerekmez.
- Testler: `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend -- --run`.
- Görev sonunda **tek commit**.

## Dosyalar

- **Oluştur:** `queen-editor/backend/tests/test_producer_contract.py`
- **Değiştir:** `queen-editor/backend/features/photo_generation/data/comfy_photo_generator.py`
- **Değiştir:** `queen-editor/backend/features/photo_generation/data/mmaudio_generator.py`
- **Değiştir:** `queen-editor/backend/features/photo_generation/domain/ports.py`
- **Değiştir:** `queen-editor/backend/tests/test_mmaudio_generator.py`

---

### Adım 1 — Sözleşme testini yaz

`queen-editor/backend/tests/test_producer_contract.py` dosyasını oluştur:

```python
"""The contract between the queue and the three real producers.

Every other test in the suite runs one side of this contract: a producer's own test calls it
directly, and the queue's tests run against fakes. Both sides can be green while they disagree
about the call -- which is exactly what shipped. This file runs the real producer classes under
the real loop, and it is the only place that does.

Fake here is what a test machine cannot have: the ComfyUI server, torch, and ffmpeg. The graphs
are the shipped ones, because a producer that cannot patch its own graph does not satisfy the
contract in practice.
"""
import os

from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator
from backend.features.photo_generation.data.comfy_video_generator import ComfyVideoGenerator
from backend.features.photo_generation.data.mmaudio_generator import MMAudioGenerator
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.run_loop import make_job

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PHOTO_GRAPH = os.path.join(ROOT, "workflow_api.json")
VIDEO_GRAPH = os.path.join(ROOT, "workflow_video_api.json")


class PhotoComfy:
    """The photo graph's server: takes a workflow, answers with a picture."""

    def submit(self, workflow):
        self.submitted = workflow
        return "p1"

    def wait(self, prompt_id, timeout):
        return {"outputs": {}}

    def fetch_output(self, history):
        return b"PNG"


class VideoComfy:
    """The video graph's server. Records the upload, because that upload IS the frame's photo
    reaching the video producer."""

    def __init__(self):
        self.uploaded = []

    def upload_image(self, name, data):
        self.uploaded.append((name, data))
        return name

    def submit(self, workflow):
        self.submitted = workflow
        return "p2"

    def wait(self, prompt_id, timeout):
        return {"outputs": {}}

    def fetch_output(self, history, extensions=()):
        return b"MP4"


class Sampler:
    def render(self, video, prompt, negative, seed, duration):
        return b"RIFFwav"


class Ffmpeg:
    """Reads the file it is asked about, so the test can prove which bytes arrived."""

    def __init__(self):
        self.saw = None

    def duration(self, video):
        with open(video, "rb") as handle:
            self.saw = handle.read()
        return 5.0

    def cut(self, video, start, duration, target):
        with open(target, "wb") as handle:
            handle.write(b"piece")

    def join(self, parts, target, fade_ms):
        raise AssertionError("a five second video is one piece")


class Store:
    def __init__(self):
        self.saved = []
        self.files = {}

    def save(self, _project, filename, data):
        self.saved.append(filename)
        self.files[filename] = data
        return filename

    def read(self, _project, filename):
        return self.files.get(filename)


class Record:
    """Folds rows the way DrivePhotoRecord does: latest line per (frame, layer).

    No `prompts()`: this run has no prompt writers, so the loop never asks. A fake that answers
    questions nobody asked would hide the day one starts being asked.
    """

    def __init__(self):
        self.rows = []

    def append(self, _project, entry):
        self.rows.append(entry)

    def mark(self, _project, frame, layer, file, status, at, error=None):
        self.rows.append({"frame": frame, "layer": layer, "file": file, "status": status})

    def slots(self, _project):
        folded = {}
        for row in self.rows:
            folded.setdefault(row["frame"], {})[row["layer"]] = {
                "status": row.get("status", "done"), "file": row["file"]}
        return folded


class Plan:
    def __init__(self, frames):
        self._frames = frames

    def read(self, _project):
        return {"frames": list(self._frames)}


class Runner:
    """The two things the loop asks of a runner, and nothing else."""

    def stop_requested(self):
        return False

    def report(self, _state):
        pass


# One frame, all three layers -- so the run also proves the order: the video is made from the
# photo the same run produced, and the sound from that video.
FRAMES = [
    {"id": "P0_0", "type": "photo", "number": 0, "variant": 0,
     "prompt": "kraliçe tahtta", "negative": "blurry", "seed": 1, "model": ""},
    {"id": "P0_0", "type": "video", "number": 0, "variant": 0,
     "prompt": "kamera yaklaşır", "negative": "", "seed": 2, "model": ""},
    {"id": "P0_0", "type": "audio", "number": 0, "variant": 0,
     "prompt": "dalga sesi", "negative": "", "seed": 3, "model": ""},
]


def test_the_queue_runs_the_three_real_producers_end_to_end(tmp_path):
    store, record, video_comfy, ffmpeg = Store(), Record(), VideoComfy(), Ffmpeg()
    producers = {
        layers.PHOTO: ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60),
        layers.VIDEO: ComfyVideoGenerator(video_comfy, VIDEO_GRAPH, timeout=60),
        layers.AUDIO: MMAudioGenerator(Sampler(), ffmpeg, tmp_dir=str(tmp_path)),
    }

    state = make_job(Runner(), store, record, Plan(FRAMES), producers,
                     lambda: "2026-08-13T00:00:00+00:00", "düğün")()

    assert state["status"] == "done"
    # The domain names every file; no producer gets a say in it.
    assert store.saved == ["P0_0.png", "P0_0_V1_0.mp4", "P0_0_V1_0_S1_0.wav"]
    # And what landed under each name is what its producer answered -- bytes, not a pair.
    assert store.files["P0_0.png"] == b"PNG"
    assert store.files["P0_0_V1_0.mp4"] == b"MP4"
    assert store.files["P0_0_V1_0_S1_0.wav"] == b"RIFFwav"


def test_each_layer_is_made_from_the_one_below_it(tmp_path):
    store, video_comfy, ffmpeg = Store(), VideoComfy(), Ffmpeg()
    producers = {
        layers.PHOTO: ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60),
        layers.VIDEO: ComfyVideoGenerator(video_comfy, VIDEO_GRAPH, timeout=60),
        layers.AUDIO: MMAudioGenerator(Sampler(), ffmpeg, tmp_dir=str(tmp_path)),
    }

    make_job(Runner(), store, Record(), Plan(FRAMES), producers,
             lambda: "2026-08-13T00:00:00+00:00", "düğün")()

    assert video_comfy.uploaded == [("P0_0.png", b"PNG")]   # the video hangs on the frame's photo
    assert ffmpeg.saw == b"MP4"                             # the sound is laid over that video
```

### Adım 2 — Testi koş, kırmızı olduğunu gör

Çalıştır: `python -m pytest queen-editor/backend/tests/test_producer_contract.py -q`

Beklenen: **FAIL** — `ComfyPhotoGenerator.generate() got an unexpected keyword argument 'source'`.
Kuyruk üç deneme yapıp `status: "error"` döndüğü için `state["status"] == "done"` de tutmaz.

### Adım 3 — Foto üreticisi sözleşmeyi karşılasın

`comfy_photo_generator.py` içinde imzayı genişlet:

```python
    def generate(self, prompt, negative, seed, model="", source=None):
        """`source` a photo's business is nobody's: a picture is made from its words alone. The
        argument is here because the queue has one call shape for every producer -- see
        ports.PhotoGenerator.
        """
```

Gövde değişmez.

### Adım 4 — Koş, kırmızının yer değiştirdiğini gör

Çalıştır: `python -m pytest queen-editor/backend/tests/test_producer_contract.py -q`

Beklenen: **FAIL**, ama artık ses satırında —
`assert store.files["P0_0_V1_0_S1_0.wav"] == b"RIFFwav"`, gelen değer
`("P0_0_V1_0.wav", b"RIFFwav")`.

### Adım 5 — Ses üreticisi yalnız bayt döndürsün

`mmaudio_generator.py` içinde docstring'i ve dönüşü düzelt:

```python
    def generate(self, prompt, negative, seed, model="", source=None):
        """`source` is the frame's video as (name, bytes); the answer is its sound as bytes.

        The name is not ours to give: the queue names every layer file from the domain's scheme
        (photo_name.layer_file), and a second name written here drifts from it -- as it had.

        `model` belongs to the port rather than to this engine: which weights are used is the
        installation's answer, and a sound job carries no choice of its own.
        """
```

ve `return` satırı:

```python
            return self._sound_for(room, video, prompt, negative or NEGATIVE, seed)
```

`name` artık kullanılmıyor; ayrıştırmayı da kaldır:

```python
        _name, data = source
```

### Adım 6 — Ses üreticisinin kendi testini yeni cevaba göre yaz

`test_mmaudio_generator.py` içinde:

```python
def test_the_answer_is_the_sound_itself(tmp_path):
    assert make(tmp_path).generate("waves", "", 1, source=SOURCE) == b"RIFFwav"
```

(eski `test_the_answer_is_a_wav_named_after_the_video` bunun yerine geçer)

### Adım 7 — Koş, yeşil olduğunu gör

Çalıştır:
`python -m pytest queen-editor/backend/tests/test_producer_contract.py queen-editor/backend/tests/test_mmaudio_generator.py -q`

Beklenen: **PASS**.

### Adım 8 — Portu sözleşmenin sahibi yap

`ports.py` içinde `PhotoGenerator`:

```python
class PhotoGenerator(Protocol):
    def generate(self, prompt: str, negative: str, seed: int, model: str = "",
                 source: tuple | None = None) -> bytes:
        """Render one layer and return its bytes -- nothing else, and no name.

        `source` is the file this layer is made from as (name, bytes): a video's photo, a sound's
        video. A layer that is made from its words alone is given None, and every producer takes
        the argument whether it uses it or not -- the queue has one call shape, not three.

        The file's name is the domain's (photo_name.layer_file), never the producer's.

        An empty model means the graph's own default.
        """
        ...
```

### Adım 9 — Takımın tamamını koş

Çalıştır: `python -m pytest queen-editor -q`

Beklenen: **PASS**, düşen test yok. Ön yüz değişmediği için `npm test` da değişmeden geçmeli:
`npm test --prefix queen-editor/frontend -- --run`.

### Adım 10 — Commit

```bash
git add queen-editor/backend docs/superpowers
git commit -m "fix(queen-editor): make every producer answer the same call"
```
