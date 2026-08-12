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
from backend.features.photo_generation.domain import layers
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


def _job(kind, fid, number, variant):
    """The plan line for one layer.

    The prompt is empty on purpose: a language model writes it when the job's turn comes, and a box
    the user was never shown must not pretend to hold their words.
    """
    return {"id": fid, "type": kind, "number": number, "variant": variant,
            "prompt": "", "negative": "", "seed": None, "model": ""}


def queue_layer(runner, store, record, plan_store, order_store, producers, now, project, kind,
                files=None, variants=1, log=None, writers=None):
    """Returns how many jobs of this kind the queue took."""
    if files is not None and (not isinstance(files, list)
                              or any(not isinstance(name, str) for name in files)):
        raise InvalidScope("Seçim listesi metin dizisi olmalı.")
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
    jobs, born = [], {}
    # Written oldest first, the direction the engine works in: the gallery is newest-first and its
    # foot is what gets made first, so a plan written the way it reads would run backwards wherever
    # the gallery's own order file has nothing to say.
    for frame in reversed(scope):
        fid = frame["id"]
        number, variant = family(frame)
        held = frame.get("layers", {})
        owed = variants
        if kind not in held:
            jobs.append(_job(kind, fid, number, variant))
            owed -= 1
        for _ in range(owed):
            copy = next_id(taken, number)
            taken.add(copy)
            # A real frame, born holding everything below the layer being made. No flag and no
            # field -- the gallery draws it, deletes it and orders it by the rules it has.
            carry_layers(record, project, copy, frame, kind, now)
            born.setdefault(fid, []).append(copy)
            jobs.append(_job(kind, copy, number, variant_of(copy)))

    if born:
        order_store.write(project, placed([frame["id"] for frame in gallery], born))
    plan_store.append(project, jobs)
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers)
    return len(jobs)
