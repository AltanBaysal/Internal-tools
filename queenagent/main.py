"""Composition root -- the only place that wires concrete classes together."""
from backend import config
from backend.features.settings.data.file_settings_store import FileSettingsStore
from backend.features.settings.domain.usecases.read_settings import read_settings
from backend.features.settings.presentation.routes import make_settings_bp
from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.data.xai_engine import XaiEngine
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.services.xai.client import XaiClient
from backend.web.app import create_app

store = Store(config.ROOT)
settings_store = FileSettingsStore(store)
# The two features never import each other; binding the key to the engine is this file's job, and
# it is handed as a function so a key saved in Settings takes effect on the next request.
engine = XaiEngine(
    XaiClient(
        lambda: read_settings(settings_store).api_key,
        config.XAI_MODEL,
        config.XAI_BASE_URL,
    )
)
app = create_app(
    blueprints=(
        make_workspace_bp(
            FileProjectStore(store),
            FileChatStore(store),
            FileFileStore(store),
            engine,
            config.XAI_MODEL,
        ),
        make_settings_bp(settings_store),
    ),
)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)
