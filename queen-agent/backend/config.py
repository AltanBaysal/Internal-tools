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
# DeepSeek's own key, since Madde 146, and it travels the same road. No row spends it since Madde
# 334 -- the account has no credit, so the pair goes through OpenRouter -- and it is read all the
# same: going back is a madde of its own, and it is the two rows below pointing at
# https://api.deepseek.com again (no /v1: that is DeepSeek's own documented base, and the client
# appends /chat/completions to whatever it is handed).
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
# What every answer spends while the DeepSeek pair goes through OpenRouter (Madde 334), on the
# same road.
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Who may answer the DeepSeek pair on OpenRouter, and it is a terms choice rather than a routing
# preference.
#
# OpenRouter serves these weights from many providers and picks one on its own; `order` names
# DeepSeek and `allow_fallbacks` false is what keeps it there. Whichever provider answers is whose
# terms the request runs under, at least one of them forbids this work, and DeepSeek's are the ones
# the direct API ran under. When DeepSeek does not answer, the error shows rather than another
# provider answering -- the user's call of 25 September, and Madde 149's road with DeepSeek where
# DeepInfra was.
#
# A body field rather than a header: this is where OpenRouter reads it.
_ONLY_DEEPSEEK = {"provider": {"order": ["deepseek"], "allow_fallbacks": False}}

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
# Since Madde 334 a row can say two more things, and only the DeepSeek pair does: `model` is what
# the provider is told when that is not the id itself, and `extra` is what the row adds to the body
# of every request it makes. Absent rather than empty on Grok's -- a field saying nothing is noise.
MODELS = {
    # Nothing points here since Madde 202 moved the writing to DeepSeek, and by Madde 183's own rule
    # -- a row nobody will use is dead configuration -- this one would go. Kept knowingly: deleting
    # it takes XAI_API_KEY and its secret in the notebook with it, and what the run was for was
    # trying another writer. If the lines come out worse, going back is the constant below.
    "grok-4.3": {"base_url": "https://api.x.ai/v1", "key": "XAI_API_KEY"},
    # Through OpenRouter until DeepSeek's own account is paid for (Madde 334). The ids stay
    # DeepSeek's own -- the menu and every message on disk carry them -- and OpenRouter is told
    # V4.1 Flash for both, because that is what DeepSeek's own API had been answering both with
    # since 14 September.
    "deepseek-v4-flash": {
        "base_url": "https://openrouter.ai/api/v1",
        "key": "OPENROUTER_API_KEY",
        "model": "deepseek/deepseek-v4.1-flash",
        "extra": _ONLY_DEEPSEEK,
    },
    "deepseek-v4-pro": {
        "base_url": "https://openrouter.ai/api/v1",
        "key": "OPENROUTER_API_KEY",
        "model": "deepseek/deepseek-v4.1-flash",
        "extra": _ONLY_DEEPSEEK,
    },
}

# What answers when a turn named nothing -- which is every message written before Madde 146.
#
# The cheaper of the two the composer offers since Madde 177, and the same id models.js defaults to:
# one of them answers what an empty button says and this one answers where the request goes, and the
# two parting would show a name on the screen that nothing on the wire matched.
DEFAULT_MODEL = "deepseek-v4-flash"

# Who writes a frame's action when a tool asks for one (Madde 175). A role rather than a choice, by
# the user's decision of 5 September: what the composer offers is which model runs the conversation,
# and no picker on the screen reaches this line. It is here because it is a wiring fact -- the same
# kind of fact as an address or a key -- and because the model it names is chosen for what it will
# write rather than for how it reasons.
#
# DeepSeek since Madde 202 (the user's decision, 8 September). The role was built on 175's finding
# that the model running the conversation would not write that kind of sentence; it writes it now,
# and a second provider for one line was buying nothing. It is the same id DEFAULT_MODEL carries,
# and the two are still separate decisions: one says what an empty button means, this one says who
# writes an action, and either can move without the other.
PROMPT_MODEL = "deepseek-v4-flash"


def engine_for(model_id):
    """Which model, over which address, spending which key, told the provider under which name, and
    carrying what in its body.

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
    # `get` on the last two: a row whose provider knows the model by its id has no other name to
    # give, and a row with nothing for the body has nothing -- a row with nothing to say rather than
    # a row missing something.
    return (
        chosen,
        wiring["base_url"],
        globals()[wiring["key"]],
        wiring.get("model", chosen),
        wiring.get("extra"),
    )
