"""How a frame born from another one is named, placed and given what it stands on.

Three acts make one: a variant past the first (queue_layer), a second attempt at a layer
(regenerate), and whatever asks the same next. What they share is here, so the answer cannot drift
between them.

A copy frame keeps its source's prompt number and takes the next variant, so its name still says
what produced the picture (design v3, madde 97).
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import frame_id, number_of, variant_of


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


def carry_layers(record, project, copy, frame, kind, now):
    """Give the new frame everything below the layer that is about to be made.

    A video copy shares the picture, a sound copy shares the picture and the video (madde 102). The
    rows point at the source's own files: one picture, two frames holding it.
    """
    words = frame.get("prompts", {})
    for under in queue.ORDER[:queue.ORDER.index(kind)]:
        file = frame.get("layers", {}).get(under)
        if not file:
            continue
        record.append(project, {"file": file, "frame": copy, "layer": under,
                                "status": queue.DONE, "prompt": words.get(under, ""),
                                "negative": frame.get("negative", ""),
                                "seed": frame.get("seed"), "createdAt": now()})
