"""VideoExporter over ffmpeg -- the only place that knows how a video file is cut or joined.

Streams are copied wherever they can be: the graph already produced the size, codec and frame rate
the export wants, so re-encoding would cost minutes and quality for nothing. Two things are encoded.
A sound being laid over a video, because a wav cannot ride in an mp4 as it is. And the merged
export, which stands on a landscape canvas of its own (madde 259) and carries the disclaimer over
its first minute (250) -- a frame moved onto another canvas with a picture over it is a new picture.
Cutting the pieces stays a copy (madde 261); each piece is fitted onto the canvas inside the one
encode that joins them (478). Where the card can do that encoding, it does (253).

`run` is injected so tests can read the command instead of needing ffmpeg on the machine; Colab has
ffmpeg installed, which is where this really runs.
"""
import json
import subprocess

# The canvas a merged export stands on -- landscape and fixed, the user's call (madde 259): exports
# are taken landscape either way, and no resolution is offered (260 dropped, "1080 otomatik").
# Written down rather than taken from the pieces, which come in two shapes since madde 476: H3's
# landscape 1024x576, exactly 16:9, fills it; its portrait 576x864 stands in it with bars (478).
MERGED_WIDTH = 1920
MERGED_HEIGHT = 1080
# And the rate it runs at, set on the join's output (`-r`). concat joins pieces of different rates
# into a stream of no known rate, and an mp4 then falls back to 25 fps, doubling frames of a 24 fps
# video to fill it. 24 is H3's own, the Director's `frame_rate` in both graphs, so an H3 piece keeps
# every frame and anything else -- an old WAN video -- is brought to it. On the join, not on each
# piece: an `fps` filter at the end of a piece's chain drops that piece's last frame (madde 478,
# measured on ffmpeg 7.1).
MERGED_FPS = 24

# How the disclaimer sits on the canvas, and for how long -- the user's call, 21 September. It took
# the full width until they saw a real export, and then asked for room either side: sağdan soldan az
# boşluk ver, ekranın %80'i olsun (madde 291). Both are fractions because both rules are: the canvas
# can move, and the numbers move with it. The margin is a fraction for its own reason -- text stuck
# to the bottom edge sits under the player's bar on a phone.
DISCLAIMER_WIDTH = 0.8      # of the canvas width
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
# The merged export's sound comes out of a filter, which cannot be copied, so it is encoded: aac at
# the bitrate H3's own Combine writes (`audio_bitrate` in both graphs), so the join's sound is not
# thinner than the pieces' (madde 478).
SOUND_BITRATE = "192k"
_SOUND_ENCODE = ["-c:a", "aac", "-b:a", SOUND_BITRATE]


class FfmpegVideoExporter:
    def __init__(self, run=None, ffmpeg="ffmpeg", ffprobe="ffprobe", disclaimer=None):
        self._run = run or subprocess.run
        self._ffmpeg = ffmpeg
        # Ships with ffmpeg, and the notebook installs them together. One question left, asked once
        # of each piece: what sound it carries (madde 286) and how long its picture runs, where its
        # sound is cut (521). Its size is not asked -- the canvas is written down (259), and each
        # piece is fitted by its real size inside ffmpeg (478).
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

    def silent(self, video, target):
        """One frame's video at `target` with no sound at all: the picture copied, every sound
        stream left behind -- the video's own too, which an H3 video carries (madde 510)."""
        self._ffmpeg_run(["-i", video, "-c", "copy", "-an", target])

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

    def _filtergraph(self, count, cuts):
        """The filtergraph that puts each of `count` pieces on the canvas, joins them, and stamps
        the join's first minute. Inputs 0 to count-1 are the pieces, input `count` the disclaimer.
        `cuts` is where each piece's sound ends, in seconds -- None for a piece whose length is not
        known -- or None for a set with no sound.

        Each piece is fitted on its own, so pieces of two shapes join (madde 478): `decrease` fits
        rather than fills -- the largest size that goes inside the canvas with the piece's own
        aspect ratio kept -- and `pad` centres it. ffmpeg reads each piece's real size as it scales,
        so nothing of ours decides the shape: a 1024x576 piece, exactly 16:9, scales to the whole
        1920x1080 and the pad adds nothing; a 576x864 one becomes 720x1080 with 600 pixels of bar
        either side. `increase` would fill the canvas by cutting a portrait frame's top and bottom
        off, and a user's finished frame is not traded for a tidy edge (FOUNDATION 1). The user was
        shown the bars and took them (madde 259).

        concat wants every segment the same size and pixel shape, so `setsar=1` closes each piece's
        chain; the frame rate is set once, on the join's output (`MERGED_FPS`). It picks a common
        sample rate and channel layout for the sound by itself (ffmpeg's concat filter docs); it
        does need every piece to carry a sound stream, which `_evened_out` sees to.

        Each piece's sound is cut where its picture ends (madde 521). A piece's sound runs longer
        than its picture -- aac fills its last frame out to 1024 samples, and H3's sound or a
        layer's can run past the last frame -- and concat makes each segment as long as its longest
        stream, so every such piece would push the rest of the timeline later: the last frame held
        while the sound plays on, and the picture, which the join's 24 fps moves in whole frames,
        out of step with the sound by up to a frame. Cut, the sound is never the longer stream, so a
        segment lasts exactly as long as its picture and no join adds anything to the next. A sound
        shorter than its picture -- the silence `_with_sound` writes -- is padded by concat.

        Centring is left to ffmpeg -- `(W-w)/2`, `(ow-iw)/2` -- because the scaled picture's width
        is ffmpeg's number, not ours. `enable`'s single quotes are ffmpeg's own escaping: without
        them the comma in `lt(t,60)` would split the chain in two. `t` is the joined video's own
        clock, so the minute ends on the minute even when a piece straddles it (madde 250).
        """
        fit = (f"scale={MERGED_WIDTH}:{MERGED_HEIGHT}:force_original_aspect_ratio=decrease,"
               f"pad={MERGED_WIDTH}:{MERGED_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1")
        fitted = "".join(f"[{at}:v]{fit}[v{at}];" for at in range(count))
        if cuts is not None:
            # A piece whose length ffprobe did not give joins uncut, as before madde 521: a sound
            # running a little into the next piece is a smaller harm than no export at all.
            cut = "".join(f"[{at}:a]atrim=end={end}[a{at}];"
                          for at, end in enumerate(cuts) if end is not None)
            segments = "".join(f"[v{at}][{at}:a]" if end is None else f"[v{at}][a{at}]"
                               for at, end in enumerate(cuts))
            joined = f"{cut}{segments}concat=n={count}:v=1:a=1[c][a];"
        else:
            segments = "".join(f"[v{at}]" for at in range(count))
            joined = f"{segments}concat=n={count}:v=1:a=0[c];"
        return (f"{fitted}{joined}"
                f"[{count}:v]scale={round(MERGED_WIDTH * DISCLAIMER_WIDTH)}:-1[d];"
                f"[c][d]overlay=(W-w)/2:H-h-{round(MERGED_HEIGHT * DISCLAIMER_MARGIN)}:"
                f"enable='lt(t,{DISCLAIMER_SECONDS})'[v]")

    def streams(self, video):
        """How long the file's picture runs, in seconds, and what sound it carries as (sample rate,
        channel layout), or None for none at all -- the two things the join needs of a piece, from
        one reading of it (madde 286, 521).

        Its own words on failure: a missing file, something that is not a video and an ffprobe that
        is not installed all look the same from here, and only ffprobe knows which one happened.
        An answer that is not JSON is a failure too, named with the file and what ffprobe wrote.

        No audio stream is an answer, not a failure: a WAN video with no sound layer has none --
        the ones made before madde 435 stay in their projects -- and ffprobe lists none. A value
        ffprobe leaves out of the sound's shape comes back empty.

        No picture length is an answer too: the length comes back None, and that piece's sound joins
        uncut, as every piece's did before madde 521. Every piece is an mp4 our own copy wrote,
        whose picture has one; but a sound running a little long is a smaller harm than losing the
        export (FOUNDATION 1), and a length guessed would cut it in the wrong place. It is read as a
        number, so it reaches the filtergraph as one and never as whatever text the header held.

        JSON, written with no options: ffprobe splits a writer's option string on colons, so asking
        csv to separate with one left `s=` without a value, and the refused string took the merged
        export down before a piece was joined (madde 288). And it names each field, so neither the
        order ffprobe prints them in nor which stream comes first is relied on.
        """
        done = self._run(
            [self._ffprobe, "-v", "error",
             "-show_entries", "stream=codec_type,duration,sample_rate,channel_layout",
             "-of", "json", video],
            capture_output=True, text=True)
        if done.returncode != 0:
            tail = (done.stderr or "").strip().splitlines()[-1:] or ["ffprobe başarısız oldu"]
            raise RuntimeError(tail[0])
        said = (done.stdout or "").strip()
        try:
            listed = json.loads(said or "{}").get("streams", [])
        except (ValueError, AttributeError):
            raise RuntimeError(f"{video}: ffprobe JSON yerine şunu yazdı: {said[:200]}") from None
        picture = next((s for s in listed if s.get("codec_type") == "video"), {})
        heard = next((s for s in listed if s.get("codec_type") == "audio"), None)
        try:
            seconds = float(picture["duration"])
        except (KeyError, ValueError):
            seconds = None
        if heard is None:
            return seconds, None
        return seconds, (heard.get("sample_rate", ""), heard.get("channel_layout", ""))

    def _with_sound(self, piece, rate, layout):
        """The piece again, beside itself, with a silent track of the given shape.

        Only a stream is added: `-c:v copy` means not one frame is re-encoded. `-shortest` is what
        stops anullsrc, which runs forever.

        The shape comes from a piece that has sound rather than from a guess (madde 286): concat
        would convert a shape that differs, but one copied from the set leaves it nothing to do.
        Only the values ffprobe gave are named: `r=` with nothing after it is refused by ffmpeg,
        while a value left out takes anullsrc's own default, which concat converts like any other.
        """
        head, _dot, _tail = piece.rpartition(".")
        target = f"{head or piece}-sound.mp4"
        shape = ":".join(f"{key}={value}" for key, value in (("r", rate), ("cl", layout)) if value)
        silence = f"anullsrc={shape}" if shape else "anullsrc"
        self._ffmpeg_run(["-i", piece, "-f", "lavfi", "-i", silence,
                          "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
                          "-shortest", target])
        return target

    def _evened_out(self, pieces):
        """The pieces to join, with silence written into the ones that carry no sound, and where
        each one's sound is cut -- its picture's length -- or None when the set has no sound at all.

        concat joins one sound segment for every picture segment, so a project whose frames are
        only partly sounded would name a sound stream that one of its pieces does not have.

        One rule: if any piece has sound, all of them must. Both even sets therefore cost nothing --
        all sounded needs no silence, and none sounded has no shape to copy and needs none
        (FOUNDATION 3). The user's call, in their own words: sesi olmayan karelere sessiz eklenir.

        A silenced piece is cut at the length asked of the piece it was written from: its picture
        is that one, copied.
        """
        asked = [self.streams(piece) for piece in pieces]
        carried = next((sound for _seconds, sound in asked if sound), None)
        if carried is None:
            return list(pieces), None
        rate, layout = carried
        return ([piece if sound else self._with_sound(piece, rate, layout)
                 for piece, (_seconds, sound) in zip(pieces, asked)],
                [seconds for seconds, _sound in asked])

    def merge(self, pieces, target):
        """The pieces, in the order given, on the landscape canvas, with the disclaimer over its
        first minute -- in one ffmpeg call, which is one encode of the whole timeline.

        A project holds landscape and portrait videos side by side (madde 476), and the concat
        demuxer reads the files as one stream and cannot take two sizes, so each piece goes in as an
        input of its own, is fitted onto the canvas, and the concat filter joins the fitted pieces
        (`_filtergraph`, 478). The pieces stay copies and the fitting happens inside this one
        encode: fitting them at the cut would encode every frame twice, once there and once here
        for the disclaimer.

        What it costs: every input is opened when the call starts and stays open until it ends, so
        memory grows O(N) with the pieces, a decoder each; how much a piece takes is measured in the
        Colab trial. `-threads 1` caps each decoder at one thread and its frames: concat reads one
        segment at a time, so only one decoder works at once and the cap costs no speed.

        Every piece is asked its picture's length and its sound, once each, and a missing sound is
        answered rather than refused: a partly sounded set gets silence written into the pieces that
        have none (madde 286). Each sound is then cut at its picture's length (madde 521).

        A piece ffmpeg cannot read, or a set it cannot join, stops the call with ffmpeg's own words.
        """
        joined, cuts = self._evened_out(pieces)
        inputs = [part for piece in joined for part in ("-threads", "1", "-i", piece)]
        sound = ["-map", "[a]", *_SOUND_ENCODE] if cuts is not None else []
        self._ffmpeg_run([*inputs, "-i", self._disclaimer,
                          "-filter_complex", self._filtergraph(len(joined), cuts),
                          "-map", "[v]", "-r", str(MERGED_FPS), *self._encoder(), *sound, target])

    def _ffmpeg_run(self, args):
        done = self._run([self._ffmpeg, "-y", *args], capture_output=True, text=True)
        if done.returncode != 0:
            # ffmpeg's own last words, never a guessed cause. The tail is what carries the reason;
            # the rest is the banner it prints on every run.
            tail = (done.stderr or "").strip().splitlines()[-1:] or ["ffmpeg başarısız oldu"]
            raise RuntimeError(tail[0])
