import pytest

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
# Not under /fake: the pieces of a merged export are cut on the machine's own disk, never on Drive.
PIECES = "/tmp/fake-pieces"


class ExportStore(FakeStore):
    """FakeStore with the paths an export asks for, and a note of what it wrote and removed."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.removed = []
        self.photos = []

    def file_path(self, project, filename):
        return f"/fake/{project}/{filename}"

    def make_export_folder(self, project, stamp):
        return f"/fake/{project}/export/{stamp}"

    def export_path(self, folder, filename):
        return f"{folder}/{filename}"

    def remove_dir(self, path):
        self.removed.append(path)

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


class FakeExporter:
    def __init__(self, fails_on=None):
        self.pieces = []
        self.merged = None
        self.fails_on = fails_on          # the target whose write blows up

    def piece(self, video, audio, target):
        if target == self.fails_on:
            raise RuntimeError("ffmpeg: disk dolu")
        self.pieces.append((video, audio, target))

    def merge(self, pieces, target):
        self.merged = (list(pieces), target)


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
        f"{FOLDER}/01.mp4", f"{FOLDER}/02.mp4"]
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
        f"{FOLDER}/01.mp4", f"{FOLDER}/02.mp4"]
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

    assert exporter.merged == ([f"{PIECES}/01.mp4", f"{PIECES}/02.mp4"], f"{FOLDER}/düğün.mp4")


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
        f"{FOLDER}/01.mp4", f"{FOLDER}/02.mp4"]
    assert store.removed == []


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
    exporter = FakeExporter(fails_on=f"{FOLDER}/02.mp4")
    runner = sync_runner()

    with pytest.raises(RuntimeError):
        export(store, record, plan_store, exporter, runner=runner)

    assert store.removed == [FOLDER]


def test_the_reason_a_run_failed_is_the_tool_own_words():
    store, record, plan_store = with_videos()
    runner = sync_runner()

    runner.start("separate", lambda: run_export(
        runner, store, record, plan_store, FakeOrderStore(),
        FakeExporter(fails_on=f"{FOLDER}/01.mp4"), lambda: "2026-08-12 14-32", "düğün", "separate"))

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
    """

    def __init__(self, returncode=0, stderr="", sizes=None, probe_returncode=0, probe_stderr=""):
        self.calls = []
        self.returncode = returncode
        self.stderr = stderr
        self.sizes = dict(sizes or {})
        self.probe_returncode = probe_returncode
        self.probe_stderr = probe_stderr

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        if "ffprobe" in args[0]:
            size = self.sizes.get(args[-1], next(iter(self.sizes.values()), "848x480"))
            return _Answer(self.probe_returncode, size + "\n", self.probe_stderr)
        return _Answer(self.returncode, "", self.stderr)


def ffmpeg_calls(run):
    return [call for call in run.calls if call[0] == "ffmpeg"]


def probe_calls(run):
    return [call for call in run.calls if "ffprobe" in call[0]]


def test_a_silent_piece_is_copied_rather_than_re_encoded():
    run = FakeRun()

    FfmpegVideoExporter(run=run).piece("0.mp4", None, "01.mp4")

    assert run.calls[0] == ["ffmpeg", "-y", "-i", "0.mp4", "-c", "copy", "01.mp4"]


def test_a_sound_is_laid_over_the_video():
    run = FakeRun()

    FfmpegVideoExporter(run=run).piece("0.mp4", "0.wav", "01.mp4")

    assert run.calls[0] == ["ffmpeg", "-y", "-i", "0.mp4", "-i", "0.wav", "-c:v", "copy",
                            "-c:a", "aac", "-shortest", "01.mp4"]


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

    assert [call[-1] for call in probe_calls(run)] == ["a.mp4", "b.mp4"]


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
