"""Composition root -- the only place that wires concrete classes together."""
from backend import config
from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.data.memory_permissions import MemoryPermissions
from backend.features.workspace.data.memory_stops import MemoryStops
from backend.features.workspace.data.xai_engine import XaiEngine
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.services.xai.client import XaiClient
from backend.web.app import create_app

store = Store(config.ROOT)
# One transport per model since Madde 146, built from the table rather than written out three
# times: a fourth model is then a row in config.py and nothing here.
#
# Where the key comes from is still this file's decision, not the client's -- which is why it is
# handed over as a function even though the value settles once, at startup. `engine_for` is asked
# for each id in turn, so the address and the key a model spends stay its own.
engine = XaiEngine(
    {
        model: XaiClient(
            lambda wiring=config.engine_for(model): wiring[2],
            model,
            config.engine_for(model)[1],
        )
        for model in config.MODELS
    },
    default=config.DEFAULT_MODEL,
)
app = create_app(
    blueprints=(
        make_workspace_bp(
            FileProjectStore(store),
            FileChatStore(store),
            FileFileStore(store),
            engine,
            # One registry each for the whole app: two of either would be two requests unable to
            # find each other.
            MemoryStops(),
            MemoryPermissions(),
        ),
    ),
)

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)
