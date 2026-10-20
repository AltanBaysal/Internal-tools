"""Make a frame's photo again from corrected words, in the frame's own place (madde 481).

The agent's fix of a mixed-up photo: the prompt and the negative change, the old photo is deleted, and
the new one is made where the old one stood -- "eski fotoğraflar aynı yerde olur sırası yeni bir yer
geçmez". What fixes a mix-up is the words, not a reseed (the user: "seed değiştirmek kurtarmıyor"), so
the rest of the line stays as it was: the model, the lora, the orientation, the scene, and the seed on
the frame's card. For a variant made in a batch that seed is its plan line's own, which the batch never
used -- a batch renders from its head's seed (madde 411) -- so the picture made alone is not the
batch's picture again; it was never going to be, with other words.

The new photo is a new identity standing in the old frame's place in the gallery's order, rather than
the old identity made again: a photo's name is served as immutable, so new bytes under the old name
would show the old picture for good, and a copy frame may hold the old file, which must not change
under it (madde 102). Its name is regenerate's rule (madde 99): the same words are the next variant of
the family, new words the next number. Standing where the old frame stood, it has the old frame's
number on the gallery's badge, and the queue makes it at that place.

The user may allow the fix minutes after it was described (madde 480), so `seen` -- the frame as the
change was described from -- is held against the frame as it is now. A frame that changed in between
is left alone, and so is one another frame's queued video is to arrive at.

Written in the order that loses nothing at any crash: the new line, the order with the new frame in
the old one's place, then the old photo's file, then the lines saying the old frame's layers are gone.
A crash before the last two leaves the old frame whole, beside the new one.
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain import orientation as orientations
from backend.features.photo_generation.domain.copy_frame import (
    family,
    known_ids,
    made_by,
    next_id,
)
from backend.features.photo_generation.domain.photo_name import frame_id, number_of, variant_of
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.run_queue import Busy, run_queue
from backend.features.photo_generation.domain.usecases.start_batch import (
    ProjectMissing,
    next_number,
)

# What a fix answers. The words are the agent's to turn into a sentence.
FIXED = "fixed"
WAITING = "waiting"         # made, but another project's run holds the worker
CHANGED = "changed"         # the frame is not what the caller saw: nothing was written
LINKED = "linked"           # another frame's queued video ends on this photo: nothing was written

# What a frame holds and what its photo is made from: if any of it moved since the caller saw the
# frame, the fix the user allowed was a fix of another frame. A video landed or queued is here too,
# in layers and owed.
WATCHED = ("status", "layers", "owed", "failed", "prompts", "negative")


def _born(store, record, plan_store, project, frame, prompt):
    """The new identity, by regenerate's rule (madde 99)."""
    number, _variant = family(frame)
    said = (frame["prompts"].get(layers.PHOTO) or "").strip()
    if number is not None and prompt.strip() == said:
        return next_id(known_ids(record, plan_store, project), number)
    return frame_id(next_number(store, plan_store, record, project), 0)


def fix_photo(runner, store, record, plan_store, order_store, producers, now, project, seen,
              prompt, negative, log=None, writers=None, stills=None, references=None):
    """Returns FIXED, WAITING, CHANGED or LINKED.

    `seen` is the frame's gallery card as the caller saw it. The caller has decided it may be fixed:
    it has a photo and no video, made or coming. Only the photo and the frame's red slots close
    here, so a video is never deleted even if one were ever asked about.
    """
    try:
        gallery = list_frames(record, store, plan_store, order_store, project)
    except ProjectMissing:
        return CHANGED
    frame = next((card for card in gallery if card["id"] == seen.get("id")), None)
    if frame is None or any(frame.get(key) != seen.get(key) for key in WATCHED):
        return CHANGED

    fid = frame["id"]
    plan = plan_store.read(project)["frames"]
    slots = record.slots(project)
    # A linked video still owed arrives at this frame's photo when its turn comes (madde 402): with
    # the photo deleted it would fail on a frame it can no longer find. Read off the open jobs, which
    # are the queue's own answer; a video already made arrived at the picture it was handed.
    if any(job.get("linkedTo") == fid for job in queue.open_jobs(plan, slots)):
        return LINKED

    line = made_by(plan, frame)
    born = _born(store, record, plan_store, project, frame, prompt)
    plan_store.append(project, [{
        "id": born, "type": layers.PHOTO, "number": number_of(born), "variant": variant_of(born),
        "prompt": prompt, "negative": negative,
        # The card's seed: its line's, or for a copy frame its source's row's.
        "seed": frame.get("seed"),
        "model": line.get("model", ""), "lora": line.get("lora", ""),
        orientations.FIELD: orientations.of(line),
        # The gallery finds a scene by the family's number, so a new number's line says it.
        **({"scene": frame["scene"]} if frame["scene"] else {}),
    }])
    order_store.write(project, [born if card["id"] == fid else card["id"] for card in gallery])

    # The slots read above still hold: the plan and the order were written since, the record was not.
    closing = {(fid, slot) for slot, cell in slots.get(fid, {}).items()
               if (slot == layers.PHOTO and layers.is_taken(cell["status"]))
               or cell["status"] == queue.FAILED}
    # A file another frame still holds stays (madde 101); the disk first, so a failed delete leaves
    # the record saying what is still there (remove_frames' order).
    for file in sorted(layers.files_to_unlink(slots, closing)):
        store.delete(project, file)
    for _fid, slot in sorted(closing):
        record.mark(project, fid, slot, slots[fid][slot]["file"], queue.DELETED, now())

    try:
        run_queue(runner, store, record, plan_store, producers, now, project, log,
                  order_store=order_store, writers=writers, stills=stills, references=references)
    except Busy:
        return WAITING
    return FIXED
