# Madde 422 — H3 videosu projenin uzunluğunda, test turunun planı

> **Koşum:** bu oturumda, satır satır, ana klasörde (`feat/queen-editor-v9`). Testler yazılır, dört
> satır koşulur, yeni testlerin kırmızısı görülür. **Commit yok:** değişiklik 421'le birlikte
> kullanıcının Changes'inde okunur.

**Hedef:** Projenin uzunluk ayarını ve kapısını; kuyruğa giren H3 videosunun o anki uzunluğu
taşıdığını ve onunla çıktığını; Tekrar dene'nin o anki uzunluğu kullandığını; uzunluğun H3'ün
Director'ına üç yerde gittiğini; WAN'ın değişmediğini; ve `main.py`'nin bunları bağladığını anlatan
testler.

**Yaklaşım:** Kuyruk ve döngü `test_photo_usecases.py`'nin sahteleriyle, yeni bir dosyada; kapı
gerçek `DriveStorage`'la elle kurulur; üreticiler kendi testlerinin sahte istemcisiyle; `main.py`
kendi testinde. Bugünkü sahte üreticiler `seconds=None` alır.

**Araçlar:** pytest (`parametrize`, `tmp_path`, `monkeypatch`), Flask test istemcisi.

**Spec:** [m422 test turu](../specs/2026-10-06-queen-editor-m422-h3-uzunlugu-testler-design.md)

## Her yere geçerli kurallar

- Test adları ve docstring'ler **İngilizce**; kullanıcının gördüğü cümle Türkçe ve birebir:
  `Video uzunluğu 4, 8 ya da 12 saniye olmalı.`, `Proje yok: <proje>`.
- Testler dört satırla koşulur; `skip` / `xfail` yok. Bu turda kaynak kod değişmiyor.
- Yeni modüller testin içinde içe aktarılır, toplanırken düşmesin.

**Arayüz — uygulama turunun vereceği:**
- `backend.features.photo_generation.data.video_length_store.DriveVideoLengthStore(storage)` —
  `project_exists(project)`, `read(project) -> int | None`, `write(project, seconds)`; dosya
  `video_length.json`.
- `backend.features.photo_generation.domain.usecases.video_length` —
  `get_video_length(lengths, project) -> int`, `save_video_length(lengths, project, seconds)`.
- `backend.features.photo_generation.presentation.video_length_routes.make_video_length_blueprint(
  get_video_length, save_video_length)` — `GET`/`PUT /api/projects/<project>/video-length`.
- `queue_layer`, `queue_references`, `regenerate`, `retry_frame`, `retry_failed` →
  `length=None` anahtar argümanı: `length(project) -> int`, ya da `None`.
- Her üretici: `generate(…, references=(), seconds=None)`.
- `backend.main._video_length` — H3 oturumunda fonksiyon, WAN'da `None`.

---

## Görev 1: Sahte üreticiler uzunluğu alır

**Dosyalar:** Değiştir: `queen-editor/backend/tests/test_photo_usecases.py`,
`queen-editor/backend/tests/test_photo_routes.py`

- [ ] **Adım 1: İki dosyada da** sahte üreticilerin imzasındaki `references=()):` →
  `references=(), seconds=None):` (test_photo_usecases'ta 18, test_photo_routes'ta 5 yer).
- [ ] **Adım 2: İki casus** (`test_progress_is_reported_before_each_frame`,
  `test_frames_added_while_the_loop_runs_are_produced_in_the_same_run`) uzunluğu da alıp geçirir:

```python
    def spy(prompt, negative, seed, model="", lora="", source=None, end=None, references=(),
            seconds=None):
        seen.append(runner.status())
        return original(prompt, negative, seed, model, lora, source, end, references, seconds)
```

```python
    def spy(prompt, negative, seed, model="", lora="", source=None, end=None, references=(),
            seconds=None):
        seen.append(prompt)
        if prompt == "ilk":
            plan_store.append("düğün", [{"number": 9, "letter": "a", "prompt": "sonradan",
                                         "negative": "", "seed": 7, "model": ""}])
        return rendering(prompt, negative, seed, model, lora, source, end, references, seconds)
```

- [ ] **Adım 3: `FakeGenerator` ne aldığını yazar** — `__init__`'te, `self.references`'tan sonra.
  Adı `lengths`, `seconds` değil: `test_variant_batch.py`'nin `BatchGenerator`'ı bu alt sınıfta
  `seconds`'ı bir grubun ne kadar çalıştığı için kullanıyor, ve aynı ad onu ezer.

```python
        # How long each render was asked to run (madde 422). Apart for the reason the others are, and
        # not called seconds: a subclass keeps how long its batch works under that name.
        self.lengths = []
```

ve `generate`'te, `self.ends.append(end)`'den sonra:

```python
        self.lengths.append(seconds)
```

## Görev 2: `backend/tests/test_video_length.py` — yeni

**Dosya:** Oluştur: `queen-editor/backend/tests/test_video_length.py`

```python
"""Madde 422: an H3 video is made at the length saved for the project -- 4, 8 or 12 seconds, 8 when
nothing is saved. The project keeps it in a file of its own behind a door that saves and reads it
(424's panel will use it), and every H3 video put in the queue carries the length of that moment and
comes out at it, even if the project's length changes while it waits.

The door's modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
from functools import partial

import pytest

from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.usecases.queue_layer import queue_layer
from backend.features.photo_generation.domain.usecases.queue_references import queue_references
from backend.features.photo_generation.domain.usecases.regenerate import regenerate
from backend.features.photo_generation.domain.usecases.retry_failed import retry_failed
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.services.drive.storage import DriveStorage
from backend.tests.test_photo_usecases import (
    FakeGenerator,
    FakeOrderStore,
    FakePlanStore,
    FakePool,
    FakeRecord,
    FakeReferenceOrders,
    FakeStore,
    frame,
    idle_runner,
    sync_runner,
)
from backend.web.app import create_app

URL = "/api/projects/düğün/video-length"
REFUSED = {"error": "Video uzunluğu 4, 8 ya da 12 saniye olmalı."}


# --- The project's setting and its door ----------------------------------------------------------

def client_over(drive):
    """The door wired by hand over a Drive folder -- the wiring main.py does. A fresh store every
    call, so a second client reads what is on disk rather than what the first one holds."""
    from backend.features.photo_generation.data.video_length_store import DriveVideoLengthStore
    from backend.features.photo_generation.domain.usecases.video_length import (
        get_video_length,
        save_video_length,
    )
    from backend.features.photo_generation.presentation.video_length_routes import (
        make_video_length_blueprint,
    )
    dist = drive.parent / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text("x", encoding="utf-8")
    lengths = DriveVideoLengthStore(DriveStorage(str(drive)))
    blueprint = make_video_length_blueprint(get_video_length=partial(get_video_length, lengths),
                                            save_video_length=partial(save_video_length, lengths))
    return create_app(dist_dir=str(dist), blueprints=[blueprint]).test_client()


@pytest.fixture
def drive(tmp_path):
    """A Drive root holding one project, düğün."""
    root = tmp_path / "drive"
    (root / "düğün").mkdir(parents=True)
    return root


def test_a_project_with_no_length_saved_is_eight(drive):
    """The user's words (v9-1, 5 Ekim): "varsalın 8 olsun"."""
    response = client_over(drive).get(URL)

    assert response.status_code == 200
    assert response.get_json() == {"seconds": 8}


@pytest.mark.parametrize("seconds", [4, 8, 12])
def test_a_length_put_down_comes_back(drive, seconds):
    client = client_over(drive)

    response = client.put(URL, json={"seconds": seconds})

    assert response.status_code == 204
    assert client.get(URL).get_json() == {"seconds": seconds}


def test_the_length_stays_with_the_project(drive):
    """"evet hatıkasnsjın": kept with the project, so it is there when the project is opened again
    -- in a file of its own, apart from the photo panel's and Referanstan's (CODE-STANDARD)."""
    client_over(drive).put(URL, json={"seconds": 12})

    assert client_over(drive).get(URL).get_json() == {"seconds": 12}
    assert (drive / "düğün" / "video_length.json").exists()
    assert not (drive / "düğün" / "settings.json").exists()
    assert not (drive / "düğün" / "reference_settings.json").exists()


@pytest.mark.parametrize("body", [{"seconds": 5}, {"seconds": 0}, {"seconds": 16},
                                  {"seconds": "8"}, {"seconds": 8.5}, {"seconds": True},
                                  {"seconds": None}, {}],
                         ids=["5", "0", "16", "text", "fraction", "true", "null", "missing"])
def test_a_length_other_than_4_8_or_12_is_refused(drive, body):
    """bool is an int in Python, and True would silently mean a one-second video."""
    client = client_over(drive)

    response = client.put(URL, json=body)

    assert response.status_code == 400
    assert response.get_json() == REFUSED
    assert client.get(URL).get_json() == {"seconds": 8}
    assert not (drive / "düğün" / "video_length.json").exists()


def test_an_unknown_project_is_a_404(drive):
    # Every folder under the root is a project: a write to an unknown name must not conjure one.
    client = client_over(drive)

    for response in (client.get("/api/projects/yok/video-length"),
                     client.put("/api/projects/yok/video-length", json={"seconds": 8})):
        assert response.status_code == 404
        assert response.get_json() == {"error": "Proje yok: yok"}
    assert not (drive / "yok").exists()


@pytest.mark.parametrize("raw", ["{ yarım", "[]", '{"seconds": 5}', '{"seconds": "12"}',
                                 '{"seconds": true}'])
def test_a_length_that_cannot_be_read_is_eight(drive, raw):
    # A file half-written or edited by hand must not keep the panel from opening.
    (drive / "düğün" / "video_length.json").write_text(raw, encoding="utf-8")

    assert client_over(drive).get(URL).get_json() == {"seconds": 8}


# --- What a job put in the queue carries -----------------------------------------------------------

def at(seconds):
    """The project's length as the queue asks for it -- main.py binds it over the store."""
    return lambda _project: seconds


def photographed(*numbers):
    """A project whose frames all have their photo."""
    store, record = FakeStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(number) for number in numbers])
    for number in numbers:
        record.append("düğün", {"file": f"{number}_a.png", "frame": f"{number}_a",
                                "layer": "photo", "status": "done"})
        store.files[f"{number}_a.png"] = b"PNG"
    return store, record, plan_store


def from_kareden(store, record, plan_store, kind=layers.VIDEO, variants=1, length=None):
    """Kareden's press, the worker never getting to it: the lines it wrote."""
    queue_layer(idle_runner(), store, record, plan_store, FakeOrderStore(), {}, lambda: "t",
                "düğün", kind, variants=variants, length=length)
    return plan_store.appended[-1]


def test_a_video_from_kareden_carries_the_projects_length():
    """Every variant too: a copy frame's video is put in the queue by the same press."""
    store, record, plan_store = photographed(0, 1)

    jobs = from_kareden(store, record, plan_store, variants=2, length=at(12))

    assert [job["seconds"] for job in jobs] == [12, 12, 12, 12]


def test_a_sound_carries_no_length():
    # Only H3's video has a length to choose; a sound is laid over the whole of its video.
    store, record, plan_store = photographed(0)
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})

    jobs = from_kareden(store, record, plan_store, kind=layers.AUDIO, length=at(12))

    assert "seconds" not in jobs[0]


def test_a_session_whose_video_model_takes_no_length_queues_none():
    """"h3e özel": a WAN session's video job carries no length, and WAN makes the video its graph
    says. A length on its line would be a lie about how long that video is."""
    store, record, plan_store = photographed(0)

    jobs = from_kareden(store, record, plan_store, length=None)

    assert "seconds" not in jobs[0]


def test_a_card_from_referanstan_carries_the_projects_length():
    """"Evet, iki sekme de" -- Referanstan's cards are made at the chosen length too."""
    plan_store = FakePlanStore()

    queue_references(idle_runner(), FakeStore(), FakeRecord(), plan_store, FakeOrderStore(),
                     FakePool(), FakeReferenceOrders(), {}, lambda: 7, lambda: "t", True,
                     "düğün", '["gotik kız"]', 2, length=at(4))

    assert [job["seconds"] for job in plan_store.appended[-1]] == [4, 4]


def make_again(kind, length):
    """Yeniden üret — yeni kare on 0_a: the line it wrote."""
    store, record, plan_store = photographed(0, 1)
    regenerate(idle_runner(), store, record, plan_store, FakeOrderStore(), {}, lambda: 7,
               lambda: "t", "düğün", "0_a", kind, "kadın dönüyor", length=length)
    return plan_store.appended[-1][0]


def test_a_video_made_again_carries_the_projects_length():
    """The frame page's Yeniden üret makes the new video at the project's length ("Evet")."""
    assert make_again(layers.VIDEO, at(8))["seconds"] == 8


def test_a_photo_made_again_carries_no_length():
    assert "seconds" not in make_again(layers.PHOTO, at(8))


def red_videos(*numbers, seconds):
    """Frames whose loop video blew up; each was put in the queue at `seconds`, with its words and
    its own seed."""
    store, record, plan_store = photographed(*numbers)
    for number in numbers:
        plan_store.frames.append({"id": f"{number}_a", "type": "video", "number": number,
                                  "variant": 0, "prompt": "kadın dönüyor", "negative": "",
                                  "seed": 5, "model": "", "mode": "loop", "seconds": seconds})
        record.mark("düğün", f"{number}_a", "video", f"{number}_a_V1_0.mp4", queue.FAILED, "t",
                    error="node 41")
    return store, record, plan_store


def test_tekrar_dene_makes_a_red_video_again_at_the_projects_length_now():
    """"Tekrar dene — bu kareye" uses the project's length ("Evet"): the video goes back in the
    queue, and it goes at the length of that moment. Everything else about it stays -- its words,
    its seed, and the picture a loop ends on."""
    store, record, plan_store = red_videos(0, seconds=4)
    generator = FakeGenerator()

    retry_frame(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                lambda: "t", "düğün", "0_a", length=at(12))

    assert generator.lengths == [12]
    assert generator.calls == [("kadın dönüyor", "", 5, "")]
    assert generator.ends == [("0_a.png", b"PNG")]


def test_tekrar_dene_at_the_length_the_video_already_has_plans_nothing_new():
    # A retry re-plans nothing when nothing moved -- the queue is exactly what it was.
    store, record, plan_store = red_videos(0, seconds=8)
    generator = FakeGenerator()

    retry_frame(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                lambda: "t", "düğün", "0_a", length=at(8))

    assert plan_store.appended == []
    assert generator.lengths == [8]


def test_retrying_them_all_makes_every_red_video_at_the_projects_length_now():
    """The queue panel's Tekrar dene is the same verb for every red tile at once."""
    store, record, plan_store = red_videos(0, 1, seconds=4)
    generator = FakeGenerator()

    retry_failed(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", length=at(12))

    assert generator.lengths == [12, 12]


# --- How long a video is made ------------------------------------------------------------------

def made(job):
    """One video job planned by hand on a photographed frame, run to the end: what the producer
    was handed, and the row the video left."""
    store, record, plan_store = photographed(0)
    plan_store.frames.append({"id": "0_a", "type": "video", "number": 0, "variant": 0,
                              "prompt": "kadın dönüyor", "negative": "", "seed": 5, "model": "",
                              **job})
    generator = FakeGenerator()
    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
             lambda: "t", "düğün")()
    return generator, next(row for row in record.rows if row.get("layer") == "video")


def test_a_video_is_made_at_the_length_its_job_carries():
    """And its row says so: 423 adds up each video's own length for the export."""
    generator, row = made({"seconds": 12})

    assert generator.lengths == [12]
    assert row["seconds"] == 12


def test_a_job_that_carries_no_length_is_made_at_the_graphs_own():
    """Every video queued before madde 422, and every one a WAN session queued: the producer is told
    nothing, and its graph says how long the video runs."""
    generator, row = made({})

    assert generator.lengths == [None]
    assert "seconds" not in row


def test_a_waiting_video_comes_out_at_the_length_it_was_added_with():
    """"Eklendiği uzunlukta": the length is on the job, not read again when its turn comes."""
    store, record, plan_store = photographed(0)
    saved = {"seconds": 8}
    from_kareden(store, record, plan_store, length=lambda _project: saved["seconds"])
    saved["seconds"] = 12
    generator = FakeGenerator()

    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
             lambda: "t", "düğün")()

    assert generator.lengths == [8]
```

## Görev 3: `backend/tests/test_comfy_h3_video_generator.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_comfy_h3_video_generator.py`

- [ ] **Adım 1: Sahte Director'ın `builder_state`'i, gönderilen grafik gibi, süreyi taşır** —
  `director()`'da:

```python
    state = {"version": 2, "mode": mode, "duration": duration, "prompt_mode": "simple",
             "simple_prompt": ""}
```

- [ ] **Adım 2: Dosyanın sonuna 422'nin testleri** (`every_mode`'dan ve `shipped_generator`'dan
  sonra):

```python
# --- Madde 422: the length the video is made at ----------------------------------------------------

def durations(client):
    """Every place the Director keeps how long the video runs: its own input, and the two builder
    states. Which one the node reads cannot be told without running it, so all three are asked."""
    said = sent_director(client)
    return (said["duration"], json.loads(said["builder_state"])["duration"],
            json.loads(said["timeline_data"])["builder_state"]["duration"])


@every_mode
def test_an_h3_video_is_made_at_the_length_it_is_handed(tmp_path, asked):
    """The graph's own note: "set duration (s)" on the Director. Nothing else in the graph counts
    frames -- the latent comes out of the Director's guide."""
    client = FakeClient()

    generator(tmp_path, client).generate("motion", "", 42, seconds=12, **asked)

    assert durations(client) == (12, 12, 12)


def test_an_fl2va_prompt_says_the_video_arrives_at_the_end_of_its_length(tmp_path):
    client = FakeClient()

    generator(tmp_path, client).generate("motion", "", 42, source=("P0_0.png", b"PNG"),
                                         end=("P1_0.png", b"END"), seconds=8)

    assert sent_director(client)["prompt"] == f"{fl2va_sentence('8.00')}\n\nmotion"


@every_mode
def test_a_video_handed_no_length_keeps_the_graphs_own(tmp_path, asked):
    """Every job queued before madde 422, and every one a WAN session queued, comes out at the
    length it was added with: the graph's own four seconds."""
    client = FakeClient()

    generator(tmp_path, client).generate("motion", "", 42, **asked)

    assert durations(client) == (4, 4, 4)


@every_mode
def test_every_h3_video_of_the_shipped_graphs_is_made_at_the_length_it_is_handed(asked):
    client = FakeClient()

    shipped_generator(client).generate("motion", "", 42, seconds=8, **asked)

    assert durations(client) == (8, 8, 8)
```

## Görev 4: `backend/tests/test_comfy_video_generator.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_comfy_video_generator.py` — sonuna:

```python
# --- Madde 422: WAN keeps its own length ------------------------------------------------------------

@pytest.mark.parametrize("asked, node, own", [
    ({"source": ("P0_0.png", b"PNG")}, "178", 5),
    ({"source": ("P0_0.png", b"PNG"), "end": ("P1_0.png", b"END")}, "335", 9),
], ids=["standard", "first-last"])
def test_wan_takes_a_length_and_runs_as_long_as_its_graph_says(tmp_path, asked, node, own):
    """"h3e özel": the queue hands every producer the job's length, and WAN keeps its graph's own."""
    client = FakeClient()

    generator(tmp_path, client).generate("kadın dönüyor", "", 42, seconds=12, **asked)

    assert client.submitted[node]["inputs"]["value"] == own
```

## Görev 5: `backend/tests/test_producer_contract.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_producer_contract.py` —
`test_each_layer_is_made_from_the_one_below_it`'ten sonra:

```python
def test_a_producer_that_makes_no_video_takes_a_length_anyway(tmp_path):
    """Madde 422: a video job carries how long it is, and the queue hands it to whichever producer
    it calls -- one call shape. A photo and a sound take it and ignore it."""
    photo = ComfyPhotoGenerator(PhotoComfy(), PHOTO_GRAPH, timeout=60).generate(
        "kraliçe tahtta", "blurry", 1, seconds=8)
    sound = MMAudioGenerator(Sampler(), Ffmpeg(), tmp_dir=str(tmp_path)).generate(
        "dalga sesi", "", 4242, source=("P0_0_V1_0.mp4", b"MP4"), seconds=8)

    assert photo == b"PNG"
    assert sound == b"RIFFwav"


def test_the_queue_hands_the_real_producers_a_video_job_that_carries_its_length(tmp_path):
    """The real loop, the real producers: WAN takes the job's length and keeps its own, and the
    run goes through."""
    store, video_comfy, ffmpeg = Store(), VideoComfy(), Ffmpeg()
    timed = [{**job, "seconds": 8} if job["type"] == "video" else job for job in FRAMES]

    state = make_job(Runner(), store, Record(), Plan(timed),
                     producers_over(video_comfy, ffmpeg, tmp_path),
                     lambda: "2026-10-06T00:00:00+00:00", "düğün")()

    assert state["status"] == "done"
    assert store.saved == ["P0_0.png", "P0_0_V1_0.mp4", "P0_0_V1_0_S1_0.wav"]
```

## Görev 6: `backend/tests/test_composition_root.py`

**Dosya:** Değiştir: `queen-editor/backend/tests/test_composition_root.py` —
`test_the_app_serves_the_agents_doors`'tan sonra:

```python
@pytest.mark.parametrize("video_model", ["", "h3"])
def test_the_app_serves_the_projects_video_length(import_main, video_model):
    """Madde 422: the door's own tests wire it by hand, so only this one reads main.py's wiring. A
    project that does not exist answers in the door's words -- a door never hung would not."""
    main = import_main(video_model)

    response = main.app.test_client().get("/api/projects/m422-yok/video-length")

    assert response.status_code == 404
    assert response.get_json() == {"error": "Proje yok: m422-yok"}


def test_an_h3_session_queues_its_videos_at_the_projects_length(import_main, monkeypatch,
                                                                tmp_path):
    """The queue's doors read the length the door saved: one store behind both."""
    (tmp_path / "düğün").mkdir()
    monkeypatch.setenv("QE_DRIVE_ROOT", str(tmp_path))
    main = import_main("h3")

    assert main._video_length("düğün") == 8
    main.app.test_client().put("/api/projects/düğün/video-length", json={"seconds": 12})
    assert main._video_length("düğün") == 12


def test_a_wan_session_queues_its_videos_with_no_length(import_main):
    """"h3e özel": a WAN video runs as long as its graph says."""
    main = import_main("")

    assert main._video_length is None
```

## Görev 7: Koşu — kırmızı

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-editor` pytest'inde 44 kırmızı — `test_video_length.py`'de 30 (kapının 19 durumu
`ModuleNotFoundError`; kuyruğun 10 testi `TypeError: … unexpected keyword argument 'length'`;
`test_a_video_is_made_at_the_length_its_job_carries` — üretici `None` aldı),
`test_comfy_h3_video_generator.py`'de 7, `test_comfy_video_generator.py`'de 2,
`test_producer_contract.py`'de 1, `test_composition_root.py`'de 4. Yeşil kalan yeni testler:
`test_a_job_that_carries_no_length_is_made_at_the_graphs_own`,
`test_a_video_handed_no_length_keeps_the_graphs_own` (3 durum),
`test_the_queue_hands_the_real_producers_a_video_job_that_carries_its_length`. Öteki her şey —
421'in testleri ve imzası değişen sahtelerle bugünkü testler — yeşil; iki frontend satırı
etkilenmez.

- [ ] **Adım 2: Commit yok.**
