"""The gallery: every frame that has a place in it, in the order it is shown, top first.

One answer, not two. The plan says what was asked for and the record says what became of it; putting
those together here is what lets the gallery be a single sequence instead of four buckets, and it is
why a frame turns into a photo without moving.

"running" is not among the statuses: a frame being rendered has no line on disk (a dead process must
not leave one behind), so the screen learns it from the live worker and draws the pending frame it
already has in place.

A frame is a box, and the layer that opened it decides whether it is here: a card exists because
something was planned for it, and the first thing planned that is still there is what its row is
read from (madde 292, 294). Nothing about the photo is special any more -- a card opened by a video
is a card, a card whose picture was deleted is still a card, and the jobs that come after the
opening one are that card's layers rather than cards of their own. A card with no layer left to
speak for it is not drawn: boş kutu yaşamaz.
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


def _words(said, planned, kind=layers.PHOTO):
    """What each of the frame's layers was made from.

    The record answers for every layer; the opening layer's own prompt can also come from the plan,
    which is where a frame planned before the record carried prompts still keeps it. `kind` is that
    opening layer, and it defaults to the photo because every frame written before madde 292 was
    opened by one.
    """
    words = dict(said)
    if planned and not words.get(kind):
        words[kind] = planned
    return words


def _status(slots, job):
    """What the record last said about this job's own slot, or None when it has never spoken."""
    cell = slots.get(job["id"], {}).get(queue.type_of(job))
    return cell["status"] if cell else None


def _spoken_for(status):
    """May a layer in this state open a card -- is it here, or still coming?"""
    return status in SHOWN or queue.is_open(status)


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


def _per_layer(cells, field):
    """{layer: the field's value} -- only the layers whose line carried it.

    Both of this shape's users answer the same kind of question about one layer at a time: which
    mode made it, and which picture it arrived at. Written as maps rather than fields named for the
    video, because both would have to be renamed the day a second layer gains a mode.
    """
    return {slot: cell[field] for slot, cell in cells.items() if cell.get(field)}


def list_frames(record, store, plan_store, order_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")

    slots = record.slots(project)
    photos = {row["frame"]: row for row in record.list(project)}
    planned = plan_store.read(project)["frames"]
    owed = _owed_layers(planned, slots)
    said = record.prompts(project)

    # The job that opened each card, read in the plan's own order. Nothing is written down for this:
    # the plan's sequence already says which job came first, and a field repeating it would be a
    # second answer to one question. A job whose slot has been closed is skipped -- a deleted layer
    # cannot speak for the card -- so a card with no job left to open it is absent from here, and
    # that absence is the whole of "boş kutu yaşamaz" (madde 294).
    opening = {}
    for frame in planned:
        if _spoken_for(_status(slots, frame)):
            opening.setdefault(frame["id"], frame)

    def card(base, fid, kind, status):
        """One row: what it was asked for, plus what it holds now."""
        cells = slots.get(fid, {})
        photo = cells.get(layers.PHOTO)
        return {**base, "id": fid,
                # The photo slot's own file while it holds one: a copy frame's picture is its
                # source's, not the name its own number would give. A card with nothing produced --
                # or with its picture deleted -- is drawn under the name its identity gives.
                "file": photo["file"] if photo and layers.is_taken(photo["status"])
                        else photo_file(fid),
                "layers": _taken_files(cells),
                "owed": owed.get(fid, []), "failed": _failed_layers(cells),
                "errors": _reasons(cells), "modes": _per_layer(cells, "mode"),
                "endsOn": _per_layer(cells, "endsOn"),
                "prompts": _words(said.get(fid, {}), base.get("prompt"), kind),
                "status": status}

    frames = []
    # Newest first, the same direction the record answers in, so an unordered gallery already reads
    # the way the design wants it.
    for frame in reversed(planned):
        fid = frame["id"]
        if opening.get(fid) is not frame:
            # Every job after the opening one is this card's layer, and a card nothing opens has no
            # place here at all. Read as a row of its own a layer would draw the card twice.
            continue
        # The card's own state is its opening layer's: a card born from a video is done when that
        # video landed, exactly as a card born from a photo is done when the photo did.
        status = _status(slots, frame)
        frames.append(card(frame, fid, queue.type_of(frame),
                           status if status in SHOWN else "pending"))

    # Cards the plan does not open: projects generated before the plan became permanent kept only
    # their last batch, and a copy frame's carried layers were never planned at all (copy_frame).
    # They belong to the gallery for as long as they hold something -- the same rule, read from the
    # record because that is all they have.
    held = [fid for fid in list(photos) + list(slots)
            if fid not in opening and _taken_files(slots.get(fid, {}))]
    for fid in dict.fromkeys(held):
        frames.append(card(photos.get(fid, {}), fid, layers.PHOTO, queue.DONE))

    return apply_order(frames, order_store.read(project))
