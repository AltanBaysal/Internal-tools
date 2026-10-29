"""A video's sound turned off (madde 510, 515): which frames may be silenced, and what a press may
say.

The user's words (29 Ekim): "bazen sesin kapatmak istiyoruz spesifik bir videonun export olurken
yapamıyoruz". Turned off, the video plays and exports with no sound at all -- H3's own and an old
MMAudio layer's, if it has one -- and the layer itself stays in the project.

Every video whose file has landed can be turned off (madde 515, "evet lütfen"): H3's video carries
a sound of its own, so whether a sound layer lies over it is not asked. That is answered here, from
the record's cell, for a press (`require_video`). The export needs no second copy of it: it takes
only the frames whose video has landed (`export_summary.exportable`), and among those a mark is
simply the frame's identity in the list.
"""
from backend.features.photo_generation.domain import layers


class InvalidMute(Exception):
    """A value a press cannot carry (message is user-facing)."""


class NoVideo(Exception):
    """The frame asked to be silenced has no video to turn off (message is user-facing)."""


def check(on):
    """Refuse anything but True or False: 1 is not True here, a sound is off or on."""
    if not isinstance(on, bool):
        raise InvalidMute("Ses kapalı ya da açık olmalı.")


def require_video(slots, frame):
    """NoVideo unless the frame's video has landed. `slots` is the record's fold for the project:
    {frame: {slot: {"status", "file", ...}}} -- asked of the record because a press has no gallery
    row in hand. A video that blew up or is back in line is not there to be heard."""
    cell = slots.get(frame, {}).get(layers.VIDEO)
    if not cell or cell["status"] != layers.DONE:
        raise NoVideo(f"Bu karenin videosu yok: {frame}")
