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

# ComfyUI's own folder on this machine -- where a producer's model group is installed. The notebook
# passes it in; the literal below is only the fallback.
COMFY_ROOT = os.environ.get("QE_COMFY_ROOT", "/content/ComfyUI")

# The graph ships in the repo (our own copy -- never read collab-toolbox's file).
WORKFLOW_PATH = os.path.join(os.path.dirname(_BACKEND_DIR), "workflow_api.json")
# The video graph the same way: our own WAN 2.2 I2V export, exported from ComfyUI and committed.
VIDEO_WORKFLOW_PATH = os.path.join(os.path.dirname(_BACKEND_DIR), "workflow_video_api.json")
# Sound has no graph: MMAudio runs inside this process, so its weights are a model file the
# producers feature installs, not an asset that ships here (user's decision, 2026-08-13).

RENDER_TIMEOUT = 15 * 60   # seconds for one photo; a T4 render is ~1 min, so this is a stall guard
VIDEO_TIMEOUT = 30 * 60    # seconds for one video; 5s of WAN takes minutes, so this is a stall guard
POLL_INTERVAL = 5          # seconds between /history polls

# Civitai's login cookie: the gated model files sit behind it. Comes from Colab Secrets through the
# notebook, like the xAI key; empty means those installs stop and say which source they wanted.
CIVITAI_COOKIE = os.environ.get("QE_CIVITAI_COOKIE", "")

# The language model that writes a video's prompt (design v3, madde 27). The key comes from Colab
# Secrets through the notebook; without one the app still starts and photos still render -- only a
# video job's turn stops the run, with the client's own sentence.
XAI_API_KEY = os.environ.get("QE_XAI_API_KEY", "")
XAI_MODEL = os.environ.get("QE_XAI_MODEL", "grok-4.3")
XAI_URL = os.environ.get("QE_XAI_URL", "https://api.x.ai/v1/chat/completions")
XAI_TIMEOUT = 120          # seconds per request; one prompt is a short answer
