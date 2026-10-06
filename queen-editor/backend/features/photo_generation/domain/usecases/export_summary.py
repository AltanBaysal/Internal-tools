"""What an export would write: how many videos, how long they run, and where they would land.

Read from the gallery rather than from disk, so "which frames have a video" has the same answer here
as everywhere else -- a second count would be a second truth, and the video is stitched in exactly
the gallery's order.

The length is not measured: each video's line says how long it runs -- its producer's answer for
the video it made (madde 423). A line written before that says nothing, and its video ran as long
as its graph says. Measuring each file would cost a process and a Drive read per video, every time
the screen asks.
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
    """`seconds()` answers how long a video made at its graph's own length runs -- what a line that
    says no length is counted at.

    Asked rather than known: the length is the video graph's own setting, and a copy of the number
    here would go on being quoted after the graph moved. It is this session's graph, and such a
    line -- written before madde 423 -- does not say which model made its video, so one another
    session's model made is counted at this one's.
    """
    # Raises ProjectMissing when there is no such project.
    frames = list_frames(record, store, plan_store, order_store, project)
    videos = exportable(frames)
    graph = seconds()
    # A video whose sound blew up is silent too: what is not there cannot be laid over it.
    silent = [frame for frame in videos
              if not frame.get("layers", {}).get(layers.AUDIO)
              or layers.AUDIO in frame.get("failed", [])]
    return {"videos": len(videos),
            "seconds": sum(frame["lengths"].get(layers.VIDEO, graph) for frame in videos),
            "silent": len(silent),
            # What the sequence will not hold: every frame with no video, produced or not.
            "withoutVideo": len(frames) - len(videos),
            # Where an export lands is the store's answer: building a path is not the domain's job.
            "folder": store.export_dir(project)}
