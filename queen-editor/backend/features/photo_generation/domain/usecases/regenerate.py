"""Make a layer again -- as a new frame, never over the one that is there.

"üret = ekle" holds here too (madde 77): the source frame and its files stay exactly as they are and
the result enters the gallery beside it. What makes this different from the panels is only where the
prompt comes from -- the user typed it.

Which number the new frame takes is madde 99's rule: the same words are another variant of the same
prompt's family, changed words are a new prompt and take the next number. Compared stripped, because
space around the text is not an edit.

The layer's round never grows (madde 98). The design's own answer to "the second attempt" is a new
frame, so the second attempt is that frame's first round -- there is no place left for the number to
climb.
"""
from backend.features.photo_generation.domain import layers, production_mode, queue
from backend.features.photo_generation.domain.copy_frame import (
    carry_layers,
    family,
    known_ids,
    next_id,
    placed,
)
from backend.features.photo_generation.domain.photo_name import frame_id, number_of, variant_of
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.retry_frame import FrameMissing  # noqa: F401
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import (  # noqa: F401
    ProjectMissing,
    next_number,
)


class LayerMissing(Exception):
    """The frame does not carry what this layer would be made from (message is user-facing)."""


class NoNextFrame(Exception):
    """A linked video was asked for on a frame the film has nothing after (message is user-facing).

    Its own exception rather than InvalidMode: the mode is a real one and the request is
    understood -- what is missing is a frame to end on.
    """


def regenerate(runner, store, record, plan_store, order_store, producers, new_seed, now,
               project, fid, kind, prompt, negative="", log=None, writers=None,
               mode=production_mode.STANDARD):
    """Returns the identity of the frame the new layer will be made on.

    The source is named by its identity rather than by a file: a copy frame shares its source's
    picture (madde 102), so one file name can belong to two frames and each of them has its own
    layer to make again.

    `mode` is what the new video should be, and the form's default is the source video's own -- so
    changing only the prompt keeps the video the user had (madde 94). A linked one's target is
    worked out here, from the gallery already open on this side.

    `negative` is the box's own words, the same way `prompt` is (Fark 98). Only a photo carries one:
    the layers over it are made from what is under them, so whatever is passed for a video or a
    sound is dropped here rather than at the caller.
    """
    # Above the gallery read: an unknown mode is an unknown mode even in a project that is not
    # there, and the cheap refusal comes first.
    production_mode.validate(mode, kind)
    gallery = list_frames(record, store, plan_store, order_store, project)
    source = next((frame for frame in gallery if frame["id"] == fid), None)
    if source is None:
        raise FrameMissing(f"Bu kare galeride yok: {fid}")
    under = queue.ORDER[:queue.ORDER.index(kind)]
    if source["status"] != queue.DONE or any(slot not in source.get("layers", {})
                                             for slot in under):
        raise LayerMissing(f"Bu karede {kind} üretilemez: altındaki katman yok.")

    number, _variant = family(source)
    said = (source.get("prompts", {}).get(kind) or "").strip()
    if prompt.strip() == said:
        # The same words: another variant of the same prompt's family.
        born = next_id(known_ids(record, plan_store, project), number)
    else:
        # New words are a new prompt: it takes the next number and starts its own family.
        born = frame_id(next_number(store, plan_store, record, project), 0)

    # Nothing at all for the plain mode: every caller before this madde named none, and the plan has
    # to keep reading back exactly the same way.
    mark = {} if mode == production_mode.STANDARD else {"mode": mode}
    if mode == production_mode.LINKED:
        target = production_mode.frame_after(gallery, fid)
        if target is None:
            # Named rather than planned with nothing: a job carrying no target reaches the render
            # and fails there on a frame it cannot even name.
            raise NoNextFrame("Bu son kare — bağlanacak sonraki kare yok.")
        mark["linkedTo"] = target

    carry_layers(record, project, born, source, kind, now)
    plan_store.append(project, [{
        "id": born, "type": kind, "number": number_of(born), "variant": variant_of(born),
        "prompt": prompt,
        # Only a photo is made from a prompt, a negative and a seed of its own; the layers above it
        # are made from what is under them, and the model that renders them is not the user's to
        # pick.
        "negative": negative if kind == layers.PHOTO else "",
        "seed": new_seed() if kind == layers.PHOTO else None,
        "model": source.get("model", "") if kind == layers.PHOTO else "",
        **mark,
    }])
    order_store.write(project, placed([frame["id"] for frame in gallery], {source["id"]: [born]}))
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers)
    return born
