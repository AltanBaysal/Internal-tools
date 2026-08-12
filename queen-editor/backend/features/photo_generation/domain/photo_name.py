"""How a frame is identified and how its photo file is named.

The two are not the same thing, and this is the file that keeps them apart. The identity says which
frame; the name says which file. A photo file can belong to more than one frame -- a copy frame
shares its source's picture -- and one frame can own three files, so a name can never stand in for
an identity.

The identity is given at birth and never rewritten: gallery order, the detail page's address and
the selection all point at it, and an identity that grew as layers arrived would break every one of
them the first time a video landed.
"""


def frame_id(number, letter):
    """The frame's identity: number = prompt, letter = variant."""
    return f"{number}_{letter}"


def frame_id_of(name):
    """"12_a.png" -> "12_a"; a name that already is an identity comes back unchanged."""
    return name[: -len(".png")] if name.endswith(".png") else name


def file_name(number, letter):
    """The name a frame's photo is stored under."""
    return f"{frame_id(number, letter)}.png"


def number_of(filename):
    """"12_a.png" -> 12; anything that does not fit the scheme -> None."""
    if not filename.endswith(".png"):
        return None
    number, _, letter = filename[: -len(".png")].partition("_")
    if not number.isdigit() or len(letter) != 1 or not letter.isalpha():
        return None
    return int(number)
