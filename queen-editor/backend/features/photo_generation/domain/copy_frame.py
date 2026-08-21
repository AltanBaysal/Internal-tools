"""How a frame born from another one is named, placed and given what it stands on.

Three acts make one: a variant past the first (queue_layer), a second attempt at a layer
(regenerate), and whatever asks the same next. What they share is here, so the answer cannot drift
between them.

A copy frame keeps its source's prompt number and takes the next variant, so its name still says
what produced the picture (design v3, madde 97).
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import (
    copy_id,
    copy_parts,
    frame_id,
    number_of,
    variant_of,
)


def next_id(ids, number):
    """The identity a new frame in `number`'s family takes; `ids` is every identity in the project.

    One past the highest variant ever used, never a gap: a gap belongs to a frame that was deleted,
    and reusing its name would bind one name to two different pictures -- with browsers still
    holding the old bytes under an immutable cache header. The same rule numbers work under
    (start_batch.next_number), for the same reason.
    """
    used = [variant_of(fid) for fid in ids if number_of(fid) == number]
    used = [variant for variant in used if variant is not None]
    return frame_id(number, max(used) + 1 if used else 0)


def next_copy_id(ids, source):
    """The identity a twin of `source` takes; `ids` is every identity the project has used.

    One past the highest copy index that base has ever carried, never a gap -- next_id's rule, for
    next_id's reason: the name of a deleted twin stays claimed. Counted against the base rather than
    the source, so copying a copy gives C2_P11_1 rather than a nested name.
    """
    base = copy_parts(source)[1]
    used = [copy_parts(fid)[0] for fid in ids if copy_parts(fid)[1] == base]
    used = [index for index in used if index is not None]
    return copy_id(base, max(used) + 1 if used else 1)


def known_ids(record, plan_store, project):
    """Every identity the project has ever used -- deleted frames included, so no name is reused."""
    return ({frame["id"] for frame in plan_store.read(project)["frames"]}
            | set(record.slots(project)))


def family(frame):
    """The (number, variant) pair the frame's identity claims -- the plan's own fields as a fallback.

    Read off the identity rather than the plan, because a copy frame has no photo job in the plan:
    its row comes from the record, and its name is the only thing that says which prompt's family
    it belongs to.
    """
    number, variant = number_of(frame["id"]), variant_of(frame["id"])
    return (number if number is not None else frame.get("number"),
            variant if variant is not None else frame.get("variant"))


def placed(gallery, born):
    """The gallery's own sequence with each frame's new copies hanging directly above it.

    Above rather than below for two reasons: the gallery's rule is newest on top and a copy is newer
    than its source, and the engine reads the gallery from its foot up -- so the source's own layer
    is made first and its copies follow.

    The whole sequence is written, not just the copies: a project nobody has dragged has no order
    file at all, and a file naming the copies alone would send every other frame to the top.
    """
    sequence = []
    for fid in gallery:
        sequence.extend(reversed(born.get(fid, [])))
        sequence.append(fid)
    return sequence


# What a carried layer keeps about how it was made: the frame's own map, and the field the row
# takes. One file, two frames holding it -- without these the twin's tile would read video while the
# original reads loop, and its detail page could not say where the video arrived.
CARRIED = (("modes", "mode"), ("endsOn", "endsOn"))


def _carry(record, project, copy, frame, slots, now):
    """Write the new frame's rows for `slots`, pointing at the source's own files.

    The rows are the source's: one picture, two frames holding it (madde 102).
    """
    words = frame.get("prompts", {})
    failed = frame.get("failed", [])
    for under in slots:
        file = frame.get("layers", {}).get(under)
        # A layer that blew up still names a file in the frame's map, but that file is not on disk:
        # a done row about it on the new frame would say it is.
        if not file or under in failed:
            continue
        made = {field: frame.get(source, {})[under]
                for source, field in CARRIED if frame.get(source, {}).get(under)}
        record.append(project, {"file": file, "frame": copy, "layer": under,
                                "status": queue.DONE, "prompt": words.get(under, ""),
                                "negative": frame.get("negative", ""),
                                "seed": frame.get("seed"), "createdAt": now(), **made})


def carry_layers(record, project, copy, frame, kind, now):
    """Give the new frame everything below the layer that is about to be made.

    A video copy shares the picture, a sound copy shares the picture and the video (madde 102).
    """
    _carry(record, project, copy, frame, queue.ORDER[:queue.ORDER.index(kind)], now)


def carry_all(record, project, copy, frame, now):
    """Give the new frame every layer its source holds -- a twin with nothing left to produce."""
    _carry(record, project, copy, frame, queue.ORDER, now)
