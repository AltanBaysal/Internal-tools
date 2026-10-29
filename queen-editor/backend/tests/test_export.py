import inspect
import json
import os
from types import SimpleNamespace

import pytest

from backend import config
from backend.features.photo_generation.data.comfy_h3_video_generator import (
    DIRECTOR_NODE as H3_DIRECTOR,
)
from backend.features.photo_generation.data.comfy_h3_video_generator import SIZES as H3_SIZES
from backend.features.photo_generation.data.ffmpeg_video_exporter import (
    MERGED_FPS,
    MERGED_HEIGHT,
    MERGED_WIDTH,
    SOUND_BITRATE,
    FfmpegVideoExporter,
)
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.domain.orientation import LANDSCAPE, PORTRAIT
from backend.features.photo_generation.domain.usecases.run_export import run_export
from backend.features.photo_generation.export_runner import ExportRunner
from backend.services.storage import storage as storage_module
from backend.services.storage.storage import Storage
from backend.tests.test_photo_usecases import (
    FakeOrderStore,
    FakePlanStore,
    FakeRecord,
    FakeStore,
    NoMutes,
    frame,
)

MINUTE = "2026-08-12 14-32"         # the export's opening, which names its dated folder
FOLDER = f"/fake/queenEditorExport/{MINUTE} düğün"
# Not under /fake: every piece is cut on the machine's own disk, never on Drive (madde 235, 472).
PIECES = "/tmp/fake-pieces"


class ExportStore(FakeStore):
    """FakeStore with what an export asks of it, and a note of what it wrote and removed."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.removed = []
        self.photos = []
        self.videos = []
        self.exports = []
        self.order = []               # what happened, in the order it happened

    def file_path(self, project, filename):
        return f"/fake/{project}/{filename}"

    def open_export(self, project, stamp):
        """The real one opens the export's folder in the exports' root; that is tested against a
        real folder in test_photo_store.py."""
        self.order.append("open_export")
        return self._folder(project, stamp)

    def _folder(self, project, stamp):
        return f"/fake/queenEditorExport/{stamp} {project}"

    def piece_path(self, pieces, filename):
        return f"{pieces}/{filename}"

    def make_pieces_dir(self):
        """Where every piece is cut -- the real one answers with a folder on the machine's own
        disk, and the path here is outside the Drive root on purpose."""
        self.order.append("make_pieces_dir")
        return PIECES

    def remove_pieces(self, path):
        self.removed.append(path)

    def remove_export(self, project, stamp, videos, in_use):
        """What the run handed its cleanup is written down; what the real one does with it is
        tested against real folders in test_photo_store.py."""
        self.removed.append(self._folder(project, stamp))
        self.taken_back = (list(videos), in_use)

    def copy_photo(self, project, photo, stamp, filename):
        """Every call is written down and none is skipped.

        The real store refuses a target that is already there, and that refusal is tested against a
        real folder next door. A fake that copied the rule would leave these tests sinning against
        their own double instead of the code.
        """
        self.photos.append((photo, stamp, filename))
        self.order.append("copy_photo")

    def copy_video(self, project, stamp, source, filename):
        """A separate export's piece, carried to Drive as soon as it is cut."""
        self.videos.append((source, stamp, filename))
        self.order.append("copy_video")

    def copy_export(self, project, stamp, source, filename):
        """The merged file's one trip to Drive, written down.

        The real one lands in a single save, and that is tested against a real folder in
        test_photo_store.py: ffmpeg writes the join on the machine's own disk, and Drive sees the
        file only once it is whole (madde 282).
        """
        self.exports.append((source, stamp, filename))
        self.order.append("copy_export")


class FakeExporter:
    def __init__(self, fails_on=None, store=None):
        self.pieces = []
        self.merged = None
        self.fails_on = fails_on          # the target whose write blows up
        # When a store is handed over, the export's steps are written into its one timeline: the
        # copy to Drive has to come after the join, and the videos all have to come before the
        # first photo (madde 289).
        self.store = store

    def piece(self, video, audio, target):
        if target == self.fails_on:
            raise RuntimeError("ffmpeg: disk dolu")
        self.pieces.append((video, audio, target))
        if self.store is not None:
            self.store.order.append("piece")

    def merge(self, pieces, target):
        if target == self.fails_on:
            raise RuntimeError("ffmpeg: disk dolu")
        self.merged = (list(pieces), target)
        if self.store is not None:
            self.store.order.append("merge")


def sync_runner():
    return ExportRunner(spawn=lambda fn: fn())


def with_videos(sound_on=()):
    """A project whose two frames both carry a video; `sound_on` names the ones with a sound too."""
    store, record = ExportStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0), frame(1)])
    for number in (0, 1):
        fid = f"{number}_a"
        record.append("düğün", {"file": f"{fid}.png", "frame": fid, "layer": "photo",
                                "status": "done"})
        record.append("düğün", {"file": f"{fid}_V1_0.mp4", "frame": fid, "layer": "video",
                                "status": "done"})
        if fid in sound_on:
            record.append("düğün", {"file": f"{fid}_V1_0_S1_0.wav", "frame": fid, "layer": "audio",
                                    "status": "done"})
    return store, record, plan_store


def with_a_copy():
    """One picture, two videos: the second frame is a copy and holds the first one's photo.

    That is what a copy frame is -- it produces no picture of its own, its photo row names the
    source's file -- and it is why one export used to write the same image under two numbers
    (madde 236).
    """
    store, record = ExportStore(), FakeRecord()
    plan_store = FakePlanStore(frames=[frame(0), frame(0, letter="b")])
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done"})
    record.append("düğün", {"file": "0_a.png", "frame": "0_b", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "0_b_V1_0.mp4", "frame": "0_b", "layer": "video",
                            "status": "done"})
    return store, record, plan_store


def export(store, record, plan_store, exporter, mode="separate", runner=None):
    return run_export(runner or sync_runner(), store, record, plan_store, FakeOrderStore(),
                      exporter, lambda: MINUTE, "düğün", mode, mutes=NoMutes())


def test_separate_export_numbers_the_videos_from_the_foot_of_the_gallery():
    store, record, plan_store = with_videos()
    exporter = FakeExporter()

    folder = export(store, record, plan_store, exporter)

    # The gallery reads 1_a above 0_a; the sequence starts at its foot, so 0_a is 01.
    assert [target for _v, _a, target in exporter.pieces] == [
        f"{PIECES}/01.mp4", f"{PIECES}/02.mp4"]
    assert [video for video, _a, _t in exporter.pieces] == [
        "/fake/düğün/0_a_V1_0.mp4", "/fake/düğün/1_a_V1_0.mp4"]
    assert [name for _s, _stamp, name in store.videos] == ["01.mp4", "02.mp4"]
    assert folder == FOLDER


class DriveGoneAtOpening(ExportStore):
    """The mount has dropped before the run begins: the export's folder cannot be opened."""

    def open_export(self, project, stamp):
        raise OSError(107, "Transport endpoint is not connected")


def test_an_export_opens_its_place_on_drive_before_anything_is_cut():
    """Madde 473, 494: the export's folder sits directly under the exports' root, where no save
    opens a folder, so the run opens it first -- and before the machine's own pieces folder, so a
    mount that refuses leaves nothing to clean up on either disk."""
    _, record, plan_store = with_videos()
    store = DriveGoneAtOpening()
    exporter = FakeExporter()

    with pytest.raises(OSError):
        export(store, record, plan_store, exporter)

    assert store.order == []
    assert exporter.pieces == [] and store.removed == []


def test_a_frame_with_a_sound_is_written_with_it():
    store, record, plan_store = with_videos(sound_on=("0_a",))
    exporter = FakeExporter()

    export(store, record, plan_store, exporter)

    assert exporter.pieces[0][1] == "/fake/düğün/0_a_V1_0_S1_0.wav"
    assert exporter.pieces[1][1] is None       # nothing to lay over the second one


def test_a_sound_that_blew_up_leaves_its_video_silent():
    store, record, plan_store = with_videos(sound_on=("0_a",))
    record.mark("düğün", "0_a", "audio", "0_a_V1_0_S1_0.wav", "failed", "t")
    exporter = FakeExporter()

    export(store, record, plan_store, exporter)

    assert exporter.pieces[0][1] is None


def test_a_frame_with_no_video_is_skipped():
    store, record, plan_store = with_videos()
    record.append("düğün", {"file": "2_a.png", "frame": "2_a", "layer": "photo", "status": "done"})
    exporter = FakeExporter()

    export(store, record, plan_store, exporter)

    assert len(exporter.pieces) == 2


def test_every_exported_frame_leaves_its_photo_beside_its_video():
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter())

    # The number is the video's own: the frame written as 01.mp4 puts its picture in as 01.png, so
    # the photos folder reads as the same sequence and nothing has to be matched up by hand.
    assert store.photos == [
        ("0_a.png", MINUTE, "01.png"),
        ("1_a.png", MINUTE, "02.png"),
    ]


def test_a_photo_keeps_the_extension_it_was_saved_with():
    store, record, plan_store = with_videos()
    record.append("düğün", {"file": "2_a.jpg", "frame": "2_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "2_a_V1_0.mp4", "frame": "2_a", "layer": "video",
                            "status": "done"})

    export(store, record, plan_store, FakeExporter())

    # The number belongs to the export, the extension to the picture. Writing .png into the code
    # would name the first jpg wrongly and there would be nothing on screen to say so.
    #
    # 2_a leads because the plan does not know it: a frame the plan lost is added at the end of the
    # gallery, and the export reads the gallery from its foot. The whole list is written out rather
    # than the one row, so the order is on the page instead of inside an index.
    assert store.photos == [
        ("2_a.jpg", MINUTE, "01.jpg"),
        ("0_a.png", MINUTE, "02.png"),
        ("1_a.png", MINUTE, "03.png"),
    ]


def test_a_frame_with_no_video_leaves_no_photo_either():
    store, record, plan_store = with_videos()
    record.append("düğün", {"file": "2_a.png", "frame": "2_a", "layer": "photo", "status": "done"})

    export(store, record, plan_store, FakeExporter())

    # The photos folder is the video list, picture for picture: a frame the sequence does not hold
    # has no number to be filed under.
    assert len(store.photos) == 2


def test_frames_sharing_one_photo_leave_one_picture_in_the_export():
    """The folder is read by a person using the pictures, and the same image three times over is
    what the user kept running into (madde 236)."""
    store, record, plan_store = with_a_copy()

    export(store, record, plan_store, FakeExporter())

    assert store.photos == [("0_a.png", MINUTE, "01.png")]


def test_a_shared_photo_is_filed_under_the_first_frame_that_uses_it():
    """The number stays the frame's own, gaps and all: it is what says which video the picture
    belongs to, and consecutive numbering would buy tidiness by cutting that tie."""
    store, record, plan_store = with_a_copy()
    record.append("düğün", {"file": "1_a.png", "frame": "1_a", "layer": "photo", "status": "done"})
    record.append("düğün", {"file": "1_a_V1_0.mp4", "frame": "1_a", "layer": "video",
                            "status": "done"})

    export(store, record, plan_store, FakeExporter())

    # 1_a leads: the plan does not know it, and a frame the plan lost stands at the end of the
    # gallery, which the export reads from its foot. So the shared picture is 02, not 01, and the
    # copy frame's 03 writes nothing.
    assert store.photos == [
        ("1_a.png", MINUTE, "01.png"),
        ("0_a.png", MINUTE, "02.png"),
    ]


def test_a_copy_frames_video_is_written_all_the_same():
    """Only the picture is shared. The copy frame's video is its own file and its own place in the
    sequence."""
    store, record, plan_store = with_a_copy()
    exporter = FakeExporter()

    export(store, record, plan_store, exporter)

    assert [name for _s, _stamp, name in store.videos] == ["01.mp4", "02.mp4"]
    assert [video for video, _a, _t in exporter.pieces] == [
        "/fake/düğün/0_a_V1_0.mp4", "/fake/düğün/0_b_V1_0.mp4"]


def test_a_merged_export_writes_the_shared_photo_once_too():
    store, record, plan_store = with_a_copy()

    export(store, record, plan_store, FakeExporter(), mode="merged")

    assert store.photos == [("0_a.png", MINUTE, "01.png")]


def test_frames_with_pictures_of_their_own_each_leave_one():
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter())

    assert len(store.photos) == 2


def test_merged_export_writes_one_file_named_after_the_project():
    store, record, plan_store = with_videos()
    exporter = FakeExporter()

    export(store, record, plan_store, exporter, mode="merged")

    # The join happens on the machine's own disk, beside the pieces: ffmpeg used to write the
    # encoded stream onto the Drive mount a piece at a time, which is a known Colab slowness
    # (madde 282). It is cut under a name no piece can have (madde 474); Drive still gets the
    # project's.
    assert exporter.merged == ([f"{PIECES}/01.mp4", f"{PIECES}/02.mp4"], f"{PIECES}/birlesik.mp4")
    assert store.exports == [(f"{PIECES}/birlesik.mp4", MINUTE, "düğün.mp4")]


def test_a_merged_export_cuts_its_pieces_outside_the_drive_folder():
    """The pieces are scaffolding for the join, and Drive is slow enough that writing the whole set
    there a second time is what the user felt (madde 235)."""
    store, record, plan_store = with_videos()
    exporter = FakeExporter()

    export(store, record, plan_store, exporter, mode="merged")

    assert [target for _v, _a, target in exporter.pieces] == [
        f"{PIECES}/01.mp4", f"{PIECES}/02.mp4"]


def test_a_merged_export_takes_its_pieces_away_and_leaves_the_export_alone():
    store, record, plan_store = with_videos()

    folder = export(store, record, plan_store, FakeExporter(), mode="merged")

    assert store.removed == [PIECES]
    assert folder == FOLDER


def test_a_merged_export_leaves_the_photos_in_the_drive_folder():
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter(), mode="merged")

    # The user's call: the pictures stay whichever export wrote them.
    assert store.photos == [
        ("0_a.png", MINUTE, "01.png"),
        ("1_a.png", MINUTE, "02.png"),
    ]


def test_a_separate_export_cuts_on_the_machine_and_carries_each_piece_to_drive():
    """Madde 472: ffmpeg wrote a separate export's pieces straight onto the Drive mount, beside the
    storage door. It cuts them on the machine's own disk now, like the merged export's, and each
    goes to Drive whole the moment it is cut -- so the count on screen is what Drive holds."""
    store, record, plan_store = with_videos()
    exporter = FakeExporter()

    export(store, record, plan_store, exporter)

    assert [target for _v, _a, target in exporter.pieces] == [
        f"{PIECES}/01.mp4", f"{PIECES}/02.mp4"]
    assert store.videos == [(f"{PIECES}/01.mp4", MINUTE, "01.mp4"),
                            (f"{PIECES}/02.mp4", MINUTE, "02.mp4")]


def test_a_separate_exports_videos_are_never_taken_away_again():
    """A finished run takes away only what it cut on the machine. The videos on Drive are the
    export itself -- FOUNDATION 1: the user's work is sacred, and nothing is worth a deleted
    export."""
    store, record, plan_store = with_videos()

    folder = export(store, record, plan_store, FakeExporter())

    assert store.removed == [PIECES]
    assert folder == FOLDER


def test_a_separate_export_copies_every_piece_untouched():
    """The separate export carries no disclaimer at all: at 480 wide it could not be read, and the
    user took it off until a readable one is drawn (madde 261). So nothing is asked of a piece
    beyond the three things it has always taken.

    Both modes go through the same call now, which is the point -- the merged export's disclaimer
    rides on the join (madde 250), never on a piece.
    """
    store, record, plan_store = with_videos()
    exporter = FakeExporter()

    export(store, record, plan_store, exporter)

    assert exporter.pieces == [
        ("/fake/düğün/0_a_V1_0.mp4", None, f"{PIECES}/01.mp4"),
        ("/fake/düğün/1_a_V1_0.mp4", None, f"{PIECES}/02.mp4"),
    ]


def test_the_merged_file_reaches_drive_once_it_is_whole():
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter(), mode="merged")

    assert store.exports == [(f"{PIECES}/birlesik.mp4", MINUTE, "düğün.mp4")]


def test_a_merged_export_carries_no_piece_to_drive():
    """Its pieces are scaffolding for the join; only the joined file goes to Drive."""
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter(), mode="merged")

    assert store.videos == []


def test_the_copy_to_drive_comes_after_the_join():
    """The order is the whole point: while the join runs, the Drive folder holds nothing, so a
    half written mp4 is never there to be seen (FOUNDATION 1, madde 94's own reasoning).

    The timeline holds the cutting and the photos as well now (madde 289), and this test is about
    the last two steps of it -- so it reads only those.
    """
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter(store=store), mode="merged")

    assert [step for step in store.order if step in ("merge", "copy_export")] == [
        "merge", "copy_export"]


def test_the_videos_are_all_written_before_the_first_photo():
    """The user saw the two jobs happening at once and asked for them apart: ilk videolar
    yüklensin, sonra fotoğraflar eklensin (21 Eylül).

    Not for tidiness -- the files that come out are the same either way. It is that 287 cannot say
    which step is expensive while both live inside one: a counter crawling through a frame does not
    say whether the time went on reading a video off Drive or writing a picture back to it.
    """
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter(store=store))

    assert store.order == ["open_export", "make_pieces_dir", "piece", "copy_video", "piece",
                           "copy_video", "copy_photo", "copy_photo"]


def test_a_merged_export_stamps_the_disclaimer_after_the_photos_are_in():
    """The third step the user named. The disclaimer rides on the join itself (madde 250), so
    "sonra disclaimer" means the join standing behind both loops -- and what moves here is the
    photos, which gather in front of it."""
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter(store=store), mode="merged")

    assert store.order == ["open_export", "make_pieces_dir", "piece", "piece", "copy_photo",
                           "copy_photo", "merge", "copy_export"]


def test_a_join_that_blew_up_copies_nothing_to_drive():
    store, record, plan_store = with_videos()
    exporter = FakeExporter(fails_on=f"{PIECES}/birlesik.mp4")

    with pytest.raises(RuntimeError):
        export(store, record, plan_store, exporter, mode="merged")

    assert store.exports == []
    assert store.removed == [PIECES, FOLDER]


def test_a_separate_export_has_no_merged_file_to_copy():
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter())

    assert store.exports == []


def test_a_merged_export_that_blows_up_leaves_neither_folder_behind():
    store, record, plan_store = with_videos()
    exporter = FakeExporter(fails_on=f"{PIECES}/02.mp4")

    with pytest.raises(RuntimeError):
        export(store, record, plan_store, exporter, mode="merged")

    assert store.removed == [PIECES, FOLDER]


def test_a_cancelled_merged_export_leaves_neither_folder_behind():
    store, record, plan_store = with_videos()
    runner = sync_runner()
    runner.cancel("merged")

    assert export(store, record, plan_store, FakeExporter(), mode="merged", runner=runner) is None
    assert store.removed == [PIECES, FOLDER]


def test_a_failed_export_takes_its_half_written_folder_with_it():
    store, record, plan_store = with_videos()
    exporter = FakeExporter(fails_on=f"{PIECES}/02.mp4")
    runner = sync_runner()

    with pytest.raises(RuntimeError):
        export(store, record, plan_store, exporter, runner=runner)

    assert store.removed == [PIECES, FOLDER]


def test_the_reason_a_run_failed_is_the_tool_own_words():
    store, record, plan_store = with_videos()
    runner = sync_runner()

    runner.start("separate", lambda: run_export(
        runner, store, record, plan_store, FakeOrderStore(),
        FakeExporter(fails_on=f"{PIECES}/01.mp4"), lambda: MINUTE, "düğün", "separate",
        mutes=NoMutes()))

    assert runner.state()["separate"]["state"] == "error"
    assert runner.state()["separate"]["error"] == "ffmpeg: disk dolu"


class DriveGoneAtCleanup(ExportStore):
    """The mount drops while a run is being taken down: the dated folder cannot be removed."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleanups = 0

    def remove_export(self, project, stamp, videos, in_use):
        self.cleanups += 1
        raise OSError(107, "Transport endpoint is not connected")


def test_a_cleanup_drive_refuses_leaves_the_machine_clear_and_both_reasons_on_screen():
    """The pieces go first, since nothing stops their going. The screen says why the run failed
    first, and then that its half export is still on Drive -- the folder that looks finished, which
    madde 94 forbids leaving unsaid."""
    _, record, plan_store = with_videos()
    store = DriveGoneAtCleanup()
    runner = sync_runner()

    runner.start("separate", lambda: run_export(
        runner, store, record, plan_store, FakeOrderStore(),
        FakeExporter(fails_on=f"{PIECES}/02.mp4"), lambda: MINUTE, "düğün", "separate",
        mutes=NoMutes()))

    assert runner.state()["separate"]["error"] == (
        "ffmpeg: disk dolu — Yarım export silinemedi: "
        "[Errno 107] Transport endpoint is not connected")
    assert store.removed == [PIECES]


def test_a_cleanup_drive_refuses_keeps_the_runs_own_error_as_the_cause():
    _, record, plan_store = with_videos()

    with pytest.raises(RuntimeError) as caught:
        export(DriveGoneAtCleanup(), record, plan_store, FakeExporter(fails_on=f"{PIECES}/02.mp4"))

    assert str(caught.value.__cause__) == "ffmpeg: disk dolu"


def test_a_cancel_drive_refuses_is_cleaned_up_once():
    """A cancelled run is taken down once, outside the work: a cleanup that fails there must not
    land in the work's own failure path and be tried again."""
    _, record, plan_store = with_videos()
    store = DriveGoneAtCleanup()
    runner = sync_runner()
    runner.cancel("separate")

    with pytest.raises(OSError):
        export(store, record, plan_store, FakeExporter(), runner=runner)

    assert store.cleanups == 1
    assert store.removed == [PIECES]


def test_cancelling_stops_between_pieces_and_takes_its_export_back():
    store, record, plan_store = with_videos()
    runner = sync_runner()
    runner.cancel("separate")
    exporter = FakeExporter()

    assert export(store, record, plan_store, exporter, runner=runner) is None
    assert exporter.pieces == []
    assert store.removed == [PIECES, FOLDER]


class ExporterThatCancelsOnTheLastPiece(FakeExporter):
    """Cancels the run as the last piece is cut, which puts the stop in the gap between the two
    loops: every video is written and no photo is."""

    def __init__(self, runner, mode, total):
        super().__init__()
        self._runner, self._mode, self._total = runner, mode, total

    def piece(self, video, audio, target):
        super().piece(video, audio, target)
        if len(self.pieces) == self._total:
            self._runner.cancel(self._mode)


def test_cancelling_once_the_videos_are_done_writes_no_photos_and_takes_its_export_back():
    """The second loop carries a cancel check of its own, and it sits at the top of it -- so
    "before the first photo" and "between two photos" are one line (FOUNDATION 3).

    The stop stays between work units: half a copied picture is as bad as half a cut video, and
    the run takes back what it wrote either way (madde 94, 474).
    """
    store, record, plan_store = with_videos()
    runner = sync_runner()
    exporter = ExporterThatCancelsOnTheLastPiece(runner, "separate", total=2)

    assert export(store, record, plan_store, exporter, runner=runner) is None
    assert len(exporter.pieces) == 2
    assert store.photos == []
    assert store.removed == [PIECES, FOLDER]


def test_a_failed_separate_export_takes_back_the_videos_it_carried_to_drive():
    """Madde 474: its cleanup is handed what it wrote, not the folder -- the other mode may be
    writing into the same one. 02 never reached Drive: a save is whole or absent."""
    store, record, plan_store = with_videos()

    with pytest.raises(RuntimeError):
        export(store, record, plan_store, FakeExporter(fails_on=f"{PIECES}/02.mp4"))

    assert store.taken_back == (["01.mp4"], False)


def test_a_failed_merged_export_has_no_file_of_its_own_on_drive():
    """Its join goes up last, in one save: a run that fails never left it there."""
    store, record, plan_store = with_videos()

    with pytest.raises(RuntimeError):
        export(store, record, plan_store, FakeExporter(fails_on=f"{PIECES}/birlesik.mp4"),
               mode="merged")

    assert store.taken_back == ([], False)


def test_a_failed_export_leaves_the_photos_to_the_one_writing_beside_it():
    """A merged export still running has nothing on Drive yet but the photos the two share; the
    runner is the one that knows it is there."""
    store, record, plan_store = with_videos()
    runner = ExportRunner(spawn=lambda fn: None)
    runner.start("merged", lambda: None)
    runner.report("merged", state="photos", target=FOLDER)

    with pytest.raises(RuntimeError):
        export(store, record, plan_store, FakeExporter(fails_on=f"{PIECES}/02.mp4"),
               runner=runner)

    assert store.taken_back == (["01.mp4"], True)


class CuttingExporter:
    """Writes real files the way ffmpeg does: the output is opened, and emptied, before any input
    is read (`-y`). So a join whose output is one of its own pieces reads that piece back empty --
    the fault madde 474 found."""

    def __init__(self, fails_on=None):
        self.fails_on = fails_on          # the piece name whose cut blows up

    def piece(self, video, audio, target):
        if os.path.basename(target) == self.fails_on:
            raise RuntimeError("ffmpeg: disk dolu")
        with open(target, "wb") as handle:
            handle.write(os.path.basename(video).encode())

    def merge(self, pieces, target):
        with open(target, "wb") as joined:
            for piece in pieces:
                with open(piece, "rb") as handle:
                    joined.write(handle.read() + b"|")


def on_drive(tmp_path, project):
    """A real store over a Drive root holding the project and its two pictures, and the exports'
    root beside it (madde 494) -- which is what comes back, with the store."""
    drive, exports = tmp_path / "drive", tmp_path / "export"
    (drive / project).mkdir(parents=True)
    exports.mkdir()
    for photo in ("0_a.png", "1_a.png"):
        (drive / project / photo).write_bytes(photo.encode())
    return exports, DrivePhotoStore(Storage(str(drive)), Storage(str(exports)))


def export_to(store, runner, project, mode, exporter):
    _, record, plan_store = with_videos()
    return run_export(runner, store, record, plan_store, FakeOrderStore(), exporter,
                      lambda: MINUTE, project, mode, mutes=NoMutes())


def test_a_project_named_like_a_piece_gets_a_whole_merged_file(tmp_path):
    """The join was cut as <proje>.mp4 beside pieces named 01.mp4, 02.mp4 …, so a project named 01
    had ffmpeg write over its own first piece. It is cut as birlesik.mp4 now, and Drive still gets
    the project's name."""
    exports, store = on_drive(tmp_path, "01")

    export_to(store, sync_runner(), "01", "merged", CuttingExporter())

    landed = exports / f"{MINUTE} 01" / "01.mp4"
    assert landed.read_bytes() == b"0_a_V1_0.mp4|1_a_V1_0.mp4|"


def test_a_failed_export_leaves_the_one_finished_beside_it_in_the_same_minute(tmp_path):
    """Madde 474: the two modes share the minute's folder, and a failed run used to take all of it.
    Now it takes back its own videos; the merged file and the photos it counts on stay."""
    exports, store = on_drive(tmp_path, "düğün")
    runner = sync_runner()
    export_to(store, runner, "düğün", "merged", CuttingExporter())

    with pytest.raises(RuntimeError):
        export_to(store, runner, "düğün", "separate", CuttingExporter(fails_on="02.mp4"))

    folder = exports / f"{MINUTE} düğün"
    assert sorted(path.name for path in folder.iterdir()) == ["düğün.mp4", "foto"]
    assert sorted(path.name for path in (folder / "foto").iterdir()) == ["01.png", "02.png"]
    assert (folder / "düğün.mp4").read_bytes() == b"0_a_V1_0.mp4|1_a_V1_0.mp4|"


def test_a_failed_export_alone_leaves_nothing_but_the_exports_root(tmp_path):
    """Nobody else wrote into the folder, so half an export goes whole (madde 94)."""
    exports, store = on_drive(tmp_path, "düğün")

    with pytest.raises(RuntimeError):
        export_to(store, sync_runner(), "düğün", "separate", CuttingExporter(fails_on="02.mp4"))

    assert list(exports.iterdir()) == []


@pytest.mark.parametrize("mode", ["separate", "merged"])
def test_an_export_drive_has_no_room_for_stops_with_drives_words(tmp_path, monkeypatch, mode):
    """Madde 497: the export's first save to Drive is refused, the screen shows the export failed
    with the numbers, and the half export is taken back."""
    exports, store = on_drive(tmp_path, "düğün")
    monkeypatch.setattr(storage_module.shutil, "disk_usage",
                        lambda path: SimpleNamespace(total=100, used=100, free=0))
    runner = sync_runner()

    runner.start(mode, lambda: export_to(store, runner, "düğün", mode, CuttingExporter()))

    state = runner.state()[mode]
    assert state["state"] == "error"
    assert "Drive'da yer yok" in state["error"]
    assert list(exports.iterdir()) == []


def test_the_state_counts_what_has_been_written():
    store, record, plan_store = with_videos()
    runner = sync_runner()

    export(store, record, plan_store, FakeExporter(), runner=runner)

    # The steps each carry their own second now (madde 287); this test is about the counter, so it
    # reads the rest of the state and leaves them to the tests that are about them.
    state = runner.state()["separate"]
    assert {key: value for key, value in state.items() if key != "steps"} == {
        "state": "done", "written": 2, "total": 2, "target": FOLDER, "error": None}
    # The mode nobody asked for is untouched.
    assert runner.state()["merged"]["state"] == "idle"


class FakeClock:
    """A clock that moves a second every time it is read, so a duration is a count of readings.

    No test waits a real second, and none of them is allowed to read differently on a slow
    machine: what is asserted here is which step was timed, not how fast this box is.
    """

    def __init__(self):
        self.readings = 0

    def __call__(self):
        self.readings += 1
        return float(self.readings)


def timed_runner(clock):
    return ExportRunner(spawn=lambda fn: fn(), clock=clock)


def test_a_merged_export_leaves_every_step_with_its_own_seconds():
    """255 gave the step a name, and a name says where the run is. This says which step is
    expensive, which is what the user asked for: neye zaman harcadığımızı görürüz (21 Eylül).

    Four steps, in the order the run walks them. The copy to Drive is the one that had no name at
    all: while it ran, the screen still said the disclaimer was being stamped (madde 282 opened it,
    287 closes it).
    """
    store, record, plan_store = with_videos()
    runner = timed_runner(FakeClock())

    export(store, record, plan_store, FakeExporter(), mode="merged", runner=runner)

    assert [step["step"] for step in runner.state()["merged"]["steps"]] == [
        "running", "photos", "merging", "saving"]
    assert [step["seconds"] for step in runner.state()["merged"]["steps"]] == [1.0, 1.0, 1.0, 1.0]


def test_a_separate_export_leaves_the_two_steps_it_has():
    """The roadmap's line said a separate export has one step -- 289 spent that reason: it writes
    all the videos and then all the photos, like the merged one. So the same two reports serve both
    modes, and the screen stops saying N/N yazıldı while pictures are still going to Drive."""
    store, record, plan_store = with_videos()
    runner = timed_runner(FakeClock())

    export(store, record, plan_store, FakeExporter(), runner=runner)

    assert [step["step"] for step in runner.state()["separate"]["steps"]] == ["running", "photos"]


def test_the_clock_is_read_once_a_step_and_not_once_a_frame():
    """The measurement is meant to be cheap: a clock around the steps, and nothing parsed out of
    ffmpeg's output -- that was the cost 255 turned down."""
    store, record, plan_store = with_videos()
    clock = FakeClock()

    export(store, record, plan_store, FakeExporter(), mode="merged", runner=timed_runner(clock))

    # One reading opens the run, and one closes each of the four steps.
    assert clock.readings == 5


def test_a_mode_writing_its_photos_is_busy():
    """The guard asked whether the state was running or merging, and a list like that goes stale
    the moment a step is added: a second export could have started while the pictures were being
    written. Busy is the other side of resting now."""
    runner = ExportRunner(spawn=lambda fn: None)

    runner.start("separate", lambda: None)
    runner.report("separate", state="photos")

    assert runner.start("separate", lambda: None) is False


def test_a_cancelled_run_leaves_no_steps_on_the_screen():
    """The steps of a run that was called off say nothing about anything: its own files are gone
    and so is the reason to read them."""
    store, record, plan_store = with_videos()
    runner = timed_runner(FakeClock())
    exporter = ExporterThatCancelsOnTheLastPiece(runner, "separate", total=2)

    export(store, record, plan_store, exporter, runner=runner)

    assert runner.state()["separate"]["steps"] == ()


def test_a_second_run_of_the_same_mode_is_refused_while_one_is_going():
    runner = ExportRunner(spawn=lambda fn: None)     # claims the mode, never runs the job

    assert runner.start("separate", lambda: None) is True
    assert runner.start("separate", lambda: None) is False
    # The other mode is free: the design lets the two run side by side.
    assert runner.start("merged", lambda: None) is True


def test_the_runner_says_whether_the_other_mode_is_writing_into_a_folder():
    """What a failed export asks before taking the shared photos away (madde 474): only the other
    mode counts, only while it is busy, and only in the same folder."""
    runner = ExportRunner(spawn=lambda fn: None)
    runner.start("merged", lambda: None)
    runner.report("merged", state="photos", target=FOLDER)

    assert runner.others_writing("separate", FOLDER) is True
    assert runner.others_writing("merged", FOLDER) is False
    assert runner.others_writing("separate", "/fake/queenEditorExport/başka") is False

    runner.report("merged", state="done")

    assert runner.others_writing("separate", FOLDER) is False


def test_a_cancelled_mode_is_not_counted_as_writing():
    """It is on its way to taking its own back, not writing on."""
    runner = ExportRunner(spawn=lambda fn: None)
    runner.start("merged", lambda: None)
    runner.report("merged", state="photos", target=FOLDER)

    runner.cancel("merged")

    assert runner.others_writing("separate", FOLDER) is False


def test_two_exports_cancelled_together_leave_nothing_behind(tmp_path):
    """Madde 494: the screen cancels both modes at once, and each cleanup used to see the other as
    still busy -- so neither took the shared photos or the folder, and a half export stayed."""
    exports, store = on_drive(tmp_path, "düğün")
    folder = store.open_export("düğün", MINUTE)
    store.copy_photo("düğün", "0_a.png", MINUTE, "01.png")
    runner = ExportRunner(spawn=lambda fn: None)
    for mode in ("merged", "separate"):
        runner.start(mode, lambda: None)
        runner.report(mode, state="photos", target=folder)
    for mode in ("merged", "separate"):
        runner.cancel(mode)

    for mode in ("merged", "separate"):
        store.remove_export("düğün", MINUTE, [], in_use=runner.others_writing(mode, folder))

    assert list(exports.iterdir()) == []


class _Answer:
    """What subprocess.run hands back for one call."""

    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class FakeRun:
    """subprocess.run's answer, and a note of what it was asked to run.

    `sounds` answers the one question ffprobe is asked of a piece -- its sample rate and channel
    layout, separated the way csv separates by itself (madde 288), or an empty line for a piece with
    no audio at all. Nothing is the default: a set where no piece carries sound is one of the two
    even sets, so a test that says nothing about sound asks about that (madde 286). A probe and an
    ffmpeg run fail differently, so each carries its own exit code and message.

    No piece has a size here: the join never asks one (madde 478), and ffmpeg is not on this
    machine to measure anything.
    """

    def __init__(self, returncode=0, stderr="", probe_returncode=0, probe_stderr="", nvenc=False,
                 sounds=None):
        self.calls = []
        self.returncode = returncode
        self.stderr = stderr
        self.sounds = dict(sounds or {})
        self.joined = None                # the pieces the join read, in the order it read them
        self.probe_returncode = probe_returncode
        self.probe_stderr = probe_stderr
        # Whether the trial encode on the card comes back. False is a machine that cannot encode
        # with nvenc -- what every test that says nothing about it is asking about (madde 257).
        self.nvenc = nvenc

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        if "-filter_complex" in args:
            # Every input but the last, which is the disclaimer.
            self.joined = [args[at + 1] for at, part in enumerate(args) if part == "-i"][:-1]
        if "ffprobe" in args[0]:
            # An empty answer is what a file with no audio stream gets, and it is an answer.
            return _Answer(self.probe_returncode, self.sounds.get(args[-1], "") + "\n",
                           self.probe_stderr)
        if "nullsrc" in args:
            return _Answer(0 if self.nvenc else 1, "",
                           "" if self.nvenc else "No capable devices found")
        return _Answer(self.returncode, "", self.stderr)


def ffmpeg_calls(run):
    """The writing calls -- trying the card out is not one of them."""
    return [call for call in run.calls if call[0] == "ffmpeg" and "nullsrc" not in call]


def encoder_calls(run):
    """The trial encodes: what this machine can do is tried, not looked up (madde 257)."""
    return [call for call in run.calls if "nullsrc" in call]


def probe_calls(run):
    return [call for call in run.calls if "ffprobe" in call[0]]


def sound_calls(run):
    """The question asked of a piece: what sound it carries, if any (madde 286)."""
    return [call for call in probe_calls(run) if "a:0" in call]


def test_a_silent_piece_is_copied_rather_than_re_encoded():
    run = FakeRun()

    FfmpegVideoExporter(run=run).piece("0.mp4", None, "01.mp4")

    assert run.calls[0] == ["ffmpeg", "-y", "-i", "0.mp4", "-c", "copy", "01.mp4"]


def test_a_sound_is_laid_over_the_video():
    """The picture from the video, the sound from the layer -- named, not left to ffmpeg. An H3
    video carries a sound of its own (madde 243), and a sound layer takes its place; left to its
    own choice ffmpeg keeps whichever stream it likes best."""
    run = FakeRun()

    FfmpegVideoExporter(run=run).piece("0.mp4", "0.wav", "01.mp4")

    assert run.calls[0] == ["ffmpeg", "-y", "-i", "0.mp4", "-i", "0.wav",
                            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                            "-c:a", "aac", "-shortest", "01.mp4"]


# How each piece is put on the canvas. The canvas is the user's call and it is landscape: exports
# are taken landscape either way, and the disclaimer only becomes readable at that width (madde 259).
# `decrease` fits rather than crops, so nothing is lost and a portrait piece gets bars; a 16:9 one
# fills the canvas (madde 478). Each piece is fitted on its own, so pieces of two shapes can join.
FIT = ("scale=1920:1080:force_original_aspect_ratio=decrease,"
       "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1")
# The disclaimer takes 80% of the width, leaving room either side (madde 291), over the joined
# video's first minute (madde 250).
OVER = "scale=1536:-1[d];[c][d]overlay=(W-w)/2:H-h-43:enable='lt(t,60)'[v]"


def expected_graph(count, sounded=False):
    """The filtergraph a join of `count` pieces is handed: each piece fitted, the fitted pieces
    joined -- with their sound when they carry some -- and the disclaimer, the last input, laid over
    the join."""
    fitted = "".join(f"[{at}:v]{FIT}[v{at}];" for at in range(count))
    if sounded:
        joined = "".join(f"[v{at}][{at}:a]" for at in range(count))
        joined += f"concat=n={count}:v=1:a=1[c][a];"
    else:
        joined = "".join(f"[v{at}]" for at in range(count))
        joined += f"concat=n={count}:v=1:a=0[c];"
    return f"{fitted}{joined}[{count}:v]{OVER}"


GRAPH = expected_graph(2)
# Each piece is an input of its own, its decoder capped at one thread (madde 478).
INPUTS = ["-threads", "1", "-i", "a.mp4", "-threads", "1", "-i", "b.mp4"]
# The join's frame rate, set once on its output: an `fps` filter in each piece's chain drops that
# piece's last frame (madde 478, measured on ffmpeg 7.1).
RATE = ["-r", "24"]
# The joined sound, encoded at H3's own bitrate.
SOUND = ["-map", "[a]", "-c:a", "aac", "-b:a", "192k"]
ENCODE =["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]
# What the same work looks like on the GPU (madde 253). nvenc takes -rc/-cq where x264 takes -crf,
# and "fast" rather than p1-p7: Colab's ffmpeg may be old enough not to know the p-levels.
NVENC = ["-c:v", "h264_nvenc", "-preset", "fast", "-rc", "vbr", "-cq", "23",
         "-pix_fmt", "yuv420p"]
# The question asked of ffmpeg: not which encoders it was built with, but whether this machine can
# encode with the card. nullsrc is a made-up picture, -t 0.1 a tenth of a second of it, and
# `-f null -` writes it nowhere (madde 257).
TRIAL = ["ffmpeg", "-hide_banner", "-f", "lavfi", "-i", "nullsrc", "-t", "0.1",
         "-c:v", "h264_nvenc", "-f", "null", "-"]


def test_piece_takes_no_disclaimer():
    """The separate export went back to what it was before madde 249: its pieces are copies, and
    there is no caller left that would ask for an overlay. A flag defaulting to False would only
    make the next reader look for the place that passes True (madde 261)."""
    assert list(inspect.signature(FfmpegVideoExporter.piece).parameters) == [
        "self", "video", "audio", "target"]


def test_the_gpu_is_tried_rather_than_looked_up_in_a_list(tmp_path):
    """`ffmpeg -encoders` answers for the build, not for the machine: a box with no card, a driver
    that does not match or a card whose encoder sessions are taken all list h264_nvenc and then
    fail mid-export (madde 257). So the card is tried, on a tenth of a second written nowhere."""
    run = FakeRun(nvenc=True)

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4"], str(tmp_path / "d.mp4"))

    assert encoder_calls(run) == [TRIAL]


def test_an_unusable_gpu_leaves_the_export_running_on_the_cpu(tmp_path):
    """The trial failing is an answer, not an error: losing a whole export to a guess is worse than
    a slow export (FOUNDATION 1)."""
    run = FakeRun(nvenc=False)

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4"], str(tmp_path / "d.mp4"))

    said = ffmpeg_calls(run)[0]
    assert ENCODE == [part for part in said if part in ENCODE]
    assert "h264_nvenc" not in said


def test_a_merged_export_is_encoded_on_the_gpu_too(tmp_path):
    """The join is where the whole timeline is encoded, so it is where the GPU is worth most."""
    run = FakeRun(nvenc=True)
    target = str(tmp_path / "düğün.mp4")

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"], target)

    assert ffmpeg_calls(run)[0] == [
        "ffmpeg", "-y", *INPUTS, "-i", "d.png",
        "-filter_complex", GRAPH, "-map", "[v]", *RATE, *NVENC, target]


def test_the_card_is_tried_once_and_not_again(tmp_path):
    """The answer cannot change while the process lives, and a trial costs a process."""
    run = FakeRun(nvenc=True)
    exporter = FfmpegVideoExporter(run=run, disclaimer="d.png")

    exporter.merge(["a.mp4"], str(tmp_path / "bir.mp4"))
    exporter.merge(["a.mp4"], str(tmp_path / "iki.mp4"))

    assert len(encoder_calls(run)) == 1


def test_a_copied_piece_never_asks_which_encoder_there_is():
    """Copying has no encoder, so it has no question either."""
    run = FakeRun()

    FfmpegVideoExporter(run=run, disclaimer="d.png").piece("0.mp4", None, "01.mp4")

    assert encoder_calls(run) == []


def test_the_disclaimer_ships_in_the_repo():
    """The notebook clones this repo and builds nothing, so a file that is not committed is a file
    every export fails on (FOUNDATION 1 and 3)."""
    assert os.path.isfile(config.DISCLAIMER_PATH)


def test_a_failure_says_what_the_tool_said():
    run = FakeRun(returncode=1, stderr="banner\n0.mp4: No such file or directory")

    with pytest.raises(RuntimeError) as caught:
        FfmpegVideoExporter(run=run).piece("0.mp4", None, "01.mp4")

    assert str(caught.value) == "0.mp4: No such file or directory"


def test_the_join_writes_no_list_file_anywhere(tmp_path):
    """The pieces go to ffmpeg as its inputs, one `-i` each, in the order given, so the join needs
    no file of its own: nothing of ours is written beside the pieces or beside the target, where a
    session that dies mid-run would leave it (madde 284)."""
    pieces = tmp_path / "parçalar"
    drive = tmp_path / "drive"
    pieces.mkdir()
    drive.mkdir()
    first, second = str(pieces / "01.mp4"), str(pieces / "02.mp4")
    run = FakeRun()

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge([first, second],
                                                           str(drive / "düğün.mp4"))

    assert run.joined == [first, second]
    assert list(pieces.iterdir()) == [] and list(drive.iterdir()) == []


def test_no_piece_is_asked_its_size(tmp_path):
    """Each piece is fitted onto the canvas by its own filter, so the join no longer has to know
    what a piece measures: ffmpeg reads the real size as it scales. The one question left for a
    piece is its sound (madde 286)."""
    run = FakeRun()

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    assert probe_calls(run) == sound_calls(run)
    assert [call[-1] for call in probe_calls(run)] == ["a.mp4", "b.mp4"]


def test_a_merged_export_joins_and_stamps_in_one_call(tmp_path):
    """The disclaimer rides on the join rather than on the pieces, which is what makes its clock the
    joined video's own: `lt(t,60)` counts the merged stream, so the minute ends exactly on the
    minute even when a frame straddles it (madde 250, user's call).

    One call: each piece is fitted, the fitted pieces are joined, and the disclaimer goes over the
    join, all in one filtergraph -- so nothing has to know which frame starts at which second, and
    the timeline is encoded once.
    """
    run = FakeRun()
    target = str(tmp_path / "düğün.mp4")

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"], target)

    assert ffmpeg_calls(run) == [[
        "ffmpeg", "-y", *INPUTS, "-i", "d.png",
        "-filter_complex", GRAPH, "-map", "[v]", *RATE, *ENCODE, target]]


def test_every_pieces_decoder_is_held_to_one_thread(tmp_path):
    """Every input stays open for the whole call, so memory grows with the pieces; `-threads 1`
    caps what each decoder holds. concat reads one segment at a time, so only one decoder works at
    once and the cap costs no speed. The disclaimer is one picture and needs no cap."""
    pieces = ["a.mp4", "b.mp4", "c.mp4"]
    run = FakeRun()

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(pieces, str(tmp_path / "düğün.mp4"))

    said = ffmpeg_calls(run)[0]
    for piece in pieces:
        at = said.index(piece)
        assert said[at - 3:at] == ["-threads", "1", "-i"]


def test_the_filtergraph_word_for_word(tmp_path):
    """Two sounded pieces, written out in full rather than built: `expected_graph` above is the same
    rule in a loop, and a rule checked only against its own copy checks nothing."""
    run = FakeRun(sounds={"a.mp4": "48000,stereo", "b.mp4": "48000,stereo"})

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    assert filtergraph(run) == (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
        "[1:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
        "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
        "[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[c][a];"
        "[2:v]scale=1536:-1[d];"
        "[c][d]overlay=(W-w)/2:H-h-43:enable='lt(t,60)'[v]")


def test_a_sounded_join_maps_the_joined_sound_and_encodes_it(tmp_path):
    """A filter's output cannot be copied, so the joined sound is encoded -- aac, which is what the
    pieces carried, at the bitrate H3 writes them with. It is the join's own `[a]` that is mapped,
    not any one piece's."""
    run = FakeRun(sounds={"a.mp4": "48000,stereo"})
    target = str(tmp_path / "düğün.mp4")

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4"], target)

    said = ffmpeg_calls(run)[-1]
    assert filtergraph(run) == expected_graph(1, sounded=True)
    assert said[said.index("-filter_complex") + 2:] == [
        "-map", "[v]", *RATE, *ENCODE, *SOUND, target]


def test_the_joined_sound_keeps_h3s_own_bitrate():
    """The pieces' sound is H3's, written by its Combine at `audio_bitrate`; the join encodes it
    once more, and at a lower rate it would come out thinner than it went in."""
    for path in (config.H3_VIDEO_WORKFLOW_PATH, config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH):
        with open(path, encoding="utf-8") as handle:
            graph = json.load(handle)
        rates = {node["inputs"]["audio_bitrate"] for node in graph.values()
                 if "audio_bitrate" in node.get("inputs", {})}
        assert rates == {SOUND_BITRATE}


def test_a_join_with_no_sound_anywhere_maps_none(tmp_path):
    """The common set before sound layers: concat is told there is no audio (a=0), and nothing asks
    for a stream that is not there."""
    run = FakeRun()

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    said = ffmpeg_calls(run)[0]
    assert "a=0" in filtergraph(run)
    assert "[a]" not in said and "-c:a" not in said


def filtergraph(run):
    """What the merged call handed -filter_complex."""
    call = ffmpeg_calls(run)[-1]
    return call[call.index("-filter_complex") + 1]


def merged(pieces, tmp_path, name="düğün.mp4"):
    """One merged export over the given pieces, and the FakeRun that watched it."""
    run = FakeRun()
    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(pieces, str(tmp_path / name))
    return run


def test_landscape_portrait_and_mixed_sets_join_on_the_same_rule(tmp_path):
    """Since 476 a project can hold landscape 1024x576 videos beside portrait 576x864 ones -- old
    frames stay portrait, and every generation picks its own shape. The concat demuxer read the
    pieces as one stream and so refused two sizes; each piece now goes through its own fit, so a
    mixed set joins like any other (madde 478, the roadmap's "dikey videolar bugünkü gibi bantlı
    kalır").

    The rule is the same whatever the pieces measure: ffmpeg reads each piece's real size as it
    scales it, so neither the plan line's orientation -- which copy frames and frames made before
    476 do not carry -- nor a probe of ours decides anything.
    """
    landscape = merged(["yatay1.mp4", "yatay2.mp4"], tmp_path, "yatay.mp4")
    portrait = merged(["dikey1.mp4", "dikey2.mp4"], tmp_path, "dikey.mp4")
    mixed = merged(["yatay1.mp4", "dikey1.mp4"], tmp_path, "karisik.mp4")

    assert filtergraph(landscape) == filtergraph(portrait) == filtergraph(mixed) == GRAPH
    assert mixed.joined == ["yatay1.mp4", "dikey1.mp4"]


def fitted(width, height):
    """The size a picture is fitted to on the canvas and the bar left either side and above, by the
    rule `force_original_aspect_ratio=decrease` and `pad=…:(ow-iw)/2:(oh-ih)/2` follow: each side
    rescaled from the other, the smaller kept. It checks that H3's sizes fit the canvas as the item
    wants; it is not ffmpeg, which is not on this machine, and Colab is where the real picture is
    seen. Python's `round` differs from ffmpeg's av_rescale only on an exact half, which these
    sizes never reach: both of their divisions come out whole."""
    scaled_w = min(round(MERGED_HEIGHT * width / height), MERGED_WIDTH)
    scaled_h = min(round(MERGED_WIDTH * height / width), MERGED_HEIGHT)
    return scaled_w, scaled_h, (MERGED_WIDTH - scaled_w) // 2, (MERGED_HEIGHT - scaled_h) // 2


def test_a_landscape_h3_video_fills_the_canvas_and_a_portrait_one_keeps_its_bars():
    """The item's own sentence, on the sizes H3 is really asked for: 1024x576 is exactly 16:9, so it
    scales to the whole 1920x1080 and the pad adds nothing; 576x864 becomes 720x1080 with 600
    pixels of bar each side, as today. Every number is even, which yuv420p needs, and both scales
    keep pixels square: (oh*iw)/(ow*ih) is 1 for each."""
    assert fitted(*H3_SIZES[LANDSCAPE][:2]) == (1920, 1080, 0, 0)
    assert fitted(*H3_SIZES[PORTRAIT][:2]) == (720, 1080, 600, 0)


def test_the_canvas_runs_at_h3s_own_frame_rate():
    """concat joins pieces of different rates into a stream of no known rate, and an mp4 then falls
    back to 25 fps -- frames of a 24 fps H3 video would be doubled up to fill it. So the join's
    output is set to the canvas's rate, and that rate is H3's own: the Director's `frame_rate` in
    both graphs, so an H3 piece keeps every frame."""
    for path in (config.H3_VIDEO_WORKFLOW_PATH, config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH):
        with open(path, encoding="utf-8") as handle:
            graph = json.load(handle)
        assert graph[H3_DIRECTOR]["inputs"]["frame_rate"] == MERGED_FPS


def test_a_merged_export_stands_on_a_landscape_canvas(tmp_path):
    """Fitted, never cropped: the user's word was "sığdır", and they took the bars knowingly --
    a 576x864 frame becomes 720x1080 with 600 pixels of bar either side. `decrease` is what picks
    the largest size that fits inside the canvas; `increase` would fill it by cutting the frame's
    top and bottom off, and FOUNDATION 1 does not trade a user's finished frame for a tidy edge.
    """
    said = filtergraph(merged(["a.mp4"], tmp_path))

    assert "scale=1920:1080:force_original_aspect_ratio=decrease" in said
    assert "pad=1920:1080:(ow-iw)/2:(oh-ih)/2" in said
    assert "crop" not in said and "increase" not in said


def test_the_disclaimer_leaves_room_either_side(tmp_path):
    """The user's call once they had seen a real export: disclaimer sağdan soldan az boşluk ver,
    ekranın %80'i olsun (21 Eylül). So 1536 of the 1920, and 192 pixels of room each side.

    The cost was said out loud and taken: the PNG is 1902 wide, drawn for the full canvas, so at
    80% its two lines shrink with it -- about 39 pixels tall rather than 49.

    A portrait piece's 720 pixels still do not bound it: the disclaimer runs over the bars.
    """
    said = filtergraph(merged(["a.mp4"], tmp_path))

    assert "[1:v]scale=1536:-1[d]" in said
    assert "scale=1920:-1" not in said             # the full width it used to take
    assert "H-h-43" in said                        # 4% of 1080, the margin the user kept


def test_every_piece_is_asked_whether_it_carries_sound(tmp_path):
    """concat joins a sound segment for every picture segment, so a set that has sound needs it in
    every piece. A piece has sound when its frame had a sound layer, or when the source video
    carried its own (an H3 video does, madde 243); a WAN video with no sound layer has none. So one
    project can hold both (madde 286).
    """
    run = FakeRun()

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    assert [call[-1] for call in sound_calls(run)] == ["a.mp4", "b.mp4"]


def test_the_sound_question_is_written_out_word_for_word(tmp_path):
    """The whole command, not a piece of it: what broke the export in Colab was one argument of it.

    `-of csv=s=:p=0` asked csv to separate with a colon, and a colon is what ffprobe splits the
    writer's own option string on -- so `s=` was left with no value and the writer refused the
    string, taking the merge down before a single piece was joined (madde 288). The separator is
    csv's own now: an option that is not written cannot be written wrong.

    FakeRun answers a command without judging it -- it is not ffprobe and cannot be -- so a
    malformed argument is invisible to every test that only asks whether something was asked.
    """
    run = FakeRun()

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4"], str(tmp_path / "düğün.mp4"))

    assert sound_calls(run)[0] == [
        "ffprobe", "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=sample_rate,channel_layout", "-of", "csv=p=0", "a.mp4"]


def test_a_set_that_all_carries_sound_is_joined_with_nothing_written_first(tmp_path):
    """The rule costs nothing where nothing is wrong: the join is still the only writing call."""
    run = FakeRun(sounds={"a.mp4": "48000,stereo", "b.mp4": "48000,stereo"})

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    assert len(ffmpeg_calls(run)) == 1
    assert run.joined == ["a.mp4", "b.mp4"]


def test_a_set_that_carries_no_sound_at_all_is_joined_untouched(tmp_path):
    """The other even set: a WAN project with no sound layers. concat is told there is no sound
    (a=0), so silence would be work bought for nothing (FOUNDATION 3)."""
    run = FakeRun()

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    assert len(ffmpeg_calls(run)) == 1
    assert run.joined == ["a.mp4", "b.mp4"]


def test_a_silent_piece_gets_silence_written_beside_it_when_another_has_sound(tmp_path):
    """The user's call, in their own words: "sesi olmayan karelere sessiz eklenir gayet basit".
    Nothing is lost -- the sounded pieces keep their sound, and the silent ones become silent
    rather than streamless.

    The video is copied, not encoded: only a sound track is added. `-shortest` is what stops
    anullsrc, which runs forever.
    """
    run = FakeRun(sounds={"a.mp4": "48000,stereo"})
    target = str(tmp_path / "düğün.mp4")

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"], target)

    written = ffmpeg_calls(run)[0]
    assert written == ["ffmpeg", "-y", "-i", "b.mp4",
                       "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                       "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                       "-shortest", "b-sound.mp4"]
    # And the join reads the repaired piece in the silent one's place, order untouched, with the
    # set's sound joined and mapped: one sounded piece is enough to make the set a sounded one.
    assert run.joined == ["a.mp4", "b-sound.mp4"]
    assert filtergraph(run) == expected_graph(2, sounded=True)
    join = ffmpeg_calls(run)[-1]
    assert join[join.index("-filter_complex") + 2:] == [
        "-map", "[v]", *RATE, *ENCODE, *SOUND, target]


def test_the_silence_matches_the_sound_the_other_pieces_carry(tmp_path):
    """The silence takes the shape of the set's own sound, from the piece that has some, so the join
    has nothing to convert -- concat would pick a common shape and convert by itself, but a shape
    copied is one that cannot be guessed wrong."""
    run = FakeRun(sounds={"a.mp4": "44100,mono"})

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    assert "anullsrc=r=44100:cl=mono" in ffmpeg_calls(run)[0]


def test_a_join_that_fails_says_what_ffmpeg_said(tmp_path):
    """A piece that cannot be read, or two that concat will not join, stop the join with ffmpeg's
    own last line -- never a cause guessed here: only ffmpeg knows which piece it could not take,
    and why."""
    run = FakeRun(returncode=1, stderr="banner\nb.mp4: Invalid data found when processing input")

    with pytest.raises(RuntimeError) as caught:
        FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                               str(tmp_path / "düğün.mp4"))

    assert str(caught.value) == "b.mp4: Invalid data found when processing input"


def test_a_sound_that_cannot_be_read_says_what_ffprobe_said(tmp_path):
    """A missing file, a file that is not a video, an ffprobe that is not installed -- three causes
    with one symptom, and only ffprobe knows which. Guessing one here would be the repo's own
    "never invent a cause" rule broken in the place it was written for. Nothing is joined then.
    """
    run = FakeRun(probe_returncode=1, probe_stderr="a.mp4: No such file or directory")

    with pytest.raises(RuntimeError) as caught:
        FfmpegVideoExporter(run=run).merge(["a.mp4", "b.mp4"], str(tmp_path / "düğün.mp4"))

    assert str(caught.value) == "a.mp4: No such file or directory"
    assert ffmpeg_calls(run) == []
