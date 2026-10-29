"""Read and change which frames' sound is turned off (madde 510).

The messages are user-facing Turkish; presentation forwards them untouched.
"""
from backend.features.photo_generation.domain import mute
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def get_muted(mutes, project):
    """The identities of the frames whose sound is off."""
    if not mutes.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return mutes.read(project)


def set_muted(mutes, record, project, frame, on):
    """Turn the frame's sound off or on, and answer with the new list.

    The value is refused before the project is looked for: the cheap refusal comes first. The project
    must already exist -- every folder under the root counts as one. Turning off asks the record
    whether the frame holds a sound, since only a sound can be turned off; turning on is always
    taken, so a mark left on a frame whose sound has gone can still be taken off.
    """
    mute.check(on)
    if not mutes.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    if on:
        mute.require_sound(record.slots(project), frame)
    return mutes.put(project, frame, on)
