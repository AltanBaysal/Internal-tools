"""Madde 426: Mutlu son -- a switch in the video panel, off until it is turned on, kept with the
project the way the length is (madde 422). A video put in the queue while it is on carries it, and
is made with HMCumshot and asked of Queen AI with its ending; one put in while it is off carries
nothing, and is made exactly as before.

The door's modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
from functools import partial

import pytest

from backend.features.photo_generation.domain import layers
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
    FakeWriter,
    idle_runner,
    sync_runner,
)
from backend.tests.test_video_length import at, photographed, red_videos
from backend.web.app import create_app

URL = "/api/projects/düğün/happy-ending"
REFUSED = {"error": "Mutlu son açık ya da kapalı olmalı."}


# --- The project's switch and its door -----------------------------------------------------------

def client_over(drive):
    """The door wired by hand over a Drive folder -- the wiring main.py does. A fresh store every
    call, so a second client reads what is on disk rather than what the first one holds."""
    from backend.features.photo_generation.data.happy_ending_store import DriveHappyEndingStore
    from backend.features.photo_generation.domain.usecases.happy_ending import (
        get_happy_ending,
        save_happy_ending,
    )
    from backend.features.photo_generation.presentation.happy_ending_routes import (
        make_happy_ending_blueprint,
    )
    dist = drive.parent / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text("x", encoding="utf-8")
    switches = DriveHappyEndingStore(DriveStorage(str(drive)))
    blueprint = make_happy_ending_blueprint(get_happy_ending=partial(get_happy_ending, switches),
                                            save_happy_ending=partial(save_happy_ending, switches))
    return create_app(dist_dir=str(dist), blueprints=[blueprint]).test_client()


@pytest.fixture
def drive(tmp_path):
    """A Drive root holding one project, düğün."""
    root = tmp_path / "drive"
    (root / "düğün").mkdir(parents=True)
    return root


def test_a_project_with_nothing_saved_has_it_off(drive):
    """Hizalama, 8 Ekim: "varsayılanı kapalı"."""
    response = client_over(drive).get(URL)

    assert response.status_code == 200
    assert response.get_json() == {"on": False}


@pytest.mark.parametrize("on", [True, False])
def test_the_switch_put_down_comes_back(drive, on):
    client = client_over(drive)

    response = client.put(URL, json={"on": on})

    assert response.status_code == 204
    assert client.get(URL).get_json() == {"on": on}


def test_the_switch_stays_with_the_project_in_a_file_of_its_own(drive):
    """"uzunluk gibi projeye kaydedilir": there when the project is opened again -- in its own file,
    apart from the length's, which answers another question (CODE-STANDARD)."""
    client_over(drive).put(URL, json={"on": True})

    assert client_over(drive).get(URL).get_json() == {"on": True}
    assert (drive / "düğün" / "happy_ending.json").exists()
    assert not (drive / "düğün" / "video_length.json").exists()
    assert not (drive / "düğün" / "settings.json").exists()


@pytest.mark.parametrize("body", [{"on": 1}, {"on": 0}, {"on": "true"}, {"on": None}, {}],
                         ids=["1", "0", "text", "null", "missing"])
def test_anything_but_on_or_off_is_refused(drive, body):
    """1 is not True here: a switch is on or off, and a number would be a guess at which."""
    client = client_over(drive)

    response = client.put(URL, json=body)

    assert response.status_code == 400
    assert response.get_json() == REFUSED
    assert client.get(URL).get_json() == {"on": False}
    assert not (drive / "düğün" / "happy_ending.json").exists()


def test_an_unknown_project_is_a_404(drive):
    # Every folder under the root is a project: a write to an unknown name must not conjure one.
    client = client_over(drive)

    for response in (client.get("/api/projects/yok/happy-ending"),
                     client.put("/api/projects/yok/happy-ending", json={"on": True})):
        assert response.status_code == 404
        assert response.get_json() == {"error": "Proje yok: yok"}
    assert not (drive / "yok").exists()


@pytest.mark.parametrize("raw", ["{ yarım", "[]", '{"on": 1}', '{"on": "true"}', "{}"])
def test_a_switch_that_cannot_be_read_is_off(drive, raw):
    # A file half-written or edited by hand must not keep the panel from opening.
    (drive / "düğün" / "happy_ending.json").write_text(raw, encoding="utf-8")

    assert client_over(drive).get(URL).get_json() == {"on": False}


# --- What a job put in the queue carries -----------------------------------------------------------

def switched(on):
    """The project's switch as the queue asks for it -- main.py binds it over the store."""
    return lambda _project: on


def kareden(kind=layers.VIDEO, variants=1, ending=None, length=None):
    store, record, plan_store = photographed(0, 1)
    if kind == layers.AUDIO:
        for number in (0, 1):
            record.append("düğün", {"file": f"{number}_a_V1_0.mp4", "frame": f"{number}_a",
                                    "layer": "video", "status": "done"})
    queue_layer(idle_runner(), store, record, plan_store, FakeOrderStore(), {}, lambda: "t",
                "düğün", kind, variants=variants, length=length, ending=ending)
    return plan_store.appended[-1]


def test_a_video_from_kareden_carries_the_switch_when_it_is_on():
    """Every variant too: a copy frame's video is put in the queue by the same press."""
    jobs = kareden(variants=2, ending=switched(True))

    assert [job["happyEnding"] for job in jobs] == [True, True, True, True]


def test_a_video_put_in_while_it_is_off_carries_nothing_about_it():
    """Off, the plan line is exactly what it was before madde 426."""
    jobs = kareden(ending=switched(False), length=at(8))

    assert [set(job) - {"id", "type", "number", "variant", "prompt", "negative", "seed",
                        "model", "mode"} for job in jobs] == [{"seconds"}, {"seconds"}]


def test_a_sound_carries_no_switch():
    # The ending is the video's; a sound is laid over the whole of it.
    jobs = kareden(kind=layers.AUDIO, ending=switched(True))

    assert all("happyEnding" not in job for job in jobs)


def test_a_card_from_referanstan_carries_the_switch():
    plan_store = FakePlanStore()

    queue_references(idle_runner(), FakeStore(), FakeRecord(), plan_store, FakeOrderStore(),
                     FakePool(), FakeReferenceOrders(), {}, lambda: 7, lambda: "t", "düğün",
                     '["gotik kız"]', 2, length=at(4), ending=switched(True))

    assert [(job["seconds"], job["happyEnding"]) for job in plan_store.appended[-1]] == \
        [(4, True), (4, True)]


def make_again(kind, ending):
    """Yeniden üret — yeni kare on 0_a: the line it wrote."""
    store, record, plan_store = photographed(0, 1)
    regenerate(idle_runner(), store, record, plan_store, FakeOrderStore(), {}, lambda: 7,
               lambda: "t", "düğün", "0_a", kind, "kadın dönüyor", ending=ending)
    return plan_store.appended[-1][0]


def test_a_video_made_again_carries_the_switch():
    assert make_again(layers.VIDEO, switched(True))["happyEnding"] is True


def test_a_video_made_again_while_it_is_off_carries_nothing_about_it():
    assert "happyEnding" not in make_again(layers.VIDEO, switched(False))


def test_a_photo_made_again_carries_no_switch():
    assert "happyEnding" not in make_again(layers.PHOTO, switched(True))


def test_tekrar_dene_makes_a_red_video_again_with_the_switch_as_it_is_now():
    """Tekrar dene puts the video back the way it puts it back at the length of now (madde 422).
    Everything else about it stays -- its words, its seed, and the picture a loop ends on."""
    store, record, plan_store = red_videos(0, seconds=8)
    generator = FakeGenerator()

    retry_frame(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                lambda: "t", "düğün", "0_a", length=at(8), ending=switched(True))

    assert generator.endings == [True]
    assert generator.calls == [("kadın dönüyor", "", 5, "")]
    assert generator.ends == [("0_a.png", b"PNG")]


def test_tekrar_dene_takes_the_ending_off_once_the_switch_is_off():
    store, record, plan_store = red_videos(0, seconds=8)
    plan_store.frames[-1]["happyEnding"] = True
    generator = FakeGenerator()

    retry_frame(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                lambda: "t", "düğün", "0_a", length=at(8), ending=switched(False))

    assert generator.endings == [False]
    assert "happyEnding" not in plan_store.appended[-1][0]


def test_tekrar_dene_with_nothing_moved_plans_nothing_new():
    # A retry re-plans nothing when nothing moved -- the queue is exactly what it was.
    store, record, plan_store = red_videos(0, seconds=8)
    plan_store.frames[-1]["happyEnding"] = True
    generator = FakeGenerator()

    retry_frame(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                lambda: "t", "düğün", "0_a", length=at(8), ending=switched(True))

    assert plan_store.appended == []
    assert generator.endings == [True]


def test_tekrar_dene_writes_one_line_when_the_length_and_the_switch_both_moved():
    store, record, plan_store = red_videos(0, seconds=4)

    retry_frame(idle_runner(), store, record, plan_store, {}, lambda: "t", "düğün", "0_a",
                length=at(12), ending=switched(True))

    assert len(plan_store.appended) == 1
    line = plan_store.appended[0][0]
    assert (line["seconds"], line["happyEnding"]) == (12, True)


def test_retrying_them_all_makes_every_red_video_with_the_switch_as_it_is_now():
    """The queue panel's Tekrar dene is the same verb for every red tile at once."""
    store, record, plan_store = red_videos(0, 1, seconds=8)
    generator = FakeGenerator()

    retry_failed(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
                 lambda: "t", "düğün", length=at(8), ending=switched(True))

    assert generator.endings == [True, True]


# --- What the loop hands the producer and the writer ------------------------------------------------

def run_one(job, writer=None):
    """One video job planned by hand on a photographed frame, run to the end."""
    store, record, plan_store = photographed(0)
    # Words on the photo, so a writer has something to write from (run_loop._has_words).
    record.rows[0]["prompt"] = "kırmızı elbiseli kadın"
    plan_store.frames.append({"id": "0_a", "type": "video", "number": 0, "variant": 0,
                              "prompt": "" if writer else "kadın dönüyor", "negative": "",
                              "seed": 5, "model": "", **job})
    generator = FakeGenerator()
    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
             lambda: "t", "düğün", writers={layers.VIDEO: writer} if writer else None)()
    return generator


@pytest.mark.parametrize("job, handed", [({"happyEnding": True}, True), ({}, False)],
                         ids=["on", "off"])
def test_the_producer_is_handed_the_switch_its_job_carries(job, handed):
    assert run_one(job).endings == [handed]


@pytest.mark.parametrize("job, handed", [({"happyEnding": True}, True), ({}, False)],
                         ids=["on", "off"])
def test_the_writer_is_handed_the_switch_its_job_carries(job, handed):
    """The ending is asked for in the prompt as well (the LoRA author: "this is mostly prompting")."""
    writer = FakeWriter()

    run_one(job, writer)

    assert writer.endings == [handed]


def test_a_waiting_video_comes_out_with_the_switch_it_was_added_with():
    """Like the length: the switch is on the job, not read again when its turn comes."""
    store, record, plan_store = photographed(0)
    saved = {"on": True}
    queue_layer(idle_runner(), store, record, plan_store, FakeOrderStore(), {}, lambda: "t",
                "düğün", layers.VIDEO, ending=lambda _project: saved["on"])
    saved["on"] = False
    generator = FakeGenerator()

    make_job(sync_runner(), store, record, plan_store, {layers.VIDEO: generator},
             lambda: "t", "düğün")()

    assert generator.endings == [True]
