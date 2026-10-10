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
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

# Which models exist, and what each id means to the transport. Nothing on the screen names one
# since Madde 358, so no name or price a person would read is kept anywhere.
#
# The key's NAME sits here rather than its value, so this stays a mapping and carries no secret.
# engine_for is the one place that reads the environment.
#
# Madde 82 named one model here, Madde 146 made it three and put a picker in the composer, and
# Madde 336 left DeepSeek one name. Madde 358 took the picker out: the constant below says which
# row answers. Madde 383 took out the other provider's row, which nothing had pointed at since
# Madde 202, and its key with it.
MODELS = {
    # No /v1: this is DeepSeek's own documented base, and the client appends /chat/completions to
    # whatever it is handed.
    #
    # One name of DeepSeek's since Madde 336, the one the model has today. DeepSeek's notice of 10
    # September closed deepseek-v4-pro -- its requests go to Flash, billed as Flash, with no error --
    # and left deepseek-v4-flash an alias. Messages on disk still name both, as a record; nothing is
    # steered by it.
    "deepseek-flash": {"base_url": "https://api.deepseek.com", "key": "DEEPSEEK_API_KEY"},
}

# What answers every turn. The one place that says so since Madde 358: the screen names no model and
# the browser sends none, so this line is the whole of the choice.
DEFAULT_MODEL = "deepseek-flash"

# How long a model request may say nothing before it is cut (Madde 460). Silence, not total length:
# an answer that keeps talking runs as long as it needs, and any byte counts as talking -- the
# keep-alive comments a service sends while it queues a request too. A cut try is one failed try of
# the black box, so a service that has gone quiet for good costs each step of a turn five of these
# before its card shows. 180 is where it starts; a long DeepSeek turn has not been measured against
# it yet.
MODEL_IDLE_SECONDS = 180


def engine_for(model_id):
    """Which model, over which address, spending which key -- for a row of the table above.

    No fallback: the only caller is main.py walking the table itself, so an id outside it is a
    wiring mistake, and it stops the app at startup rather than being answered by another model.
    """
    wiring = MODELS[model_id]
    # The module's own constant, looked up by the name the row carries -- not a second read of the
    # environment. There is one road for a key and it is the assignment above; a row that fetched
    # its own would be a second one, and the two would part the day either moved.
    return model_id, wiring["base_url"], globals()[wiring["key"]]
