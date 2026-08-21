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
from backend.features.photo_generation.domain.photo_name import photo_file
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing

# What the gallery draws. A removed or deleted frame is gone from it entirely.
SHOWN = (queue.DONE, queue.FAILED)


def _taken_files(cells):
    """The files a frame really has right now -- an emptied slot names nothing."""
    return {slot: cell["file"] for slot, cell in cells.items()
            if layers.is_taken(cell["status"])}


def _owed_layers(jobs, slots):
    """{frame: [layer, ...]} -- what the queue still owes each frame, in the engine's own order.

    The gallery's own question once a frame is a stack: its photo can be done while its video is
    still coming, and one status field cannot say both.
    """
    owed = {}
    for job in queue.open_jobs(jobs, slots):
        owed.setdefault(job["id"], []).append(queue.type_of(job))
    return owed


def _words(said, planned):
    """What each of the frame's layers was made from.

    The record answers for every layer; the photo's own prompt can also come from the plan, which is
    where a frame planned before the record carried prompts still keeps it.
    """
    words = dict(said)
    if planned and not words.get(layers.PHOTO):
        words[layers.PHOTO] = planned
    return words


def _failed_layers(cells):
    """The frame's layers whose latest line says the render blew up, in layer order."""
    return [slot for slot in queue.ORDER
            if (cells.get(slot) or {}).get("status") == queue.FAILED]


def _reasons(cells):
    """{layer: why it blew up} -- the renderer's own sentence, for the layers that have one.

    Only the detail page shows it. The gallery says a frame is red and no more (madde 79): a
    technical line under every red tile would drown the grid it belongs to.
    """
    return {slot: cells[slot]["error"] for slot in _failed_layers(cells)
            if cells[slot].get("error")}


def _modes(cells):
    """{layer: the mode it was made in} -- only the layers whose line named one.

    Video is the only layer with a mode today. Written as a map rather than a field named for the
    video, because the tile's loop badge and the detail page's information row ask the same
    question, and a name would have to change the day a second layer gains one.
    """
    return {slot: cell["mode"] for slot, cell in cells.items() if cell.get("mode")}


def list_frames(record, store, plan_store, order_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    slots = record.slots(project)
    photos = {row["frame"]: row for row in record.list(project)}
    planned = plan_store.read(project)["frames"]
    owed = _owed_layers(planned, slots)
    said = record.prompts(project)

    frames = []
    seen = set()
    # Newest first, the same direction the record answers in, so an unordered gallery already reads
    # the way the design wants it.
    for frame in reversed(planned):
        if queue.type_of(frame) != layers.PHOTO:
            # A frame's row comes from its photo job alone. The plan holds one job per layer, and a
            # video job is that frame's layer -- read as a row of its own it would draw the frame
            # twice.
            continue
        fid = frame["id"]
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
                       "file": photo["file"] if photo else photo_file(fid),
                       "layers": _taken_files(cells),
                       "owed": owed.get(fid, []), "failed": _failed_layers(cells),
                       "errors": _reasons(cells), "modes": _modes(cells),
                       "prompts": _words(said.get(fid, {}), frame.get("prompt")),
                       "status": status if status in SHOWN else "pending"})

    # Photos the plan no longer knows about: projects generated before the plan became permanent
    # kept only their last batch, and those photos are still the gallery's.
    for fid, row in photos.items():
        if fid not in seen:
            cells = slots.get(fid, {})
            frames.append({**row, "id": fid, "layers": _taken_files(cells),
                           "owed": owed.get(fid, []), "failed": _failed_layers(cells),
                           "errors": _reasons(cells), "modes": _modes(cells),
                           "prompts": _words(said.get(fid, {}), row.get("prompt")),
                           "status": queue.DONE})

    return apply_order(frames, order_store.read(project))
