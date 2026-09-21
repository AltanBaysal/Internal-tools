"""What a reference is: a file in the project's pool, and the kind H3 will read it as.

The pool is a folder, and the folder is the truth (madde 297). There is no index beside it, so a
file the user drops in from Drive is in the pool and one they take away is gone -- a second document
saying which files exist could only ever disagree with the files.

The three words are H3's own labels -- <Picture N>, <Video N>, <Audio N> -- because feeding them is
what the pool is for. A card's layers are a different question and keep their own words
(domain/layers.py): a reference is not a layer, and one vocabulary over both would blur both.
"""
import os

PICTURE = "picture"
VIDEO = "video"
AUDIO = "audio"

# What the pool can read, by extension. A file whose extension is not here is not a reference: the
# pool would not know which row to put it in, nor which label to write for it in a prompt.
KNOWN = {
    ".png": PICTURE, ".jpg": PICTURE, ".jpeg": PICTURE, ".webp": PICTURE,
    ".mp4": VIDEO, ".mov": VIDEO, ".webm": VIDEO,
    ".wav": AUDIO, ".mp3": AUDIO, ".m4a": AUDIO, ".ogg": AUDIO,
}


def kind_of(name):
    """Which of the three this file is, or None when the pool cannot read it."""
    return KNOWN.get(os.path.splitext(name)[1].lower())


def free_name(name, taken):
    """The name this file is stored under: the user's own, kept inside the pool and never over one
    that is already there.

    The name arrives from a browser, so it is not a name until it has been through here: everything
    up to the last separator goes, both kinds, because the string was typed on somebody else's
    machine.

    A name already in the pool takes the next number instead of replacing it. What the user put in
    the pool is their own work, and a second file that happens to share a name is still a second
    file.
    """
    bare = name.replace("\\", "/").rsplit("/", 1)[-1].lstrip(".") or "referans"
    if bare not in taken:
        return bare
    stem, extension = os.path.splitext(bare)
    number = 2
    while f"{stem}-{number}{extension}" in taken:
        number += 1
    return f"{stem}-{number}{extension}"
