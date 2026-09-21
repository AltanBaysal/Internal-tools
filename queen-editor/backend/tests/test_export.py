import inspect
import os

import pytest

from backend import config
from backend.features.photo_generation.data.ffmpeg_video_exporter import FfmpegVideoExporter
from backend.features.photo_generation.domain.usecases.run_export import run_export
from backend.features.photo_generation.export_runner import ExportRunner
from backend.tests.test_photo_usecases import (
    FakeOrderStore,
    FakePlanStore,
    FakeRecord,
    FakeStore,
    frame,
)

FOLDER = "/fake/düğün/export/2026-08-12 14-32"
# Where a separate export's videos go: the dated folder held 22 of them beside the photos folder,
# and the user asked for them gathered (madde 283).
VIDEOS = f"{FOLDER}/video"
# Not under /fake: the pieces of a merged export are cut on the machine's own disk, never on Drive.
PIECES = "/tmp/fake-pieces"


class ExportStore(FakeStore):
    """FakeStore with the paths an export asks for, and a note of what it wrote and removed."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.removed = []
        self.photos = []
        self.exports = []
        self.order = []               # what happened, in the order it happened

    def file_path(self, project, filename):
        return f"/fake/{project}/{filename}"

    def make_export_folder(self, project, stamp):
        return f"/fake/{project}/export/{stamp}"

    def export_path(self, folder, filename):
        return f"{folder}/{filename}"

    def remove_dir(self, path):
        self.removed.append(path)

    def make_videos_dir(self, folder):
        """Where a separate export writes its videos -- a folder of its own inside the dated one."""
        return f"{folder}/video"

    def make_pieces_dir(self):
        """Where a merged export cuts its pieces -- the real one answers with a folder on the
        machine's own disk, and the path here is outside the Drive root on purpose."""
        self.pieces_dir = PIECES
        return PIECES

    def copy_photo(self, source, folder, filename):
        """Every call is written down and none is skipped.

        The real store refuses a target that is already there, and that refusal is tested against a
        real folder next door. A fake that copied the rule would leave these tests sinning against
        their own double instead of the code.
        """
        self.photos.append((source, folder, filename))

    def copy_export(self, source, folder, filename):
        """The merged file's one trip to Drive, written down.

        The real one lands in a single move, and that is tested against a real folder in
        test_photo_store.py: ffmpeg now writes the join on the machine's own disk, and Drive sees
        the file only once it is whole (madde 282).
        """
        self.exports.append((source, folder, filename))
        self.order.append("copy_export")


class FakeExporter:
    def __init__(self, fails_on=None, store=None):
        self.pieces = []
        self.merged = None
        self.fails_on = fails_on          # the target whose write blows up
        # When a store is handed over, the order of the two steps is written down in it: the copy
        # to Drive has to come after the join, or a half file is what Drive holds.
        self.store = store

    def piece(self, video, audio, target):
        if target == self.fails_on:
            raise RuntimeError("ffmpeg: disk dolu")
        self.pieces.append((video, audio, target))

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
                      exporter, lambda: "2026-08-12 14-32", "düğün", mode)


def test_separate_export_numbers_the_videos_from_the_foot_of_the_gallery():
    store, record, plan_store = with_videos()
    exporter = FakeExporter()

    folder = export(store, record, plan_store, exporter)

    # The gallery reads 1_a above 0_a; the sequence starts at its foot, so 0_a is 01.
    assert [target for _v, _a, target in exporter.pieces] == [
        f"{VIDEOS}/01.mp4", f"{VIDEOS}/02.mp4"]
    assert [video for video, _a, _t in exporter.pieces] == [
        "/fake/düğün/0_a_V1_0.mp4", "/fake/düğün/1_a_V1_0.mp4"]
    assert folder == FOLDER


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
        ("/fake/düğün/0_a.png", FOLDER, "01.png"),
        ("/fake/düğün/1_a.png", FOLDER, "02.png"),
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
        ("/fake/düğün/2_a.jpg", FOLDER, "01.jpg"),
        ("/fake/düğün/0_a.png", FOLDER, "02.png"),
        ("/fake/düğün/1_a.png", FOLDER, "03.png"),
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

    assert store.photos == [("/fake/düğün/0_a.png", FOLDER, "01.png")]


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
        ("/fake/düğün/1_a.png", FOLDER, "01.png"),
        ("/fake/düğün/0_a.png", FOLDER, "02.png"),
    ]


def test_a_copy_frames_video_is_written_all_the_same():
    """Only the picture is shared. The copy frame's video is its own file and its own place in the
    sequence."""
    store, record, plan_store = with_a_copy()
    exporter = FakeExporter()

    export(store, record, plan_store, exporter)

    assert [target for _v, _a, target in exporter.pieces] == [
        f"{VIDEOS}/01.mp4", f"{VIDEOS}/02.mp4"]
    assert [video for video, _a, _t in exporter.pieces] == [
        "/fake/düğün/0_a_V1_0.mp4", "/fake/düğün/0_b_V1_0.mp4"]


def test_a_merged_export_writes_the_shared_photo_once_too():
    store, record, plan_store = with_a_copy()

    export(store, record, plan_store, FakeExporter(), mode="merged")

    assert store.photos == [("/fake/düğün/0_a.png", FOLDER, "01.png")]


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
    # (madde 282). The name is still the project's.
    assert exporter.merged == ([f"{PIECES}/01.mp4", f"{PIECES}/02.mp4"], f"{PIECES}/düğün.mp4")


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
        ("/fake/düğün/0_a.png", FOLDER, "01.png"),
        ("/fake/düğün/1_a.png", FOLDER, "02.png"),
    ]


def test_a_separate_export_writes_its_pieces_into_the_drive_folder_and_removes_nothing():
    """Separate export's whole job is those files: nothing here is scaffolding."""
    store, record, plan_store = with_videos()
    exporter = FakeExporter()

    export(store, record, plan_store, exporter)

    assert [target for _v, _a, target in exporter.pieces] == [
        f"{VIDEOS}/01.mp4", f"{VIDEOS}/02.mp4"]
    assert store.removed == []


def test_a_separate_exports_videos_are_never_taken_away_again():
    """The trap this item walks into. A finished run removes the folder it cut into when that is
    not the dated folder -- a rule written for a merged export's pieces on the machine's own disk
    (madde 235). Now that the videos sit in a folder of their own, that rule would match the
    separate export too and delete exactly what the user asked for.

    So the condition belongs to the mode, not to the paths. FOUNDATION 1: the user's work is
    sacred, and nothing this item does is worth a deleted export.
    """
    store, record, plan_store = with_videos()

    folder = export(store, record, plan_store, FakeExporter())

    assert store.removed == []
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
        ("/fake/düğün/0_a_V1_0.mp4", None, f"{VIDEOS}/01.mp4"),
        ("/fake/düğün/1_a_V1_0.mp4", None, f"{VIDEOS}/02.mp4"),
    ]


def test_the_merged_file_reaches_drive_once_it_is_whole():
    store, record, plan_store = with_videos()

    folder = export(store, record, plan_store, FakeExporter(), mode="merged")

    assert store.exports == [(f"{PIECES}/düğün.mp4", folder, "düğün.mp4")]


def test_the_copy_to_drive_comes_after_the_join():
    """The order is the whole point: while the join runs, the Drive folder holds nothing, so a
    half written mp4 is never there to be seen (FOUNDATION 1, madde 94's own reasoning)."""
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter(store=store), mode="merged")

    assert store.order == ["merge", "copy_export"]


def test_a_join_that_blew_up_copies_nothing_to_drive():
    store, record, plan_store = with_videos()
    exporter = FakeExporter(fails_on=f"{PIECES}/düğün.mp4")

    with pytest.raises(RuntimeError):
        export(store, record, plan_store, exporter, mode="merged")

    assert store.exports == []
    assert sorted(store.removed) == sorted([FOLDER, PIECES])


def test_a_separate_export_has_no_copying_step_at_all():
    """Its pieces are the export, and they are written where the user will look for them -- 235's
    call, and this item does not touch it."""
    store, record, plan_store = with_videos()

    export(store, record, plan_store, FakeExporter())

    assert store.exports == []


def test_a_merged_export_that_blows_up_leaves_neither_folder_behind():
    store, record, plan_store = with_videos()
    exporter = FakeExporter(fails_on=f"{PIECES}/02.mp4")

    with pytest.raises(RuntimeError):
        export(store, record, plan_store, exporter, mode="merged")

    assert sorted(store.removed) == sorted([FOLDER, PIECES])


def test_a_cancelled_merged_export_leaves_neither_folder_behind():
    store, record, plan_store = with_videos()
    runner = sync_runner()
    runner.cancel("merged")

    assert export(store, record, plan_store, FakeExporter(), mode="merged", runner=runner) is None
    assert sorted(store.removed) == sorted([FOLDER, PIECES])


def test_a_failed_export_takes_its_half_written_folder_with_it():
    store, record, plan_store = with_videos()
    exporter = FakeExporter(fails_on=f"{VIDEOS}/02.mp4")
    runner = sync_runner()

    with pytest.raises(RuntimeError):
        export(store, record, plan_store, exporter, runner=runner)

    assert store.removed == [FOLDER]


def test_the_reason_a_run_failed_is_the_tool_own_words():
    store, record, plan_store = with_videos()
    runner = sync_runner()

    runner.start("separate", lambda: run_export(
        runner, store, record, plan_store, FakeOrderStore(),
        FakeExporter(fails_on=f"{VIDEOS}/01.mp4"), lambda: "2026-08-12 14-32", "düğün", "separate"))

    assert runner.state()["separate"]["state"] == "error"
    assert runner.state()["separate"]["error"] == "ffmpeg: disk dolu"


def test_cancelling_stops_between_pieces_and_removes_the_folder():
    store, record, plan_store = with_videos()
    runner = sync_runner()
    runner.cancel("separate")
    exporter = FakeExporter()

    assert export(store, record, plan_store, exporter, runner=runner) is None
    assert exporter.pieces == []
    assert store.removed == [FOLDER]


def test_the_state_counts_what_has_been_written():
    store, record, plan_store = with_videos()
    runner = sync_runner()

    export(store, record, plan_store, FakeExporter(), runner=runner)

    assert runner.state()["separate"] == {"state": "done", "written": 2, "total": 2,
                                          "target": FOLDER, "error": None}
    # The mode nobody asked for is untouched.
    assert runner.state()["merged"]["state"] == "idle"


def test_a_second_run_of_the_same_mode_is_refused_while_one_is_going():
    runner = ExportRunner(spawn=lambda fn: None)     # claims the mode, never runs the job

    assert runner.start("separate", lambda: None) is True
    assert runner.start("separate", lambda: None) is False
    # The other mode is free: the design lets the two run side by side.
    assert runner.start("merged", lambda: None) is True


class _Answer:
    """What subprocess.run hands back for one call."""

    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class FakeRun:
    """subprocess.run's answer, and a note of what it was asked to run.

    `sizes` maps a file name to what ffprobe prints for it; a file nobody named answers with the
    first size, so a test that does not care about sizes says nothing about them. A probe and a
    concat fail differently, so each carries its own exit code and message.

    `sounds` answers the other probe -- a piece's sample rate and channel layout, or an empty line
    for a piece with no audio at all. Nothing is the default: a set where no piece carries sound is
    one of the two even sets, so a test that says nothing about sound asks about that (madde 286).
    """

    def __init__(self, returncode=0, stderr="", sizes=None, probe_returncode=0, probe_stderr="",
                 nvenc=False, sounds=None):
        self.calls = []
        self.returncode = returncode
        self.stderr = stderr
        self.sizes = dict(sizes or {})
        self.sounds = dict(sounds or {})
        self.joined = None                # what the concat list held when it was read
        self.probe_returncode = probe_returncode
        self.probe_stderr = probe_stderr
        # Whether the trial encode on the card comes back. False is a machine that cannot encode
        # with nvenc -- what every test that says nothing about it is asking about (madde 257).
        self.nvenc = nvenc

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        if "concat" in args:
            # Read the list while it is still there, the way ffmpeg would: merge takes it away
            # again, so a test can only see what it held at the moment of the call.
            with open(args[args.index("-i") + 1], encoding="utf-8") as handle:
                self.joined = [line.strip()[len("file '"):-1] for line in handle]
        if "ffprobe" in args[0]:
            if "a:0" in args:
                # An empty answer is what a file with no audio stream gets, and it is an answer.
                return _Answer(0, self.sounds.get(args[-1], "") + "\n", "")
            size = self.sizes.get(args[-1], next(iter(self.sizes.values()), "848x480"))
            return _Answer(self.probe_returncode, size + "\n", self.probe_stderr)
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


def size_calls(run):
    return [call for call in probe_calls(run) if "a:0" not in call]


def sound_calls(run):
    """The other question asked of a piece: what sound it carries, if any (madde 286)."""
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


# How the joined picture is made. The canvas is the user's call and it is landscape: exports are
# taken landscape either way, and the disclaimer only becomes readable at that width (madde 259).
# `decrease` fits rather than crops, so nothing is lost and the sides get bars; the disclaimer then
# spans the whole 1920, which is what the 1902-wide PNG was drawn for.
FIT = ("scale=1920:1080:force_original_aspect_ratio=decrease,"
       "pad=1920:1080:(ow-iw)/2:(oh-ih)/2")
STAMP = (f"[0:v]{FIT}[c];"
         "[1:v]scale=1920:-1[d];"
         "[c][d]overlay=(W-w)/2:H-h-43:enable='lt(t,60)'[v]")
ENCODE = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]
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
    run = FakeRun(sizes={"a.mp4": "480x720"}, nvenc=True)

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4"], str(tmp_path / "d.mp4"))

    assert encoder_calls(run) == [TRIAL]


def test_an_unusable_gpu_leaves_the_export_running_on_the_cpu(tmp_path):
    """The trial failing is an answer, not an error: losing a whole export to a guess is worse than
    a slow export (FOUNDATION 1)."""
    run = FakeRun(sizes={"a.mp4": "480x720"}, nvenc=False)

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4"], str(tmp_path / "d.mp4"))

    said = ffmpeg_calls(run)[0]
    assert ENCODE == [part for part in said if part in ENCODE]
    assert "h264_nvenc" not in said


def test_a_merged_export_is_encoded_on_the_gpu_too(tmp_path):
    """The join is where the whole timeline is encoded, so it is where the GPU is worth most."""
    run = FakeRun(sizes={"a.mp4": "480x720", "b.mp4": "480x720"}, nvenc=True)
    target = str(tmp_path / "düğün.mp4")

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"], target)

    assert ffmpeg_calls(run)[0] == [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp_path / "pieces.txt"),
        "-i", "d.png", "-filter_complex", STAMP, "-map", "[v]", "-map", "0:a?",
        *NVENC, "-c:a", "copy", target]


def test_the_card_is_tried_once_and_not_again(tmp_path):
    """The answer cannot change while the process lives, and a trial costs a process."""
    run = FakeRun(sizes={"a.mp4": "480x720"}, nvenc=True)
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


def test_merging_hands_ffmpeg_a_list_and_takes_it_away_again(tmp_path):
    run = FakeRun()
    target = str(tmp_path / "düğün.mp4")

    FfmpegVideoExporter(run=run).merge(["a.mp4", "b.mp4"], target)

    # The concat itself is unchanged; it is no longer the first thing run, because the sizes are
    # asked first.
    assert ffmpeg_calls(run)[0][:8] == ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
                                        str(tmp_path / "pieces.txt")]
    assert not (tmp_path / "pieces.txt").exists()


def test_merging_asks_every_piece_how_big_it_is(tmp_path):
    """Streams are copied rather than re-encoded, which is only safe while every piece is the same
    size. Nothing checked that until madde 218 made it possible for one project to hold two."""
    run = FakeRun(sizes={"a.mp4": "848x480", "b.mp4": "848x480"})

    FfmpegVideoExporter(run=run).merge(["a.mp4", "b.mp4"], str(tmp_path / "düğün.mp4"))

    # The size question only: a piece is asked about its sound as well now (madde 286), and this
    # test is about the older of the two.
    assert [call[-1] for call in size_calls(run)] == ["a.mp4", "b.mp4"]


def test_a_merged_export_joins_and_stamps_in_one_call(tmp_path):
    """The disclaimer rides on the join rather than on the pieces, which is what makes its clock the
    joined video's own: `lt(t,60)` counts the merged stream, so the minute ends exactly on the
    minute even when a frame straddles it (madde 250, user's call).

    Joining is one read already, and the filter sits on top of that read -- so nothing has to know
    which frame starts at which second, and no piece is ever encoded next to a copied one.

    The sound is mapped and copied: the pieces carry their own, and `?` is for a set that has none.
    """
    run = FakeRun(sizes={"a.mp4": "480x720", "b.mp4": "480x720"})
    target = str(tmp_path / "düğün.mp4")

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"], target)

    assert ffmpeg_calls(run)[0] == [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp_path / "pieces.txt"),
        "-i", "d.png", "-filter_complex", STAMP, "-map", "[v]", "-map", "0:a?",
        *ENCODE, "-c:a", "copy", target]


def filtergraph(run):
    """What the merged call handed -filter_complex."""
    call = ffmpeg_calls(run)[0]
    return call[call.index("-filter_complex") + 1]


def merged(sizes, tmp_path, name="düğün.mp4"):
    """One merged export over pieces of the given sizes, and the FakeRun that watched it."""
    run = FakeRun(sizes=sizes)
    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(list(sizes), str(tmp_path / name))
    return run


def test_the_merged_canvas_is_the_same_whatever_the_pieces_measure(tmp_path):
    """The canvas is written down, not inherited. It used to be the first piece's own size, which is
    why the merged file came out vertical at 480 wide and the disclaimer could not be read there
    (madde 259).

    Two projects, one vertical and one landscape, and one frame: whatever the graph produced, the
    export stands on the same 1920x1080. This is what makes the item need no measurement -- what
    today's file measures cannot change the answer.
    """
    vertical = merged({"a.mp4": "480x720", "b.mp4": "480x720"}, tmp_path, "dikey.mp4")
    landscape = merged({"c.mp4": "848x480", "d.mp4": "848x480"}, tmp_path, "yatay.mp4")

    assert filtergraph(vertical) == filtergraph(landscape) == STAMP


def test_a_merged_export_stands_on_a_landscape_canvas(tmp_path):
    """Fitted, never cropped: the user's word was "sığdır", and they took the bars knowingly --
    a 480x720 frame becomes 720x1080 with 600 pixels of bar either side. `decrease` is what picks
    the largest size that fits inside the canvas; `increase` would fill it by cutting the frame's
    top and bottom off, and FOUNDATION 1 does not trade a user's finished frame for a tidy edge.
    """
    said = filtergraph(merged({"a.mp4": "480x720"}, tmp_path))

    assert "scale=1920:1080:force_original_aspect_ratio=decrease" in said
    assert "pad=1920:1080:(ow-iw)/2:(oh-ih)/2" in said
    assert "crop" not in said and "increase" not in said


def test_the_disclaimer_fills_the_canvas_width(tmp_path):
    """The user asked for it twice over -- "disclaimerı da ona göre büyüt, asıl videodan büyük
    olabilir" and "yatayda dolduracak şekilde" -- so the 80% of madde 249 is gone. The PNG is
    1902 wide, which means 1920 barely scales it and its two lines stay about 99 pixels tall:
    the first size at which they can be read.

    The 720-pixel video does not bound it: the disclaimer runs over the bars, which is exactly what
    "asıl videodan büyük olabilir" allows.
    """
    said = filtergraph(merged({"a.mp4": "480x720"}, tmp_path))

    assert "[1:v]scale=1920:-1[d]" in said
    assert "scale=384:-1" not in said              # 80% of the old 480-wide canvas
    assert "H-h-43" in said                        # 4% of 1080, measured from the canvas now


def test_every_piece_is_asked_whether_it_carries_sound(tmp_path):
    """merge asks a piece its size and refuses a set holding two, but it never asked about the
    streams -- and concat wants every file to carry the same ones. A piece has sound when its frame
    had a sound layer, or when the source video carried its own (an H3 video does, madde 243); a
    WAN video with no sound layer has none. So one project can hold both, and `-map 0:a?` does not
    save it: that only allows a set with no sound at all (madde 286).
    """
    run = FakeRun(sizes={"a.mp4": "480x720", "b.mp4": "480x720"})

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    assert [call[-1] for call in sound_calls(run)] == ["a.mp4", "b.mp4"]


def test_a_set_that_all_carries_sound_is_joined_with_nothing_written_first(tmp_path):
    """The rule costs nothing where nothing is wrong: the join is still the only writing call."""
    run = FakeRun(sizes={"a.mp4": "480x720", "b.mp4": "480x720"},
                  sounds={"a.mp4": "48000:stereo", "b.mp4": "48000:stereo"})

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    assert len(ffmpeg_calls(run)) == 1
    assert run.joined == ["a.mp4", "b.mp4"]


def test_a_set_that_carries_no_sound_at_all_is_joined_untouched(tmp_path):
    """The other even set, and the common one: a WAN project with no sound layers. `-map 0:a?`
    already carries it, so silence would be work bought for nothing (FOUNDATION 3)."""
    run = FakeRun(sizes={"a.mp4": "480x720", "b.mp4": "480x720"})

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
    run = FakeRun(sizes={"a.mp4": "480x720", "b.mp4": "480x720"},
                  sounds={"a.mp4": "48000:stereo"})

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    written = ffmpeg_calls(run)[0]
    assert written == ["ffmpeg", "-y", "-i", "b.mp4",
                       "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                       "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                       "-shortest", "b-sound.mp4"]
    # And the join reads the repaired piece in the silent one's place, order untouched.
    assert run.joined == ["a.mp4", "b-sound.mp4"]


def test_the_silence_matches_the_sound_the_other_pieces_carry(tmp_path):
    """A guessed 48000:stereo would stop concat just as surely as no stream at all: what has to
    match is the set's own sound, so the numbers come from the piece that has some."""
    run = FakeRun(sizes={"a.mp4": "480x720", "b.mp4": "480x720"},
                  sounds={"a.mp4": "44100:mono"})

    FfmpegVideoExporter(run=run, disclaimer="d.png").merge(["a.mp4", "b.mp4"],
                                                           str(tmp_path / "düğün.mp4"))

    assert "anullsrc=r=44100:cl=mono" in ffmpeg_calls(run)[0]


def test_mixed_sizes_stop_the_merge_and_name_what_was_found(tmp_path):
    """A project made before the frames went landscape and added to afterwards. concat -c copy
    would write a file whose later pieces are unplayable, and say nothing.

    The message is a list rather than a sentence: "the pieces are different sizes" does not tell
    anyone which frame to re-render.
    """
    run = FakeRun(sizes={"a.mp4": "848x480", "b.mp4": "480x720"})

    with pytest.raises(RuntimeError) as caught:
        FfmpegVideoExporter(run=run).merge(["a.mp4", "b.mp4"], str(tmp_path / "düğün.mp4"))

    said = str(caught.value)
    assert "a.mp4" in said and "848x480" in said
    assert "b.mp4" in said and "480x720" in said


def test_nothing_is_merged_when_the_sizes_disagree(tmp_path):
    """Stopping after writing half a file would leave exactly what the export's own rule forbids:
    a folder that looks finished."""
    run = FakeRun(sizes={"a.mp4": "848x480", "b.mp4": "480x720"})

    with pytest.raises(RuntimeError):
        FfmpegVideoExporter(run=run).merge(["a.mp4", "b.mp4"], str(tmp_path / "düğün.mp4"))

    assert ffmpeg_calls(run) == []
    assert not (tmp_path / "pieces.txt").exists()


def test_a_size_that_cannot_be_read_says_what_ffprobe_said(tmp_path):
    """A missing file, a file that is not a video, an ffprobe that is not installed -- three causes
    with one symptom, and only ffprobe knows which. Guessing one here would be the repo's own
    "never invent a cause" rule broken in the place it was written for.
    """
    run = FakeRun(sizes={"a.mp4": ""}, probe_returncode=1,
                  probe_stderr="a.mp4: No such file or directory")

    with pytest.raises(RuntimeError) as caught:
        FfmpegVideoExporter(run=run).merge(["a.mp4", "b.mp4"], str(tmp_path / "düğün.mp4"))

    assert "a.mp4: No such file or directory" in str(caught.value)
