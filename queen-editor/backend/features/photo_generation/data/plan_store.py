"""PlanStore over Storage -- the only place that knows the plan file's name and shape.

The plan is the queue: what work was asked for, in the order it was asked for. It is only ever
appended to. A job is never taken out of it and never marked -- what became of a job is the photo
record's answer, and a plan that repeated it would give one truth two writers. That is also why the
whole file is rewritten once per submitted batch rather than once per job: a Colab machine dying
mid-write would otherwise take the entire queue with it.

A frame carries its identity, not a file name: which file a layer lands in is the naming scheme's
answer, and repeating it here would give it a second owner.

Rewriting the whole file means an append reads it first, so two at once would each write back the
plan they read and the later would drop the earlier's jobs. So each project has a lock here, held by
every append (madde 512). It is more than the plan's: it is the project's write gate for the doors
that name or close frames, which read the plan, the record and the order and write them back
together, and hold it from the first read to the last write (PlanStore.held says why). The doors
that queue work hold it on to the worker's claim, and a rename takes both names' around the
folder's move (madde 522), so neither a door's writes nor its claim fall on both sides of a move.
The loop writes the record outside it. One process serves every press, so a lock in memory is
enough.
"""
import json
import threading
from contextlib import contextmanager

from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.photo_name import legacy_frame_id

FILE = "plan.json"


def _empty():
    return {"negative": "", "frames": []}


def _parse(raw):
    """The plan file's object; an empty plan when there is no file. A ValueError when the text is
    not a plan this store wrote."""
    if raw is None:
        return {"frames": []}
    data = json.loads(raw)
    if not isinstance(data, dict) or not isinstance(data.get("frames"), list):
        raise ValueError('"frames" listesi yok')
    return data


def _plan(data):
    """{"negative": <legacy field>, "frames": [...]} -- every frame filled in from what it predates.

    The negative used to be one field for the whole plan, because a plan was one run. A live queue
    holds batches submitted with different negatives, so it belongs to the frame now; the old
    top-level field is still read and handed to frames that predate the change.
    """
    legacy = data.get("negative")
    legacy = legacy if isinstance(legacy, str) else ""
    frames = []
    for frame in data["frames"]:
        if not isinstance(frame, dict) or not isinstance(frame.get("number"), int):
            continue
        negative = frame.get("negative")
        model = frame.get("model")
        lora = frame.get("lora")
        identity = frame.get("id")
        kind = frame.get("type")
        # A frame planned before models could be chosen carries none, and empty means "the graph's
        # own checkpoint" -- so those frames render exactly as they always did. The lora is the
        # same one level down: empty is a frame that named none, and gets the default. One planned
        # before identities were written down keeps the one it was born with, or the gallery order
        # pointing at it would stop finding it. One planned before the queue knew types can only be
        # a photo job, because that was the only kind there was.
        frames.append({**frame,
                       "id": identity if isinstance(identity, str)
                       else legacy_frame_id(frame["number"], frame.get("letter", "a")),
                       "type": kind if isinstance(kind, str) else layers.PHOTO,
                       "negative": negative if isinstance(negative, str) else legacy,
                       "model": model if isinstance(model, str) else "",
                       "lora": lora if isinstance(lora, str) else ""})
    return {"negative": legacy, "frames": frames}


class DrivePlanStore:
    def __init__(self, storage):
        self._storage = storage
        # One per project name, made on its first hold: a press on one project never waits for
        # another's.
        self._locks = {}
        self._made = threading.Lock()

    @contextmanager
    def held(self, project):
        """The project's write gate: no other append, and no other door that names or closes
        frames, gets in for as long as the caller holds it.

        Re-entrant: a door that holds it appends inside it.
        """
        with self._made:
            lock = self._locks.setdefault(project, threading.RLock())
        with lock:
            yield

    def read(self, project):
        """The queue as stored; see _plan for its shape."""
        try:
            return _plan(_parse(self._storage.read_text(project, FILE)))
        except ValueError:
            # A half-written or hand-edited plan must not make the project unopenable.
            return _empty()

    def append(self, project, frames):
        """Put frames at the end of the queue.

        frames: [{"id", "number", "variant", "prompt", "negative", "seed", "model", "lora"}] in
        render order; a photo's and a pool card's also carry "orientation" (madde 476). A line
        without one is left as it is: the domain reads it as the portrait it was planned in
        (orientation.of).

        Strict where read is lenient: a plan that cannot be read, taken as empty and written back,
        would be the new frames alone -- every frame queued before them gone. So the append stops
        with the reason, and the file stays as it is.
        """
        with self.held(project):
            try:
                queued = _plan(_parse(self._storage.read_text(project, FILE)))
            except ValueError as exc:
                raise OSError(f"{project}/{FILE} okunamıyor, üstüne yazılmadı: {exc}") from exc
            self._write(project, queued["frames"] + frames)

    def max_number(self, project):
        """Highest number this plan reserved, or None when there is no plan to honour."""
        numbers = [frame["number"] for frame in self.read(project)["frames"]]
        return max(numbers) if numbers else None

    def _write(self, project, frames):
        self._storage.write_text(project, FILE, json.dumps({"frames": frames},
                                                           ensure_ascii=False, indent=2))
