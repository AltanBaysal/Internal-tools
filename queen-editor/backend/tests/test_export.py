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


def test_merged_export_writes_one_file_named_after_the_project():
    store, record, plan_store = with_videos()
    exporter = FakeExporter()

    export(store, record, plan_store, exporter, mode="merged")

    assert exporter.merged == ([f"{FOLDER}/01.mp4", f"{FOLDER}/02.mp4"], f"{FOLDER}/düğün.mp4")


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


class FakeRun:
    """subprocess.run's answer, and a note of what it was asked to run."""

    def __init__(self, returncode=0, stderr=""):
        self.calls = []
        self.returncode = returncode
        self.stderr = stderr

    def __call__(self, args, **kwargs):
        self.calls.append(args)
        return self

    @property
    def stdout(self):
        return ""


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

    assert run.calls[0][:8] == ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i",
                                str(tmp_path / "pieces.txt")]
    assert not (tmp_path / "pieces.txt").exists()
