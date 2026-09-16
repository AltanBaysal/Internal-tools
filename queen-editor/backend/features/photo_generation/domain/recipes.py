"""What a row in the Model box means -- a name, a checkpoint, and a lora arrangement.

A row used to be a file: the renderer listed its checkpoints and the panel showed them. That could
not hold Slime, which is not a file at all but Nova 3DCG's checkpoint with a different lora at a
different strength. So a row is a recipe now, and a recipe is written down in two halves: the name
and the arrangement here, because this is the side that patches the graph, and the version id and
the size in the notebook, because addresses live there (FOUNDATION 9).
test_every_recipe_the_app_knows_has_a_checkbox_of_its_own holds the two halves to the same ids.

Which recipes a machine actually has is not this file's answer -- the notebook installed them and
says so through QE_PHOTO_RECIPES. The disk cannot be asked: Slime brings Nova 3DCG's checkpoint
with it, so a Slime-only machine has that file sitting there and the renderer lists it.
"""

# The lora the photo graph has always shipped with, switched on in its Power Lora Loader. Named
# here because a recipe replaces the loader's slots outright rather than adding to them: the three
# checkpoint recipes have to put it back, or picking one would quietly drop it.
_USNR = {"lora": "USNR_STYLE_ILL_V1_lokr3-000024.safetensors", "strength": 0.8}

PREFIX = "recipe:"

RECIPES = [
    {"id": "nova3dcg", "label": "Nova 3DCG XL",
     "checkpoint": "nova3DCGXL_ilV90.safetensors", "loras": [_USNR], "trigger": ""},
    {"id": "novaorange", "label": "Nova Orange XL",
     "checkpoint": "novaOrangeXL_rexV10.safetensors", "loras": [_USNR], "trigger": ""},
    {"id": "novaanime", "label": "Nova Anime XL",
     "checkpoint": "novaAnimeXL_ilV190.safetensors", "loras": [_USNR], "trigger": ""},
    # Tried against the other two candidates in ComfyUI on 15 September and picked on what came
    # out: this lora alone, at 0.9, with USNR switched off. The trigger travels with it because a
    # lora nobody names in the prompt renders an ordinary photo and raises nothing.
    {"id": "slime", "label": "Slime",
     "checkpoint": "nova3DCGXL_ilV90.safetensors",
     "loras": [{"lora": "translucent_penetration_v5.safetensors", "strength": 0.9}],
     "trigger": "translucent penetration"},
]


def find(recipe_id):
    """The recipe with this id, or None. Callers decide what a miss means: the list drops it, the
    renderer stops -- a row nobody offers is a checkout behind its notebook, a render asking for
    one is a picture that would come back wrong with nothing saying so."""
    for recipe in RECIPES:
        if recipe["id"] == recipe_id:
            return recipe
    return None
