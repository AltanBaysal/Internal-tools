"""Composition root -- the only place that wires concrete classes together."""
from backend import config
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app

app = create_app(blueprints=(make_workspace_bp(FileProjectStore(Store(config.ROOT))),))

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)
