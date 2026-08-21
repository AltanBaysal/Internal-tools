"""The loop the worker runs: take the next job the queue owes, do it, write its line, repeat.

It holds no list of its own. Every turn asks the plan and the record again, and that is the whole
mechanism behind a live queue: jobs appended while the loop runs are picked up on the next turn,
and a job that settled meanwhile is simply never reached. One loop, so the rules about failures,
pauses and what "done" means exist in exactly one place.

Which producer does the work is decided by the job's type. The loop knows none of them by name: it
is handed a {type: producer} map and looks the job's own type up in it.

Some jobs are produced with a prompt nobody typed: a video's own is written by a language model when
its turn comes. Which model that is the loop does not know either -- it looks the job's type up in a
second map, exactly the way it finds the producer.
"""
import time

from backend.features.photo_generation.domain import layers, policy, production_mode, queue, seed
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
    if mode == production_mode.STANDARD:
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


def _made_with(job, end):
    """What the produced row says about how it was made, beyond its words and its seed.

    The mode, and the name of the picture the video arrived at -- each only when there is one.

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
    return made


def make_job(runner, store, record, plan_store, producers, now, project,
             clock=time.monotonic, log=None, order_store=None, writers=None,
             new_seed=seed.random_seed):
    """Returns the callable PhotoRunner.start expects: it drains this project's queue.

    `producers` maps a job type to the thing that can do it (see ports.PhotoGenerator). A type with
    nobody to do it stops the run and says so -- skipping it silently would drop work the user asked
    for.

    `writers` maps a job type to the thing that writes its prompt when the job carries none (see
    ports.PromptWriter). A type with no writer is produced with the prompt it has, which is what a
    photo job -- whose prompt is the user's own -- always does.

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
    capturing output and the clock can be faked instead of waited on.
    """

    def snapshot():
        return (plan_store.read(project)["frames"], record.slots(project),
                order_store.read(project) if order_store else ())

    def summary(status, **extra):
        jobs, slots, _order = snapshot()
        return {"status": status, **queue.counts(jobs, slots), **extra}

    def job():
        # Attempts spent on the job in hand, which job they belong to, and the prompt written for
        # it. Memory only: a dead process must leave no count behind, and a restarted run deserves
        # three fresh tries.
        attempts, holding, written, chosen = 0, None, None, None
        while True:
            if runner.stop_requested():
                return summary("paused")
            jobs, slots, order = snapshot()
            owed = queue.open_jobs(jobs, slots, order)
            if not owed:
                return summary("done")
            current = owed[0]
            kind = queue.type_of(current)
            producer = producers.get(kind)
            if producer is None:
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
                # A different job: its predecessor's attempts, written prompt and seed are not its
                # own.
                holding, attempts, written, chosen = name, 0, None, None
            if chosen is None:
                # A layer job is planned with no seed (queue_layer). Picked before the render, and
                # once per job rather than once per attempt: all three tries share it, so the row
                # names the number every one of them used.
                chosen = current["seed"] if current["seed"] is not None else new_seed()
            # pending is what the gallery draws as "bekliyor": the queue behind the job being done.
            # failures names the tiles it draws red, each with its own Tekrar dene.
            runner.report({**queue.counts(jobs, slots), "current": current,
                           "pending": [photo_file(j["id"]) for j in owed[1:]]})
            started = clock()
            try:
                writer = (writers or {}).get(kind)
                if writer and not current["prompt"] and written is None:
                    # Asked here rather than when the job was queued: a job that waits hours would
                    # otherwise be produced from a prompt written for a gallery that has changed,
                    # and queueing 40 jobs would spend 40 requests before a single frame is made.
                    # Inside the try on purpose -- a model that will not answer is a failure like
                    # any other, and the three attempts and the frame-fault rule already say what
                    # happens next.
                    source = _prompts_of(record, project, fid)
                    # Nothing to convert: asking would buy an invented prompt. I2V sees the picture
                    # itself, so producing with an empty prompt is a real answer here.
                    if any(source.values()):
                        written = writer.write(source)
                prompt = current["prompt"] or written or ""
                # Held in a variable because a loop ends on the very file it is made from: reading
                # it twice would be the same download from Drive twice, once per video.
                under = _source_for(kind, store, slots, project, fid)
                # Held because the row names it too: the picture the video arrives at is what the
                # detail page prints for a linked one.
                ending = _end_for(current, store, slots, project, fid, under)
                data = producer.generate(prompt, current["negative"], chosen,
                                         current["model"], source=under, end=ending)
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
                    # owes the rest nothing, so the tile turns red where it stands and work goes on.
                    record.mark(project, fid, kind, name, queue.FAILED, now(),
                                error=policy.frame_reason(exc, attempts))
                    attempts, holding = 0, None
                    continue
                # No answer came at all, three times: the next job would fall the same way, so the
                # run stops. Deliberately no line for the job -- it stays owed, and resuming starts
                # from it rather than leaving a red tile the user has to rescue by hand.
                return summary("error", error=f"{policy.stop_reason(attempts)}\n{exc}")
            rendered = clock()
            filename = store.save(project, name, data)
            # Only after the file exists: the line is what "this layer is here" means.
            record.append(project, {"file": filename, "frame": fid, "layer": kind,
                                    "status": queue.DONE,
                                    "prompt": prompt, "negative": current["negative"],
                                    "seed": chosen, "createdAt": now(),
                                    **_made_with(current, ending)})
            if log:
                # Two numbers, never one: the render is the GPU's share and the writes are the
                # pipeline's, and speed decisions need to tell them apart.
                log(f"⏱ {filename} · render {rendered - started:.1f} sn"
                    f" · drive {clock() - rendered:.1f} sn")
            # No attempt counter to clear here: the next turn holds a different job, and that is
            # the one place the count resets.

    return job
