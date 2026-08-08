"""PhotoRecord over DriveStorage -- the only place that knows the record file's name and shape.

This is the log of what happened to every planned frame: one JSON object per line, appended right
after the event itself, never rewritten. Append-only is the point -- a session that dies mid-write
loses at most the line it was adding, where rewriting the whole file could lose every earlier one.
So a photo landing, a deletion, a failed render and a frame pulled out of the queue are all lines;
reading folds them and the latest line about a file wins.
"""
import json

from backend.features.photo_generation.domain import queue
from backend.features.photo_generation.domain.photo_name import number_of

FILE = "photos.jsonl"


def _status_of(row):
    """A row's status, including rows written before the field existed.

    Those older rows are exactly two kinds: a photo landing (prompt + createdAt) and a deletion
    (deletedAt). Nothing needs migrating -- the projects already on Drive keep reading.
    """
    status = row.get("status")
    if isinstance(status, str):
        return status
    return queue.DELETED if row.get("deletedAt") else queue.DONE


class DrivePhotoRecord:
    def __init__(self, storage):
        self._storage = storage

    def append(self, project, entry):
        """entry: {"file", "status", …} -- a produced photo also carries prompt, negative, seed."""
        self._storage.append_line(project, FILE, json.dumps(entry, ensure_ascii=False))

    def mark(self, project, file, status, at, error=None):
        """Write down an event that produced no photo: a failure, a deletion, a frame pulled out of
        the queue, or a frame put back in line."""
        entry = {"file": file, "status": status, "at": at}
        if error is not None:
            # The server's own words, verbatim -- never a guessed cause.
            entry["error"] = error
        self.append(project, entry)

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

    def statuses(self, project):
        """{file name: latest status} -- the fold every "what happened to this frame" question
        reads, the queue rule included."""
        return {row["file"]: _status_of(row) for row in self._rows(project)}

    def list(self, project):
        """Every photo that still exists, newest first."""
        live = {}
        for row in self._rows(project):
            if _status_of(row) == queue.DONE:
                live[row["file"]] = row
            else:
                live.pop(row["file"], None)
        return list(reversed(list(live.values())))

    def max_number(self, project):
        """Highest number the record has ever seen, whatever became of the frame; None when empty.

        Every line counts -- deleted, failed and removed included. Their numbers have to stay
        claimed, or a new photo would take the name of an old one: same name, a different prompt,
        and browsers still holding the old bytes under an immutable cache header.
        """
        numbers = [n for n in (number_of(row["file"]) for row in self._rows(project))
                   if n is not None]
        return max(numbers) if numbers else None
