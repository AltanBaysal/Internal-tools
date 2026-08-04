"""Produce one frame again -- the one whose tile is red.

The frame comes from the plan, so it is rendered with the prompt and seed it was planned with: a
retry has to be the same frame, not a new one that happens to take its name.
"""
from backend.features.photo_generation.domain.photo_name import file_name
from backend.features.photo_generation.domain.run_loop import make_job
from backend.features.photo_generation.domain.usecases.start_batch import Busy, ProjectMissing


class FrameMissing(Exception):
    """The plan has no frame under that name."""


def retry_frame(runner, store, record, plan_store, generator, now, project, file):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    plan = plan_store.read(project)
    frames = [f for f in plan["frames"] if file_name(f["number"], f["letter"]) == file]
    if not frames:
        raise FrameMissing(f"Bu kare planda yok: {file}")

    job = make_job(runner, store, record, generator, now, project, plan["negative"], frames)
    if not runner.start(project, job):
        raise Busy("Zaten bir üretim sürüyor.")
