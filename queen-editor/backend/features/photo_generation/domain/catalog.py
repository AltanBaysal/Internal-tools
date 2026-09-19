"""What the two boxes of the photo panel mean -- a model, and a lora laid over it.

A model is a checkpoint and nothing more. A lora is one file with a strength, and the word the
prompt has to carry for it to show. Which lora a frame renders with is the lora box's answer alone:
a model has no arrangement of its own (madde 238).

Written down in two halves: the names and the files here, because this is the side that patches the
graph, and the version ids and the sizes in the notebook, because addresses live there
(FOUNDATION 9). test_every_model_the_app_knows_has_a_checkbox_of_its_own holds the two halves to the
same ids.

Which models a machine has is not this file's answer -- the notebook installed them and says so
through QE_PHOTO_MODELS. The loras need no such list: both files come down with the photo group
whatever was ticked.
"""

MODELS = [
    {"id": "nova3dcg", "label": "Nova 3DCG XL", "checkpoint": "nova3DCGXL_ilV90.safetensors"},
    # Read from Civitai's own API in madde 222's trial: a checkpoint on the Illustrious base, so the
    # graph's loras load onto it.
    {"id": "dasiwa", "label": "DaSiWa Illustrious | Anime",
     "checkpoint": "DasiwaIllustriousAnime_epitaphecstasy.safetensors"},
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
     "trigger": "translucent penetration"},
]

# What a frame that names no lora renders with, and what the panel fills an empty box with: the
# list's first row, read from one place so the two can never name different loras.
DEFAULT_LORA = LORAS[0]["id"]

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


def find_lora(lora_id):
    """The lora with this id, or None."""
    return next((lora for lora in LORAS if lora["id"] == lora_id), None)
