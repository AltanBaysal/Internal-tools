"""What the queue still owes and what blew up, read from Drive rather than from memory.

This is how a half-finished run survives a dead session: the plan and the record are both on Drive
and the queue is one minus the other -- the same rule the worker runs on, so the screen and the
worker can never disagree. Failures come from the same place, which is why a red frame is still red
after the server restarts.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import file_name
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def get_queue(record, store, plan_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    frames = plan_store.read(project)["frames"]
    statuses = record.statuses(project)
    return {"pending": [file_name(f["number"], f["letter"])
                        for f in queue.open_frames(frames, statuses)],
            "failed": queue.counts(frames, statuses)["failures"],
            "total": len(frames)}
