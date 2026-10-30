"""Put a layer job on every frame in scope, and a copy frame under every variant past the first.

One use case for video and for sound: what differs is which slot is being filled, which layer has to
be under it, and what a copy carries -- all three are the same rule read at a different height of
the stack.

Scope is decided here rather than on screen: what a frame really holds is the record's answer, and a
panel that decided it would be a second truth about the same question.

A frame whose own layer has not landed is skipped: the card has not settled yet, so there is nothing
to hang anything on. What a layer needs UNDER it is layers.NEEDS' answer -- a video hangs on nothing
(madde 293). A frame that already has this layer is never written over -- "üret = ekle" means
the extra one becomes a frame of its own, sharing what is under it and taking the next variant of
its source's number (madde 25, 102). A frame whose layer is already in line -- put back, or planned
and not yet made -- is not given it again.
Both are the record's answer, read under the press's gate, not the gallery's (madde 513).
"""
from backend.features.photo_generation.domain import layers, production_mode, queue, video_settings
from backend.features.photo_generation.domain.copy_frame import (
    carry_layers,
    family,
    known_ids,
    next_id,
    placed,
)
from backend.features.photo_generation.domain.frame_list import checked
from backend.features.photo_generation.domain.photo_name import layer_file, variant_of
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import (  # noqa: F401
    MAX_VARIANTS,
    InvalidVariants,
    ProjectMissing,
)


def frames_in_scope(gallery, kind, frames=None):
    """The frames a `kind` job can be hung on, in gallery order.

    `frames` is the gallery's own selection, by identity; None means every frame that does not hold
    this layer yet. A frame that already holds one is out of the None scope and inside a
    selection's: the panel's row is called "Videosu olmayan kareler", while picking a frame by hand
    says "this one" -- and that is the only way madde 25's "every variant of a frame that already
    has a video" can be asked for.

    Identities, not file names: a copy frame shows its source's picture, so a name would pick every
    frame showing it when one was chosen (madde 520).
    """
    chosen = None if frames is None else set(frames)
    scope = []
    for frame in gallery:
        if chosen is not None and frame["id"] not in chosen:
            continue
        # Only a card that has settled can carry anything -- the layer that opened it landed (madde
        # 292). Done alone no longer says so: a copy is done once the picture it carries is there,
        # while the layer it was born for may still be coming or red (madde 519) -- so that opening
        # layer, the plan job the row is read from, is asked too. A name that claims no number
        # cannot be planned at all: the plan keeps a number per job and reads back only the jobs
        # that have one.
        # The row's `type` is its opening plan job's, spread into the row by list_frames' card(); a
        # row without one -- an old photo job, or a Kopyala twin read from the record with nothing
        # planned for it yet -- reads as opened by its photo. Once a layer is planned for a twin,
        # that job opens it, as it opens a variant's copy.
        opening = queue.type_of(frame)
        if frame["status"] != "done" or opening in frame.get("owed", ()) \
                or opening in frame.get("failed", ()) or family(frame)[0] is None:
            continue
        held, broken = frame.get("layers", {}), frame.get("failed", [])
        # What this layer hangs on has to be there and has to be sound: a frame without it -- or
        # whose copy of it blew up -- is never in scope, however it was chosen (madde 31). The rule
        # is layers.NEEDS', read here rather than written again.
        under = layers.NEEDS.get(kind)
        if under is not None and (under not in held or under in broken):
            continue
        if chosen is None and kind in held:
            continue
        scope.append(frame)
    return scope


def _job(kind, fid, number, variant, mark=()):
    """The plan line for one layer.

    The prompt is empty on purpose: a language model writes it as soon as the job is queued and it
    goes on the card, in the record (madde 403) -- a box the user was never shown must not pretend
    to hold their words.

    `mark` is what the production mode adds -- nothing at all for a layer that ends nowhere.
    """
    return {"id": fid, "type": kind, "number": number, "variant": variant,
            "prompt": "", "negative": "", "seed": None, "model": "", **dict(mark)}


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
    target = production_mode.frame_after(gallery, fid)
    if target is None:
        # The brief's decision: production is not blocked, this one frame stays out and the rest go
        # in. Fixing the selection and pressing again is all it takes.
        return None
    return {"mode": mode, "linkedTo": target}


def queue_layer(runner, store, record, plan_store, order_store, producers, now, project, kind,
                frames=None, variants=1, log=None, writers=None,
                mode=production_mode.STANDARD, stills=None, references=None, length=None,
                ending=None):
    """Returns how many jobs of this kind the queue took.

    `frames` names the selection by identity, the way every other door that acts on frames does;
    None is the panel's other row, every frame without this layer.

    `length` answers how long the project's videos run now (madde 422); None hands the jobs none,
    and each is made at its graph's own. `ending` answers whether they end happily now (madde 426);
    None, or off, hands them nothing about it.
    """
    if frames is not None:
        checked(frames, "Katman eklenecek")
    production_mode.validate(mode, kind)
    # bool is an int in Python, and True would silently mean "1 variant".
    if isinstance(variants, bool) or not isinstance(variants, int) \
            or not 1 <= variants <= MAX_VARIANTS:
        raise InvalidVariants(f"Varyant sayısı 1-{MAX_VARIANTS} arası bir tam sayı olmalı.")
    # Held from the gallery read to the jobs written: a press at the same moment would otherwise
    # read the same names and give its copies the same ones (madde 512).
    with plan_store.held(project):
        gallery = list_frames(record, store, plan_store, order_store, project)
        scope = frames_in_scope(gallery, kind, frames)
        if not scope:
            # Nothing owed and nothing started: an empty scope is a result, not a failure.
            return 0

        # Asked once per press, and only of a video: every job this press puts in the queue carries
        # the length and the switch of this moment (madde 422, 426).
        timed = video_settings.carried(length, ending, project) if kind == layers.VIDEO else {}
        taken = known_ids(record, plan_store, project)
        # What the log says about each slot, and what decides it: the gallery was read a moment
        # earlier, and the loop writes without waiting for this press -- a video that landed in
        # between is a video here (madde 513).
        slots = record.slots(project)
        jobs, born = [], {}
        # Written oldest first, the direction the engine works in: the gallery is newest-first and
        # its foot is what gets made first, so a plan written the way it reads would run backwards
        # wherever the gallery's own order file has nothing to say.
        for frame in reversed(scope):
            fid = frame["id"]
            mark = _mark(kind, mode, gallery, fid)
            if mark is None:
                continue
            mark = {**mark, **timed}
            number, variant = family(frame)
            cell = slots.get(fid, {}).get(kind)
            status = cell["status"] if cell else None
            # Taken, or free with its name still under another frame: a copy frame holds the file
            # this frame let go of, and the layer made again would be saved over it (madde 513).
            # The name is the one the loop will save under (run_loop's own).
            video = (slots.get(fid, {}).get(layers.VIDEO) or {}).get("file")
            full = layers.is_taken(status) or layers.held_elsewhere(
                slots, fid, layer_file(kind, fid, video=video))
            if frames is None and full:
                # Landed since the gallery was read, or its name is a copy's: the row is "frames
                # without this layer", and this one cannot be given its own.
                continue
            owed = variants
            in_line = status == queue.QUEUED or (status is None
                                                  and kind in frame.get("owed", ()))
            if not full and in_line:
                # Already in line -- put back, or planned and never written about yet, the usual
                # second press before the first is made: the frame's own job is the first variant,
                # and it is not added again (the user, 29 Ekim -- "galeri sırada / kayıt bitti
                # demesi lazım değil mi"). Planned is the gallery's owed, the plan's answer, which
                # only these gated doors write; the record still saying nothing is today's read.
                owed -= 1
            elif not full:
                if status is not None:
                    # Free is not the same as never written about: emptying the queue writes removed
                    # and deleting a layer writes deleted, and both close the job for good. queued
                    # is the one line that reopens it -- the same line Tekrar dene writes, with the
                    # slot's own file name -- and without it the job appended below lands in a plan
                    # the queue cannot see it in. Reported 2026-08-14: after emptying the queue,
                    # sound could never be queued again. It names the closed status it reopens, so
                    # a layer that lands before it is not reopened by it (madde 513).
                    record.mark(project, fid, kind, cell["file"], queue.QUEUED, now(),
                                seen=status)
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
            # Every frame in scope was dropped for want of something to end on. Nothing owed and
            # nothing started, exactly as an empty scope already is.
            return 0
        if born:
            order_store.write(project, placed([frame["id"] for frame in gallery], born))
        plan_store.append(project, jobs)
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers, stills=stills,
              references=references)
    return len(jobs)
