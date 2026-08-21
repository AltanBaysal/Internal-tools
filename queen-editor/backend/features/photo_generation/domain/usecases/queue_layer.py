"""Put a layer job on every frame in scope, and a copy frame under every variant past the first.

One use case for video and for sound: what differs is which slot is being filled, which layer has to
be under it, and what a copy carries -- all three are the same rule read at a different height of
the stack.

Scope is decided here rather than on screen: what a frame really holds is the record's answer, and a
panel that decided it would be a second truth about the same question.

A frame whose photo has not landed is skipped: every layer hangs on a picture, and there is nothing
to hang it on yet. A frame that already has this layer is never written over -- "üret = ekle" means
the extra one becomes a frame of its own, sharing what is under it and taking the next variant of
its source's number (madde 25, 102).
"""
from backend.features.photo_generation.domain import layers, production_mode, queue
from backend.features.photo_generation.domain.copy_frame import (
    carry_layers,
    family,
    known_ids,
    next_id,
    placed,
)
from backend.features.photo_generation.domain.photo_name import variant_of
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import (  # noqa: F401
    MAX_VARIANTS,
    InvalidVariants,
    ProjectMissing,
)


class InvalidScope(Exception):
    """The selection was not a list of file names (message is user-facing)."""


class InvalidMode(Exception):
    """A production mode nobody knows, or one given to a layer that ends nowhere."""


def frames_in_scope(gallery, kind, files=None):
    """The frames a `kind` job can be hung on, in gallery order.

    `files` is the gallery's own selection; None means every frame that does not hold this layer
    yet. A frame that already holds one is out of the None scope and inside a selection's: the
    panel's row is called "Videosu olmayanlar", while picking a frame by hand says "this one" --
    and that is the only way madde 25's "every variant of a frame that already has a video" can be
    asked for.
    """
    chosen = None if files is None else set(files)
    scope = []
    for frame in gallery:
        if chosen is not None and frame["file"] not in chosen:
            continue
        # Only a produced photo can carry anything. A name that claims no number cannot be planned
        # at all: the plan keeps a number per job and reads back only the jobs that have one.
        if frame["status"] != "done" or family(frame)[0] is None:
            continue
        held, broken = frame.get("layers", {}), frame.get("failed", [])
        # Sound is mixed over a video, so a frame without one -- or whose video blew up -- is never
        # in its scope, however it was chosen (madde 31). The photo needs no check of its own: a
        # frame whose status is done has one.
        if kind == layers.AUDIO and (layers.VIDEO not in held or layers.VIDEO in broken):
            continue
        if chosen is None and kind in held:
            continue
        scope.append(frame)
    return scope


def _job(kind, fid, number, variant, mark=()):
    """The plan line for one layer.

    The prompt is empty on purpose: a language model writes it when the job's turn comes, and a box
    the user was never shown must not pretend to hold their words.

    `mark` is what the production mode adds -- nothing at all for a layer that ends nowhere.
    """
    return {"id": fid, "type": kind, "number": number, "variant": variant,
            "prompt": "", "negative": "", "seed": None, "model": "", **dict(mark)}


def _frame_after(gallery, fid):
    """The frame a linked video ends on: the one that comes after it in the film.

    The film's sequence, not the gallery's reading order. The gallery is newest-first and the export
    stitches it reversed (export_summary.exportable) -- the foot of the gallery is the film's first
    frame -- so the frame that plays next is the one ABOVE, at index - 1. Linking downwards would
    make every chain run against the film it is part of.

    None where there is nothing to end on: the last frame of the film -- the top of the gallery --
    has no next, and a next whose photo never landed is the same emptiness seen from closer up.
    """
    for index, frame in enumerate(gallery):
        if frame["id"] != fid:
            continue
        after = gallery[index - 1] if index > 0 else None
        return after["id"] if after and after["status"] == queue.DONE else None
    return None


def _mark(kind, mode, gallery, fid):
    """What the mode writes into this frame's plan line, or None when it takes no job at all.

    Resolved as the job is queued rather than as it is rendered: the user can drag the gallery while
    the queue runs, and a target read hours later would not be the one they were looking at when
    they pressed the button.
    """
    if kind != layers.VIDEO:
        return {}
    if mode != production_mode.LINKED:
        return {"mode": mode}
    target = _frame_after(gallery, fid)
    if target is None:
        # The brief's decision: production is not blocked, this one frame stays out and the rest go
        # in. Fixing the selection and pressing again is all it takes.
        return None
    return {"mode": mode, "linkedTo": target}


def queue_layer(runner, store, record, plan_store, order_store, producers, now, project, kind,
                files=None, variants=1, log=None, writers=None,
                mode=production_mode.STANDARD):
    """Returns how many jobs of this kind the queue took."""
    if files is not None and (not isinstance(files, list)
                              or any(not isinstance(name, str) for name in files)):
        raise InvalidScope("Seçim listesi metin dizisi olmalı.")
    if mode not in production_mode.ALL:
        raise InvalidMode(f"Üretim modu şunlardan biri olmalı: {', '.join(production_mode.ALL)}.")
    if mode != production_mode.STANDARD and kind != layers.VIDEO:
        # Only a video ends on a picture. Ignoring the argument would hide the caller's mistake
        # behind a sound that came out fine.
        raise InvalidMode("Üretim modu yalnız video işine verilebilir.")
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= MAX_VARIANTS:
        raise InvalidVariants(f"Varyant sayısı 1-{MAX_VARIANTS} arası bir tam sayı olmalı.")
    gallery = list_frames(record, store, plan_store, order_store, project)
    scope = frames_in_scope(gallery, kind, files)
    if not scope:
        # Nothing owed and nothing started: an empty scope is a result, not a failure.
        return 0

    taken = known_ids(record, plan_store, project)
    # What the log last said about each slot. Read once: the only cells consulted below belong to
    # frames that already exist, and the rows written during the loop are about other slots.
    slots = record.slots(project)
    jobs, born = [], {}
    # Written oldest first, the direction the engine works in: the gallery is newest-first and its
    # foot is what gets made first, so a plan written the way it reads would run backwards wherever
    # the gallery's own order file has nothing to say.
    for frame in reversed(scope):
        fid = frame["id"]
        mark = _mark(kind, mode, gallery, fid)
        if mark is None:
            continue
        number, variant = family(frame)
        held = frame.get("layers", {})
        owed = variants
        if kind not in held:
            settled = slots.get(fid, {}).get(kind)
            if settled:
                # Free is not the same as never written about: emptying the queue writes removed and
                # deleting a layer writes deleted, and both close the job for good. queued is the one
                # line that reopens it -- the same line Tekrar dene writes, with the slot's own file
                # name -- and without it the job appended below lands in a plan the queue cannot see
                # it in. Reported 2026-08-14: after emptying the queue, sound could never be queued
                # again.
                record.mark(project, fid, kind, settled["file"], queue.QUEUED, now())
            jobs.append(_job(kind, fid, number, variant, mark))
            owed -= 1
        for _ in range(owed):
            copy = next_id(taken, number)
            taken.add(copy)
            # A real frame, born holding everything below the layer being made. No flag and no
            # field -- the gallery draws it, deletes it and orders it by the rules it has.
            carry_layers(record, project, copy, frame, kind, now)
            born.setdefault(fid, []).append(copy)
            jobs.append(_job(kind, copy, number, variant_of(copy), mark))

    if not jobs:
        # Every frame in scope was dropped for want of something to end on. Nothing owed and nothing
        # started, exactly as an empty scope already is.
        return 0
    if born:
        order_store.write(project, placed([frame["id"] for frame in gallery], born))
    plan_store.append(project, jobs)
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers)
    return len(jobs)
