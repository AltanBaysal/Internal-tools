"""The gallery's order: the record says what exists, the order file says in what sequence.

Kept as a pure function so the rule is testable without Drive: it can neither invent a photo nor
hide one -- whatever the order file says, the result is always exactly the record's own set.
"""


def apply_order(rows, order):
    """rows: record rows, newest first. order: stored file names. Returns rows in gallery order."""
    by_file = {row["file"]: row for row in rows}
    ordered = []
    seen = set()
    for file in order:
        row = by_file.get(file)
        if row is not None and file not in seen:
            seen.add(file)
            ordered.append(row)
    # A photo the order file has never heard of is new: it belongs on top, and among themselves
    # those keep the record's own newest-first sequence.
    fresh = [row for row in rows if row["file"] not in seen]
    return fresh + ordered
