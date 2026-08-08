"""The project in one file: where its photos live, and which prompt made each one, in video order.

The list comes from list_frames rather than from the record directly, so "which frames exist and in
what order" keeps exactly one answer -- an export that disagreed with the gallery would be a second
truth, and the video is stitched from this order.

Two things separate the file from the gallery. It is the gallery **reversed**: the badge counts up
from the bottom, and the bottom frame is the video's first. And it holds only frames that became
photos -- a pending frame has no file to stitch.
"""
from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.usecases.list_frames import list_frames


def export_project(record, store, plan_store, order_store, project):
    frames = list_frames(record, store, plan_store, order_store, project)
    return {
        "folder": store.photo_dir(project),
        # Only what the next tool needs: a name and the prompt behind it. The rest of the trace
        # (negative, seed, time) stays in the record.
        "photos": [{"file": frame["file"], "prompt": frame.get("prompt", "")}
                   for frame in reversed(frames) if frame["status"] == queue.DONE],
    }
