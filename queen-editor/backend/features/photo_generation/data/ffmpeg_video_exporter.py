"""VideoExporter over ffmpeg -- the only place that knows how a video file is cut or joined.

Streams are copied, never re-encoded: the graph already produced the size, codec and frame rate the
export wants, so re-encoding would cost minutes and quality for nothing. The only stream that is
encoded is a sound being laid over a video, because a wav cannot ride in an mp4 as it is.

`run` is injected so tests can read the command instead of needing ffmpeg on the machine; Colab has
ffmpeg installed, which is where this really runs.
"""
import os
import subprocess


class FfmpegVideoExporter:
    def __init__(self, run=None, ffmpeg="ffmpeg"):
        self._run = run or subprocess.run
        self._ffmpeg = ffmpeg

    def piece(self, video, audio, target):
        """One frame's video at `target`, with its sound over it when there is one."""
        if audio:
            # -shortest: the sound is written for the video it was made from, but a frame off
            # either way must not stretch the piece.
            self._ffmpeg_run([
                "-i", video, "-i", audio, "-c:v", "copy", "-c:a", "aac", "-shortest", target])
        else:
            self._ffmpeg_run(["-i", video, "-c", "copy", target])

    def merge(self, pieces, target):
        """The pieces, in the order given, as one file."""
        # concat's list file lives beside the pieces: ffmpeg reads the paths relative to it, and
        # -safe 0 is what lets an absolute path through.
        folder = os.path.dirname(target)
        list_file = os.path.join(folder, "pieces.txt")
        with open(list_file, "w", encoding="utf-8") as handle:
            for piece in pieces:
                # Single quotes are concat's own escaping for a path with spaces in it.
                handle.write(f"file '{piece}'\n")
        try:
            self._ffmpeg_run(["-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", target])
        finally:
            # The list is scaffolding, not part of the export.
            os.remove(list_file)

    def _ffmpeg_run(self, args):
        done = self._run([self._ffmpeg, "-y", *args], capture_output=True, text=True)
        if done.returncode != 0:
            # ffmpeg's own last words, never a guessed cause. The tail is what carries the reason;
            # the rest is the banner it prints on every run.
            tail = (done.stderr or "").strip().splitlines()[-1:] or ["ffmpeg başarısız oldu"]
            raise RuntimeError(tail[0])
