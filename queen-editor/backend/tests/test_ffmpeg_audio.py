import pytest

from backend.features.photo_generation.data.ffmpeg_audio import FfmpegAudio


class FakeRun:
    """Stands in for subprocess.run: writes down every command and answers what it is told to."""

    def __init__(self, stdout="", returncode=0, stderr=""):
        self.calls = []
        self.stdout = stdout
        self.returncode = returncode
        self.stderr = stderr

    def __call__(self, args, **_kwargs):
        self.calls.append(args)
        return type("Done", (), {"returncode": self.returncode, "stdout": self.stdout,
                                 "stderr": self.stderr})()


def test_the_duration_comes_back_as_a_number():
    run = FakeRun(stdout="5.280000\n")
    assert FfmpegAudio(run=run).duration("/v/0.mp4") == pytest.approx(5.28)
    assert "/v/0.mp4" in run.calls[0]


def test_reading_a_duration_that_fails_says_what_the_tool_said():
    run = FakeRun(returncode=1, stderr="moov atom not found")
    with pytest.raises(RuntimeError) as exc:
        FfmpegAudio(run=run).duration("/v/0.mp4")
    assert "moov atom not found" in str(exc.value)


def test_a_piece_is_cut_at_the_size_and_rate_the_model_reads():
    run = FakeRun()
    FfmpegAudio(run=run).cut("/v/0.mp4", 8.0, 8.0, "/tmp/p2.mp4")

    args = run.calls[0]
    assert args[args.index("-ss") + 1] == "8.0"
    assert args[args.index("-t") + 1] == "8.0"
    # 25 fps for Synchformer, 720p to keep the encoder's work sane, and no sound of its own.
    assert "fps=25,scale=-2:720" in args
    assert "-an" in args
    assert args[-1] == "/tmp/p2.mp4"


def test_one_piece_is_copied_rather_than_crossfaded():
    """acrossfade needs two inputs; a single piece has nothing to fade into."""
    copied = []
    audio = FfmpegAudio(run=FakeRun(), copy=lambda src, dst: copied.append((src, dst)))

    audio.join(["/tmp/a1.wav"], "/tmp/out.wav", fade_ms=100)

    assert copied == [("/tmp/a1.wav", "/tmp/out.wav")]


def test_pieces_are_joined_with_a_fade_at_every_seam():
    run = FakeRun()
    FfmpegAudio(run=run).join(["/tmp/a1.wav", "/tmp/a2.wav", "/tmp/a3.wav"], "/tmp/out.wav",
                              fade_ms=100)

    args = run.calls[0]
    chain = args[args.index("-filter_complex") + 1]
    # Two seams for three pieces, and the last one carries the label that gets mapped out.
    assert chain == ("[0:a][1:a]acrossfade=d=0.1:c1=tri:c2=tri[a1];"
                     "[a1][2:a]acrossfade=d=0.1:c1=tri:c2=tri[outa]")
    assert args[args.index("-map") + 1] == "[outa]"
    assert args[-1] == "/tmp/out.wav"


def test_a_failed_join_carries_ffmpegs_own_last_line():
    run = FakeRun(returncode=1, stderr="banner\nInvalid argument\n")
    with pytest.raises(RuntimeError) as exc:
        FfmpegAudio(run=run).join(["/tmp/a1.wav", "/tmp/a2.wav"], "/tmp/out.wav", fade_ms=100)
    assert str(exc.value) == "Invalid argument"
