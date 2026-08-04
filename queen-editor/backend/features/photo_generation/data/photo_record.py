"""PhotoRecord over DriveStorage -- the only place that knows the record file's name and shape.

This is the gallery's log: one JSON object per line, appended right after the photo itself is
written, never rewritten. Append-only is the point -- a session that dies mid-write loses at most
the line it was adding, where rewriting the whole file could lose every earlier one. Deleting a
photo therefore appends a deletion row instead of removing anything, and reading folds the log.
"""
import json

from backend.features.photo_generation.domain.photo_name import number_of

FILE = "photos.jsonl"


class DrivePhotoRecord:
    def __init__(self, storage):
        self._storage = storage

    def append(self, project, entry):
        """entry: {"file", "prompt", "negative", "seed", "createdAt"}."""
        self._storage.append_line(project, FILE, json.dumps(entry, ensure_ascii=False))

    def mark_deleted(self, project, file, at):
        """Write down that a photo is gone, without touching the rows already there."""
        self.append(project, {"file": file, "deletedAt": at})

    def _rows(self, project):
        """Every readable row, in the order it was written.

        A line that will not parse is skipped rather than raised on: the last one can be
        half-written after a session death, and one bad line must not hide the photos before it.
        """
        rows = []
        for line in self._storage.read_lines(project, FILE):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict) and isinstance(row.get("file"), str):
                rows.append(row)
        return rows

    def list(self, project):
        """Every photo that still exists, newest first."""
        live = {}
        for row in self._rows(project):
            if row.get("deletedAt"):
                live.pop(row["file"], None)
            else:
                live[row["file"]] = row
        return list(reversed(list(live.values())))

    def max_number(self, project):
        """Highest number the record has ever seen, deleted photos included; None when empty.

        Deleted rows still count: their number has to stay claimed, or a new photo would take the
        name of a deleted one -- same name, a different prompt, and browsers still holding the old
        bytes under an immutable cache header.
        """
        numbers = [n for n in (number_of(row["file"]) for row in self._rows(project))
                   if n is not None]
        return max(numbers) if numbers else None
