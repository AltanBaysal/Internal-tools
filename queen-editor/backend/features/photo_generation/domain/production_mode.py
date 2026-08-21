"""How a video job says where it ends.

Three identities and nothing else. What the user reads in Turkish is the frontend's business: a name
and its label pulled apart on purpose, so renaming one on screen never touches what is written in a
plan file that has to keep reading back for months.

Only a video has a mode. A photo is made from its words and a sound is laid over the whole of a
video -- neither arrives anywhere, so neither is asked.
"""
from backend.features.photo_generation.domain import layers, queue

STANDARD = "standard"
LOOP = "loop"
LINKED = "linked"

# What the queue validates against. A mode missing from here could never be asked for.
ALL = (STANDARD, LOOP, LINKED)


def of(job):
    """The mode a planned job carries, as the engine should read it.

    Anything the list does not know reads as the plain one, and so does a job with no mode at all:
    every video planned before this madde carries none, and each has to go on rendering exactly as
    it does today. The queue refuses an unknown mode at the door, so by the time a job is being
    rendered the plain reading is the only honest one left.
    """
    mode = job.get("mode")
    return mode if mode in ALL else STANDARD


class InvalidMode(Exception):
    """A production mode nobody knows, or one given to a layer that ends nowhere.

    Lives here rather than with either use case: two of them raise it, and the rule it stands for is
    about modes.
    """


def validate(mode, kind):
    """Refuse a mode this list does not know, or one asked of a layer that arrives nowhere.

    Both callers -- the queue and making a layer again -- want exactly these two answers, so they
    ask once rather than each keeping a copy that could drift.
    """
    if mode not in ALL:
        raise InvalidMode(f"Üretim modu şunlardan biri olmalı: {', '.join(ALL)}.")
    if mode != STANDARD and kind != layers.VIDEO:
        # Only a video ends on a picture. Ignoring the argument would hide the caller's mistake
        # behind a sound that came out fine.
        raise InvalidMode("Üretim modu yalnız video işine verilebilir.")


def frame_after(gallery, fid):
    """The frame a linked video ends on: the one that comes after it in the film.

    The film's sequence, not the gallery's reading order. The gallery is newest-first and the export
    stitches it reversed (export_summary.exportable) -- the foot of the gallery is the film's first
    frame -- so the frame that plays next is the one ABOVE, at index - 1. Linking downwards would
    make every chain run against the film it is part of.

    None where there is nothing to end on: the last frame of the film -- the top of the gallery --
    has no next, and a next whose photo never landed is the same emptiness seen from closer up.
    """
    for index, frame in enumerate(gallery):
        if frame["id"] != fid:
            continue
        after = gallery[index - 1] if index > 0 else None
        return after["id"] if after and after["status"] == queue.DONE else None
    return None
