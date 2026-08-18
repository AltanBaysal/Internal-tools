from backend.features.settings.data.file_settings_store import FileSettingsStore
from backend.features.settings.domain.usecases.read_settings import read_settings
from backend.features.settings.domain.usecases.save_settings import save_settings
from backend.services.store.store import Store


def _settings(tmp_path):
    return FileSettingsStore(Store(str(tmp_path)))


def test_before_anything_is_saved_the_key_is_empty(tmp_path):
    # The app starts without one: only asking for an answer fails.
    assert read_settings(_settings(tmp_path)).api_key == ""


def test_a_saved_key_is_read_back(tmp_path):
    settings = _settings(tmp_path)
    save_settings(settings, api_key="xai-abc123")
    assert read_settings(settings).api_key == "xai-abc123"


def test_it_lives_beside_the_projects_under_one_name(tmp_path):
    save_settings(_settings(tmp_path), api_key="xai-abc123")
    assert (tmp_path / "settings.json").exists()


def test_an_empty_key_can_be_saved(tmp_path):
    # This is how a key is removed; there is no second road for it.
    settings = _settings(tmp_path)
    save_settings(settings, api_key="xai-abc123")
    save_settings(settings, api_key="")
    assert read_settings(settings).api_key == ""


def test_saving_hands_back_what_was_saved(tmp_path):
    assert save_settings(_settings(tmp_path), api_key="xai-abc123").api_key == "xai-abc123"
