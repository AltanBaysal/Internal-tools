"""Twin the frames the user picked -- everything they hold, beside them.

Not a new idea: a copy frame is what a video variant past the first already is (copy_frame). What is
new is that the user asks for it, and that the twin takes EVERY layer rather than the ones under the
job about to run -- an exact twin has nothing left to produce.

So nothing is planned and nothing is queued. The twin's rows are the whole of it, and it reaches the
gallery the way any photo the plan does not know about does (list_frames). Its rows point at the
source's own files: one picture on disk, two frames holding it, and the last of them to be deleted
is what unlinks it (layers.files_to_unlink).

An identity the gallery does not know is skipped rather than refused, and so is a frame that has not
been produced yet: the first can be deleted in another tab while this selection sits open, and the
second owns no layer to twin. Refusing the whole press over either would leave the rest undone.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.copy_frame import (
    carry_all,
    known_ids,
    next_copy_id,
    placed,
)
from backend.features.photo_generation.domain.frame_list import checked
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


def copy_frames(record, store, plan_store, order_store, now, project, frames):
    checked(frames, "Kopyalanacak")
    # Raises ProjectMissing when there is no such project.
    gallery = list_frames(record, store, plan_store, order_store, project)
    by_id = {frame["id"]: frame for frame in gallery}

    # Every name the project has ever used, growing as the twins are born: two copies of one source
    # in a single press must not be handed the same name.
    ids = known_ids(record, plan_store, project)
    born, copies = {}, []
    for fid in frames:
        frame = by_id.get(fid)
        if frame is None or frame["status"] != queue.DONE:
            continue
        twin = next_copy_id(ids, fid)
        ids.add(twin)
        carry_all(record, project, twin, frame, now)
        born.setdefault(fid, []).append(twin)
        copies.append(twin)

    if copies:
        # Written once at the end rather than per twin: it is a single small document, and one write
        # is one chance to be interrupted instead of N.
        order_store.write(project, placed([frame["id"] for frame in gallery], born))
    return {"copies": copies}
