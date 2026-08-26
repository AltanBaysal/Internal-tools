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

# One road for the key, and this is it. On Colab it arrives from Secrets through the notebook, in a
# shell it is exported before the server starts -- and the app cannot tell the two apart. It used to
# be typed into a Settings screen instead, until that screen's own endpoint handed the key back in
# plain text to anyone holding a link that has no password.
#
# Empty rather than absent when it is unset: the app starts without a key and only asking for an
# answer fails.
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")

# What every chat answers with. Since Madde 82 this is the only place a model is named: a chat no
# longer carries one and nothing on the way to the engine can override it.
#
# Grok Build since Madde 72: $1/$2 per 1M against grok-4.3's $1.25/$2.50, and 256k of context
# against its 1M. The window is a quarter of what it was and the runs here are long -- a structure
# file, a scenario and a frame list pile up in one chat. That cost was named and accepted; the
# context work is Madde 71. Prices verified against xAI's documentation on 2026-08-18.
XAI_MODEL = os.environ.get("XAI_MODEL", "grok-build-0.1")
XAI_BASE_URL = os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1")
