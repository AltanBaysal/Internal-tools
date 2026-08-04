"""PlanStore over DriveStorage -- the only place that knows the plan file's name and shape.

The plan is the queue a run works through, not a log of it: it is written once when a batch is
submitted and replaced by the next batch's plan. What a frame actually produced belongs to the
photo record.

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

    def write(self, project, negative, frames):
        """frames: [{"number", "letter", "prompt", "seed"}] in the order they will render."""
        self._storage.write_text(project, FILE, json.dumps(
            {"negative": negative, "frames": frames}, ensure_ascii=False, indent=2))

    def read(self, project):
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
        negative = data.get("negative")
        return {"negative": negative if isinstance(negative, str) else "",
                "frames": [f for f in data["frames"]
                           if isinstance(f, dict) and isinstance(f.get("number"), int)]}

    def clear(self, project):
        """Forget the queue. Written as an empty plan rather than deleted: a project folder that
        once had a plan keeps a readable one, and "no frames left" is a plain answer to read."""
        self.write(project, "", [])

    def max_number(self, project):
        """Highest number this plan reserved, or None when there is no plan to honour."""
        numbers = [frame["number"] for frame in self.read(project)["frames"]]
        return max(numbers) if numbers else None
