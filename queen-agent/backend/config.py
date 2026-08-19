"""Runtime configuration -- the single place for paths, ports and engine settings."""
import os

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Vite writes the built frontend here; Flask serves it (see web/app.py).
DIST_DIR = os.path.join(os.path.dirname(_BACKEND_DIR), "frontend", "dist")

HOST = "127.0.0.1"
PORT = 8100  # queen-editor owns 8000 and both can run on this machine at the same time

# Every project is a folder under this root. It lives outside the repo so user data never lands in
# the source tree and `git status` never sees it.
ROOT = os.environ.get("QUEENAGENT_ROOT", os.path.join(os.path.expanduser("~"), "QueenAgent"))

# The API key is not here: it is written in the app's own Settings screen and lives in settings.json
# under ROOT. One road, and it can be changed without restarting the server.
#
# What a chat that picked no model of its own answers with. Every chat may carry its own choice, so
# this is the starting point rather than the only model. Verified against xAI's documentation on
# 2026-08-09.
XAI_MODEL = os.environ.get("XAI_MODEL", "grok-4.5")
XAI_BASE_URL = os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1")
