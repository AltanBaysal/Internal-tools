"""Mutlu son (madde 426): the project's switch, and what it can be set to.

The user's words (8 Ekim): "mutlu son içinde bu modeli lora olarak ekleyip kapatalım videoda böyle
bir özellik olsun". Off until it is turned on, and kept with the project the way the length is
(madde 422). What a video job carries from it is video_settings' answer.
"""


class InvalidSwitch(Exception):
    """A value the switch cannot be set to (message is user-facing)."""


def check(on):
    """Refuse anything but True or False. 1 is not True here: a switch is on or off, and a number
    would be a guess at which."""
    if not isinstance(on, bool):
        raise InvalidSwitch("Mutlu son açık ya da kapalı olmalı.")
