"""Madde 510: a video's sound turned off from its frame page; madde 515: on every video.

The user's words (29 Ekim): "bazen sesin kapatmak istiyoruz spesifik bir videonun export olurken
yapamıyoruz". Turned off, the video plays silent on its page and comes out silent in the export --
no sound at all, H3's own included -- while the others keep theirs. The sound stays in the project
and comes back when it is turned on again; it stays off until then.

Every video whose file has landed can be turned off, with or without an old MMAudio sound over it
(madde 515, "evet lütfen"): H3's video carries a sound of its own.

The door's modules are imported inside the tests: they are written after this file, and an import at
the top would stop the whole collection instead of failing these questions.
"""
import json
import threading
from functools import partial

import pytest

from backend.features.photo_generation.data.ffmpeg_video_exporter import FfmpegVideoExporter
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.domain.usecases.export_summary import export_summary
from backend.features.photo_generation.domain.usecases.run_export import run_export
from backend.services.storage.storage import Storage
from backend.tests.test_export import (
    MINUTE,
    PIECES,
    FakeExporter,
    FakeRun,
    sync_runner,
    with_videos,
)
from backend.tests.test_photo_usecases import FakeOrderStore, frame
from backend.web.app import create_app

FILE = "muted.json"


def mute_store(root):
    from backend.features.photo_generation.data.mute_store import DriveMuteStore
    return DriveMuteStore(Storage(str(root)))


@pytest.fixture
def drive(tmp_path):
    """A Drive root holding one project, düğün."""
    root = tmp_path / "drive"
    (root / "düğün").mkdir(parents=True)
    return root


# --- The store -------------------------------------------------------------------------------------

def test_a_project_with_nothing_turned_off_has_an_empty_list(drive):
    assert mute_store(drive).read("düğün") == []


def test_a_frame_turned_off_is_written_down_and_turned_on_again_is_taken_out(drive):
    store = mute_store(drive)

    assert store.put("düğün", "P0_0", True) == ["P0_0"]
    assert store.put("düğün", "P1_0", True) == ["P0_0", "P1_0"]
    assert mute_store(drive).read("düğün") == ["P0_0", "P1_0"]
    assert store.put("düğün", "P0_0", False) == ["P1_0"]
    assert json.loads((drive / "düğün" / FILE).read_text(encoding="utf-8")) == {
        "frames": ["P1_0"]}


class CountingStorage(Storage):
    """A real door that counts its writes."""

    def __init__(self, root):
        super().__init__(root)
        self.writes = 0

    def write_text(self, folder, name, text):
        self.writes += 1
        return super().write_text(folder, name, text)


def test_asking_for_what_is_already_so_writes_nothing(drive):
    """A round trip to Drive saved: the list would come out the same."""
    from backend.features.photo_generation.data.mute_store import DriveMuteStore
    storage = CountingStorage(str(drive))
    store = DriveMuteStore(storage)
    store.put("düğün", "P0_0", True)

    assert store.put("düğün", "P0_0", True) == ["P0_0"]
    assert store.put("düğün", "P9_0", False) == ["P0_0"]
    assert storage.writes == 1


@pytest.mark.parametrize("text", ["{bozuk", '{"frames": "P0_0"}', '["P0_0"]',
                                  '{"frames": [1]}'],
                         ids=["not-json", "not-a-list", "not-an-object", "not-names"])
def test_a_file_that_cannot_be_read_is_never_taken_as_empty(drive, text):
    """Read as empty, the export would let every turned-off sound back in, and a press would write
    the other frames' marks away."""
    (drive / "düğün" / FILE).write_text(text, encoding="utf-8")
    store = mute_store(drive)

    with pytest.raises(OSError, match="düğün/muted.json okunamıyor"):
        store.read("düğün")
    with pytest.raises(OSError, match="düğün/muted.json okunamıyor"):
        store.put("düğün", "P1_0", True)
    assert (drive / "düğün" / FILE).read_text(encoding="utf-8") == text


class SlowStorage(Storage):
    """A door whose first read of the list waits a moment -- long enough for a second press to
    read the same list, when nothing keeps it out."""

    def __init__(self, root):
        super().__init__(root)
        self.reads = 0
        self.second = threading.Event()

    def read_text(self, folder, name):
        self.reads += 1
        if self.reads == 1:
            # Released at once by a second read that got in; waited out when none could.
            self.second.wait(0.3)
        else:
            self.second.set()
        return super().read_text(folder, name)


def test_two_presses_at_once_both_stay(drive):
    """The list is read, changed and written back: two presses reading the same list would each
    write their own frame alone."""
    from backend.features.photo_generation.data.mute_store import DriveMuteStore
    store = DriveMuteStore(SlowStorage(str(drive)))

    first = threading.Thread(target=store.put, args=("düğün", "P0_0", True))
    first.start()
    store.put("düğün", "P1_0", True)
    first.join()

    assert sorted(mute_store(drive).read("düğün")) == ["P0_0", "P1_0"]


# --- The door --------------------------------------------------------------------------------------

def videos_on(root, *frames, failed=(), sound=()):
    """A real photo record over the project: each frame with a video, the ones in `failed` with a
    video that blew up, the ones in `sound` with an old MMAudio sound over it too."""
    record = DrivePhotoRecord(Storage(str(root)))
    for fid in frames:
        record.append("düğün", {"file": f"{fid}_V1_0.mp4", "frame": fid, "layer": "video",
                                "status": "failed" if fid in failed else "done"})
        if fid in sound:
            record.append("düğün", {"file": f"{fid}_V1_0_S1_0.wav", "frame": fid,
                                    "layer": "audio", "status": "done"})
    return record


def client_over(drive, record=None):
    """The door wired by hand over a Drive folder -- the wiring main.py does. A fresh store every
    call, so a second client reads what is on disk rather than what the first one holds."""
    from backend.features.photo_generation.domain.usecases.mute import get_muted, set_muted
    from backend.features.photo_generation.presentation.mute_routes import make_mute_blueprint
    dist = drive.parent / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "index.html").write_text("x", encoding="utf-8")
    mutes = mute_store(drive)
    record = record or DrivePhotoRecord(Storage(str(drive)))
    blueprint = make_mute_blueprint(get_muted=partial(get_muted, mutes),
                                    set_muted=partial(set_muted, mutes, record))
    return create_app(dist_dir=str(drive.parent / "dist"), blueprints=[blueprint]).test_client()


LIST = "/api/projects/düğün/muted"


def press(fid):
    return f"/api/projects/düğün/frames/{fid}/muted"


def test_nothing_is_turned_off_to_begin_with(drive):
    response = client_over(drive).get(LIST)

    assert response.status_code == 200
    assert response.get_json() == {"frames": []}


def test_a_sound_turned_off_stays_off_and_comes_back_when_turned_on(drive):
    """"kapatılan ses, yeniden açılana kadar kapalı kalır" -- a fresh client reads it off disk."""
    videos_on(drive, "P0_0", "P1_0")
    client = client_over(drive)

    response = client.put(press("P0_0"), json={"muted": True})

    assert response.status_code == 200
    assert response.get_json() == {"frames": ["P0_0"]}
    assert client_over(drive).get(LIST).get_json() == {"frames": ["P0_0"]}

    assert client.put(press("P0_0"), json={"muted": False}).get_json() == {"frames": []}
    assert client_over(drive).get(LIST).get_json() == {"frames": []}


def test_a_video_with_an_old_sound_over_it_is_turned_off_too(drive):
    """Its old MMAudio sound and the video's own go out together (madde 515)."""
    videos_on(drive, "P0_0", sound=("P0_0",))

    response = client_over(drive).put(press("P0_0"), json={"muted": True})

    assert response.status_code == 200
    assert response.get_json() == {"frames": ["P0_0"]}


@pytest.mark.parametrize("failed", [False, True], ids=["no-video", "video-blew-up"])
def test_a_frame_whose_video_has_not_landed_cannot_be_turned_off(drive, failed):
    """Only a video that is there has a sound to turn off -- the switch is drawn on no other."""
    videos_on(drive, "P0_0", failed=("P0_0",) if failed else ())
    client = client_over(drive)

    response = client.put(press("P0_0" if failed else "P5_0"), json={"muted": True})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": f"Bu karenin videosu yok: {'P0_0' if failed else 'P5_0'}"}
    assert not (drive / "düğün" / FILE).exists()


def test_turning_on_is_taken_whatever_the_frame_holds(drive):
    """A mark left on a frame whose video has gone can still be taken off."""
    videos_on(drive, "P0_0")
    client = client_over(drive)
    client.put(press("P0_0"), json={"muted": True})
    (drive / "düğün" / "photos.jsonl").unlink()

    response = client.put(press("P0_0"), json={"muted": False})

    assert response.status_code == 200
    assert response.get_json() == {"frames": []}


@pytest.mark.parametrize("body", [{"muted": 1}, {"muted": "true"}, {"muted": None}, {}],
                         ids=["1", "text", "null", "missing"])
def test_anything_but_off_or_on_is_refused(drive, body):
    videos_on(drive, "P0_0")
    client = client_over(drive)

    response = client.put(press("P0_0"), json=body)

    assert response.status_code == 400
    assert response.get_json() == {"error": "Ses kapalı ya da açık olmalı."}
    assert not (drive / "düğün" / FILE).exists()


def test_an_unknown_project_is_a_404(drive):
    # Every folder under the root is a project: a write to an unknown name must not conjure one.
    client = client_over(drive)

    for response in (client.get("/api/projects/yok/muted"),
                     client.put("/api/projects/yok/frames/P0_0/muted", json={"muted": False})):
        assert response.status_code == 404
        assert response.get_json() == {"error": "Proje yok: yok"}
    assert not (drive / "yok").exists()


def test_a_list_that_cannot_be_read_reaches_the_screen_in_its_own_words(drive):
    (drive / "düğün" / FILE).write_text("{bozuk", encoding="utf-8")

    response = client_over(drive).get(LIST)

    assert response.status_code == 503
    assert "düğün/muted.json okunamıyor" in response.get_json()["error"]


# --- The export ------------------------------------------------------------------------------------

class FakeMutes:
    """The list as the store answers it, and how many times it was asked."""

    def __init__(self, frames=(), fails=None):
        self.frames = list(frames)
        self.fails = fails
        self.reads = 0

    def read(self, project):
        self.reads += 1
        if self.fails:
            raise OSError(self.fails)
        return list(self.frames)


class SilencingExporter(FakeExporter):
    """FakeExporter, with the silent cut written into the same list of pieces."""

    def silent(self, video, target):
        self.pieces.append((video, "SESSİZ", target))


def export(mutes, mode="separate", sound_on=("0_a", "1_a")):
    store, record, plan_store = with_videos(sound_on=sound_on)
    exporter = SilencingExporter()
    run_export(sync_runner(), store, record, plan_store, FakeOrderStore(), exporter,
               lambda: MINUTE, "düğün", mode, mutes=mutes)
    return store, exporter


@pytest.mark.parametrize("mode", ["separate", "merged"])
def test_a_turned_off_video_is_cut_with_no_sound_and_the_others_keep_theirs(mode):
    _store, exporter = export(FakeMutes(["0_a"]), mode=mode)

    assert exporter.pieces == [
        ("/fake/düğün/0_a_V1_0.mp4", "SESSİZ", f"{PIECES}/01.mp4"),
        ("/fake/düğün/1_a_V1_0.mp4", "/fake/düğün/1_a_V1_0_S1_0.wav", f"{PIECES}/02.mp4")]
    if mode == "merged":
        # In its place in the join: the order is the gallery's, sound or none.
        assert exporter.merged[0] == [f"{PIECES}/01.mp4", f"{PIECES}/02.mp4"]


def test_a_turned_off_video_with_no_sound_layer_loses_its_own_sound():
    """An H3 video carries a sound of its own, so a mark on one with no layer over it counts too
    (madde 515): cut silent, where a plain copy would keep H3's sound."""
    _store, exporter = export(FakeMutes(["1_a"]), sound_on=("0_a",))

    assert exporter.pieces == [
        ("/fake/düğün/0_a_V1_0.mp4", "/fake/düğün/0_a_V1_0_S1_0.wav", f"{PIECES}/01.mp4"),
        ("/fake/düğün/1_a_V1_0.mp4", "SESSİZ", f"{PIECES}/02.mp4")]


def test_a_video_left_on_keeps_its_own_sound():
    """No layer and no mark: copied with H3's sound, as it always was."""
    _store, exporter = export(FakeMutes(["0_a"]), sound_on=())

    assert exporter.pieces[1] == ("/fake/düğün/1_a_V1_0.mp4", None, f"{PIECES}/02.mp4")


def test_the_list_is_read_once_an_export():
    mutes = FakeMutes(["0_a"])

    export(mutes)

    assert mutes.reads == 1


def test_a_list_that_cannot_be_read_stops_the_export_before_its_folder_is_opened():
    """Read as empty it would put the turned-off sounds back; read after the folder is opened it
    would leave a folder to take back."""
    store, record, plan_store = with_videos(sound_on=("0_a",))
    runner = sync_runner()

    runner.start("separate", lambda: run_export(
        runner, store, record, plan_store, FakeOrderStore(), SilencingExporter(),
        lambda: MINUTE, "düğün", "separate",
        mutes=FakeMutes(fails="düğün/muted.json okunamıyor: bozuk")))

    assert runner.state()["separate"]["error"] == "düğün/muted.json okunamıyor: bozuk"
    assert "open_export" not in store.order


def test_a_silent_cut_copies_the_picture_and_takes_no_sound():
    """"Sessiz, hiç ses yok demek": an H3 video carries a sound of its own (madde 243), and a plain
    copy would keep it."""
    run = FakeRun()

    FfmpegVideoExporter(run=run).silent("0.mp4", "01.mp4")

    assert run.calls[0] == ["ffmpeg", "-y", "-i", "0.mp4", "-c", "copy", "-an", "01.mp4"]


# --- The export summary ----------------------------------------------------------------------------

def summary(mutes, sound_on):
    store, record, plan_store = with_videos(sound_on=sound_on)
    return export_summary(record, store, plan_store, FakeOrderStore(), lambda: 4, "düğün",
                          mutes=mutes)


def test_the_summary_counts_the_turned_off_sounds():
    said = summary(FakeMutes(["0_a"]), sound_on=("0_a",))

    assert said["muted"] == 1


def test_the_summary_counts_a_turned_off_video_with_no_sound_layer():
    said = summary(FakeMutes(["0_a", "1_a"]), sound_on=("0_a",))

    assert said["muted"] == 2


def test_the_summary_counts_no_mark_on_a_frame_with_no_video():
    """The export takes no such frame, so there is no sound of its to turn off. The frame is a real
    one of the project's, a photo with no video, marked beside a video that counts."""
    store, record, plan_store = with_videos()
    plan_store.frames.append(frame(2))
    record.append("düğün", {"file": "2_a.png", "frame": "2_a", "layer": "photo", "status": "done"})

    said = export_summary(record, store, plan_store, FakeOrderStore(), lambda: 4, "düğün",
                          mutes=FakeMutes(["0_a", "2_a"]))

    assert said["withoutVideo"] == 1
    assert said["muted"] == 1


def test_the_summary_reads_the_list_once():
    mutes = FakeMutes()

    summary(mutes, sound_on=())

    assert mutes.reads == 1
