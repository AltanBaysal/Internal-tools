"""The gallery: every frame that has a place in it, in the order it is shown, top first.

One answer, not two. The plan says what was asked for and the record says what became of it; putting
those together here is what lets the gallery be a single sequence instead of four buckets, and it is
why a frame turns into a photo without moving.

"running" is not among the statuses: a frame being rendered has no line on disk (a dead process must
not leave one behind), so the screen learns it from the live worker and draws the pending frame it
already has in place.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.gallery_order import apply_order
from backend.features.photo_generation.domain.photo_name import file_name
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing

# What the gallery draws. A removed or deleted frame is gone from it entirely.
SHOWN = (queue.DONE, queue.FAILED)


def list_frames(record, store, plan_store, order_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    statuses = record.statuses(project)
    photos = {row["file"]: row for row in record.list(project)}

    frames = []
    seen = set()
    # Newest first, the same direction the record answers in, so an unordered gallery already reads
    # the way the design wants it.
    for frame in reversed(plan_store.read(project)["frames"]):
        file = file_name(frame["number"], frame["letter"])
        status = statuses.get(file)
        if status is not None and status not in SHOWN and not queue.is_open(status):
            continue                    # removed or deleted: it has no place in the gallery
        seen.add(file)
        frames.append({**frame, "file": file,
                       "status": status if status in SHOWN else "pending"})

    # Photos the plan no longer knows about: projects generated before the plan became permanent
    # kept only their last batch, and those photos are still the gallery's.
    for file, row in photos.items():
        if file not in seen:
            frames.append({**row, "status": queue.DONE})

    return apply_order(frames, order_store.read(project))
