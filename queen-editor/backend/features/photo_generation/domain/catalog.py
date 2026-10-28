"""What the two boxes of the photo panel mean -- a model, and a lora laid over it.

A model is a checkpoint and nothing more, but for Krea 2 Turbo and Qwen Image 2.1 Turbo, which are
graphs of their own (madde 482, 499). A pick of the lora box is files laid over the model, each with
a strength, and the word the prompt has to carry for them to show. Which picks a model offers is
the lora box's answer alone (madde 238): the shared box, or the box a model's row carries when the
shared one does not fit it -- Illustrious loras on a graph of its own, or picks that draw well on
one checkpoint only (madde 486, 499, 501). A row says too when its model takes no negative; the
panel then shows that row's box and no negative box, and its frames record what they are drawn
with.

Written down in two halves: the names and the files here, because this is the side that patches the
graph, and the version ids and the sizes in the notebook, because addresses live there
(FOUNDATION 9). test_every_model_the_app_knows_has_a_checkbox_of_its_own holds the two halves to the
same ids.

Which models a machine has is not this file's answer -- the notebook installed them and says so
through QE_PHOTO_MODELS. The loras need no such list: the shared box's files come down with the
photo group whatever was ticked, and the files of a box a row carries with that model's tick.
"""

# Krea 2 Turbo and Qwen Image 2.1 Turbo: each rendered with its own graph, so main.py hands their
# frames to their own producers.
KREA2 = "krea2"
QWEN = "qwen21turbo"

# What makes Translucent Penetration show, on every model it is drawn on. The Qwen version's page
# lists no trained word -- its captions were rewritten in prose -- and the model page says these two
# words are all it takes; the user's call is that Queen Editor puts them in (madde 499).
SLIME_TRIGGER = "translucent penetration"

# The files the two own boxes lay over their models, one LoraLoaderModelOnly each. SNOFS is the lora
# of the user's Krea workflow, at its 0.8 (the user's call); test_workflow_asset holds the graph's
# node 53:15 to this row. The two Translucent Penetration versions are from the same Civitai page as
# Nova's Slime, at the 1.0 each version's page recommends.
SNOFS_KREA = {"lora": "snofs_krea_v1_5.safetensors", "strength": 0.8}
SLIME_KREA = {"lora": "translucent_penetration_v5_krea2.safetensors", "strength": 1.0}
SLIME_QWEN = {"lora": "translucent_penetration_v5_qwen_image_2_1.safetensors", "strength": 1.0}

# A pick of an own box is files laid one over another, and a trigger: SNOFS + Slime is two files,
# and Slime keeps SNOFS's effect under it (the user's words). The first row is what an empty pick
# draws.
KREA2_LORAS = [
    {"id": "snofs", "label": "SNOFS", "files": [SNOFS_KREA], "trigger": ""},
    {"id": "snofs_slime", "label": "SNOFS + Slime", "files": [SNOFS_KREA, SLIME_KREA],
     "trigger": SLIME_TRIGGER},
]
QWEN_LORAS = [
    {"id": "translucent_penetration", "label": "Translucent Penetration", "files": [SLIME_QWEN],
     "trigger": SLIME_TRIGGER},
]

LORAS = [
    # The lora the photo graph has always shipped with, switched on in its loader. First, because it
    # is the default: the user's call, on every model (madde 238).
    {"id": "usnr", "label": "USNR",
     "lora": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors", "strength": 0.8, "trigger": ""},
    # Tried against two other candidates in ComfyUI on 15 September and picked on what came out:
    # this lora alone, at 0.9, with USNR switched off -- which is why a pick fills the loader alone
    # instead of joining what was there. The trigger travels with it because a lora nobody names in
    # the prompt renders an ordinary photo and raises nothing.
    {"id": "slime", "label": "Slime",
     "lora": "translucent_penetration_v5.safetensors", "strength": 0.9,
     "trigger": SLIME_TRIGGER},
]

# What a frame that names no lora renders with, and what the panel fills an empty box with: the
# list's first row, read from one place so the two can never name different loras.
DEFAULT_LORA = LORAS[0]["id"]

# The two futa loras the user picked in madde 501's trial, at the user's strengths, and the words
# each one's Civitai page trains on: Flaccid Futa v3.0 IL and Futa on Male IL v2.
FUTA_FLACCID = {"lora": "futa_flaccid_v3.safetensors", "strength": 0.5}
FUTA_ON_MALE = {"lora": "futa_on_male_il_v2.safetensors", "strength": 1.0}
FUTA_FLACCID_TRIGGER = "flaccid futa"
FUTA_ON_MALE_TRIGGER = "futa on male, futa with male, futanari"


def _one_file(lora):
    """A row of the shared box as a pick of an own box: its one file, and its word."""
    return {"id": lora["id"], "label": lora["label"],
            "files": [{"lora": lora["lora"], "strength": lora["strength"]}],
            "trigger": lora["trigger"]}


# DaSiWa's box: the shared one, then the two futa picks. Neither draws well on Nova (the user's
# trial), so Nova keeps the shared box. Futa on male lays both files and carries both words, in the
# same order (the user's words: "0.50 futa flaccid 1.00 futa on male olucak 2 lora").
DASIWA_LORAS = [_one_file(lora) for lora in LORAS] + [
    {"id": "futa", "label": "Futa", "files": [FUTA_FLACCID], "trigger": FUTA_FLACCID_TRIGGER},
    {"id": "futa_on_male", "label": "Futa on male", "files": [FUTA_FLACCID, FUTA_ON_MALE],
     "trigger": f"{FUTA_FLACCID_TRIGGER}, {FUTA_ON_MALE_TRIGGER}"},
]

MODELS = [
    {"id": "nova3dcg", "label": "Nova 3DCG XL", "checkpoint": "nova3DCGXL_ilV90.safetensors"},
    # Read from Civitai's own API in madde 222's trial: a checkpoint on the Illustrious base, so the
    # graph's loras load onto it.
    {"id": "dasiwa", "label": "DaSiWa Illustrious | Anime",
     "checkpoint": "DasiwaIllustriousAnime_epitaphecstasy.safetensors", "loras": DASIWA_LORAS},
    # Picked in madde 485's trial; no checkpoint, because the graph loads a DiT, its encoder and its
    # VAE by name (assets/workflow_photo_krea2_api.json). No negative: the graph's is the prompt
    # zeroed, and at cfg 1 ComfyUI does not compute it.
    {"id": KREA2, "label": "Krea 2 Turbo", "loras": KREA2_LORAS, "negative": False},
    # The official Turbo template, 8 steps at cfg 1 (the user's call, madde 499), in
    # assets/workflow_photo_qwen_api.json. cfg 1 computes no negative here either.
    {"id": QWEN, "label": "Qwen Image 2.1 Turbo", "loras": QWEN_LORAS, "negative": False},
]

# Boş -- no lora at all. A value of its own rather than an empty one: empty is a frame that never
# named a lora, and the panel fills an empty box with the default.
NO_LORA = "none"

# What the value looked like before the two boxes: one `recipe:<id>` naming a model and a lora
# together. Frames planned then still carry it, in the plan and in the project's settings. No
# migration was written (the user's call); the renderer reads these as the pair they meant, and the
# two removed Novas fall to Nova 3DCG as madde 226 decided. USNR is named rather than left to the
# default: these frames were made with it, whatever the default becomes.
LEGACY = {
    "recipe:nova3dcg": ("nova3dcg", "usnr"),
    "recipe:slime": ("nova3dcg", "slime"),
    "recipe:novaorange": ("nova3dcg", "usnr"),
    "recipe:novaanime": ("nova3dcg", "usnr"),
}
LEGACY_PREFIX = "recipe:"


def find_model(model_id):
    """The model with this id, or None."""
    return next((model for model in MODELS if model["id"] == model_id), None)


def own_loras(model_id):
    """The box this model's row carries, or None when the shared lora box's pick is what renders --
    for a row that carries none, and any value a line carried from before models had rows."""
    return (find_model(model_id) or {}).get("loras")


def find_lora(lora_id):
    """The shared box's lora with this id, or None."""
    return next((lora for lora in LORAS if lora["id"] == lora_id), None)


def box_row(model_id, lora_id):
    """The row with this id in the box this model is drawn with, or None when that box does not hold
    it. The one place that knows which box that is: the model's own when its row carries one, the
    shared one otherwise -- whose row comes as a pick of one file, so every box answers in one shape:
    files laid one over another, and a trigger."""
    own = own_loras(model_id)
    if own is not None:
        return next((row for row in own if row["id"] == lora_id), None)
    lora = find_lora(lora_id)
    return _one_file(lora) if lora else None


def drawn_with(model_id, lora, negative):
    """(lora, negative) a photo of this model is drawn with -- what its plan line records, whoever
    writes the line (madde 486). The ones it was given, but for a model whose row says otherwise: a
    model with a box of its own draws a pick that box does not hold -- an empty one, or Nova's lora
    on a Krea line planned before 486 -- with the box's first row, and one that takes no negative
    is drawn with none. Boş stays Boş. An id this checkout does not know keeps the user's own."""
    model = find_model(model_id) or {}
    own = model.get("loras")
    if own and lora != NO_LORA and box_row(model_id, lora) is None:
        lora = own[0]["id"]
    return lora, negative if model.get("negative", True) else ""


def own_pick(model_id, lora):
    """The row of this model's own box a frame is drawn with, or None for Boş -- through drawn_with,
    so a producer draws exactly what the line records."""
    lora, _negative = drawn_with(model_id, lora, "")
    return None if lora == NO_LORA else box_row(model_id, lora)


def pick(model_id, lora):
    """What a frame of this model on the photo graph is drawn with, as box_row's shape -- no file and
    no word for Boş -- or None for an id its box does not hold.

    The line's lora as drawn_with records it, so a model whose row carries a box draws a pick that box
    does not hold with its first row (madde 499). The shared box draws an empty pick with the default
    (madde 238), and an id it does not know comes back None for the renderer to stop on.
    """
    lora, _negative = drawn_with(model_id, lora, "")
    if lora == NO_LORA:
        return {"files": [], "trigger": ""}
    return box_row(model_id, lora or DEFAULT_LORA)


def with_trigger(prompt, lora):
    """The prompt a frame is sent with when it is drawn with this row -- box_row's or pick's, or None
    for no lora at all: the row's word in front of the user's own. A lora loaded and never named in
    the prompt renders an ordinary photo and raises nothing anywhere -- the rule Slime has had since
    it came in, and the user's call for Krea's, Qwen's and DaSiWa's (madde 499, 501)."""
    return f"{lora['trigger']}, {prompt}" if lora and lora["trigger"] else prompt
