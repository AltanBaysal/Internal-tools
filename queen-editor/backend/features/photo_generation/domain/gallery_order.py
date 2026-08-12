"""The gallery's order: the record says what exists, the order file says in what sequence.

Kept as a pure function so the rule is testable without Drive: it can neither invent a frame nor
hide one -- whatever the order file says, the result is always exactly the record's own set.

Keyed by frame identity, not by file name: two frames can share one picture, and a list of file
names could not say which of them it meant.
"""


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
