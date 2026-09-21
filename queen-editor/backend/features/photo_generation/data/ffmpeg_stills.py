"""One picture out of a video, over ffmpeg -- the video's very first frame.

A card whose video landed without a picture gets one from the video itself (madde 296): the gallery
is quicker to walk through as stills, and export writes the photo slot rather than the video.

The bytes come from Drive and ffmpeg reads paths, so the file is written into a room of this class's
own and the room goes whatever happens -- a failed extraction must not leave a video on the disk.

`run` is injected so tests can read the command instead of needing ffmpeg on the machine; Colab has
ffmpeg installed, which is where this really runs.
"""
import os
import shutil
import subprocess
import tempfile


class FfmpegStills:
    def __init__(self, run=None, ffmpeg="ffmpeg", tmp_dir=None):
        self._run = run or subprocess.run
        self._ffmpeg = ffmpeg
        self._tmp_dir = tmp_dir

    def first_frame(self, video):
        """The video's opening frame as PNG bytes.

        No seek: what is wanted is where the video begins, and -ss would hand back some other frame.
        """
        room = tempfile.mkdtemp(dir=self._tmp_dir)
        try:
            source = os.path.join(room, "video.mp4")
            with open(source, "wb") as handle:
                handle.write(video)
            picture = os.path.join(room, "first.png")
            done = self._run([self._ffmpeg, "-y", "-i", source, "-frames:v", "1", picture],
                             capture_output=True, text=True)
            if done.returncode != 0:
                # ffmpeg's own last words, never a guessed cause.
                raise RuntimeError(_last_line(done.stderr, "ffmpeg ilk kareyi çıkaramadı"))
            with open(picture, "rb") as handle:
                return handle.read()
        finally:
            shutil.rmtree(room, ignore_errors=True)


def _last_line(stderr, fallback):
    lines = (stderr or "").strip().splitlines()
    return lines[-1] if lines else fallback
