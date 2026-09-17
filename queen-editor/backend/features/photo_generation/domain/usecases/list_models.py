"""Which rows the Model box offers.

A row is `{"value", "label"}`: what the renderer is sent, and what the user reads. The value is a
recipe id and the label is the name it was picked by.

The rows are the recipes the notebook installed, in the order it lists them. With none, photo was
not installed on this machine, and the answer is an empty list rather than a question to ComfyUI:
asking it for checkpoints there could only come back empty or fall over, and falling over put an
error card on the project screen (madde 229).
"""
from backend.features.photo_generation.domain import recipes


def list_models(chosen):
    # An id this checkout does not know is a notebook that moved ahead of it. Dropping the one row
    # keeps the rest usable; emptying the list would close the panel for a reason the user cannot
    # act on.
    found = [recipes.find(recipe_id) for recipe_id in chosen]
    return [{"value": recipes.PREFIX + recipe["id"], "label": recipe["label"]}
            for recipe in found if recipe]
