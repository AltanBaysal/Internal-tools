"""The loop the worker runs: take the next frame the queue owes, render it, write its line, repeat.

It holds no list of its own. Every turn asks the plan and the record again, and that is the whole
mechanism behind a live queue: frames appended while the loop runs are picked up on the next turn,
and a frame that settled meanwhile is simply never reached. One loop, so the rules about failures,
pauses and what "done" means exist in exactly one place.
"""
from backend.features.photo_generation.domain import policy, queue
from backend.features.photo_generation.domain.photo_name import file_name


def make_job(runner, store, record, plan_store, generator, now, project):
    """Returns the callable PhotoRunner.start expects: it drains this project's queue."""

    def snapshot():
        return plan_store.read(project)["frames"], record.statuses(project)

    def summary(status, **extra):
        frames, statuses = snapshot()
        return {"status": status, **queue.counts(frames, statuses), **extra}

    def job():
        consecutive = 0
        while True:
            if runner.stop_requested():
                return summary("paused")
            frames, statuses = snapshot()
            owed = queue.open_frames(frames, statuses)
            if not owed:
                return summary("done")
            frame = owed[0]
            name = file_name(frame["number"], frame["letter"])
            # pending is what the gallery draws as "bekliyor": the queue behind the frame being
            # rendered. failures names the tiles it draws red, each with its own Tekrar dene.
            runner.report({**queue.counts(frames, statuses), "current": frame,
                           "pending": [file_name(f["number"], f["letter"]) for f in owed[1:]]})
            try:
                data = generator.generate(frame["prompt"], frame["negative"], frame["seed"])
            except Exception as exc:
                if runner.stop_requested():
                    # The user's own pause killed this render -- that is not a failure. The frame
                    # writes no line, so it stays owed and is produced again on resume.
                    return summary("paused")
                record.mark(project, name, queue.FAILED, now(), error=str(exc))
                consecutive += 1
                # getattr, not isinstance: domain must not import the ComfyUI service.
                reason = policy.stop_reason(consecutive, getattr(exc, "infra", False))
                if reason:
                    return summary("error", error=f"{reason}\n{exc}")
                continue
            filename = store.save(project, frame["number"], frame["letter"], data)
            # Only after the photo exists: the line is what "this photo is here" means.
            record.append(project, {"file": filename, "status": queue.DONE,
                                    "prompt": frame["prompt"], "negative": frame["negative"],
                                    "seed": frame["seed"], "createdAt": now()})
            consecutive = 0

    return job
