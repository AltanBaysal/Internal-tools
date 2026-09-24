import pytest

from backend.features.photo_generation.data.ffmpeg_stills import FfmpegStills


class FakeRun:
    """ffmpeg, without ffmpeg: keeps the command and writes to the target it was given.

    Written here rather than shared with test_ffmpeg_audio: each file tries one tool, and the fake
    standing beside the calls it answers is half of what makes either readable.
    """

    def __init__(self, returncode=0, stderr="", writes=b"PNG"):
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = ""
        self.writes = writes
        self.calls = []

    def __call__(self, args, **_kwargs):
        self.calls.append(args)
        if self.returncode == 0:
            with open(args[-1], "wb") as handle:
                handle.write(self.writes)
        return self


def test_the_first_frame_comes_back_as_bytes(tmp_path):
    run = FakeRun()

    data = FfmpegStills(run=run, tmp_dir=str(tmp_path)).first_frame(b"MP4")

    assert data == b"PNG"


def test_only_the_first_frame_is_asked_for(tmp_path):
    run = FakeRun()

    FfmpegStills(run=run, tmp_dir=str(tmp_path)).first_frame(b"MP4")

    args = run.calls[0]
    # One frame and no seek: the picture is the video's very beginning, which is what makes it the
    # card's own (madde 296).
    assert args[args.index("-frames:v") + 1] == "1"
    assert "-ss" not in args
    assert args[-1].endswith(".png")


def test_the_video_reaches_ffmpeg_as_a_file(tmp_path):
    """The bytes arrive from Drive, and ffmpeg reads paths -- so the room it works in is this
    class's own business, and nothing of it is left behind."""
    seen = {}
    run = FakeRun()
    original = run.__call__

    def watch(args, **kwargs):
        with open(args[args.index("-i") + 1], "rb") as handle:
            seen["video"] = handle.read()
        return original(args, **kwargs)

    FfmpegStills(run=watch, tmp_dir=str(tmp_path)).first_frame(b"MP4")

    assert seen["video"] == b"MP4"
    assert list(tmp_path.iterdir()) == []


def test_a_failed_extraction_carries_ffmpegs_own_last_line(tmp_path):
    run = FakeRun(returncode=1, stderr="banner\nmoov atom not found\n")

    with pytest.raises(RuntimeError) as exc:
        FfmpegStills(run=run, tmp_dir=str(tmp_path)).first_frame(b"MP4")

    assert str(exc.value) == "moov atom not found"
