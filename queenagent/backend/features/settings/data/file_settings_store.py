"""FileSettingsStore -- the only place that knows the settings.json schema.

The file sits at the root, beside the project folders. It can never be mistaken for one: the project
list reads only directories that carry a project.json.
"""
import json

from backend.features.settings.domain.settings import Settings

SETTINGS_FILE = "settings.json"


class FileSettingsStore:
    def __init__(self, store):
        self._store = store

    def get(self):
        if not self._store.exists(SETTINGS_FILE):
            return Settings()
        raw = json.loads(self._store.read_text(SETTINGS_FILE))
        return Settings(api_key=raw.get("apiKey", ""))

    def replace(self, settings):
        self._store.write_text(
            SETTINGS_FILE,
            json.dumps({"apiKey": settings.api_key}, ensure_ascii=False, indent=2),
        )
