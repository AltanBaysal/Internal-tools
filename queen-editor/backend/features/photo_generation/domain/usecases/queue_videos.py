"""Put a video job on every frame in scope that has no video yet.

Scope is decided here rather than on screen: what a frame really holds is the record's answer, and a
panel that decided it would be a second truth about the same question.

A frame whose photo has not landed is skipped: a video hangs on a picture, and there is nothing to
hang it on yet. So is a frame that already has a video -- "üret = ekle" means no production ever
writes over a layer that is already there.
"""
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing  # noqa: F401


class InvalidScope(Exception):
    """The selection was not a list of file names (message is user-facing)."""


def frames_in_scope(record, store, plan_store, order_store, project, files=None):
    """The frames a video job can be hung on, in gallery order.

    `files` is the gallery's own selection; None means every frame that has no video.
    """
    chosen = None if files is None else set(files)
    scope = []
    for frame in list_frames(record, store, plan_store, order_store, project):
        if chosen is not None and frame["file"] not in chosen:
            continue
        # Only a produced photo can carry one, and only if it is not carrying one already.
        if frame["status"] != "done" or layers.VIDEO in frame.get("layers", {}):
            continue
        scope.append(frame)
    return scope


def queue_videos(runner, store, record, plan_store, order_store, producers, now, project,
                 files=None, log=None):
    """Returns how many video jobs the queue took."""
    if files is not None and (not isinstance(files, list)
                              or any(not isinstance(name, str) for name in files)):
        raise InvalidScope("Seçim listesi metin dizisi olmalı.")
    scope = frames_in_scope(record, store, plan_store, order_store, project, files)
    if not scope:
        # Nothing owed and nothing started: an empty scope is a result, not a failure.
        return 0
    # Written oldest first, the direction the engine works in: the gallery is newest-first and its
    # foot is what gets made first, so a plan written the way it reads would run backwards wherever
    # the gallery's own order file has nothing to say.
    jobs = [{"id": frame["id"], "type": layers.VIDEO, "number": frame.get("number"),
             "variant": frame.get("variant"), "prompt": "", "negative": "", "seed": None,
             "model": ""}
            for frame in reversed(scope)]
    plan_store.append(project, jobs)
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store)
    return len(jobs)
