"""What an export would write: how many videos, how long they run, and where they would land.

Read from the gallery rather than from disk, so "which frames have a video" has the same answer here
as everywhere else -- a second count would be a second truth, and the video is stitched in exactly
the gallery's order.

The length is not measured. Video duration cannot be chosen in this version: the graph produces a
fixed length, so the total is the count times that length (design v3, madde 86's own example --
22 videos, 1:50).
"""
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.usecases.list_frames import list_frames

# How long one produced video runs. A number rather than a measurement: every video is the same
# length until the graph's length becomes a setting, and opening a process per file to ask would
# cost more than the answer is worth.
VIDEO_SECONDS = 5


def exportable(frames):
    """The frames a video export would take, from the foot of the gallery up.

    The foot is the video's first frame: the gallery's badge counts up from there, and the export
    follows the same reading (design v2's rule, kept).
    """
    return [frame for frame in reversed(frames)
            if frame.get("layers", {}).get(layers.VIDEO)
            and layers.VIDEO not in frame.get("failed", [])]


def export_summary(record, store, plan_store, order_store, project):
    # Raises ProjectMissing when there is no such project.
    videos = exportable(list_frames(record, store, plan_store, order_store, project))
    return {"videos": len(videos), "seconds": len(videos) * VIDEO_SECONDS,
            # Where an export lands is the store's answer: building a path is not the domain's job.
            "folder": store.export_dir(project)}
