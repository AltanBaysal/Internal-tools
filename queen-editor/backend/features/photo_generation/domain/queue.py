"""What the queue still owes: the plan minus the frames that already settled.

One pure rule, so "is this frame still coming?" has a single answer that the worker, the queue
endpoint and the gallery all read the same way.

A frame's state lives in the photo record as one line per event, latest line wins. Two states are
deliberately absent from disk: a frame with no line at all is pending -- the plan already says it
was asked for, and repeating that as a flag would give one truth two writers -- and a running frame
belongs to the live worker, because a dead process must never leave "running" behind.
"""
from backend.features.photo_generation.domain.photo_name import file_name

DONE = "done"           # the photo landed and its file is on disk
FAILED = "failed"       # the render blew up; the tile stays red until Tekrar dene
REMOVED = "removed"     # a pending frame pulled out of the queue; never produced
DELETED = "deleted"     # a produced photo the user deleted
QUEUED = "queued"       # a settled frame put back in line

# QUEUED is the only written status that reopens a frame; the rest settle it for good.


def is_open(status):
    """True while the frame is still owed: never written about, or put back in line."""
    return status is None or status == QUEUED


def _name(frame):
    return file_name(frame["number"], frame["letter"])


def open_frames(frames, statuses):
    """The plan frames still owed: the untouched ones in plan order, then the ones put back in line.

    Tekrar dene must not jump the queue (design v2, G10). A frame the user sent back has already had
    its turn, so it waits behind everything that has not had one; among themselves the re-queued
    frames keep plan order, which is all the design asks for. Where a frame sits in the GALLERY does
    not change -- that is Madde 5's rule, and this is only the order it is rendered in.
    """
    fresh = [f for f in frames if statuses.get(_name(f)) is None]
    requeued = [f for f in frames if statuses.get(_name(f)) == QUEUED]
    return fresh + requeued


def next_frame(frames, statuses):
    """The frame the worker should render now, or None when nothing is owed."""
    owed = open_frames(frames, statuses)
    return owed[0] if owed else None


def counts(frames, statuses):
    """The numbers the status endpoint publishes -- read from disk rather than from a run's memory,
    so they are still right after the server restarts."""
    names = [_name(f) for f in frames]
    failures = [name for name in names if statuses.get(name) == FAILED]
    return {"total": len(frames),
            "done": sum(1 for name in names if statuses.get(name) == DONE),
            "failed": len(failures),
            "failures": failures}
