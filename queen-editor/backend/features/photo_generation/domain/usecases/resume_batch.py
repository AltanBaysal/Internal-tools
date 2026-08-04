"""Carry on with the frames a paused run never got to.

What is left is not kept in a queue of its own: it is the plan minus what the record shows was
produced. Two places holding "what remains" would be two chances to disagree, and the plan is
already on Drive, so a resumed run needs nothing the session had to remember.
"""
from backend.features.photo_generation.domain.photo_name import file_name
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.usecases.start_batch import Busy, ProjectMissing


class NothingToResume(Exception):
    """The plan has no frame left to produce."""


def remaining_frames(plan_frames, produced):
    """Plan frames whose photo is not in the record, in the plan's own order."""
    return [frame for frame in plan_frames
            if file_name(frame["number"], frame["letter"]) not in produced]


def resume_batch(runner, store, record, plan_store, generator, now, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    plan = plan_store.read(project)
    produced = {row["file"] for row in record.list(project)}
    frames = remaining_frames(plan["frames"], produced)
    if not frames:
        raise NothingToResume("Devam edilecek kare yok.")

    job = make_job(runner, store, record, generator, now, project, plan["negative"], frames)
    if not runner.start(project, job):
        raise Busy("Zaten bir üretim sürüyor.")
