"""PhotoRecord over DriveStorage -- the only place that knows the record file's name and shape.

This is the log of what happened to every layer of every planned frame: one JSON object per line,
appended right after the event itself, never rewritten. Append-only is the point -- a session that
dies mid-write loses at most the line it was adding, where rewriting the whole file could lose every
earlier one. So a photo landing, a video landing, a deletion, a failed render, a frame pulled out of
the queue and a prompt written for a layer still owed are all lines; reading folds them and the
latest line about a slot wins.

Folded per (frame, layer) rather than per file, because a file can be shared: a copy frame points at
its source's picture, and closing one of them must not close the other.
"""
import json

from backend.features.photo_generation.data.file_cache import FileCache
from backend.features.photo_generation.domain import layers, queue
from backend.features.photo_generation.domain.photo_name import frame_id_of, number_of

FILE = "photos.jsonl"

# A line saying a layer's prompt was written (madde 403). Nothing became of the layer: it is exactly
# as owed as it was, so the status fold passes over the line.
WRITTEN = "written"


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


def _parse(lines):
    """Every readable row, in the order it was written.

    A line that will not parse is skipped rather than raised on: the last one can be half-written
    after a session death, and one bad line must not hide the photos before it.
    """
    rows = []
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and isinstance(row.get("file"), str):
            rows.append(row)
    return rows


class DrivePhotoRecord:
    def __init__(self, storage):
        self._storage = storage
        # Three of this class's answers come from the same file, and the gallery asks for all
        # three on every poll. Parsed once, kept until the file itself changes.
        self._cache = FileCache(storage)

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

    def prompt_written(self, project, frame, layer, file, prompt, at):
        """Write down the prompt a model wrote for a layer still owed -- the words it will be made
        with (madde 403). `file` is the layer's own name, as on every other line about it."""
        self.append(project, {"frame": frame, "layer": layer, "file": file, "status": WRITTEN,
                              "prompt": prompt, "at": at})

    def _rows(self, project):
        """Every readable row, in the order it was written. Read from disk only once per change."""
        return self._cache.parsed(project, FILE, _parse)

    def slots(self, project):
        """{frame: {slot: {"status", "file"[, "error"][, "mode"][, "endsOn"][, "renderSeconds"]}}}
        -- the latest line per (frame, slot) wins.

        A failure line also carries why: the renderer's own sentence, which the detail page prints
        under the red frame. A produced video's line carries the mode it was made in, and the
        picture it arrived at when it arrived at one. A produced layer's line says how many seconds
        the model worked on it. None of the four is on every line, so none of those keys is always
        there.

        A written prompt's line is passed over: a job never written about has to stay one, and the
        queue tells it apart from a job put back in line by exactly that.
        """
        folded = {}
        for row in self._rows(project):
            if _status_of(row) == WRITTEN:
                continue
            cell = {"status": _status_of(row), "file": row["file"]}
            if isinstance(row.get("error"), str):
                cell["error"] = row["error"]
            if isinstance(row.get("mode"), str):
                # Only a produced video's line names one, and the lines already on Drive name none
                # -- so the key is there only when the line had it.
                cell["mode"] = row["mode"]
            if isinstance(row.get("endsOn"), str):
                cell["endsOn"] = row["endsOn"]
            if isinstance(row.get("renderSeconds"), (int, float)):
                # Only a layer produced since madde 405 says how long it took; nothing is filled in
                # for the lines before it.
                cell["renderSeconds"] = row["renderSeconds"]
            folded.setdefault(_frame_of(row), {})[_layer_of(row)] = cell
        return folded

    def prompts(self, project):
        """{frame: {layer: prompt}} -- what each layer was made from; the latest line wins. A layer
        still owed says the prompt written for it, the one it will be made with (madde 403).

        Read by whoever needs a frame's own words: a copy frame carries them over, the detail page
        shows them, and the model that writes a video's or a sound's prompt starts from them.
        """
        folded = {}
        for row in self._rows(project):
            prompt = row.get("prompt")
            if isinstance(prompt, str):
                folded.setdefault(_frame_of(row), {})[_layer_of(row)] = prompt
        return folded

    def written_prompts(self, project):
        """{frame: {layer: prompt}} -- the prompt a model wrote for a layer still owed.

        It holds until the next line about that slot: the layer landing (its own row carries the
        prompt from then on), blowing up, being pulled out, deleted, or put back in line -- a layer
        queued again is written for again.
        """
        latest = {}
        for row in self._rows(project):
            latest[(_frame_of(row), _layer_of(row))] = (
                row.get("prompt") if _status_of(row) == WRITTEN else None)
        folded = {}
        for (frame, layer), prompt in latest.items():
            if isinstance(prompt, str):
                folded.setdefault(frame, {})[layer] = prompt
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
