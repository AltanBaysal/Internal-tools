"""Composition root -- the only place that wires concrete classes together."""
from backend import config
from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.data.xai_engine import XaiEngine
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.services.xai.client import XaiClient
from backend.web.app import create_app

store = Store(config.ROOT)
engine = XaiEngine(XaiClient(config.XAI_API_KEY, config.XAI_MODEL, config.XAI_BASE_URL))
app = create_app(
    blueprints=(make_workspace_bp(FileProjectStore(store), FileChatStore(store), engine),),
)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)
