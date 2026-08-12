"""What the queue still owes: the plan minus the jobs that already settled, type by type.

One pure rule, so "is this job still coming?" has a single answer that the worker, the queue
endpoint and the gallery all read the same way.

A job's state lives in the photo record as one line per event, latest line wins, folded per
(frame, layer). Two states are deliberately absent from disk: a job with no line at all is pending
-- the plan already says it was asked for, and repeating that as a flag would give one truth two
writers -- and a running job belongs to the live worker, because a dead process must never leave
"running" behind.

The engine finishes one type before it starts the next: photos, then videos, then audio. That is
the design's rule (madde 36) and it pays for itself twice -- each type loads its own producer, so
hopping between them would reload a model every turn, and a video needs the photo it hangs on to
exist first.
"""
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.photo_name import photo_file

# The words a line can carry. They are defined with the layers they describe; re-exported here
# because "what the queue owes" is read in terms of them everywhere else.
DONE = layers.DONE
FAILED = layers.FAILED
REMOVED = layers.REMOVED
DELETED = layers.DELETED
QUEUED = layers.QUEUED

# QUEUED is the only written status that reopens a job; the rest settle it for good.

# The order the engine works in.
ORDER = (layers.PHOTO, layers.VIDEO, layers.AUDIO)


def is_open(status):
    """True while the job is still owed: never written about, or put back in line."""
    return status is None or status == QUEUED


def type_of(job):
    """A job planned before the queue knew types can only be a photo job."""
    kind = job.get("type")
    return kind if isinstance(kind, str) else layers.PHOTO


def _status(slots, job):
    cell = slots.get(job["id"], {}).get(type_of(job))
    return cell["status"] if cell else None


def open_jobs(jobs, slots):
    """The jobs still owed, in the order the engine will do them.

    Type first, then the plan's own order. Inside a type, a job the user sent back with Tekrar dene
    waits behind everything that has never had a turn (design v2, G10); among themselves the
    re-queued ones keep plan order. Where a frame sits in the GALLERY does not change -- that is
    Madde 5's rule, and this is only the order work is done in.
    """
    owed = []
    for kind in ORDER:
        same = [j for j in jobs if type_of(j) == kind]
        fresh = [j for j in same if _status(slots, j) is None]
        requeued = [j for j in same if _status(slots, j) == QUEUED]
        owed += fresh + requeued
    return owed


def next_job(jobs, slots):
    """The job the worker should do now, or None when nothing is owed."""
    owed = open_jobs(jobs, slots)
    return owed[0] if owed else None


def counts(jobs, slots):
    """The numbers the status endpoint publishes -- read from disk rather than from a run's memory,
    so they are still right after the server restarts.

    Looked up by identity, published as file names: the screen marks its red tiles by file.
    """
    failures = [photo_file(j["id"]) for j in jobs if _status(slots, j) == FAILED]
    return {"total": len(jobs),
            "done": sum(1 for j in jobs if _status(slots, j) == DONE),
            "failed": len(failures),
            "failures": failures}
