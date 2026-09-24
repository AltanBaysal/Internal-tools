"""ReferenceSettingsStore over DriveStorage -- the only place that knows Referanstan's record file.

settings_store's twin. The photo panel's file is written when a photo batch is sent and this one
when a reference production is, so they never share a file (CODE-STANDARD, Separation of concerns).
Like that one it keeps the prompt text exactly as typed, and reads anything unreadable as empty:
its only job is to refill the boxes.
"""
import json

FILE = "reference_settings.json"


def _empty():
    return {"prompts": "", "variants": None}


def _text(value):
    return value if isinstance(value, str) else ""


def _count(value):
    # bool is an int in Python, and True would silently become "1 variant".
    return value if isinstance(value, int) and not isinstance(value, bool) else None


class DriveReferenceSettingsStore:
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
        return {"prompts": _text(data.get("prompts")), "variants": _count(data.get("variants"))}

    def write(self, project, settings):
        self._storage.write_text(
            project, FILE, json.dumps(settings, ensure_ascii=False, indent=2))
