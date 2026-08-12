"""How a frame is identified, and how each of its layer files is named.

Identity and file name are not the same thing: the identity says which frame, the name says which
file. A picture can belong to two frames -- a copy frame shares its source's -- and one frame can
own three files.

The scheme says what a frame carries. A photo-only frame is P11_3; give it a video and the video
file is P11_3_V1_0.mp4; mix audio over that video and the audio file is P11_3_V1_0_S1_0.wav. Every
layer adds a pair -- round and variant -- and a layer that is not there is never written. The audio
name grows the video's rather than the frame's, because audio is mixed over one particular video.

Two schemes read, one writes. Frames born before this file said "P" are still on Drive under
<number>_<letter>, and nothing is renamed: renaming is a bulk write over work the user already
finished, and photo URLs are handed to browsers as permanent. So parsing accepts both schemes and
only new frames are named the new way.
"""


from backend.features.photo_generation.domain import layers

# The first video of a frame. A frame has at most one, and asking for a second makes a new frame
# (madde 25), so the pair stays constant until "yeniden üret" starts new rounds (madde 98).
FIRST_ROUND, FIRST_VARIANT = 1, 0


def frame_id(number, variant):
    """A frame's identity: P + the prompt number + its photo variant.

    Variants count from zero, which is the design's "a=0, b=1" rule with the letters taken out.
    """
    return f"P{number}_{variant}"


def legacy_frame_id(number, letter):
    """The identity frames born before the P scheme carry."""
    return f"{number}_{letter}"


def photo_file(frame):
    """The name a frame's photo is stored under."""
    return f"{frame}.png"


def video_file(frame, round_no, variant):
    """The name a frame's video is stored under -- the identity plus this layer's pair."""
    return f"{frame}_V{round_no}_{variant}.mp4"


def audio_file(video, round_no, variant):
    """The name an audio layer is stored under -- the VIDEO's name plus this layer's pair.

    `video` is the video file's name without its extension: audio is mixed over one video, and the
    name has to say which one.
    """
    return f"{video}_S{round_no}_{variant}.wav"


def layer_file(kind, frame, video=None):
    """The file name one produced layer takes.

    Photo and video are named from the frame's own identity; audio grows the VIDEO's name, because
    a sound is mixed over one particular video and the name has to say which one. A frame with no
    video cannot be given a sound at all, so that fallback is only there to keep a name a name.
    """
    if kind == layers.VIDEO:
        return video_file(frame, FIRST_ROUND, FIRST_VARIANT)
    if kind == layers.AUDIO:
        return audio_file(video.rsplit(".", 1)[0] if video else frame, FIRST_ROUND, FIRST_VARIANT)
    return photo_file(frame)


def frame_id_of(name):
    """A file or stored name -> the frame it belongs to; an identity comes back unchanged."""
    stem = name.rsplit(".", 1)[0] if "." in name else name
    # Layer pairs are suffixes on the identity, so the frame is whatever comes before the first one.
    for marker in ("_V", "_S"):
        cut = stem.find(marker)
        if cut != -1:
            stem = stem[:cut]
    return stem


def _parts(name):
    """The (number, variant) pair a name claims; (None, None) when it fits neither scheme.

    Both schemes are read in this one place: they are two spellings of the same pair, and a second
    copy of the parsing would let them drift apart.
    """
    stem = frame_id_of(name)
    if stem.startswith("P"):
        number, _, variant = stem[1:].partition("_")
        if number.isdigit() and variant.isdigit():
            return int(number), int(variant)
        return None, None
    number, _, letter = stem.partition("_")
    if number.isdigit() and len(letter) == 1 and letter.isalpha():
        return int(number), ord(letter) - ord("a")
    return None, None


def number_of(filename):
    """The prompt number a file's name claims; None when the name fits neither scheme.

    Both schemes claim numbers, because both name real files and a number may never be reused.
    """
    return _parts(filename)[0]


def variant_of(filename):
    """Which of its prompt's variants a file's name claims; None when it fits neither scheme."""
    return _parts(filename)[1]
