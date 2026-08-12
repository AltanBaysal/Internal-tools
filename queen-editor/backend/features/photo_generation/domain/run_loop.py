"""The loop the worker runs: take the next frame the queue owes, render it, write its line, repeat.

It holds no list of its own. Every turn asks the plan and the record again, and that is the whole
mechanism behind a live queue: frames appended while the loop runs are picked up on the next turn,
and a frame that settled meanwhile is simply never reached. One loop, so the rules about failures,
pauses and what "done" means exist in exactly one place.
"""
import time

from backend.features.photo_generation.domain import layers, policy, queue
from backend.features.photo_generation.domain.photo_name import photo_file


def make_job(runner, store, record, plan_store, generator, now, project,
             clock=time.monotonic, log=None):
    """Returns the callable PhotoRunner.start expects: it drains this project's queue.

    `log` is where the per-frame timing line goes -- None means nobody asked for one. What the line
    says is decided here; where it lands is main.py's to choose, so the loop can be tested without
    capturing output and the clock can be faked instead of waited on.
    """

    def snapshot():
        return plan_store.read(project)["frames"], record.statuses(project)

    def summary(status, **extra):
        frames, statuses = snapshot()
        return {"status": status, **queue.counts(frames, statuses), **extra}

    def job():
        # Attempts spent on the frame in hand, and which frame they belong to. Memory only: a dead
        # process must leave no count behind, and a restarted run deserves three fresh tries.
        attempts, holding = 0, None
        while True:
            if runner.stop_requested():
                return summary("paused")
            frames, statuses = snapshot()
            owed = queue.open_frames(frames, statuses)
            if not owed:
                return summary("done")
            frame = owed[0]
            fid = frame["id"]
            name = photo_file(fid)
            if name != holding:
                holding, attempts = name, 0
            # pending is what the gallery draws as "bekliyor": the queue behind the frame being
            # rendered. failures names the tiles it draws red, each with its own Tekrar dene.
            runner.report({**queue.counts(frames, statuses), "current": frame,
                           "pending": [photo_file(f["id"]) for f in owed[1:]]})
            started = clock()
            try:
                data = generator.generate(frame["prompt"], frame["negative"], frame["seed"],
                                          frame["model"])
            except Exception as exc:
                if runner.stop_requested():
                    # The user's own pause killed this render -- that is not a failure. The frame
                    # writes no line, so it stays owed and is produced again on resume.
                    return summary("paused")
                if policy.is_frame_fault(exc):
                    # The renderer answered: this one frame is what failed, the queue owes the rest
                    # nothing, and the tile turns red where it stands.
                    record.mark(project, fid, layers.PHOTO, name, queue.FAILED, now(),
                                error=str(exc))
                    continue
                attempts += 1
                reason = policy.stop_reason(attempts)
                if reason:
                    # Deliberately no line for the frame: it stays owed, so resuming starts from it
                    # rather than leaving a red tile the user has to rescue by hand.
                    return summary("error", error=f"{reason}\n{exc}")
                continue
            rendered = clock()
            filename = store.save(project, name, data)
            # Only after the photo exists: the line is what "this photo is here" means.
            record.append(project, {"file": filename, "frame": fid, "layer": layers.PHOTO,
                                    "status": queue.DONE,
                                    "prompt": frame["prompt"], "negative": frame["negative"],
                                    "seed": frame["seed"], "createdAt": now()})
            if log:
                # Two numbers, never one: the render is the GPU's share and the writes are the
                # pipeline's, and speed decisions need to tell them apart.
                log(f"⏱ {filename} · render {rendered - started:.1f} sn"
                    f" · drive {clock() - rendered:.1f} sn")
            # No attempt counter to clear here: the next turn holds a different frame, and that is
            # the one place the count resets.

    return job
