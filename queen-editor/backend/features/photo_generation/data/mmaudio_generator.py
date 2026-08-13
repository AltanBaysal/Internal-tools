"""The sound producer over MMAudio -- the only place that knows how a sound job becomes a wav.

MMAudio runs inside this process rather than behind ComfyUI (user's decision, 2026-08-13): the
notebook that already makes these sounds drives the library directly, and building a ComfyUI graph
for it would be a second way of doing something that works. The settings are that notebook's, to
the number.

The work is video work first: MMAudio reads the picture as well as the words, so the frame's video
is cut to what the model expects before anything is generated, and long videos are cut into pieces
near the length the model was trained on. Everything torch touches lives behind `sampler` -- this
file never imports it, so the suite runs on a machine with no GPU.
"""
import os
import random
import shutil
import tempfile

from backend.features.photo_generation.domain.audio_chunks import chunks

# What the sound must not contain. Ours to default, not the user's to remember: MMAudio drifts into
# music and voices unless it is told, and no sound job carries a negative of its own today.
NEGATIVE = "music, speech, voices, singing, talking, vocals"
# The fade at a seam between two pieces -- long enough to hide the click, short enough to not be
# heard as a fade.
FADE_MS = 100


def _random_seed():
    """The seed a sound job never carries. The same range photo jobs are planned in, so a seed is
    a seed wherever it was born."""
    return random.randint(0, 2**31 - 1)


class MMAudioGenerator:
    def __init__(self, sampler, ffmpeg, tmp_dir=None, new_seed=None):
        self._sampler = sampler
        self._ffmpeg = ffmpeg
        self._tmp_dir = tmp_dir
        # A port for the test's sake rather than the wiring's: which numbers come out is nobody's
        # choice, but a test cannot prove two jobs got different seeds without knowing them.
        self._new_seed = new_seed or _random_seed

    def generate(self, prompt, negative, seed, model="", source=None):
        """`source` is the frame's video as (name, bytes); the answer is its sound as bytes.

        The name is not ours to give: the queue names every layer file from the domain's scheme
        (photo_name.layer_file), and a second name written here drifts from it -- as it had.

        `model` belongs to the port rather than to this engine: which weights are used is the
        installation's answer, and a sound job carries no choice of its own.
        """
        if not source:
            raise RuntimeError("Ses için kaynak video verilmedi")
        # A sound job is planned with no seed of its own -- only photos are seeded, and a layer is
        # made from what is under it. torch's manual_seed takes a long and raises on None, so the
        # missing one is chosen here: once per job, so every piece of one sound shares it, and
        # freshly each time, so two sound variants of one video are two different sounds.
        if seed is None:
            seed = self._new_seed()
        _name, data = source
        room = tempfile.mkdtemp(dir=self._tmp_dir)
        try:
            video = os.path.join(room, "source.mp4")
            with open(video, "wb") as handle:
                handle.write(data)
            return self._sound_for(room, video, prompt, negative or NEGATIVE, seed)
        finally:
            # Whatever happened, the room goes: a failed render must not leave a video on the disk.
            shutil.rmtree(room, ignore_errors=True)

    def _sound_for(self, room, video, prompt, negative, seed):
        pieces = chunks(self._ffmpeg.duration(video))
        sounds = []
        for index, (start, length) in enumerate(pieces):
            cut = os.path.join(room, f"cut{index}.mp4")
            # Even a video short enough to stay whole goes through the cut: that is where it gets
            # the frame rate and size the model reads, so there is one way in rather than two.
            self._ffmpeg.cut(video, start, length, cut)
            sound = os.path.join(room, f"sound{index}.wav")
            with open(sound, "wb") as handle:
                handle.write(self._sampler.render(cut, prompt, negative, seed, length))
            sounds.append(sound)
        if len(sounds) == 1:
            with open(sounds[0], "rb") as handle:
                return handle.read()
        joined = os.path.join(room, "joined.wav")
        self._ffmpeg.join(sounds, joined, FADE_MS)
        with open(joined, "rb") as handle:
            return handle.read()
