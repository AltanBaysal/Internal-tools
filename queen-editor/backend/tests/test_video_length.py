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
    nothing, and its graph says how long the video runs. The row says what was made -- the
    producer's answer, this fake's graph 4 (madde 423)."""
    generator, row = made({})

    assert generator.lengths == [None]
    assert row["seconds"] == 4


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
