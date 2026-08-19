from backend.features.settings.data.file_settings_store import FileSettingsStore
from backend.features.settings.presentation.routes import make_settings_bp
from backend.services.store.store import Store
from backend.web.app import create_app


def _client(tmp_path):
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(make_settings_bp(FileSettingsStore(Store(str(tmp_path)))),),
    )
    return app.test_client()


def test_with_nothing_saved_the_key_is_empty(tmp_path):
    resp = _client(tmp_path).get("/api/settings")
    assert resp.status_code == 200
    assert resp.get_json() == {"apiKey": ""}


def test_the_key_is_returned_as_it_was_typed(tmp_path):
    # Plain text, the user's own decision: this is their machine and their key.
    client = _client(tmp_path)
    client.patch("/api/settings", json={"apiKey": "xai-abc123"})
    assert client.get("/api/settings").get_json() == {"apiKey": "xai-abc123"}


def test_saving_answers_with_what_was_saved(tmp_path):
    resp = _client(tmp_path).patch("/api/settings", json={"apiKey": "xai-abc123"})
    assert resp.status_code == 200
    assert resp.get_json() == {"apiKey": "xai-abc123"}


def test_an_empty_key_is_a_legitimate_save(tmp_path):
    client = _client(tmp_path)
    client.patch("/api/settings", json={"apiKey": "xai-abc123"})
    assert client.patch("/api/settings", json={"apiKey": ""}).status_code == 200
    assert client.get("/api/settings").get_json() == {"apiKey": ""}


def test_settings_carry_nothing_else(tmp_path):
    # The same door the chat's PATCH keeps: what a settings file holds is decided here, not by
    # whatever the browser happens to send.
    resp = _client(tmp_path).patch("/api/settings", json={"theme": "dark"})
    assert resp.status_code == 400
    assert "apiKey" in resp.get_json()["error"]
