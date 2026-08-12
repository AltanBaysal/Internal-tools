"""The loop the worker runs: take the next job the queue owes, do it, write its line, repeat.

It holds no list of its own. Every turn asks the plan and the record again, and that is the whole
mechanism behind a live queue: jobs appended while the loop runs are picked up on the next turn,
and a job that settled meanwhile is simply never reached. One loop, so the rules about failures,
pauses and what "done" means exist in exactly one place.

Which producer does the work is decided by the job's type. The loop knows none of them by name: it
is handed a {type: producer} map and looks the job's own type up in it.
"""
import time

from backend.features.photo_generation.domain import policy, queue
from backend.features.photo_generation.domain.photo_name import photo_file


def make_job(runner, store, record, plan_store, producers, now, project,
             clock=time.monotonic, log=None):
    """Returns the callable PhotoRunner.start expects: it drains this project's queue.

    `producers` maps a job type to the thing that can do it (see ports.PhotoGenerator). A type with
    nobody to do it stops the run and says so -- skipping it silently would drop work the user asked
    for.

    `log` is where the per-frame timing line goes -- None means nobody asked for one. What the line
    says is decided here; where it lands is main.py's to choose, so the loop can be tested without
    capturing output and the clock can be faked instead of waited on.
    """

    def snapshot():
        return plan_store.read(project)["frames"], record.slots(project)

    def summary(status, **extra):
        jobs, slots = snapshot()
        return {"status": status, **queue.counts(jobs, slots), **extra}

    def job():
        # Attempts spent on the job in hand, and which job they belong to. Memory only: a dead
        # process must leave no count behind, and a restarted run deserves three fresh tries.
        attempts, holding = 0, None
        while True:
            if runner.stop_requested():
                return summary("paused")
            jobs, slots = snapshot()
            owed = queue.open_jobs(jobs, slots)
            if not owed:
                return summary("done")
            current = owed[0]
            kind = queue.type_of(current)
            producer = producers.get(kind)
            if producer is None:
                return summary("error", error=f"Bu iş türü için üretici yok: {kind}")
            fid = current["id"]
            name = photo_file(fid)
            if name != holding:
                holding, attempts = name, 0
            # pending is what the gallery draws as "bekliyor": the queue behind the job being done.
            # failures names the tiles it draws red, each with its own Tekrar dene.
            runner.report({**queue.counts(jobs, slots), "current": current,
                           "pending": [photo_file(j["id"]) for j in owed[1:]]})
            started = clock()
            try:
                data = producer.generate(current["prompt"], current["negative"], current["seed"],
                                         current["model"])
            except Exception as exc:
                if runner.stop_requested():
                    # The user's own pause killed this render -- that is not a failure. The job
                    # writes no line, so it stays owed and is done again on resume.
                    return summary("paused")
                if policy.is_frame_fault(exc):
                    # The renderer answered: this one job is what failed, the queue owes the rest
                    # nothing, and the tile turns red where it stands.
                    record.mark(project, fid, kind, name, queue.FAILED, now(), error=str(exc))
                    continue
                attempts += 1
                reason = policy.stop_reason(attempts)
                if reason:
                    # Deliberately no line for the job: it stays owed, so resuming starts from it
                    # rather than leaving a red tile the user has to rescue by hand.
                    return summary("error", error=f"{reason}\n{exc}")
                continue
            rendered = clock()
            filename = store.save(project, name, data)
            # Only after the file exists: the line is what "this layer is here" means.
            record.append(project, {"file": filename, "frame": fid, "layer": kind,
                                    "status": queue.DONE,
                                    "prompt": current["prompt"], "negative": current["negative"],
                                    "seed": current["seed"], "createdAt": now()})
            if log:
                # Two numbers, never one: the render is the GPU's share and the writes are the
                # pipeline's, and speed decisions need to tell them apart.
                log(f"⏱ {filename} · render {rendered - started:.1f} sn"
                    f" · drive {clock() - rendered:.1f} sn")
            # No attempt counter to clear here: the next turn holds a different job, and that is
            # the one place the count resets.

    return job
