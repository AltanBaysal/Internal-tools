"""Composition root -- the only place that wires concrete classes together."""
import signal
import sys

from backend import config
from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import (
    FileProjectStore,
    ProjectsUnreadable,
)
from backend.features.workspace.data.live_turns import LiveTurns
from backend.features.workspace.data.model_engine import ModelEngine
from backend.features.workspace.data.old_projects import move_old_projects
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.model.client import ModelClient
from backend.services.store.store import Store
from backend.web.app import create_app

store = Store(config.ROOT)
# Read once, here, and held in memory from now on (Madde 447). A file that cannot be read stops the
# start rather than being taken as empty: the first change would then write an empty list over every
# project the user has.
try:
    projects = FileProjectStore(store)
except ProjectsUnreadable as unreadable:
    raise SystemExit(
        f"QueenAgent did not start. In {config.ROOT}: {unreadable}. Nothing was written to it."
    ) from unreadable
# Madde 448: projects in the layout before 447 move in, once. Goes once 448 is confirmed (BACKLOG).
move_old_projects(store, projects)
# One transport per model since Madde 146, built from the table rather than written out three
# times: a fourth model is then a row in config.py and nothing here.
#
# Where the key comes from is still this file's decision, not the client's -- which is why it is
# handed over as a function even though the value settles once, at startup. `engine_for` is asked
# for each id in turn, so the address and the key a model spends stay its own.
engine = ModelEngine(
    {
        model: ModelClient(
            lambda wiring=config.engine_for(model): wiring[2],
            model,
            config.engine_for(model)[1],
            config.MODEL_IDLE_SECONDS,
        )
        for model in config.MODELS
    },
    default=config.DEFAULT_MODEL,
)
app = create_app(
    blueprints=(
        make_workspace_bp(
            projects,
            # The one holder of projects.json: what they write is listed, and what it lists they read.
            FileChatStore(store, projects),
            FileFileStore(store, projects),
            engine,
            # One for the whole app: two would be two requests unable to find each other's turn.
            LiveTurns(),
        ),
    ),
)

if __name__ == "__main__":
    # The notebook stops the old server with pkill, which is SIGTERM, and Python's own answer to that
    # ends the process without waiting for anything -- the last change still queued for
    # projects.json included. Made an ordinary exit, it waits for that writer like Ctrl+C does.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    app.run(host=config.HOST, port=config.PORT)
