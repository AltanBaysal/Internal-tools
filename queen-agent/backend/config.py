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

# What a chat that picked no model of its own answers with. Every chat may carry its own choice, so
# this is the starting point rather than the only model.
#
# grok-4.3 rather than a newer one: half the price ($1.25/$2.50 against $2/$6) and twice the context
# (1M against 500k), and the runs here are long -- a structure file, a scenario and a frame list
# pile up in one chat. Verified against xAI's documentation on 2026-08-18.
XAI_MODEL = os.environ.get("XAI_MODEL", "grok-4.3")
XAI_BASE_URL = os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1")
