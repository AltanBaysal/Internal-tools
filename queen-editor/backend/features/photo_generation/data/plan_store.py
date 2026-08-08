"""PlanStore over DriveStorage -- the only place that knows the plan file's name and shape.

The plan is the queue: what was asked for, in the order it was asked for. It is only ever appended
to. A frame is never taken out of it and never marked -- what became of a frame is the photo
record's answer, and a plan that repeated it would give one truth two writers. That is also why the
whole file is rewritten once per submitted batch rather than once per frame: a Colab machine dying
mid-write would otherwise take the entire queue with it.

A frame carries its number and letter, not a file name: the "<number>_<letter>.png" scheme is
photo_store's to know, and repeating it here would give it a second owner.
"""
import json

FILE = "plan.json"


def _empty():
    return {"negative": "", "frames": []}


class DrivePlanStore:
    def __init__(self, storage):
        self._storage = storage

    def read(self, project):
        """{"negative": <legacy field>, "frames": [...]} -- every frame carrying its own negative.

        The negative used to be one field for the whole plan, because a plan was one run. A live
        queue holds batches submitted with different negatives, so it belongs to the frame now; the
        old top-level field is still read and handed to frames that predate the change.
        """
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return _empty()
        try:
            data = json.loads(raw)
        except ValueError:
            # A half-written or hand-edited plan must not make the project unopenable.
            return _empty()
        if not isinstance(data, dict) or not isinstance(data.get("frames"), list):
            return _empty()
        legacy = data.get("negative")
        legacy = legacy if isinstance(legacy, str) else ""
        frames = []
        for frame in data["frames"]:
            if not isinstance(frame, dict) or not isinstance(frame.get("number"), int):
                continue
            negative = frame.get("negative")
            frames.append({**frame,
                           "negative": negative if isinstance(negative, str) else legacy})
        return {"negative": legacy, "frames": frames}

    def append(self, project, frames):
        """Put frames at the end of the queue.

        frames: [{"number", "letter", "prompt", "negative", "seed"}] in render order.
        """
        self._write(project, self.read(project)["frames"] + frames)

    def max_number(self, project):
        """Highest number this plan reserved, or None when there is no plan to honour."""
        numbers = [frame["number"] for frame in self.read(project)["frames"]]
        return max(numbers) if numbers else None

    def _write(self, project, frames):
        self._storage.write_text(project, FILE, json.dumps({"frames": frames},
                                                           ensure_ascii=False, indent=2))
