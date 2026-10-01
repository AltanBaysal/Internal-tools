"""Runtime configuration -- the single place for paths and ports."""
import os

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Vite writes the built frontend here; Flask serves it (see web/app.py).
DIST_DIR = os.path.join(os.path.dirname(_BACKEND_DIR), "frontend", "dist")

HOST = "127.0.0.1"
PORT = 8000

# Every project is a folder under this root. The folder name is NOT owned here:
# queeneditor.ipynb's CONFIG cell picks it (DRIVE_FOLDER) and passes the mounted path in
# QE_DRIVE_ROOT, so renaming it is a one-line change there. The literal below is only the fallback
# when nothing sets the variable.
DRIVE_ROOT = os.environ.get("QE_DRIVE_ROOT", "/content/drive/MyDrive/queenEditor")

# ComfyUI runs on the same Colab machine; the notebook can point us elsewhere (tests do too).
COMFY_URL = os.environ.get("QE_COMFY_URL", "http://127.0.0.1:8188")

# ComfyUI's own folder on this machine -- where the notebook installs each producer's model group,
# and where the panel looks to answer whether one is here. The notebook passes it in; the literal
# below is only the fallback.
COMFY_ROOT = os.environ.get("QE_COMFY_ROOT", "/content/ComfyUI")

# Where the notebook sends ComfyUI's output. When ComfyUI cannot be reached, its tail goes into the
# error: nothing else can say why it was gone, and the file dies with the session.
COMFY_LOG = os.environ.get("QE_COMFY_LOG", "/content/comfyui.log")

# Which models the notebook installed, by id. The disk cannot answer this: a checkpoint left from
# another run would be listed as if it had been ticked. Empty means photo was not installed, and the
# Model box offers nothing. The loras need no such list: they come with the photo group.
PHOTO_MODELS = [part.strip() for part in os.environ.get("QE_PHOTO_MODELS", "").split(",")
                if part.strip()]

# Everything the repo ships for the app to read -- the graphs and the disclaimer (madde 251).
_ASSETS_DIR = os.path.join(os.path.dirname(_BACKEND_DIR), "assets")

# The graph ships in the repo (our own copy -- never read collab-toolbox's file).
WORKFLOW_PATH = os.path.join(_ASSETS_DIR, "workflow_api.json")
# The video graph the same way: our own WAN 2.2 I2V export, exported from ComfyUI and committed.
VIDEO_WORKFLOW_PATH = os.path.join(_ASSETS_DIR, "workflow_video_api.json")
# The second video graph: a video that ends on a chosen picture. Its own pipeline rather than the
# one above with a node swapped, so it ships beside it and standard production is untouched.
VIDEO_FIRST_LAST_WORKFLOW_PATH = os.path.join(_ASSETS_DIR, "workflow_video_first_last_api.json")
# Which video model the notebook installed: "wan", "h3", or empty when video was not installed. The
# two never share a session (madde 243), and the disk cannot say which one was picked.
VIDEO_MODEL = os.environ.get("QE_VIDEO_MODEL", "")
# MiniMax H3's two graphs, exported in madde 213's trial and made sterile in 242: I2VA for a video
# that hangs on a photo, FL2VA for one that arrives at another.
H3_VIDEO_WORKFLOW_PATH = os.path.join(_ASSETS_DIR, "workflow_video_h3_api.json")
H3_VIDEO_FIRST_LAST_WORKFLOW_PATH = os.path.join(_ASSETS_DIR,
                                                 "workflow_video_h3_first_last_api.json")
# Sound has no graph: MMAudio runs inside this process, so its weights are a model file like any
# other, installed by the notebook rather than shipped here.

# The disclaimer laid over an exported video. It ships in the repo like the graphs do, and for the
# same reason: the notebook clones and builds nothing, so a file that is not committed is a file
# every export fails on. Which picture it is, is a file rather than a setting -- replacing the
# disclaimer is replacing this file, and no code hears about it.
DISCLAIMER_PATH = os.path.join(_ASSETS_DIR, "disclaimer.png")

RENDER_TIMEOUT = 15 * 60   # seconds for one photo; a T4 render is ~1 min, so this is a stall guard
VIDEO_TIMEOUT = 30 * 60    # seconds for one video; 5s of WAN takes minutes, so this is a stall guard
POLL_INTERVAL = 5          # longest gap between /history looks; ComfyUI's done notice cuts it short

# Queen AI: the model that writes every video's prompt looking at the frame's photo, and every
# sound's from its video's prompt (madde 400, 404). The key comes from Colab Secrets through the
# notebook, under the name QueenAgent's notebook reads too; without one the app still starts and
# photos still render, and a video or sound job stops the run with the client's own sentence.
DEEPSEEK_API_KEY = os.environ.get("QE_DEEPSEEK_API_KEY", "")
# Not read from the environment: nothing probes DeepSeek, so nothing outside the app has to ask
# what the app asks.
DEEPSEEK_MODEL = "deepseek-flash"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_TIMEOUT = 120     # seconds per request; one prompt is a short answer
