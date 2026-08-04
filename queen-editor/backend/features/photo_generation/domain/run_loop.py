"""The loop one run works through: render a frame, save it, write its row, repeat.

Shared by starting a batch and by resuming a paused one, because they differ only in which frames
they are handed -- a second copy of this loop would be a second set of rules about failures, pauses
and what "done" means.
"""
from backend.features.photo_generation.domain import policy
from backend.features.photo_generation.domain.photo_name import file_name


def make_job(runner, store, record, generator, now, project, negative, frames):
    """Returns the callable PhotoRunner.start expects: it renders `frames` and reports as it goes."""
    total = len(frames)

    def job():
        done = failed = consecutive = 0
        failures = []
        for index, frame in enumerate(frames):
            if runner.stop_requested():
                return {"status": "paused", "done": done, "failed": failed, "total": total,
                        "failures": failures}
            # pending is what the gallery draws as "bekliyor": the queue behind the frame being
            # rendered, so the screen shows what is coming instead of only what has landed.
            # failures names the tiles it draws red, each with its own Tekrar dene.
            runner.report({"done": done, "failed": failed, "total": total, "current": frame,
                           "failures": failures,
                           "pending": [file_name(f["number"], f["letter"])
                                       for f in frames[index + 1:]]})
            try:
                data = generator.generate(frame["prompt"], negative, frame["seed"])
            except Exception as exc:
                if runner.stop_requested():
                    # The user's own pause killed this render -- that is not a failure. The frame
                    # keeps its reserved number and is produced again on resume.
                    return {"status": "paused", "done": done, "failed": failed, "total": total,
                            "failures": failures}
                failed += 1
                consecutive += 1
                failures.append(file_name(frame["number"], frame["letter"]))
                # getattr, not isinstance: domain must not import the ComfyUI service.
                reason = policy.stop_reason(consecutive, getattr(exc, "infra", False))
                if reason:
                    return {"status": "error", "error": f"{reason}\n{exc}",
                            "done": done, "failed": failed, "total": total, "failures": failures}
                continue
            filename = store.save(project, frame["number"], frame["letter"], data)
            # Only after the photo exists: the row is what "this photo is here" means.
            record.append(project, {"file": filename, "prompt": frame["prompt"],
                                    "negative": negative, "seed": frame["seed"],
                                    "createdAt": now()})
            done += 1
            consecutive = 0
        return {"status": "done", "done": done, "failed": failed, "total": total,
                "failures": failures}

    return job
