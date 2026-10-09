"""VideoLengthStore over DriveStorage -- the only place that knows the length file's name and shape.

A file of its own (CODE-STANDARD, Separation of concerns): it is written the moment the length is
chosen and read whenever a video is put in the queue, where settings.json is overwritten by every
photo batch. Anything unreadable reads as nothing saved, so a file half-written or edited by hand
never keeps a project from opening.
"""
import json

FILE = "video_length.json"


class DriveVideoLengthStore:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def read(self, project):
        """The saved length as a whole number, or None when there is none to read."""
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return None
        try:
            data = json.loads(raw)
        except ValueError:
            return None
        seconds = data.get("seconds") if isinstance(data, dict) else None
        # bool is an int in Python, and true would read as a one-second video.
        return seconds if isinstance(seconds, int) and not isinstance(seconds, bool) else None

    def write(self, project, seconds):
        self._storage.write_text(project, FILE, json.dumps({"seconds": seconds}))
