"""Which rows the Model box offers.

A row is `{"value", "label"}`: what the renderer is sent, and what the user reads. For a plain
checkpoint the two are the same file name; for a recipe they are not -- the value is an id and the
label is the name it was picked by.

With recipe ids from the notebook, those are the rows, in the order the notebook lists them. With
none -- a checkout running against any ComfyUI, and every test -- the answer is still the renderer's
own: what it can load, under the names it loads them by. The app keeps no list of checkpoints, and a
second one would disagree with the notebook the first time a model was added there.
"""
from backend.features.photo_generation.domain import recipes


def list_models(generator, chosen):
    if not chosen:
        return [{"value": name, "label": name} for name in generator.models()]
    # An id this checkout does not know is a notebook that moved ahead of it. Dropping the one row
    # keeps the rest usable; emptying the list would close the panel for a reason the user cannot
    # act on.
    found = [recipes.find(recipe_id) for recipe_id in chosen]
    return [{"value": recipes.PREFIX + recipe["id"], "label": recipe["label"]}
            for recipe in found if recipe]
