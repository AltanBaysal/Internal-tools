import os

import pytest

from backend.features.photo_generation.data.mmaudio_generator import (
    NEGATIVE,
    MMAudioGenerator,
)


class FakeSampler:
    """Stands in for the torch side: writes down every render and answers with bytes."""

    def __init__(self, wav=b"RIFFwav"):
        self.calls = []
        self.wav = wav

    def render(self, video, prompt, negative, seed, duration):
        self.calls.append({"video": video, "prompt": prompt, "negative": negative,
                           "seed": seed, "duration": duration})
        return self.wav


class FakeFfmpeg:
    """Answers with a fixed length and writes down what was cut and joined."""

    def __init__(self, seconds=5.0):
        self.seconds = seconds
        self.cuts = []
        self.joins = []

    def duration(self, _video):
        return self.seconds

    def cut(self, video, start, duration, target):
        self.cuts.append((video, start, duration, target))
        with open(target, "wb") as handle:
            handle.write(b"piece")

    def join(self, parts, target, fade_ms):
        self.joins.append((list(parts), target, fade_ms))
        with open(target, "wb") as handle:
            handle.write(b"joined")


def make(tmp_path, sampler=None, ffmpeg=None):
    return MMAudioGenerator(sampler or FakeSampler(), ffmpeg or FakeFfmpeg(),
                            tmp_dir=str(tmp_path))


SOURCE = ("P0_0_V1_0.mp4", b"mp4 bytes")


def test_a_sound_needs_a_video_to_sit_on(tmp_path):
    with pytest.raises(RuntimeError) as exc:
        make(tmp_path).generate("waves", "", 7)
    assert str(exc.value) == "Ses için kaynak video verilmedi"


def test_the_words_the_seed_and_the_length_reach_the_model(tmp_path):
    sampler = FakeSampler()
    generator = make(tmp_path, sampler, FakeFfmpeg(seconds=5.0))

    generator.generate("waves on rock", "", 4242, source=SOURCE)

    assert len(sampler.calls) == 1
    call = sampler.calls[0]
    assert call["prompt"] == "waves on rock"
    assert call["seed"] == 4242
    assert call["duration"] == pytest.approx(5.0)


def test_an_empty_negative_falls_back_to_the_one_the_model_needs(tmp_path):
    sampler = FakeSampler()

    make(tmp_path, sampler).generate("waves", "", 1, source=SOURCE)

    assert sampler.calls[0]["negative"] == NEGATIVE
    assert "music" in NEGATIVE and "speech" in NEGATIVE


def test_a_negative_that_was_written_wins_over_the_default(tmp_path):
    sampler = FakeSampler()

    make(tmp_path, sampler).generate("waves", "no birds", 1, source=SOURCE)

    assert sampler.calls[0]["negative"] == "no birds"


def test_a_short_video_is_rendered_in_one_go(tmp_path):
    sampler = FakeSampler()
    ffmpeg = FakeFfmpeg(seconds=5.0)

    make(tmp_path, sampler, ffmpeg).generate("waves", "", 1, source=SOURCE)

    assert len(sampler.calls) == 1
    assert len(ffmpeg.cuts) == 1          # the whole video, still prepared the one way
    assert ffmpeg.cuts[0][1:3] == (0, 5.0)
    assert ffmpeg.joins == []             # nothing to join


def test_a_long_video_is_rendered_piece_by_piece_and_joined(tmp_path):
    sampler = FakeSampler()
    ffmpeg = FakeFfmpeg(seconds=24.0)

    make(tmp_path, sampler, ffmpeg).generate("waves", "", 1, source=SOURCE)

    assert len(sampler.calls) == 3
    assert [call["duration"] for call in sampler.calls] == [8.0, 8.0, 8.0]
    assert len(ffmpeg.joins) == 1
    parts, _target, fade_ms = ffmpeg.joins[0]
    assert len(parts) == 3
    assert fade_ms == 100


def test_the_answer_is_the_sound_itself(tmp_path):
    # Bytes and nothing else: the queue names the file, not the producer.
    assert make(tmp_path).generate("waves", "", 1, source=SOURCE) == b"RIFFwav"


def test_nothing_is_left_behind_on_disk(tmp_path):
    generator = make(tmp_path)

    generator.generate("waves", "", 1, source=SOURCE)

    assert os.listdir(tmp_path) == []


def test_a_failed_render_cleans_up_after_itself(tmp_path):
    class Broken(FakeSampler):
        def render(self, *_args, **_kwargs):
            raise RuntimeError("CUDA out of memory")

    with pytest.raises(RuntimeError) as exc:
        make(tmp_path, Broken()).generate("waves", "", 1, source=SOURCE)

    assert str(exc.value) == "CUDA out of memory"
    assert os.listdir(tmp_path) == []
