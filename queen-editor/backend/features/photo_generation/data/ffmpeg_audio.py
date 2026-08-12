"""The video work a sound job needs, over ffmpeg -- cutting the input the model reads and joining
the sounds that come back.

Two things are re-encoded here on purpose, unlike the export next door which only ever copies:
  * the piece handed to MMAudio (25 fps, 720p, no sound), because Synchformer reads 25 fps and a
    frame-accurate cut needs a real encode;
  * the joined sound, because a crossfade is a filter and filters cannot copy.

`run` is injected so tests can read the command instead of needing ffmpeg on the machine; Colab has
ffmpeg installed, which is where this really runs.
"""
import shutil
import subprocess

# -vsync cfr works on every ffmpeg version (deprecated since 5, still functional). A constant frame
# rate is what makes the model's frame count agree with the duration it was told.
_CFR = ["-vsync", "cfr"]


class FfmpegAudio:
    def __init__(self, run=None, ffmpeg="ffmpeg", ffprobe="ffprobe", copy=None):
        self._run = run or subprocess.run
        self._ffmpeg = ffmpeg
        self._ffprobe = ffprobe
        self._copy = copy or shutil.copyfile

    def duration(self, video):
        """How long the video runs, in seconds -- what decides whether it is cut up at all."""
        done = self._run(
            [self._ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", video],
            capture_output=True, text=True)
        if done.returncode != 0 or not (done.stdout or "").strip():
            raise RuntimeError(_last_line(done.stderr, "ffprobe süreyi okuyamadı"))
        return float(done.stdout.strip())

    def cut(self, video, start, duration, target):
        """The slice from `start`, as the model wants to read it: 25 fps, 720p, silent.

        A whole short video comes through the same call (start 0, its full length) -- one path
        rather than two, so the model never sees a piece prepared a second way.
        """
        self._ffmpeg_run([
            "-ss", str(start), "-i", video, "-t", str(duration),
            "-vf", "fps=25,scale=-2:720", *_CFR,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23", "-an", target])

    def join(self, parts, target, fade_ms):
        """The sounds, in order, as one file with a short fade at every seam.

        The fade hides the click a hard cut leaves; it also shortens the result by fade_ms per seam,
        which is under a tenth of a second and nobody hears it.
        """
        if len(parts) == 1:
            # acrossfade needs two inputs, and a single piece has nothing to fade into.
            self._copy(parts[0], target)
            return
        inputs = []
        for part in parts:
            inputs += ["-i", part]
        fade = fade_ms / 1000.0
        # A chain, not one filter: [0][1] -> a1, [a1][2] -> a2, and the last one is what is mapped.
        chain = []
        previous = "0:a"
        for index in range(1, len(parts)):
            label = "outa" if index == len(parts) - 1 else f"a{index}"
            chain.append(f"[{previous}][{index}:a]acrossfade=d={fade}:c1=tri:c2=tri[{label}]")
            previous = label
        self._ffmpeg_run([*inputs, "-filter_complex", ";".join(chain), "-map", "[outa]", target])

    def _ffmpeg_run(self, args):
        done = self._run([self._ffmpeg, "-y", *args], capture_output=True, text=True)
        if done.returncode != 0:
            # ffmpeg's own last words, never a guessed cause.
            raise RuntimeError(_last_line(done.stderr, "ffmpeg başarısız oldu"))


def _last_line(stderr, fallback):
    lines = (stderr or "").strip().splitlines()
    return lines[-1] if lines else fallback
