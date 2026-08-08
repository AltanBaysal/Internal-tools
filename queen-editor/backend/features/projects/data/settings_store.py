"""SettingsStore over DriveStorage -- the only place that knows the settings file's name and shape.

The prompt text is kept exactly as it was typed. A parsed list would come back reformatted, and the
panel has to reopen looking the way the user left it.

Nothing here validates: this file's only job is to refill the boxes, so anything unreadable reads as
empty settings rather than making the project impossible to open.
"""
import json

FILE = "settings.json"


def _empty():
    return {"prompts": "", "negative": "", "variants": None, "model": ""}


def _text(value):
    return value if isinstance(value, str) else ""


def _count(value):
    # bool is an int in Python, and True would silently become "1 variant".
    return value if isinstance(value, int) and not isinstance(value, bool) else None


class DriveSettingsStore:
    def __init__(self, storage):
        self._storage = storage

    def project_exists(self, project):
        return self._storage.dir_exists(project)

    def read(self, project):
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return _empty()
        try:
            data = json.loads(raw)
        except ValueError:
            return _empty()
        if not isinstance(data, dict):
            return _empty()
        return {"prompts": _text(data.get("prompts")),
                "negative": _text(data.get("negative")),
                "variants": _count(data.get("variants")),
                # Settings written before models could be chosen have none; empty means the panel
                # shows whatever the renderer lists first.
                "model": _text(data.get("model"))}

    def write(self, project, settings):
        self._storage.write_text(
            project, FILE, json.dumps(settings, ensure_ascii=False, indent=2))
