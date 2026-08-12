"""The gallery: every frame that has a place in it, in the order it is shown, top first.

One answer, not two. The plan says what was asked for and the record says what became of it; putting
those together here is what lets the gallery be a single sequence instead of four buckets, and it is
why a frame turns into a photo without moving.

"running" is not among the statuses: a frame being rendered has no line on disk (a dead process must
not leave one behind), so the screen learns it from the live worker and draws the pending frame it
already has in place.

Only the photo slot decides whether a frame is here at all. Nothing deletes a photo on its own --
the photo is the base layer, so deleting it is deleting the frame -- while video and audio change
how a frame looks, never whether it exists.
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.gallery_order import apply_order
from backend.features.photo_generation.domain.photo_name import file_name, frame_id
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing

# What the gallery draws. A removed or deleted frame is gone from it entirely.
SHOWN = (queue.DONE, queue.FAILED)


def _taken_files(cells):
    """The files a frame really has right now -- an emptied slot names nothing."""
    return {slot: cell["file"] for slot, cell in cells.items()
            if layers.is_taken(cell["status"])}


def list_frames(record, store, plan_store, order_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    slots = record.slots(project)
    photos = {row["frame"]: row for row in record.list(project)}

    frames = []
    seen = set()
    # Newest first, the same direction the record answers in, so an unordered gallery already reads
    # the way the design wants it.
    for frame in reversed(plan_store.read(project)["frames"]):
        fid = frame_id(frame["number"], frame["letter"])
        cells = slots.get(fid, {})
        photo = cells.get(layers.PHOTO)
        status = photo["status"] if photo else None
        if status is not None and status not in SHOWN and not queue.is_open(status):
            continue                    # removed or deleted: it has no place in the gallery
        seen.add(fid)
        # The photo slot's own file once there is one: a copy frame's picture is its source's, not
        # the name its own number would give. A frame with nothing produced yet is drawn under the
        # name it is planned to take.
        frames.append({**frame, "id": fid,
                       "file": photo["file"] if photo
                       else file_name(frame["number"], frame["letter"]),
                       "layers": _taken_files(cells),
                       "status": status if status in SHOWN else "pending"})

    # Photos the plan no longer knows about: projects generated before the plan became permanent
    # kept only their last batch, and those photos are still the gallery's.
    for fid, row in photos.items():
        if fid not in seen:
            frames.append({**row, "id": fid, "layers": _taken_files(slots.get(fid, {})),
                           "status": queue.DONE})

    return apply_order(frames, order_store.read(project))
