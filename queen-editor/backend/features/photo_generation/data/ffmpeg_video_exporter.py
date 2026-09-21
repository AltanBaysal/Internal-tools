"""VideoExporter over ffmpeg -- the only place that knows how a video file is cut or joined.

Streams are copied wherever they can be: the graph already produced the size, codec and frame rate
the export wants, so re-encoding would cost minutes and quality for nothing. Two things are encoded.
A sound being laid over a video, because a wav cannot ride in an mp4 as it is. And the merged
export, which stands on a landscape canvas of its own (madde 259) and carries the disclaimer over
its first minute (250) -- a frame moved onto another canvas with a picture over it is a new picture.
Cutting the pieces stays a copy (madde 261). Where the card can do that encoding, it does (253).

`run` is injected so tests can read the command instead of needing ffmpeg on the machine; Colab has
ffmpeg installed, which is where this really runs.
"""
import os
import subprocess

# The canvas a merged export stands on -- landscape and fixed, the user's call (madde 259): exports
# are taken landscape either way, and no resolution is offered (260 dropped, "1080 otomatik").
# Written down rather than taken from the pieces, which is the whole item: the pieces are 480x720,
# and a disclaimer squeezed into 480 could not be read.
MERGED_WIDTH = 1920
MERGED_HEIGHT = 1080

# How the disclaimer sits on the canvas, and for how long -- the user's call, 21 September. It spans
# the full width ("yatayda dolduracak şekilde"), so there is no width fraction left to name. The
# margin stays a fraction because the rule is a fraction: text stuck to the bottom edge sits under
# the player's bar on a phone.
DISCLAIMER_MARGIN = 0.04    # of the canvas height, up from the bottom edge
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
        # Ships with ffmpeg, and the notebook installs them together. One caller left: merge asks
        # every piece its size, and only to refuse a set that holds two of them -- the canvas is
        # written down, so nothing is measured from a piece any more (madde 259).
        self._ffprobe = ffprobe
        # The picture laid over the merged export. Injected like the tools above: config knows where
        # the repo keeps it, and tests hand over a path of their own.
        self._disclaimer = disclaimer
        # Which encoder this machine has, once it has been asked. Asked rather than assumed, and
        # asked once: see _encode below.
        self._encode = None

    def piece(self, video, audio, target):
        """One frame's video at `target`, with its sound over it when there is one.

        Nothing here is encoded. The disclaimer was laid on every piece for a while (madde 249) and
        came off again (261): at 480 wide it could not be read, and burning it cost the copy. It
        lives on the merged export instead, where the canvas is wide enough for it.
        """
        if audio:
            # The picture from the video and the sound from the layer, named: an H3 video carries a
            # sound of its own, and left to choose ffmpeg keeps whichever stream it likes best.
            # -shortest: the sound is written for the video it was made from, but a frame off
            # either way must not stretch the piece.
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

    def _stamp(self):
        """The filtergraph that puts the joined video on the canvas and stamps its first minute.

        Two steps, and they have to share one read: ffmpeg is given the join once, so fitting and
        stamping happen in the same filter_complex.

        `decrease` fits rather than fills -- the largest size that goes inside the canvas with the
        source's own aspect ratio kept -- and `pad` centres it, so a 480x720 frame becomes 720x1080
        with a bar either side. `increase` would fill the canvas by cutting the frame's top and
        bottom off, and a user's finished frame is not traded for a tidy edge (FOUNDATION 1). The
        user was shown the bars and took them (madde 259).

        Centring is left to ffmpeg -- `(W-w)/2`, `(ow-iw)/2` -- because the scaled picture's width
        is ffmpeg's number, not ours. `enable`'s single quotes are ffmpeg's own escaping: without
        them the comma in `lt(t,60)` would split the chain in two.

        Nothing here is measured from the pieces, which is what makes the canvas a decision rather
        than an inheritance. Only the join asks for it (madde 261), and `t` is the joined video's
        own clock (madde 250).
        """
        return (f"[0:v]scale={MERGED_WIDTH}:{MERGED_HEIGHT}:force_original_aspect_ratio=decrease,"
                f"pad={MERGED_WIDTH}:{MERGED_HEIGHT}:(ow-iw)/2:(oh-ih)/2[c];"
                f"[1:v]scale={MERGED_WIDTH}:-1[d];"
                f"[c][d]overlay=(W-w)/2:H-h-{round(MERGED_HEIGHT * DISCLAIMER_MARGIN)}:"
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
        """The pieces, in the order given, on the landscape canvas, with the disclaimer over its
        first minute.

        The size is asked of every piece first, and mixed sizes stop the join. The canvas is
        explicit now (madde 259), so the reason is no longer which shape was meant: concat reads the
        pieces as they are and rescales nothing, so two sizes cannot be read as one stream -- and
        what it cannot read it cannot hand to a filter either.

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
                "Videolar farklı ölçüde, birleştirilemez — " + found + ". Birleştirme parçaları "
                "olduğu gibi okuyor, ölçülerini değiştirmiyor: iki farklı ölçü tek bir akış olarak "
                "okunamaz. Eski oranla üretilmiş kareleri yeniden üret ya da dışa aktarmayı ayrı "
                "dosyalar olarak al."
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
            # The sound is mapped and copied: the pieces carry their own, already aac, and `?` is
            # for a set that has none.
            self._ffmpeg_run(["-f", "concat", "-safe", "0", "-i", list_file,
                              "-i", self._disclaimer, "-filter_complex",
                              self._stamp(), "-map", "[v]", "-map", "0:a?",
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
