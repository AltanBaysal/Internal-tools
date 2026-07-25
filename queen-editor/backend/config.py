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
