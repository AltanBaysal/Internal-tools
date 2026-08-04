"""How a photo file is named: "<number>_<letter>.png" -- number = prompt, letter = variant.

Both the store (which files are on disk) and the record (which files ever existed) have to read a
number out of a name, and two copies of that rule would be two chances to disagree.
"""


def file_name(number, letter):
    """The name a frame's photo is stored under."""
    return f"{number}_{letter}.png"


def number_of(filename):
    """"12_a.png" -> 12; anything that does not fit the scheme -> None."""
    if not filename.endswith(".png"):
        return None
    number, _, letter = filename[: -len(".png")].partition("_")
    if not number.isdigit() or len(letter) != 1 or not letter.isalpha():
        return None
    return int(number)
