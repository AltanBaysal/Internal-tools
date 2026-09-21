"""VideoExporter over ffmpeg -- the only place that knows how a video file is cut or joined.

Streams are copied wherever they can be: the graph already produced the size, codec and frame rate
the export wants, so re-encoding would cost minutes and quality for nothing. Two things are encoded.
A sound being laid over a video, because a wav cannot ride in an mp4 as it is. And a piece carrying
the disclaimer (madde 249) -- an overlay is a new picture, so the picture is encoded rather than
copied, and that is what the disclaimer costs. Where the card can do that encoding, it does
(madde 253).

`run` is injected so tests can read the command instead of needing ffmpeg on the machine; Colab has
ffmpeg installed, which is where this really runs.
"""
import os
import subprocess

# How the disclaimer sits on the video, and for how long -- the user's call, 21 September. Fractions
# of the frame rather than pixels: the frame's shape changed once already (madde 218 made it
# landscape, 228 brought it back), and a pixel would have gone on being right about the old one.
DISCLAIMER_WIDTH = 0.8      # of the video's width
DISCLAIMER_MARGIN = 0.04    # of the video's height, up from the bottom edge
DISCLAIMER_SECONDS = 60     # from the start of the video

# What encoded work is encoded with. The GPU is the answer where there is one: an export leaves the
# T4 idle while two Colab vCPUs do the work, and the user measured a merge past five minutes
# (madde 253). NVENC uses its own block on the card, so it does not fight ComfyUI for CUDA.
#
# nvenc takes -rc/-cq where x264 takes -crf, and "fast" rather than the p1-p7 levels: Colab's ffmpeg
# may be old enough not to know them. On the CPU side, veryfast keeps the wait shortest and crf 18
# is close enough to lossless by eye. yuv420p in both, which is what makes the file open everywhere.
_GPU = "h264_nvenc"
_GPU_ENCODE = ["-c:v", _GPU, "-preset", "fast", "-rc", "vbr", "-cq", "23", "-pix_fmt", "yuv420p"]
_CPU_ENCODE = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]


class FfmpegVideoExporter:
    def __init__(self, run=None, ffmpeg="ffmpeg", ffprobe="ffprobe", disclaimer=None):
        self._run = run or subprocess.run
        self._ffmpeg = ffmpeg
        # Ships with ffmpeg, and the notebook installs them together. merge uses it, and so does a
        # stamped piece -- the overlay is measured from the video's own size.
        self._ffprobe = ffprobe
        # The picture laid over a stamped piece. Injected like the tools above: config knows where
        # the repo keeps it, and tests hand over a path of their own.
        self._disclaimer = disclaimer
        # Which encoder this machine has, once it has been asked. Asked rather than assumed, and
        # asked once: see _encode below.
        self._encode = None

    def piece(self, video, audio, target, disclaimer=False):
        """One frame's video at `target`, with its sound over it when there is one.

        `disclaimer` is a separate export's business: its pieces ARE the export. A merged export's
        pieces are scaffolding, and the disclaimer there belongs to the joined video's clock.
        """
        # The picture from the video and the sound from the layer, named: an H3 video carries a
        # sound of its own, and left to choose ffmpeg keeps whichever stream it likes best.
        # -shortest: the sound is written for the video it was made from, but a frame off either
        # way must not stretch the piece.
        if disclaimer:
            sound = ["-i", audio] if audio else []
            mapping = ["-map", "[v]"] + (["-map", "2:a:0"] if audio else [])
            encode = self._encoder() + (["-c:a", "aac", "-shortest"] if audio else [])
            # The disclaimer is the second input and the sound the third, whether or not there is a
            # sound: putting the picture last would tie the filter's input number to the sound.
            self._ffmpeg_run(["-i", video, "-i", self._disclaimer, *sound,
                              "-filter_complex", self._stamp(video), *mapping, *encode, target])
        elif audio:
            self._ffmpeg_run([
                "-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-shortest", target])
        else:
            self._ffmpeg_run(["-i", video, "-c", "copy", target])

    def _encoder(self):
        """The encoder arguments for this machine, settled once by trying the card out.

        Tried rather than looked up: `ffmpeg -encoders` answers for the build, not for the machine,
        so a box with no card, a mismatched driver or a card whose encoder sessions are all taken
        lists h264_nvenc and then fails in the middle of an export (madde 257). The trial is a made
        up picture, a tenth of a second of it, written nowhere.

        A trial that does not come back is an answer, not an error: the export runs on the CPU,
        which is where it stood before madde 253. Losing a whole export to a guess is worse than a
        slow export (FOUNDATION 1).

        Once, because the answer cannot change while the process lives, and a separate export
        writes one piece per frame.
        """
        if self._encode is None:
            done = self._run([self._ffmpeg, "-hide_banner", "-f", "lavfi", "-i", "nullsrc",
                              "-t", "0.1", "-c:v", _GPU, "-f", "null", "-"],
                             capture_output=True, text=True)
            self._encode = _GPU_ENCODE if done.returncode == 0 else _CPU_ENCODE
        return self._encode

    def _stamp(self, video):
        """The filtergraph for a video whose size nobody has asked for yet."""
        width, height = (int(part) for part in self.size(video).split("x"))
        return self._stamp_for(width, height)

    def _stamp_for(self, width, height):
        """The filtergraph that lays the disclaimer on the first minute of what it is given.

        Centring is left to ffmpeg -- `(W-w)/2` -- because the scaled picture's width is ffmpeg's
        number, not ours. `enable`'s single quotes are ffmpeg's own escaping: without them the comma
        in `lt(t,60)` would split the chain in two.

        A piece and a join both want this, and they differ only in whose clock `t` is: a piece's own
        for a separate export, the joined video's for a merged one (madde 250).
        """
        return (f"[1:v]scale={round(width * DISCLAIMER_WIDTH)}:-1[d];"
                f"[0:v][d]overlay=(W-w)/2:H-h-{round(height * DISCLAIMER_MARGIN)}:"
                f"enable='lt(t,{DISCLAIMER_SECONDS})'[v]")

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
        """The pieces, in the order given, as one file, with the disclaimer over its first minute.

        The size is asked of every piece first. Mixed sizes still stop the join, although the
        picture is now encoded rather than copied: which of the two shapes was meant is a question
        nobody can answer, and answering it would mean a crop or a bar the user never asked for
        (madde 218's call).

        The disclaimer rides on the join rather than on the pieces, so `t` is the joined video's own
        clock and the minute ends on the minute even when a frame straddles it (madde 250). It also
        keeps every piece a plain copy -- an encoded piece next to a copied one is what concat
        cannot swallow.
        """
        sizes = [(piece, self.size(piece)) for piece in pieces]
        if len({size for _piece, size in sizes}) > 1:
            # Piece by piece: "the pieces are different sizes" does not say which frame to redo.
            found = ", ".join(f"{os.path.basename(piece)} {size}" for piece, size in sizes)
            raise RuntimeError(
                "Videolar farklı ölçüde, birleştirilemez — " + found + ". Aynı projede iki oran "
                "var, ve tek dosyanın tek oranı olur: hangisinin istendiğini kimse söyleyemez, "
                "ikisini birden sığdırmak da kırpmak ya da bant koymak olurdu. Eski oranla "
                "üretilmiş kareleri yeniden üret ya da dışa aktarmayı ayrı dosyalar olarak al."
            )
        # concat's list file lives beside the pieces: ffmpeg reads the paths relative to it, and
        # -safe 0 is what lets an absolute path through.
        folder = os.path.dirname(target)
        list_file = os.path.join(folder, "pieces.txt")
        with open(list_file, "w", encoding="utf-8") as handle:
            for piece in pieces:
                # Single quotes are concat's own escaping for a path with spaces in it.
                handle.write(f"file '{piece}'\n")
        width, height = (int(part) for part in sizes[0][1].split("x"))
        try:
            # The sound is mapped and copied: the pieces carry their own, already aac, and `?` is
            # for a set that has none.
            self._ffmpeg_run(["-f", "concat", "-safe", "0", "-i", list_file,
                              "-i", self._disclaimer, "-filter_complex",
                              self._stamp_for(width, height), "-map", "[v]", "-map", "0:a?",
                              *self._encoder(), "-c:a", "copy", target])
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
