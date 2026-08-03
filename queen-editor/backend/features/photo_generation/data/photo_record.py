"""PhotoRecord over DriveStorage -- the only place that knows the record file's name and shape.

This is the gallery's list: one JSON object per line, appended right after the photo itself is
written, never rewritten. Append-only is the point -- a session that dies mid-write loses at most
the line it was adding, where rewriting the whole file could lose every earlier one.
"""
import json

FILE = "photos.jsonl"


class DrivePhotoRecord:
    def __init__(self, storage):
        self._storage = storage

    def append(self, project, entry):
        """entry: {"file", "prompt", "negative", "seed", "createdAt"}."""
        self._storage.append_line(project, FILE, json.dumps(entry, ensure_ascii=False))

    def list(self, project):
        """Every recorded photo, newest first.

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
        rows.reverse()
        return rows
