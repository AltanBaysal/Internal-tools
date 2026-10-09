"""HappyEndingStore over DriveStorage -- the only place that knows the switch file's name and shape.

A file of its own (CODE-STANDARD, Separation of concerns): it answers whether the project's videos
end happily, written when the switch is pressed -- not how long they run, which video_length.json
answers on a press of its own. Anything unreadable reads as nothing saved, so a file half-written or
edited by hand never keeps a project from opening.
"""
import json

FILE = "happy_ending.json"


class DriveHappyEndingStore:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def read(self, project):
        """The saved switch as True or False, or None when there is none to read."""
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return None
        try:
            data = json.loads(raw)
        except ValueError:
            return None
        on = data.get("on") if isinstance(data, dict) else None
        return on if isinstance(on, bool) else None

    def write(self, project, on):
        self._storage.write_text(project, FILE, json.dumps({"on": on}))
