"""What a run still owes, read from Drive rather than from memory.

This is how a half-finished run survives a dead session: the plan and the record are both on Drive,
and "what is left" is one minus the other -- the same rule resume_batch works from, so the screen
and the worker can never disagree about what remains.
"""
from backend.features.photo_generation.domain.photo_name import file_name
from backend.features.photo_generation.domain.usecases.resume_batch import remaining_frames
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def get_queue(record, store, plan_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    frames = plan_store.read(project)["frames"]
    produced = {row["file"] for row in record.list(project)}
    pending = remaining_frames(frames, produced)
    return {"pending": [file_name(f["number"], f["letter"]) for f in pending],
            "total": len(frames)}
