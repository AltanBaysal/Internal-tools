"""What the two boxes of the photo panel mean -- a model, and a lora laid over it.

A model is a checkpoint and the lora arrangement it normally renders with, its standard. A lora is
one file with a strength, and the word the prompt has to carry for it to show. The panel's lora box
opens on Standart, which is no lora id at all: the model's own arrangement, so a frame sent that way
renders exactly as every photo did before the box existed (madde 237).

Written down in two halves: the names and the arrangements here, because this is the side that
patches the graph, and the version ids and the sizes in the notebook, because addresses live there
(FOUNDATION 9). test_every_model_the_app_knows_has_a_checkbox_of_its_own holds the two halves to the
same ids.

Which models a machine has is not this file's answer -- the notebook installed them and says so
through QE_PHOTO_MODELS. The loras need no such list: both files come down with the photo group
whatever was ticked.
"""

# The lora the photo graph has always shipped with, switched on in its Power Lora Loader. Named
# here because an arrangement replaces the loader's slots outright rather than adding to them: Nova
# has to put it back as its standard, or picking Nova would quietly drop it.
_USNR = {"lora": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors", "strength": 0.8}

MODELS = [
    {"id": "nova3dcg", "label": "Nova 3DCG XL",
     "checkpoint": "nova3DCGXL_ilV90.safetensors", "loras": [_USNR]},
    # Read from Civitai's own API in madde 222's trial: a checkpoint on the Illustrious base, so the
    # graph's loras load onto it. Its page names no lora it is meant to run with, so its standard
    # is bare.
    {"id": "dasiwa", "label": "DaSiWa Illustrious | Anime",
     "checkpoint": "DasiwaIllustriousAnime_epitaphecstasy.safetensors", "loras": []},
]

LORAS = [
    # Tried against two other candidates in ComfyUI on 15 September and picked on what came out:
    # this lora alone, at 0.9, with USNR switched off -- which is why a chosen lora replaces the
    # model's standard instead of joining it. The trigger travels with it because a lora nobody
    # names in the prompt renders an ordinary photo and raises nothing.
    {"id": "slime", "label": "Slime",
     "lora": "translucent_penetration_v5.safetensors", "strength": 0.9,
     "trigger": "translucent penetration"},
]

# What the value looked like before the two boxes: one `recipe:<id>` naming a model and a lora
# together. Frames planned then still carry it, in the plan and in the project's settings. No
# migration was written (the user's call); the renderer reads these as the pair they meant, and the
# two removed Novas fall to Nova 3DCG as madde 226 decided.
LEGACY = {
    "recipe:nova3dcg": ("nova3dcg", ""),
    "recipe:slime": ("nova3dcg", "slime"),
    "recipe:novaorange": ("nova3dcg", ""),
    "recipe:novaanime": ("nova3dcg", ""),
}
LEGACY_PREFIX = "recipe:"


def find_model(model_id):
    """The model with this id, or None."""
    return next((model for model in MODELS if model["id"] == model_id), None)


def find_lora(lora_id):
    """The lora with this id, or None."""
    return next((lora for lora in LORAS if lora["id"] == lora_id), None)
