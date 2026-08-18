"""Save the settings and hand back what was saved."""
from backend.features.settings.domain.settings import Settings


def save_settings(settings_store, api_key):
    # Trimmed: a key pasted out of a browser brings a newline with it more often than not, and a
    # trailing space would make every request fail with a puzzling 401.
    saved = Settings(api_key=str(api_key or "").strip())
    settings_store.replace(saved)
    return saved
