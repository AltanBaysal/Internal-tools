import pytest

from backend.features.photo_generation.data.ffmpeg_clips import FfmpegClips


class FakeRun:
    """ffprobe, without ffprobe: keeps the command and answers however the test wants."""

    def __init__(self, returncode=0, stdout="4.200000\n", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.calls = []

    def __call__(self, args, **_kwargs):
        self.calls.append(args)
        return self


def test_the_length_comes_back_as_a_number(tmp_path):
    run = FakeRun()

    assert FfmpegClips(run=run, tmp_dir=str(tmp_path)).seconds(b"MP4") == pytest.approx(4.2)


def test_the_bytes_reach_ffprobe_as_a_file(tmp_path):
    """They arrive from a browser and ffprobe reads paths, so the room is this class's own and
    nothing of it is left behind."""
    seen = {}

    def watch(args, **_kwargs):
        with open(args[-1], "rb") as handle:
            seen["clip"] = handle.read()
        return FakeRun()(args)

    FfmpegClips(run=watch, tmp_dir=str(tmp_path)).seconds(b"MP4")

    assert seen["clip"] == b"MP4"
    assert list(tmp_path.iterdir()) == []


def test_a_length_that_cannot_be_read_carries_ffprobes_own_last_line(tmp_path):
    run = FakeRun(returncode=1, stdout="", stderr="banner\nmoov atom not found\n")

    with pytest.raises(RuntimeError) as exc:
        FfmpegClips(run=run, tmp_dir=str(tmp_path)).seconds(b"MP4")

    assert str(exc.value) == "moov atom not found"


def test_an_answer_with_no_number_in_it_is_a_failure(tmp_path):
    # ffprobe can return 0 and say nothing at all about a file it did not understand.
    run = FakeRun(stdout="\n")

    with pytest.raises(RuntimeError):
        FfmpegClips(run=run, tmp_dir=str(tmp_path)).seconds(b"MP4")
