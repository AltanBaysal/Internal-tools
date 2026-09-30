"""A frame's scenario: what QueenAgent's list says happens in the prompt's frames (madde 397).

Found by the prompt's number rather than written on each frame. Every card holding the prompt's
picture carries that number -- a video's variant, a twin, a card whose photo was deleted
(photo_name._parts) -- so one scene answers for the family without being copied onto each of them.
Two readers ask: the gallery, which shows it, and the queue, which hands it to the prompt writer
(madde 400).
"""
from backend.features.photo_generation.domain.photo_name import number_of


def by_number(planned):
    """{prompt number: scene}, read off the plan lines that carry one."""
    return {frame["number"]: frame["scene"] for frame in planned if frame.get("scene")}


def of(found, fid):
    """The frame's scene out of by_number's answer; empty for a frame that has none."""
    return found.get(number_of(fid), "")
