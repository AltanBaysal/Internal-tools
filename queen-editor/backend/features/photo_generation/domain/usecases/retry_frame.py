"""Put a frame back in line -- the one whose tile is red.

Retrying re-plans nothing: the frame is already in the plan with the prompt, negative and seed it
was submitted under, so putting it back in line is one line in the record. It renders where the
gallery puts it, behind the jobs that have never had a turn. The one exception is an H3 video whose
project's length or Mutlu son has moved since it was queued: it goes back the way the project is set
now, so its line is written again that way (madde 422, 426).

What goes back is the layer that blew up, onto the frame it blew up on. That is the one exception to
"üret = ekle" (design v3, madde 68): every other production adds a frame, while a retry rescues the
one the user is looking at -- producing the missing layer on a copy would leave that frame red.
"""
from backend.features.photo_generation.domain import layers, queue, video_settings
from backend.features.photo_generation.domain.photo_name import photo_file
from backend.features.photo_generation.domain.usecases.run_queue import run_queue
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class FrameMissing(Exception):
    """The plan has no frame under that name."""


def retry_frame(runner, store, record, plan_store, producers, now, project, fid, log=None,
                order_store=None, writers=None, stills=None, references=None, length=None,
                ending=None):
    """`length` answers how long the project's videos run now, and `ending` whether they end
    happily: a red video goes back that way (madde 422, 426). None leaves its line as it is."""
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    frames = plan_store.read(project)["frames"]
    target = next((f for f in frames if f["id"] == fid), None)
    if target is None:
        raise FrameMissing(f"Bu kare planda yok: {fid}")
    cells = record.slots(project).get(fid, {})
    red = [(layer, cell) for layer, cell in cells.items() if cell["status"] == queue.FAILED]
    # Before the red lines are put back, so a loop already running never takes the video the way it
    # is leaving.
    if any(layer == layers.VIDEO for layer, _cell in red):
        video_settings.as_set_now(plan_store, project, [fid], length, ending)
    for layer, cell in red:
        # The layer's own file, not the frame's photo: what goes back in line is the render that
        # blew up.
        record.mark(project, fid, layer, cell["file"], queue.QUEUED, now())
    if not red:
        # Nothing red: the frame is asking for a photo it no longer has (a deleted one), which is
        # what retry meant before a frame had layers.
        record.mark(project, fid, layers.PHOTO, photo_file(fid), queue.QUEUED, now())
    run_queue(runner, store, record, plan_store, producers, now, project, log,
              order_store=order_store, writers=writers, stills=stills,
              references=references)
