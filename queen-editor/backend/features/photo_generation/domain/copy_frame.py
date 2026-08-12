"""What a new frame in an existing prompt's family is called.

A copy frame keeps its source's prompt number and takes the next variant, so its name still says
what produced the picture (design v3, madde 97). Written apart from the use case that makes copies
because "yeniden üret" asks the same question about a different act.
"""
from backend.features.photo_generation.domain.photo_name import frame_id, number_of, variant_of


def next_id(ids, number):
    """The identity a new frame in `number`'s family takes; `ids` is every identity in the project.

    One past the highest variant ever used, never a gap: a gap belongs to a frame that was deleted,
    and reusing its name would bind one name to two different pictures -- with browsers still
    holding the old bytes under an immutable cache header. The same rule numbers work under
    (start_batch.next_number), for the same reason.
    """
    used = [variant_of(fid) for fid in ids if number_of(fid) == number]
    used = [variant for variant in used if variant is not None]
    return frame_id(number, max(used) + 1 if used else 0)
