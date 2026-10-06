"""How long an H3 video runs (madde 422): the project's one choice, and what the queue does with it.

The user's words (v9-1, 5 Ekim): "videoları veya 4 8 12 arasında seçebilmek video uzunlupunu",
"varsalın 8 olsun", "h3e özel". Only H3's length is chosen -- a WAN video runs as long as its graph
says, and in a WAN session nothing here is handed a length at all (main.py).

A video carries the length it was put in the queue with, and comes out at it however the project
changes while it waits ("Eklendiği uzunlukta"): the length is written on the job's plan line, never
read again when its turn comes.
"""
from backend.features.photo_generation.domain import layers, queue

LENGTHS = (4, 8, 12)
DEFAULT = 8


class InvalidLength(Exception):
    """A length the project cannot be set to (message is user-facing)."""


def check(seconds):
    """Refuse anything but 4, 8 or 12 whole seconds. bool is an int in Python, and True would
    silently mean a one-second video."""
    if isinstance(seconds, bool) or not isinstance(seconds, int) or seconds not in LENGTHS:
        raise InvalidLength("Video uzunluğu 4, 8 ya da 12 saniye olmalı.")


def carried(length, project):
    """What a video job put in the queue now carries about its length: the project's length at this
    moment. `length` answers it; None -- a session whose video model takes no length -- carries
    nothing."""
    return {"seconds": length(project)} if length else {}


def at_length_now(plan_store, project, fids, length):
    """Put these frames' red videos back in the queue at the project's length now.

    Tekrar dene puts a video in the queue again, and it goes at the length of that moment
    ("Tekrar dene — bu kareye" -- "Evet"). Each frame's latest video line is written again with the
    new length and everything else as it was: the plan only grows, and the engine makes a frame's
    layer from its latest line (queue._latest_per_frame). A video already at that length is left
    alone, so then a retry re-plans nothing, as it always did. One append for all of them, because
    the plan file is written whole every time.
    """
    if not length or not fids:
        return
    seconds = length(project)
    latest = {}
    for job in plan_store.read(project)["frames"]:
        if queue.type_of(job) == layers.VIDEO:
            latest[job["id"]] = job
    again = [{**latest[fid], "seconds": seconds} for fid in fids
             if fid in latest and latest[fid].get("seconds") != seconds]
    if again:
        plan_store.append(project, again)
