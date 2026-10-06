"""The loop the worker runs: take the next job the queue owes, do it, write its line, repeat.

It holds no list of its own. Every turn asks the plan and the record again, and that is the whole
mechanism behind a live queue: jobs appended while the loop runs are picked up on the next turn,
and a job that settled meanwhile is simply never reached. One loop, so the rules about failures,
pauses and what "done" means exist in exactly one place.

Which producer does the work is decided by the job's type. The loop knows none of them by name: it
is handed a {type: producer} map and looks the job's own type up in it.

Some jobs are produced with a prompt nobody typed: a video's or a sound's own is written by a language
model as soon as it is queued -- every turn writes the owed prompts before it makes anything -- and
kept on the card until its turn comes (madde 403). Which model that is the loop does not know either
-- it looks the job's type up in a second map, exactly the way it finds the producer.
"""
import time

from backend.features.photo_generation.domain import (
    layers,
    policy,
    production_mode,
    queue,
    scene,
    seed,
    variant_batch,
)
from backend.features.photo_generation.domain.photo_name import layer_file, photo_file


class MissingEndFrame(RuntimeError):
    """A linked video's target frame has no photo to end on.

    frame_level, so policy treats it the way it treats a graph that blew up: this one tile turns red
    and the queue goes on. The alternative -- quietly rendering a plain video instead -- would hand
    the user something other than what they asked for and say nothing about it.
    """

    frame_level = True


def _prompts_of(record, project, fid):
    """What the frame already says, layer by layer -- the material a prompt writer works from.

    Read from the record rather than the plan: a copy frame has no photo job of its own, and its
    rows are where its words live.
    """
    return record.prompts(project).get(fid, {})


def _unwritten(owed, writers, record, project):
    """The first owed job whose prompt a model still has to write, or None.

    A job needs one when its type has a writer, it carries no prompt of its own,
    none has been written for it yet, and the frame has words to write from -- asking with none
    would buy an invented prompt, and I2V sees the picture itself. A sound waits for its video's
    prompt: a video that carries the user's words has them in the record only once it is made. The
    record is asked only when some job could need one: a run with no writers never asks it about
    words at all.
    """
    waiting = [job for job in owed if queue.type_of(job) in writers and not job["prompt"]]
    if not waiting:
        return None
    said, written = record.prompts(project), record.written_prompts(project)
    return next((job for job in waiting
                 if queue.type_of(job) not in written.get(job["id"], {})
                 and _has_words(queue.type_of(job), said.get(job["id"], {}))), None)


def _has_words(kind, said):
    """Whether the frame says anything this job's prompt can be written from. A sound is written
    from its video's prompt alone (madde 404), so the photo's words give it nothing; a video is
    written from whatever the frame says."""
    return bool(said.get(layers.VIDEO)) if kind == layers.AUDIO else any(said.values())


# What a layer is made from: a video hangs on the frame's photo, a sound is laid over its video,
# and a photo is made from its prompt alone.
UNDER = {layers.VIDEO: layers.PHOTO, layers.AUDIO: layers.VIDEO}


def _source_for(kind, store, slots, project, fid):
    """The file a layer is made from, as (name, bytes); None for a layer that needs none.

    Read at the job's turn rather than kept in memory: the file is on Drive and the run may have
    started hours ago. `slots` is the turn's own snapshot, so nothing is asked of the record twice.
    """
    under = UNDER.get(kind)
    if under is None:
        return None
    cell = slots.get(fid, {}).get(under)
    if not cell:
        return None
    return (cell["file"], store.read(project, cell["file"]))


def _end_for(job, store, slots, project, fid, source):
    """The picture this job's video arrives at, as (name, bytes); None when it arrives nowhere.

    Read at the job's turn like the source is, and for the same reason: the file is on Drive and the
    run may have started hours ago.

    A loop ends on the frame's own picture -- the very file it is being made from -- so `source` is
    handed back rather than read a second time.
    """
    mode = production_mode.of(job)
    if mode in (production_mode.STANDARD, production_mode.REFERENCE):
        # A video made of the pool arrives nowhere either: it is not hung on a frame at all.
        return None
    if mode == production_mode.LOOP:
        return source
    target = job.get("linkedTo")
    cell = slots.get(target, {}).get(layers.PHOTO) if target else None
    if not cell:
        # Deleted between the press and the render. Named in the message, because "the frame it was
        # told to end on" is the one thing the user cannot work out from the tile.
        raise MissingEndFrame(f"Bağlanacak karenin fotoğrafı yok: {target or '?'}")
    return (cell["file"], store.read(project, cell["file"]))


def _held(slots, fid):
    """{slot: status} for one frame -- the shape layers' rules are asked in."""
    return {slot: cell["status"] for slot, cell in slots.get(fid, {}).items()}


def _first_frame(stills, video, log):
    """The video's opening frame, or None when nobody can pull one or it could not be pulled.

    A failed extraction is not the job's failure: the video was asked for, it is on disk, and its
    row is written -- the picture is a convenience. What went wrong is said rather than swallowed,
    in ffmpeg's own words.
    """
    if stills is None:
        return None
    try:
        return stills.first_frame(video)
    except Exception as exc:
        if log:
            log(f"⚠ İlk kare çıkarılamadı: {exc}")
        return None


def _made_with(job, end):
    """What the produced row says about how it was made, beyond its words and its seed.

    The mode, the name of the picture the video arrived at, and how long it was made -- each only
    when there is one.

    Which jobs carry a mode is the queue's rule (queue_layer puts the field on video jobs alone) and
    it is not written a second time here, where the two could drift apart. A photo row saying
    standard would be a field that means nothing on nearly every line it appears on.

    The ending picture is named by the file the render was actually handed, not by the target's
    identity. The detail page prints that name, and an identity resolved later can resolve to
    nothing: the frame a video ends on can be deleted while the video stays.
    """
    made = {"mode": production_mode.of(job)} if job.get("mode") else {}
    if end:
        made["endsOn"] = end[0]
    if job.get("seconds"):
        # How long the video was made, so the export can add up each one's own (madde 422).
        made["seconds"] = job["seconds"]
    return made


def _made_together(owed, jobs, slots, producer):
    """The jobs this turn's render makes: the head of the queue, and the variants of its prompt that
    go with it in one batch (madde 411).

    Together only when the producer can make a batch at all -- a photo's can, a video's and a
    sound's cannot -- and the card holds every variant the prompt was asked for. Asked with that
    count rather than with what is left of it: a prompt too big for the card is made one by one to
    its end, as before, not one by one until the rest happens to fit.
    """
    group = variant_batch.together(owed, slots)
    if len(group) > 1 and hasattr(producer, "fits_batch") \
            and producer.fits_batch(variant_batch.asked(jobs, group[0])):
        return group
    return group[:1]


def _files(name, together):
    """Each made job's file, in order: the head's own name, then the other pictures of its batch."""
    return [name] + [photo_file(other["id"]) for other in together[1:]]


def make_job(runner, store, record, plan_store, producers, now, project,
             clock=time.monotonic, log=None, order_store=None, writers=None,
             new_seed=seed.random_seed, named=None, stills=None, references=None):
    """Returns the callable PhotoRunner.start expects: it drains this project's queue.

    `producers` maps a job type to the thing that can do it (see ports.PhotoGenerator). A type with
    nobody to do it stops the run and says so -- skipping it silently would drop work the user asked
    for.

    `writers` maps a job type to the thing that writes its prompt when the job carries none (see
    ports.PromptWriter). A type with no writer is produced with the prompt it has, which is what a
    photo job -- whose prompt is the user's own -- always does. What a writer wrote goes in the
    record, where the card shows it and the producer finds it (madde 403).

    `order_store` is where the sequence comes from: the gallery's own order is the order work is
    done in, read from its foot up. Without one the plan's sequence stands, which is what a project
    nobody has dragged in looks like anyway.

    `new_seed` is where a job with no seed of its own gets one. Chosen here rather than inside a
    producer because the number has to be written on the produced layer's row as well, and this is
    the only place standing between the render and that row. A default rather than a required
    argument: every caller reaches the queue through this function, and none of them has a reason to
    know about seeds.

    `log` is where the per-frame timing line goes -- None means nobody asked for one. What the line
    says is decided here; where it lands is main.py's to choose, so the loop can be tested without
    capturing output and the clock can be faked instead of waited on. The render's seconds on that
    line are the ones written on the produced layer's row, which the card shows (madde 405).

    `stills` is what pulls a picture out of a video (see ports.Stills). None means no picture is
    pulled at all, which is what the loop did before madde 296 and what a run with no ffmpeg does.

    `references` answers with the project's reference pool as files, for a job that is made of it
    (madde 304). Asked at the job's turn rather than read off the plan: a card does not remember
    what it was made from, so a retry produces with the pool as it stands now.

    `named` is where the project's name is read from, turn by turn: a project IS a folder and it can
    be renamed under a run, so a name captured once would leave the next turn reading a folder that
    is not there. It defaults to the runner's own holder -- the runner is what every way into the
    queue already carries. A caller that hands its own is a test watching the run follow a move.
    """
    if named is None:
        named = runner.named
        named.took(project)

    def snapshot():
        project = named.now()
        return (plan_store.read(project)["frames"], record.slots(project),
                order_store.read(project) if order_store else ())

    def summary(status, **extra):
        jobs, slots, _order = snapshot()
        return {"status": status, **queue.counts(jobs, slots), **extra}

    def job():
        # Attempts spent on the job in hand, which job they belong to, and the seed chosen for it.
        # Memory only: a dead process must leave no count behind, and a restarted run deserves three
        # fresh tries.
        attempts, holding, chosen = 0, None, None
        while True:
            if runner.stop_requested():
                return summary("paused")
            # Read again every turn: a rename moves the folder under the run, and this is what lets
            # the next turn simply work in the new one.
            project = named.now()
            jobs, slots, order = snapshot()
            owed = queue.open_jobs(jobs, slots, order)
            if not owed:
                return summary("done")
            # A prompt nobody typed is written before anything is made (madde 403), so a layer
            # queued while the engine is busy has its words on the card before its own turn -- and
            # a job queued while the loop is idle has them at once. Every door into the queue ends
            # in run_queue, so this one place covers them all. Written here rather than in the
            # request that queued it: that request answers at once, and forty frames' worth of asks
            # would hold it for minutes.
            writing = _unwritten(owed, writers or {}, record, project)
            current = writing or owed[0]
            kind = queue.type_of(current)
            producer = producers.get(kind)
            if writing is None and producer is None:
                # Not a failure and not a pause: the work is fine, the engine for it is not here
                # yet. No line is written, so the job stays owed -- installing the producer and
                # starting the run again is all it takes, and cancelling that install throws
                # nothing away. The next type is deliberately not started: the order the user sees
                # in the gallery is the order things are made in.
                return summary("waiting", waitingFor=kind)
            fid = current["id"]
            # The layer's own name: what gets saved, and what a failure's line points at. A sound
            # grows the name of the video it is laid over, so the frame's video is part of it. The
            # gallery still marks its tiles by the frame's photo name (see the report below) --
            # that is the screen's identifier for a frame, not the layer's.
            name = layer_file(kind, fid, video=(slots.get(fid, {}).get(layers.VIDEO) or {}).get(
                "file"))
            if name != holding:
                # A different job: its predecessor's attempts and seed are not its own.
                holding, attempts, chosen = name, 0, None
            if writing is None and chosen is None:
                # A layer job is planned with no seed (queue_layer). Picked before the render, and
                # once per job rather than once per attempt: all three tries share it, so the row
                # names the number every one of them used.
                chosen = current["seed"] if current["seed"] is not None else new_seed()
            # pending is what the gallery draws as "bekliyor": the queue behind the job being done.
            # failures names the tiles it draws red, each with its own Tekrar dene. While a prompt
            # is written nothing is being made and every owed frame waits -- current is set to None
            # rather than left out, because a report merges into the one before it. startedAt is
            # cleared for the same reason: no model is working on anything until the render below
            # says so, and a cleared one is what makes a retried attempt's counter start again. So
            # is batch: which frames the render makes with this one is the render's to say.
            progress = {**queue.counts(jobs, slots),
                        "current": None if writing else current,
                        "pending": [photo_file(j["id"])
                                    for j in (owed if writing else owed[1:])],
                        "startedAt": None, "batch": None}
            runner.report(progress)
            # What this turn makes: the job in hand alone, unless its prompt's variants go with it.
            together = [current]
            try:
                # Held in variables because each is asked for more than once: the writer is shown
                # the file the layer is made from and the picture a video arrives at, the producer
                # makes the layer from the one and ends on the other, and the row names the ending
                # -- the detail page prints it for a linked video. The ending is found before the
                # writer is asked, so a linked video whose next frame lost its photo spends no
                # request.
                under = _source_for(kind, store, slots, project, fid)
                ending = _end_for(current, store, slots, project, fid, under)
                if writing:
                    # Inside the try on purpose -- a model that will not answer is a failure like
                    # any other, and the three attempts and the frame-fault rule already say what
                    # happens next. The mode goes with the words: a loop video has to be asked for
                    # a motion that returns, and the frame's own prompts cannot say that (madde
                    # 307). The picture and the scenario go too: H3's writer looks at the one and
                    # reads the other (madde 400), and a linked video's writer sees where it ends
                    # (402).
                    words = writers[kind].write(_prompts_of(record, project, fid),
                                                production_mode.of(current), source=under,
                                                end=ending,
                                                scene=scene.of(scene.by_number(jobs), fid))
                else:
                    # The card's prompt when the job carries none of its own. The record is asked
                    # only then, so a job the user wrote for never reaches it.
                    prompt = current["prompt"] or record.written_prompts(project).get(
                        fid, {}).get(kind, "")
                    # Only a job made of the pool has any, and it is asked for now rather than
                    # when the job was queued: the pool is the user's to change in between.
                    pool = (references(project)
                            if references
                            and production_mode.of(current) == production_mode.REFERENCE
                            else ())
                    together = _made_together(owed, jobs, slots, producer)
                    # The model's own seconds and nothing else: no wait in the queue, no prompt
                    # being written, no Drive read of what the layer is made from (madde 405).
                    # The same moment goes to the screen as wall time, the one clock a browser can
                    # count on from: its live counter and the recorded seconds measure one thing
                    # (madde 408). The progress travels with it so every report reads whole, and
                    # names the batch's other frames, which are being made as much as this one.
                    runner.report({**progress, "startedAt": now(),
                                   "batch": [other["id"] for other in together[1:]],
                                   "pending": [photo_file(j["id"])
                                               for j in owed[len(together):]]})
                    started = clock()
                    if len(together) > 1:
                        made = producer.generate_batch(prompt, current["negative"], chosen,
                                                       len(together), current["model"],
                                                       current.get("lora", ""))
                    else:
                        made = [producer.generate(prompt, current["negative"], chosen,
                                                  current["model"], current.get("lora", ""),
                                                  source=under, end=ending, references=pool,
                                                  seconds=current.get("seconds"))]
            except Exception as exc:
                if runner.stop_requested():
                    # The user's own pause killed this render -- that is not a failure. The job
                    # writes no line, so it stays owed and is done again on resume.
                    return summary("paused")
                attempts += 1
                if attempts < policy.MAX_ATTEMPTS:
                    # Every failure gets the same three tries at the same job (design v3, madde 45);
                    # what differs is what happens after the third.
                    continue
                if policy.is_frame_fault(exc):
                    # The renderer answered three times that this one job is what failed. The queue
                    # owes the rest nothing, so the tile turns red where it stands and work goes on
                    # -- every tile of a batch, which failed as one job.
                    with named.steady() as project:
                        for failed, file in zip(together, _files(name, together)):
                            record.mark(project, failed["id"], kind, file, queue.FAILED, now(),
                                        error=policy.frame_reason(exc, attempts))
                    attempts, holding = 0, None
                    continue
                # No answer came at all, three times: the next job would fall the same way, so the
                # run stops. Deliberately no line for the job -- it stays owed, and resuming starts
                # from it rather than leaving a red tile the user has to rescue by hand.
                return summary("error", error=f"{policy.stop_reason(attempts)}\n{exc}")
            if writing:
                # Under the gate, like the render's own line: the storage layer creates a folder it
                # is missing, so a line that resolved the old name after a rename would leave a
                # ghost project beside the real one.
                with named.steady() as project:
                    record.prompt_written(project, fid, kind, name, words, now())
                # The attempts were the ask's; the render that follows gets three of its own.
                attempts, holding = 0, None
                continue
            rendered = clock()
            # The attempt that made the layer, not the ones that fell: those made nothing. A batch's
            # seconds are shared out, so a picture's time reads like one made alone (madde 411).
            seconds = round((rendered - started) / len(together), 1)
            files = []
            # Together and under the gate: the storage layer creates a folder it is missing, so a
            # save that resolved the old name after a rename would leave a ghost project beside the
            # real one with this single file in it.
            with named.steady() as project:
                for landed, file, data in zip(together, _files(name, together), made):
                    filename = store.save(project, file, data)
                    files.append(filename)
                    # Only after the file exists: the line is what "this layer is here" means. Every
                    # picture of a batch names the seed the batch was made from.
                    record.append(project, {"file": filename, "frame": landed["id"], "layer": kind,
                                            "status": queue.DONE,
                                            "prompt": prompt, "negative": current["negative"],
                                            "seed": chosen, "createdAt": now(),
                                            "renderSeconds": seconds,
                                            **_made_with(current, ending)})
                # The one job that fills two slots: a card whose picture is missing takes the
                # video's first frame as its own, so the gallery and the export both find one
                # (madde 296). Under the same gate as the video, for the same reason. Whether the
                # slot is free is layers' rule, not a second reading of it here -- a red picture
                # holds its slot and is rescued by Tekrar dene alone. A video is always made alone.
                if kind == layers.VIDEO and layers.can_produce(_held(slots, fid), layers.PHOTO):
                    picture = _first_frame(stills, made[0], log)
                    if picture is not None:
                        written = store.save(project, photo_file(fid), picture)
                        # No words on the row: nobody wrote this picture, and the video's own
                        # prompt on it would answer "what was this made from" with a lie.
                        record.append(project, {"file": written, "frame": fid,
                                                "layer": layers.PHOTO, "status": queue.DONE,
                                                "prompt": "", "negative": "", "seed": None,
                                                "createdAt": now()})
            if log:
                # Two numbers, never one: the render is the GPU's share and the writes are the
                # pipeline's, and speed decisions need to tell them apart.
                log(f"⏱ {', '.join(files)} · render {rendered - started:.1f} sn"
                    f" · drive {clock() - rendered:.1f} sn")
            # No attempt counter to clear here: the next turn holds a different job, and that is
            # the one place the count resets.

    return job
