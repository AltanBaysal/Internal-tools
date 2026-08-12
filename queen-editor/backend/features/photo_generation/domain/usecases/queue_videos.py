"""Put a video job on every frame in scope, and a copy frame under every variant past the first.

Scope is decided here rather than on screen: what a frame really holds is the record's answer, and a
panel that decided it would be a second truth about the same question.

A frame whose photo has not landed is skipped: a video hangs on a picture, and there is nothing to
hang it on yet. A frame that already has a video is never written over -- "üret = ekle" means the
extra video becomes a frame of its own, sharing the picture and taking the next variant of its
source's number (madde 25).
"""
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.copy_frame import next_id
from backend.features.photo_generation.domain.photo_name import number_of, variant_of
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import (  # noqa: F401
    MAX_VARIANTS,
    InvalidVariants,
    ProjectMissing,
)


class InvalidScope(Exception):
    """The selection was not a list of file names (message is user-facing)."""


def _family(frame):
    """The (number, variant) pair the frame's identity claims -- the plan's own fields as a fallback.

    Read off the identity rather than the plan, because a copy frame has no photo job in the plan:
    its row comes from the record, and its name is the only thing that says which prompt's family
    it belongs to.
    """
    number, variant = number_of(frame["id"]), variant_of(frame["id"])
    return (number if number is not None else frame.get("number"),
            variant if variant is not None else frame.get("variant"))


def frames_in_scope(gallery, files=None):
    """The frames a video job can be hung on, in gallery order.

    `files` is the gallery's own selection; None means every frame that has no video.

    A frame that already has one is out of the None scope and inside a selection's: the panel's row
    is called "Videosu olmayanlar", while picking a frame by hand says "this one" -- and that is the
    only way madde 25's "every variant of a frame that already has a video" can be asked for.
    """
    chosen = None if files is None else set(files)
    scope = []
    for frame in gallery:
        if chosen is not None and frame["file"] not in chosen:
            continue
        # Only a produced photo can carry a video; a frame still waiting for its own has nothing to
        # hang one on. A name that claims no number cannot be planned at all: the plan keeps a
        # number per job and reads back only the jobs that have one.
        if frame["status"] != "done" or _family(frame)[0] is None:
            continue
        if chosen is None and layers.VIDEO in frame.get("layers", {}):
            continue
        scope.append(frame)
    return scope


def _video_job(fid, number, variant):
    """The plan line for one video.

    The prompt is empty on purpose: a language model writes it when the job's turn comes, and a box
    the user was never shown must not pretend to hold their words.
    """
    return {"id": fid, "type": layers.VIDEO, "number": number, "variant": variant,
            "prompt": "", "negative": "", "seed": None, "model": ""}


def _placed(gallery, born):
    """The gallery's own sequence with each frame's new copies hanging directly above it.

    Above rather than below for two reasons: the gallery's rule is newest on top and a copy is newer
    than its source, and the engine reads the gallery from its foot up -- so the source's own video
    is made first and its copies follow.

    The whole sequence is written, not just the copies: a project nobody has dragged has no order
    file at all, and a file naming the copies alone would send every other frame to the top.
    """
    placed = []
    for fid in gallery:
        placed.extend(reversed(born.get(fid, [])))
        placed.append(fid)
    return placed


def _known_ids(record, plan_store, project):
    """Every identity the project has ever used -- deleted frames included, so no name is reused."""
    return ({frame["id"] for frame in plan_store.read(project)["frames"]}
            | set(record.slots(project)))


def queue_videos(runner, store, record, plan_store, order_store, producers, now, project,
                 files=None, variants=1, log=None, writers=None):
    """Returns how many video jobs the queue took."""
    if files is not None and (not isinstance(files, list)
                              or any(not isinstance(name, str) for name in files)):
        raise InvalidScope("Seçim listesi metin dizisi olmalı.")
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= MAX_VARIANTS:
        raise InvalidVariants(f"Varyant sayısı 1-{MAX_VARIANTS} arası bir tam sayı olmalı.")
    gallery = list_frames(record, store, plan_store, order_store, project)
    scope = frames_in_scope(gallery, files)
    if not scope:
        # Nothing owed and nothing started: an empty scope is a result, not a failure.
        return 0

    taken = _known_ids(record, plan_store, project)
    jobs, born = [], {}
    # Written oldest first, the direction the engine works in: the gallery is newest-first and its
    # foot is what gets made first, so a plan written the way it reads would run backwards wherever
    # the gallery's own order file has nothing to say.
    for frame in reversed(scope):
        fid = frame["id"]
        number, variant = _family(frame)
        owed = variants
        if layers.VIDEO not in frame.get("layers", {}):
            jobs.append(_video_job(fid, number, variant))
            owed -= 1
        for _ in range(owed):
            copy = next_id(taken, number)
            taken.add(copy)
            # A real frame, born with a photo row of its own that points at its source's picture:
            # that is the whole of "kopya kare" -- no flag and no field, so the gallery draws it,
            # deletes it and orders it by the rules it already has.
            record.append(project, {"file": frame["file"], "frame": copy, "layer": layers.PHOTO,
                                    "status": queue.DONE, "prompt": frame.get("prompt", ""),
                                    "negative": frame.get("negative", ""),
                                    "seed": frame.get("seed"), "createdAt": now()})
            born.setdefault(fid, []).append(copy)
            jobs.append(_video_job(copy, number, variant_of(copy)))

    if born:
        order_store.write(project, _placed([frame["id"] for frame in gallery], born))
    plan_store.append(project, jobs)
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers)
    return len(jobs)
