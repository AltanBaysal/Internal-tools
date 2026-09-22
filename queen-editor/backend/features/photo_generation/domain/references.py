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


# What H3 takes, counted by the app rather than left to the model (madde 298): H3 complains in a
# Colab log the user never opens, and a refusal they cannot see is a refusal that does not exist.
LIMITS = {PICTURE: 9, VIDEO: 3, AUDIO: 3}
# What one clip may run, in seconds, and what a kind's clips may run together. A picture has no
# duration at all -- the count of pictures is the whole of its limit, and "the visual total" is the
# videos' total, which is the only reading of the rule that can be computed.
SHORTEST, LONGEST = 2, 15
TOGETHER = 15


class PoolLimit(Exception):
    """This file cannot go in the pool, and the sentence says why (message is user-facing)."""


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


# What each kind is called in a refusal. The pool's own words are H3's labels, which the user has
# never seen; what they see on the screen is this.
SAID = {PICTURE: "fotoğraf", VIDEO: "video", AUDIO: "ses"}


def placed(order, rows):
    """The pool with each reference's slot on it -- its place inside its own kind, counting from 1.

    `order` is {kind: [name, …]}, the sequence the user dragged. A name stays in that sequence after
    its file is gone, and that is the whole of how a gap exists: deleting a reference touches the
    folder and leaves the order alone, so the ones after it do not move (madde 300).

    They must not move, because H3 numbers references densely and by order -- a reference that slid
    up would quietly become the <Picture N> the prompt meant for another one.

    A file the order has never heard of waits at the end, among those by name: that is a fresh
    upload, and it is also what a pool with no stored order at all reads as.
    """
    out = []
    for kind in LIMITS:
        held = {row["name"]: row for row in rows if row["kind"] == kind}
        sequence = [name for name in order.get(kind, []) if isinstance(name, str)]
        unheard = sorted(name for name in held if name not in sequence)
        for slot, name in enumerate(sequence + unheard, start=1):
            if name in held:
                out.append({**held[name], "slot": slot})
    return out


def gaps(rows):
    """The kinds whose slots are not dense from 1 -- a hole somebody has to close.

    Nothing has to come after the last reference, so only a missing slot BEFORE a filled one is a
    gap. Production refuses while one is open (madde 302): H3 would pack the references tight and
    the prompt's own numbers would point at the wrong ones.
    """
    open_kinds = []
    for kind in LIMITS:
        slots = sorted(row["slot"] for row in rows if row["kind"] == kind)
        if slots and slots != list(range(1, len(slots) + 1)):
            open_kinds.append(kind)
    return open_kinds


def check(pool, incoming):
    """May these references join that pool? Raises PoolLimit with the sentence that says why.

    Both sides carry the same shape -- {"name", "kind", "seconds"} -- because the limits are about
    the two of them together: what is already in the pool counts, and a press is weighed whole
    rather than file by file.
    """
    for row in incoming:
        seconds = row["seconds"]
        if seconds is None:
            continue                    # a picture: held by the count, not by a clock
        if not SHORTEST <= seconds <= LONGEST:
            raise PoolLimit(f"{row['name']} {seconds:g} saniye — bir referans klibi "
                            f"{SHORTEST}-{LONGEST} saniye arası olmalı.")
    for kind, limit in LIMITS.items():
        held = [row for row in pool if row["kind"] == kind]
        arriving = [row for row in incoming if row["kind"] == kind]
        if not arriving:
            continue
        if len(held) + len(arriving) > limit:
            raise PoolLimit(f"{arriving[-1]['name']} havuza sığmıyor — en çok {limit} "
                            f"{SAID[kind]} referansı olabilir, şu an {len(held)} tane var.")
        total = sum(row["seconds"] or 0 for row in held + arriving)
        if total > TOGETHER:
            raise PoolLimit(f"{arriving[-1]['name']} havuza sığmıyor — {SAID[kind]} referansları "
                            f"toplam {TOGETHER} saniyeyi geçemez, bu {total:g} saniye eder.")
