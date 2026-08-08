from backend.features.projects.data.settings_store import DriveSettingsStore
from backend.services.drive.storage import DriveStorage

EMPTY = {"prompts": "", "negative": "", "variants": None, "model": ""}


def store_at(path):
    return DriveSettingsStore(DriveStorage(str(path)))


def test_reading_a_project_that_never_saved_gives_empty_settings(tmp_path):
    (tmp_path / "düğün").mkdir()
    assert store_at(tmp_path).read("düğün") == EMPTY


def test_write_then_read_round_trips(tmp_path):
    (tmp_path / "düğün").mkdir()
    store = store_at(tmp_path)
    settings = {"prompts": '["kraliçe tahtta"]', "negative": "bulanık", "variants": 4,
                "model": "nova.safetensors"}
    store.write("düğün", settings)
    assert store.read("düğün") == settings


def test_the_prompt_text_is_stored_exactly_as_written(tmp_path):
    (tmp_path / "düğün").mkdir()
    store = store_at(tmp_path)
    typed = '[\n  "kraliçe tahtta",\n]'          # trailing comma and line breaks survive
    store.write("düğün", {"prompts": typed, "negative": "", "variants": 4})
    assert store.read("düğün")["prompts"] == typed


def test_an_unreadable_file_reads_as_empty_settings(tmp_path):
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "settings.json").write_text("{ yarım", encoding="utf-8")
    assert store_at(tmp_path).read("düğün") == EMPTY


def test_fields_of_the_wrong_type_read_as_empty(tmp_path):
    (tmp_path / "düğün").mkdir()
    (tmp_path / "düğün" / "settings.json").write_text(
        '{"prompts": 5, "negative": null, "variants": true}', encoding="utf-8")
    assert store_at(tmp_path).read("düğün") == EMPTY


def test_project_exists_follows_the_folder(tmp_path):
    (tmp_path / "düğün").mkdir()
    store = store_at(tmp_path)
    assert store.project_exists("düğün") is True
    assert store.project_exists("yok") is False
