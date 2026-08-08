"""Put a frame back in line -- the one whose tile is red.

Retrying re-plans nothing: the frame is already in the plan with the prompt, negative and seed it
was submitted under, so putting it back in line is one line in the record. It renders in the plan's
own order.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import file_name
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class FrameMissing(Exception):
    """The plan has no frame under that name."""


def retry_frame(runner, store, record, plan_store, generator, now, project, file, log=None):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    frames = plan_store.read(project)["frames"]
    if not any(file_name(f["number"], f["letter"]) == file for f in frames):
        raise FrameMissing(f"Bu kare planda yok: {file}")
    record.mark(project, file, queue.QUEUED, now())
    run_queue(runner, store, record, plan_store, generator, now, project, log)
