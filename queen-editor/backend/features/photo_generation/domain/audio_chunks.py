"""How a video is cut up before a sound is made for it.

MMAudio was trained on 8-second clips, and drifting far from that costs quality -- so a long video
is not handed over whole, it is split into pieces near the length the model knows and the sounds are
joined back together afterwards.

This version's frames are about 5 seconds, so nothing here fires today. It is kept because the
length is the graph's setting rather than ours: a longer export tomorrow would quietly degrade every
sound, and nobody would remember that the rule had been dropped.

The numbers are collab-toolbox's mmaudio notebook's own (MAX_CHUNK_DURATION, TARGET_CHUNK_DURATION).
"""
import math

TARGET = 8.0     # what the model was trained on
MAXIMUM = 10.0   # longer than this and the video is split


def chunks(total, target=TARGET, maximum=MAXIMUM):
    """[(start, duration), ...] covering the whole video, in order and without gaps.

    A video at or under the limit stays whole. Past it, the piece count is whichever is larger: the
    fewest pieces that respect the limit, or the count that lands nearest the target -- so 20s
    becomes three pieces rather than two, because two would sit 2 seconds off what the model knows.
    """
    if total <= maximum:
        return [(0, total)]
    # int(x + 0.5), not round(x): Python rounds halves to even, so 20s over an 8s target would
    # answer 2 and hand the model two 10-second pieces -- the notebook rounds half up for the same
    # reason.
    count = max(math.ceil(total / maximum), int(total / target + 0.5), 1)
    size = total / count
    # The last piece takes whatever rounding left over, so the pieces always add up to the video.
    return [(index * size, min(size, total - index * size)) for index in range(count)]
