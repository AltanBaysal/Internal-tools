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
    def __init__(self, run=None, ffmpeg="ffmpeg", ffprobe="ffprobe"):
        self._run = run or subprocess.run
        self._ffmpeg = ffmpeg
        # Ships with ffmpeg, and the notebook installs them together. Only merge uses it.
        self._ffprobe = ffprobe

    def piece(self, video, audio, target):
        """One frame's video at `target`, with its sound over it when there is one."""
        if audio:
            # -shortest: the sound is written for the video it was made from, but a frame off
            # either way must not stretch the piece.
            self._ffmpeg_run([
                "-i", video, "-i", audio, "-c:v", "copy", "-c:a", "aac", "-shortest", target])
        else:
            self._ffmpeg_run(["-i", video, "-c", "copy", target])

    def size(self, video):
        """The picture's size as ffprobe writes it -- "848x480".

        Its own words on failure: a missing file, something that is not a video and an ffprobe that
        is not installed all look the same from here, and only ffprobe knows which one happened.
        """
        done = self._run(
            [self._ffprobe, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", video],
            capture_output=True, text=True)
        if done.returncode != 0:
            tail = (done.stderr or "").strip().splitlines()[-1:] or ["ffprobe başarısız oldu"]
            raise RuntimeError(tail[0])
        return (done.stdout or "").strip()

    def merge(self, pieces, target):
        """The pieces, in the order given, as one file.

        Asked of every piece first, because the join below copies streams instead of re-encoding
        them: that is only sound while they are all the same size, and since madde 218 one project
        can hold both shapes. Re-encoding to one size would be the wrong fix -- nobody can say
        which shape was meant, and the answer would be a crop or a bar the user never asked for.
        """
        sizes = [(piece, self.size(piece)) for piece in pieces]
        if len({size for _piece, size in sizes}) > 1:
            # Piece by piece: "the pieces are different sizes" does not say which frame to redo.
            found = ", ".join(f"{os.path.basename(piece)} {size}" for piece, size in sizes)
            raise RuntimeError(
                "Videolar farklı ölçüde, birleştirilemez — " + found + ". Birleştirme yeniden "
                "kodlamıyor, o yüzden çıkacak dosya bozuk olurdu. Aynı projede iki oran var: "
                "eski oranla üretilmiş kareleri yeniden üret ya da dışa aktarmayı ayrı dosyalar "
                "olarak al."
            )
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
