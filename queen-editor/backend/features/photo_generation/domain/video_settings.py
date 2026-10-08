"""What a video job carries from its project: how long it runs (madde 422) and whether it ends
happily (madde 426).

Both are the project's choice at the moment the video is put in the queue, written on the job's plan
line and never read again when its turn comes ("Eklendiği uzunlukta"). Mutlu son is written only
while it is on, so a job put in with the switch off reads exactly as one queued before it existed.
"""
from backend.features.photo_generation.domain import layers, queue

SECONDS = "seconds"
# The plan line's field, read by the loop to hand the producer and the writer.
HAPPY_ENDING = "happyEnding"


def carried(length, ending, project):
    """What a video job put in the queue now carries. `length` answers the project's length and
    `ending` its switch; either None carries nothing of its own, and the job is made at its graph's
    own length, or as before."""
    said = {SECONDS: length(project)} if length else {}
    if ending and ending(project):
        said[HAPPY_ENDING] = True
    return said


def as_set_now(plan_store, project, fids, length, ending):
    """Put these frames' red videos back in the queue the way the project is set now.

    Tekrar dene puts a video in the queue again, and it goes at the length and with the switch of
    that moment ("Tekrar dene — bu kareye" -- "Evet"). Each frame's latest video line is written again
    with them and everything else as it was: the plan only grows, and the engine makes a frame's
    layer from its latest line (queue._latest_per_frame). A switch turned off takes the field off the
    line. A video already set that way is left alone, so then a retry re-plans nothing, as it always
    did. One append for all of them, because the plan file is written whole every time.
    """
    if not (length or ending) or not fids:
        return
    now = carried(length, ending, project)
    latest = {}
    for job in plan_store.read(project)["frames"]:
        if queue.type_of(job) == layers.VIDEO:
            latest[job["id"]] = job
    again = []
    for fid in fids:
        if fid not in latest:
            continue
        line = {key: value for key, value in latest[fid].items()
                if not (ending and key == HAPPY_ENDING)}
        line.update(now)
        if line != latest[fid]:
            again.append(line)
    if again:
        plan_store.append(project, again)
