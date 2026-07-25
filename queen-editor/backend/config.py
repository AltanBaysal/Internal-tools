"""Runtime configuration -- the single place for paths and ports."""
import os

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Vite writes the built frontend here; Flask serves it (see web/app.py).
DIST_DIR = os.path.join(os.path.dirname(_BACKEND_DIR), "frontend", "dist")

HOST = "127.0.0.1"
PORT = 8000

# Every project is a folder under this root. The folder name is NOT owned here: app.ipynb's CONFIG
# cell picks it (DRIVE_FOLDER) and passes the mounted path in QE_DRIVE_ROOT, so renaming it is a
# one-line change there. The literal below is only the fallback when nothing sets the variable.
DRIVE_ROOT = os.environ.get("QE_DRIVE_ROOT", "/content/drive/MyDrive/queenEditor")

# ComfyUI runs on the same Colab machine; the notebook can point us elsewhere (tests do too).
COMFY_URL = os.environ.get("QE_COMFY_URL", "http://127.0.0.1:8188")

# The graph ships in the repo (our own copy -- never read collab-toolbox's file).
WORKFLOW_PATH = os.path.join(os.path.dirname(_BACKEND_DIR), "workflow_api.json")

RENDER_TIMEOUT = 15 * 60   # seconds for one photo; a T4 render is ~1 min, so this is a stall guard
POLL_INTERVAL = 5          # seconds between /history polls
