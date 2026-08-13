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

def exportable(frames):
    """The frames a video export would take, from the foot of the gallery up.

    The foot is the video's first frame: the gallery's badge counts up from there, and the export
    follows the same reading (design v2's rule, kept).
    """
    return [frame for frame in reversed(frames)
            if frame.get("layers", {}).get(layers.VIDEO)
            and layers.VIDEO not in frame.get("failed", [])]


def export_summary(record, store, plan_store, order_store, seconds, project):
    """`seconds()` answers how long one produced video runs.

    Asked rather than known: the length is the video graph's own setting, and a copy of the number
    here would go on being quoted after the graph moved. Every video is the same length, so one
    answer covers the sequence -- measuring each file would cost a process per video for a number
    nobody disputes.
    """
    # Raises ProjectMissing when there is no such project.
    frames = list_frames(record, store, plan_store, order_store, project)
    videos = exportable(frames)
    # A video whose sound blew up is silent too: what is not there cannot be laid over it.
    silent = [frame for frame in videos
              if not frame.get("layers", {}).get(layers.AUDIO)
              or layers.AUDIO in frame.get("failed", [])]
    return {"videos": len(videos), "seconds": len(videos) * seconds(),
            "silent": len(silent),
            # What the sequence will not hold: every frame with no video, produced or not.
            "withoutVideo": len(frames) - len(videos),
            # Where an export lands is the store's answer: building a path is not the domain's job.
            "folder": store.export_dir(project)}
