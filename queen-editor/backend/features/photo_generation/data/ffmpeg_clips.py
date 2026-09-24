"""How long a clip runs, over ffprobe -- what the pool's limits are counted from (madde 298).

Asked of the bytes, because a reference is checked before it is written: a file the pool cannot
take must not be on the disk for a moment. ffprobe reads paths, so the bytes go into a room of this
class's own and the room goes whatever happens.

`run` is injected so tests can read the command instead of needing ffprobe on the machine; Colab has
ffmpeg installed, which is where this really runs.
"""
import os
import shutil
import subprocess
import tempfile


class FfmpegClips:
    def __init__(self, run=None, ffprobe="ffprobe", tmp_dir=None):
        self._run = run or subprocess.run
        self._ffprobe = ffprobe
        self._tmp_dir = tmp_dir

    def seconds(self, data):
        """How long these bytes run, as a number."""
        room = tempfile.mkdtemp(dir=self._tmp_dir)
        try:
            clip = os.path.join(room, "clip")
            with open(clip, "wb") as handle:
                handle.write(data)
            return self.seconds_at(clip)
        finally:
            shutil.rmtree(room, ignore_errors=True)

    def seconds_at(self, path):
        """How long the file at `path` runs -- what a reference already in the pool is asked.

        Nothing is read into memory: ffprobe takes the length off the header, and the pool sits on
        Drive where a video is the slow thing to move.
        """
        done = self._run(
            [self._ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True)
        text = (done.stdout or "").strip()
        if done.returncode != 0 or not text:
            # ffprobe's own last words, never a guessed cause. It can also answer 0 and say nothing
            # at all about a file it did not understand, which is a failure like any other.
            raise RuntimeError(_last_line(done.stderr, "ffprobe süreyi okuyamadı"))
        return float(text)


def _last_line(stderr, fallback):
    lines = (stderr or "").strip().splitlines()
    return lines[-1] if lines else fallback
