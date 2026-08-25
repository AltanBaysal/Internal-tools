"""The list of frame identities a request carries, and the one rule it has to keep.

Three calls take one: deleting frames, copying them, and taking a layer off them. The rule is the
same for all three and the sentence differs only in what was being asked for, so both live here --
a second copy would drift the moment one of them was reworded.
"""


class InvalidFrames(Exception):
    """The body was not a list of frame identities (the message is user-facing)."""


def checked(frames, what):
    """`frames` back when it is a list of identities; InvalidFrames naming the ask otherwise."""
    if not isinstance(frames, list) or any(not isinstance(fid, str) for fid in frames):
        raise InvalidFrames(f"{what} kare listesi metin dizisi olmalı.")
    return frames
