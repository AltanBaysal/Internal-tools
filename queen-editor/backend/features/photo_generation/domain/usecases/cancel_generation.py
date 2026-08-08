"""Throw away what is left of a paused queue.

The photos already produced are untouched -- clearing the queue ends what is owed, it does not undo
work. Every frame still owed gets a "removed" line, and that line is also what keeps its number
dead: the record counts every name it has ever seen, and a reused name would hand a browser holding
the old bytes under an immutable cache header the wrong image.

Refused while the queue flows, so the frame being rendered right now -- which has no line yet and
therefore still reads as owed -- can never be marked removed underneath the worker.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import file_name
from backend.features.photo_generation.domain.usecases.start_batch import Busy, ProjectMissing


def cancel_generation(runner, store, record, plan_store, now, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    if runner.status().get("status") == "running":
        raise Busy("Üretim sürüyor — önce durdur.")
    frames = plan_store.read(project)["frames"]
    for frame in queue.open_frames(frames, record.statuses(project)):
        record.mark(project, file_name(frame["number"], frame["letter"]), queue.REMOVED, now())
    runner.reset()
