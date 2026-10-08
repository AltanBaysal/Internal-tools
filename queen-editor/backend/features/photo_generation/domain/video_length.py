"""How long an H3 video runs (madde 422): the project's choice, and what it can be set to.

The user's words (v9-1, 5 Ekim): "videoları veya 4 8 12 arasında seçebilmek video uzunlupunu",
"varsalın 8 olsun", "h3e özel". H3 is the one video model since madde 435, so every video job is
handed the project's length (main.py).

A video carries the length it was put in the queue with, and comes out at it however the project
changes while it waits ("Eklendiği uzunlukta"): video_settings writes it on the job's plan line, and
it is never read again when its turn comes.
"""
LENGTHS = (4, 8, 12)
DEFAULT = 8


class InvalidLength(Exception):
    """A length the project cannot be set to (message is user-facing)."""


def check(seconds):
    """Refuse anything but 4, 8 or 12 whole seconds. bool is an int in Python, and True would
    silently mean a one-second video."""
    if isinstance(seconds, bool) or not isinstance(seconds, int) or seconds not in LENGTHS:
        raise InvalidLength("Video uzunluğu 4, 8 ya da 12 saniye olmalı.")
