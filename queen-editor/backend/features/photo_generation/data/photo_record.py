"""PhotoRecord over DriveStorage -- the only place that knows the record file's name and shape.

This is the log of what happened to every layer of every planned frame: one JSON object per line,
appended right after the event itself, never rewritten. Append-only is the point -- a session that
dies mid-write loses at most the line it was adding, where rewriting the whole file could lose every
earlier one. So a photo landing, a video landing, a deletion, a failed render and a frame pulled out
of the queue are all lines; reading folds them and the latest line about a slot wins.

Folded per (frame, layer) rather than per file, because a file can be shared: a copy frame points at
its source's picture, and closing one of them must not close the other.
"""
import json

from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.photo_name import frame_id_of, number_of

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


def _frame_of(row):
    """Which frame the row is about.

    Rows written before frames had identities are one photo each, so the file name without its
    extension is the frame they belong to -- exactly the shape frame_id gives new frames.
    """
    frame = row.get("frame")
    if isinstance(frame, str):
        return frame
    return frame_id_of(row["file"])


def _layer_of(row):
    """Which slot the row is about; a row from before layers existed can only be a photo."""
    layer = row.get("layer")
    return layer if isinstance(layer, str) else layers.PHOTO


class DrivePhotoRecord:
    def __init__(self, storage):
        self._storage = storage

    def append(self, project, entry):
        """entry: {"file", "frame", "layer", "status", …} -- a produced photo also carries prompt,
        negative and seed."""
        self._storage.append_line(project, FILE, json.dumps(entry, ensure_ascii=False))

    def mark(self, project, frame, layer, file, status, at, error=None):
        """Write down an event that produced no layer: a failure, a deletion, a frame pulled out of
        the queue, or a slot put back in line."""
        entry = {"frame": frame, "layer": layer, "file": file, "status": status, "at": at}
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

    def slots(self, project):
        """{frame: {slot: {"status", "file"}}} -- the latest line per (frame, slot) wins."""
        folded = {}
        for row in self._rows(project):
            folded.setdefault(_frame_of(row), {})[_layer_of(row)] = {
                "status": _status_of(row), "file": row["file"]}
        return folded

    def prompts(self, project):
        """{frame: {layer: prompt}} -- what each layer was made from; the latest line wins.

        Read by whoever needs a frame's own words: a copy frame carries them over, and the model
        that writes a video's or a sound's prompt starts from them.
        """
        folded = {}
        for row in self._rows(project):
            prompt = row.get("prompt")
            if isinstance(prompt, str):
                folded.setdefault(_frame_of(row), {})[_layer_of(row)] = prompt
        return folded

    def list(self, project):
        """Every photo that still exists, newest first -- one row per frame, not per file."""
        live = {}
        for row in self._rows(project):
            if _layer_of(row) != layers.PHOTO:
                continue
            frame = _frame_of(row)
            if _status_of(row) == queue.DONE:
                live[frame] = {**row, "frame": frame}
            else:
                live.pop(frame, None)
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
