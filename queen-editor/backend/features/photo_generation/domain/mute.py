"""A video's sound turned off (madde 510): which frames hold a sound, which count as silenced, and
what a press may say.

The user's words (29 Ekim): "bazen sesin kapatmak istiyoruz spesifik bir videonun export olurken
yapamıyoruz". The sound is MMAudio's layer; turned off, the video plays and exports with no sound
at all, and the layer itself stays in the project.

"Does this frame hold a sound" is answered here and nowhere else in the backend: by a gallery row
(`holds_sound`) for the export and its summary, and by the record's cell (`require_sound`) for a
press. A mark counts only while the frame holds a sound -- the frame page draws the icon on no other
video -- so a mark left on a frame whose sound has gone changes nothing anywhere.
"""
from backend.features.photo_generation.domain import layers


class InvalidMute(Exception):
    """A value a press cannot carry (message is user-facing)."""


class NoSound(Exception):
    """The frame asked to be silenced has no sound to turn off (message is user-facing)."""


def check(on):
    """Refuse anything but True or False: 1 is not True here, a sound is off or on."""
    if not isinstance(on, bool):
        raise InvalidMute("Ses kapalı ya da açık olmalı.")


def holds_sound(frame):
    """Does this gallery row carry a sound? One that blew up names a file but is not there."""
    return (bool(frame.get("layers", {}).get(layers.AUDIO))
            and layers.AUDIO not in frame.get("failed", []))


def silenced(frame, muted):
    """Is this gallery row's sound turned off? `muted` is the project's list of frame identities."""
    return holds_sound(frame) and frame["id"] in muted


def require_sound(slots, frame):
    """NoSound unless the frame's sound has landed. `slots` is the record's fold for the project:
    {frame: {slot: {"status", "file", ...}}} -- the same answer holds_sound reads from a row, asked
    of the record because a press has no gallery row in hand."""
    cell = slots.get(frame, {}).get(layers.AUDIO)
    if not cell or cell["status"] != layers.DONE:
        raise NoSound(f"Bu karenin sesi yok: {frame}")
