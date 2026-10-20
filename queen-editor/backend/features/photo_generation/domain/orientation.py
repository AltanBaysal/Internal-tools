"""Which way a generation stands: landscape or portrait (madde 476).

Asked per generation, the way its negative is ("üretim başına negative prompt gibi 2 opsiyon"), and
written on the generation's plan line. Only the photo is made at it: a video follows the shape of
the photo it is made from, and is told nothing (comfy_h3_video_generator). A video made of the pool
has no photo to follow, so its card's line carries one too.

The values are the words the request and the plan carry. Which pixel sizes they mean is each
producer's to say, next to the graph it fills.
"""

LANDSCAPE = "yatay"
PORTRAIT = "dikey"
ALL = (LANDSCAPE, PORTRAIT)

# The plan line's field, read by the loop to hand the producer.
FIELD = "orientation"

# What a generation asked for without one is made in.
DEFAULT = LANDSCAPE


class InvalidOrientation(Exception):
    """An orientation nobody knows (message is user-facing)."""


def validate(value):
    """Refuse anything but the two words. Taken as the default instead, a typo would hand back a
    picture the other way round with nothing saying why."""
    if value not in ALL:
        raise InvalidOrientation(f"Yön şunlardan biri olmalı: {', '.join(ALL)}.")


def of(job):
    """The orientation a planned line carries, as the engine should read it.

    A line with none was planned before this madde, and every one of those was portrait -- so it
    reads as portrait, not as the default a new request gets, and a retried or resumed old frame
    renders exactly as it did. The doors refuse an unknown value, so nothing else reaches here.
    """
    value = job.get(FIELD)
    return value if value in ALL else PORTRAIT
