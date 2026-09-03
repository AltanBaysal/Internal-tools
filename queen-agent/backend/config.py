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
# The second provider's key, since Madde 146, and it travels the same road. The notebook demands
# all of them: the composer draws five rows, so a run opened on fewer keys would promise models it
# cannot answer with.
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
# The third, since Madde 149. Not a fourth model but a second road to two of the existing ones:
# DeepSeek V4's weights are MIT, so which provider runs them is a choice rather than a given.
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# What OpenRouter is told to do with a request, and it is not a routing preference.
#
# OpenRouter serves these weights from many providers and picks one on its own; `allow_fallbacks`
# false is what stops it. Which provider answers decides whose terms the request runs under, and
# those terms are not alike -- at least one of them forbids this work outright. So the pin is what
# keeps the run inside a contract that permits it, and dropping it would not merely make the answer
# slower.
#
# A body field rather than a header: this is where OpenRouter reads it.
_PINNED_TO_DEEPINFRA = {"provider": {"order": ["deepinfra"], "allow_fallbacks": False}}

# What each model id means to the transport, and nothing else. The list a person reads -- names and
# prices -- is the frontend's (models.js), exactly as the skills' list is: what this side knows is
# what an id resolves to, never which one is selected.
#
# The key's NAME sits here rather than its value, so this stays a mapping and carries no secret.
# engine_for is the one place that reads the environment.
#
# Madde 82 named one model here and Madde 146 made it three. That madde tore the picking machinery
# out because a single model left it idle; two more ended the premise rather than overturned it.
#
# Five since Madde 149, but still three models: the last two are the DeepSeek pair reached a second
# way. `extra` is what a row adds to the body of every request it makes, and only those two have
# anything to say there. Absent rather than empty on the rest -- a field saying nothing in three
# rows out of five is noise.
MODELS = {
    "grok-build-0.1": {"base_url": "https://api.x.ai/v1", "key": "XAI_API_KEY"},
    # No /v1: this is DeepSeek's own documented base, and the client appends /chat/completions to
    # whatever it is handed.
    "deepseek-v4-flash": {"base_url": "https://api.deepseek.com", "key": "DEEPSEEK_API_KEY"},
    "deepseek-v4-pro": {"base_url": "https://api.deepseek.com", "key": "DEEPSEEK_API_KEY"},
    # The first ids with a slash in them: OpenRouter's own naming, and nothing here takes an id
    # apart -- it is carried, compared, and looked up in this table.
    "deepseek/deepseek-v4-flash-0731": {
        "base_url": "https://openrouter.ai/api/v1",
        "key": "OPENROUTER_API_KEY",
        "extra": _PINNED_TO_DEEPINFRA,
    },
    "deepseek/deepseek-v4-pro-0813": {
        "base_url": "https://openrouter.ai/api/v1",
        "key": "OPENROUTER_API_KEY",
        "extra": _PINNED_TO_DEEPINFRA,
    },
}

# What answers when a turn named nothing -- which is every message written before Madde 146.
DEFAULT_MODEL = "grok-build-0.1"


def engine_for(model_id):
    """Which model, over which address, spending which key, carrying what in its body.

    An id nobody knows falls back to the default rather than raising, and so does an empty one:
    a record can name a model that has since been dropped, and every message on disk from before
    this field names none at all. Neither may stop a chat from being answered -- the rule
    skills.instruction_for keeps for the same reason.
    """
    chosen = model_id if model_id in MODELS else DEFAULT_MODEL
    wiring = MODELS[chosen]
    # The module's own constant, looked up by the name the row carries -- not a second read of the
    # environment. There is one road for a key and it is the assignment above; a row that fetched
    # its own would be a second one, and the two would part the day either moved.
    #
    # `get` on the last: three of the five rows have nothing to add to the body, and that is a row
    # with nothing to say rather than a row missing something.
    return chosen, wiring["base_url"], globals()[wiring["key"]], wiring.get("extra")
