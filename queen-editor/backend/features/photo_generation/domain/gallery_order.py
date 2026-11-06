"""The gallery's order: the record says what exists, the order file says in what sequence.

Kept as a pure function so the rule is testable without Drive: it can neither invent a frame nor
hide one -- whatever the order file says, the result is always exactly the record's own set.

Keyed by frame identity, not by file name: two frames can share one picture, and a list of file
names could not say which of them it meant.
"""


def keep_unnamed(named, gallery):
    """A dragged sequence, with every frame of `gallery` it does not name put back where it stood.

    named: the identities the drag sends, in its order. gallery: the gallery's whole sequence as it
    stands. A frame the drag leaves out goes directly above the frame that was under it in the
    gallery -- for a copy that arrived after the screen built its list, above its source, which is
    where copy_frame.placed put it (madde 512). One with nothing under it goes at the foot. Walked
    from the foot up, so frames left out side by side keep their own sequence.
    """
    sequence = list(named)
    held = set(sequence)
    under = None
    for fid in reversed(gallery):
        if fid not in held:
            sequence.insert(len(sequence) if under is None else sequence.index(under), fid)
            held.add(fid)
        under = fid
    return sequence


def apply_order(rows, order):
    """rows: frames, newest first. order: stored frame identities. Returns them in gallery order."""
    by_id = {row["id"]: row for row in rows}
    ordered = []
    seen = set()
    for fid in order:
        row = by_id.get(fid)
        if row is not None and fid not in seen:
            seen.add(fid)
            ordered.append(row)
    # A frame the order file has never heard of is new: it belongs on top, and among themselves
    # those keep the record's own newest-first sequence.
    fresh = [row for row in rows if row["id"] not in seen]
    return fresh + ordered
