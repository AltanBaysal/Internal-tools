"""Throw away what is left of a paused run.

The photos already produced are untouched -- cancelling ends the queue, it does not undo work.

The plan is cleared, which also releases the numbers it had reserved. That is safe precisely
because nothing can resume it any more: those frames were never written to disk and never entered
the record, so no name was ever bound to a prompt. Numbers of photos that DID land stay claimed --
the record remembers them (see start_batch.next_number).
"""
from backend.features.photo_generation.domain.usecases.start_batch import Busy, ProjectMissing


def cancel_generation(runner, store, plan_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    if runner.status().get("status") == "running":
        raise Busy("Üretim sürüyor — önce durdur.")
    plan_store.clear(project)
    runner.reset()
